import json
from typing import Optional,List
from datetime import datetime
from fastapi import APIRouter, UploadFile,Depends, File, Form, HTTPException, Query
import requests
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from database import get_db
from models import User,Course,Assignment,Question,AssignmentQuestion,AssignmentSubmission
from user_routes import get_current_user
from pydantic import BaseModel
from ragflow_client import score_subjective

router = APIRouter(prefix="/assignment", tags=["作业"])

class AssignmentChatRequest(BaseModel):
    question: str
    history: list = []

class QuestionItem(BaseModel):
    type: str
    content: str
    options: Optional[List[str]] = None
    answer: Optional[str] = None
    points: Optional[float] = 1.0
    key_knowledge: Optional[str] = None  # 关键知识点
    difficulty: Optional[str] = None  # 题目难度

class AssignmentCreateRequest(BaseModel):
    course_id: int
    title: str
    description: str
    deadline: datetime
    question_ids: List[int] = []  # 题目ID列表
    content: Optional[str] = None  #AI助手生成的纯文本内容
    answer: Optional[str] = None   #AI助手生成的参考答案




#布置考核内容
@router.post("/create")
def create_structured_assignment(
    data: AssignmentCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    '''创建整个考核内容'''
    course = db.query(Course).filter(Course.id == data.course_id).first()
    if not course or course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权创建此课程的作业")

    assignment = Assignment(
        title=data.title,
        description=data.description,
        content=data.content,
        answer=data.answer,
        deadline=data.deadline,
        course_id=data.course_id,
        creator_id=current_user.id
    )

    # 验证题目是否存在
    for i, q_id in enumerate(data.question_ids):
        question = db.query(Question).filter(Question.id == q_id).first()
        if not question:
            raise HTTPException(status_code=404, detail=f"题目ID {q_id} 不存在")
        
        # 创建作业题目记录，引用题目库中的题目
        assignment_question = AssignmentQuestion(
            assignment_id=assignment.id,
            question_id=q_id,
            order=i + 1,  # 题目顺序
            points=question.points  # 使用题目库中的分值
        )
        assignment.questions.append(assignment_question)

    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    return {"msg": "考核任务创建成功", "assignment_id": assignment.id}

#删除考核内容
@router.delete("/{assignment_id}")
def delete_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user:User = Depends(get_current_user)   
):
    '''删除考核内容'''
    # 检查作业是否存在
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="考核内容不存在")
    
    #检查权限：是否为教师
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="仅教师可删除作业")
    
    db.delete(assignment)
    db.commit()
    return {"msg": "考核内容删除成功"}

#列出所有考核内容
@router.get("/all")
def get_all_assignments(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    '''列出所有考核内容'''
    if current_user.role != "teacher" :
        raise HTTPException(status_code=403, detail="仅教师可查看所有考核内容")
    
    # 参数验证
    if page < 1:
        raise HTTPException(status_code=400, detail="页码必须大于0")
    if page_size < 1 or page_size > 100:
        raise HTTPException(status_code=400, detail="每页大小必须在1-100之间")
    
    offset = (page - 1) * page_size 
    query = db.query(Assignment)

    total_count = query.count()
    assignments = query.offset(offset).limit(page_size).all()
    #教师只能看到自己创建的assignment
    
    assignments = query.filter(Assignment.creator_id == current_user.id).all()

    #格式化返回数据
    assignment_list = [
        {
            "id": a.id,
            "title": a.title,
            "description": a.description,
            "deadline": a.deadline,
            "course_id": a.course_id,
            "created_at": a.created_at,
            "creator_id": a.creator_id
        }
        for a in assignments
    ]
    return {
        "data": assignment_list,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total_count,
            "total_pages": (total_count + page_size - 1) // page_size,
            "has_next": page * page_size < total_count,
            "has_prev": page > 1
        }
    }


#题目管理接口
@router.post("/questions")
def add_question(
    question: QuestionItem,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    '''添加题目'''
    # 检查用户有权限
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="仅教师可添加题目")

    # 根据题目类型处理options字段
    options_json = None
    if question.type in ["选择", "单选", "多选"] and question.options:
        options_json = json.dumps(question.options)
    elif question.type in ["选择", "单选", "多选"] and not question.options:
        raise HTTPException(status_code=400, detail="选择题必须提供选项")

    # 创建题目记录
    new_question = Question(
        type=question.type,
        content=question.content,
        options=options_json,  # 只有选择题才有options
        answer=question.answer,
        points=question.points,
        key_knowledge=question.key_knowledge,
        difficulty=question.difficulty  # 添加难度字段
    )

    db.add(new_question)
    db.commit()
    db.refresh(new_question)

    return {
        "msg": "题目添加成功",
        "question_id": new_question.id
    }


#删除题目
@router.delete("/questions/{question_id}")
def delete_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    '''删除题目'''
    # 检查题目是否存在
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")

    # 检查是否有作业正在使用此题目
    used_questions = db.query(AssignmentQuestion).filter(AssignmentQuestion.question_id == question_id).first()
    if used_questions:
        raise HTTPException(status_code=400, detail="此题目正在被作业使用，无法删除")

    #检查权限：是否为教师
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="仅教师可删除题目")
    db.delete(question)
    db.commit()

    return {"msg": "题目删除成功"}

#查看题库
@router.get("/questions/all")
def get_all_questions(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    question_type: Optional[str] = Query(None, description="题目类型筛选"),  # 可选：按题目类型筛选
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    '''列出所有题目'''
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="仅教师可查看所有题库")
    
    # 参数验证
    if page < 1:
        raise HTTPException(status_code=400, detail="页码必须大于0")
    if page_size < 1 or page_size > 100:
        raise HTTPException(status_code=400, detail="每页大小必须在1-100之间")
    
    offset = (page - 1) * page_size
    query = db.query(Question)
    
    # 按类型筛选
    if question_type:
        query = query.filter(Question.type == question_type)
    
    total_count = query.count()
    questions = query.offset(offset).limit(page_size).all()
    
    # 格式化返回数据
    question_list = [
        {
            "id": q.id,
            "type": q.type,
            "content": q.content,
            "options": json.loads(q.options) if q.options else None,
            "answer": q.answer,
            "points": q.points,
            "key_knowledge": q.key_knowledge,
            "difficulty": q.difficulty  # 添加难度字段
        }
        for q in questions
    ]
    
    return {
        "data": question_list,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total_count,
            "total_pages": (total_count + page_size - 1) // page_size,
            "has_next": page * page_size < total_count,
            "has_prev": page > 1
        },
        "filter": {
            "question_type": question_type
        }
    }

#单独添加题目到作业
@router.post("/{assignment_id}/questions")
def add_question_to_assignment(
    assignment_id: int,
    question_id: int = Query(..., description="题目ID"),
    points: Optional[float] = Query(None, description="可选的分值覆盖"),  # 可选的分值覆盖
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    '''单独添加题目到作业'''
    # 检查作业是否存在
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="作业不存在")
    
    # 检查权限：只有作业所属课程的教师才能添加题目
    course = db.query(Course).filter(Course.id == assignment.course_id).first()
    if not course or course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权为此作业添加题目")

    # 检查题目是否存在
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")

    # 获取当前作业的最大顺序号
    max_order = db.query(AssignmentQuestion).filter(
        AssignmentQuestion.assignment_id == assignment_id
    ).order_by(AssignmentQuestion.order.desc()).first()
    next_order = (max_order.order + 1) if max_order else 1

    # 创建新题目记录
    new_assignment_question = AssignmentQuestion(
        assignment_id=assignment_id,
        question_id=question_id,
        order=next_order,
        points=points if points is not None else question.points
    )

    db.add(new_assignment_question)
    db.commit()
    db.refresh(new_assignment_question)

    return {
        "msg": "题目添加成功", 
        "question_id": new_assignment_question.question_id,
        "assignment_id": assignment_id,
        "order": next_order
    }

#获取考核内容的所有题目
@router.get("/{assignment_id}/questions")
def get_assignment_questions(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    '''获取考核内容的所有题目'''
    # 检查作业是否存在
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="作业不存在")
    
    # 检查权限：只有课程的学生或教师才能查看题目
    course = db.query(Course).filter(Course.id == assignment.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    
    # 检查用户是否有权限查看（教师或学生）
    is_teacher = course.teacher_id == current_user.id
    is_student = current_user in course.students
    
    if not (is_teacher or is_student):
        raise HTTPException(status_code=403, detail="无权查看此作业的题目")

    # 检查学生是否已提交作业（用于决定是否显示答案）
    student_has_submitted = False
    if is_student:
        submission = db.query(AssignmentSubmission).filter(
            AssignmentSubmission.assignment_id == assignment_id,
            AssignmentSubmission.student_id == current_user.id
        ).first()
        student_has_submitted = submission is not None

    # 获取作业题目，按顺序排列
    questions = db.query(AssignmentQuestion).filter(
        AssignmentQuestion.assignment_id == assignment_id
    ).order_by(AssignmentQuestion.order).all()
    
    result = []
    for q in questions:
        # 获取题目库中的详细信息
        question_bank = q.question
        question_data = {
            "id": q.question_id,
            "order": q.order,
            "type": question_bank.type,
            "content": question_bank.content,
            "points": q.points,  # 使用作业中的分值（可能覆盖题目库中的分值）
            "key_knowledge": question_bank.key_knowledge,
            "options": json.loads(question_bank.options) if question_bank.options else None,
            "difficulty": question_bank.difficulty  # 添加难度字段
        }
        # 教师或已提交作业的学生才能看到答案
        if is_teacher or student_has_submitted:
            question_data["answer"] = question_bank.answer
        
        result.append(question_data)

    return {
        "assignment_id": assignment_id,
        "questions": result
    }

#删除作业中的特定题目
@router.delete("/{assignment_id}/questions/{question_id}")
def delete_question_from_assignment(
    assignment_id: int,
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    '''删除作业中的特定题目'''
    # 检查作业是否存在
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="作业不存在")
    
    # 检查权限：只有作业所属课程的教师才能删除题目
    course = db.query(Course).filter(Course.id == assignment.course_id).first()
    if not course or course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权删除此作业的题目")

    # 检查题目是否存在且属于该作业
    question = db.query(AssignmentQuestion).filter(
        AssignmentQuestion.assignment_id == assignment_id,
        AssignmentQuestion.question_id == question_id
    ).first()
    
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")

    db.delete(question)
    db.commit()

    return {"msg": "题目删除成功"}

#调整作业中题目的顺序
@router.put("/{assignment_id}/questions/{question_id}/order")
def update_question_order(
    assignment_id: int,
    question_id: int,
    new_order: int = Query(..., description="新的题目顺序"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    '''调整作业中题目的顺序'''
    # 检查作业是否存在
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="作业不存在")
    
    # 检查权限：只有作业所属课程的教师才能调整顺序
    course = db.query(Course).filter(Course.id == assignment.course_id).first()
    if not course or course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权调整此作业的题目顺序")

    # 检查题目是否存在且属于该作业
    question = db.query(AssignmentQuestion).filter(
        AssignmentQuestion.assignment_id == assignment_id,
        AssignmentQuestion.question_id == question_id
    ).first()
    
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")

    # 检查新顺序是否有效
    if new_order < 1:
        raise HTTPException(status_code=400, detail="顺序号必须大于0")

    # 获取作业的总题目数
    total_questions = db.query(AssignmentQuestion).filter(AssignmentQuestion.assignment_id == assignment_id).count()
    if new_order > total_questions:
        raise HTTPException(status_code=400, detail=f"顺序号不能超过题目总数 {total_questions}")

    old_order = question.order
    
    # 如果顺序没有变化，直接返回
    if old_order == new_order:
        return {"msg": "顺序未发生变化"}

    # 更新其他题目的顺序
    if old_order < new_order:
        # 向后移动：将中间题目的顺序减1
        db.query(AssignmentQuestion).filter(
            AssignmentQuestion.assignment_id == assignment_id,
            AssignmentQuestion.order > old_order,
            AssignmentQuestion.order <= new_order
        ).update({AssignmentQuestion.order: AssignmentQuestion.order - 1})
    else:
        # 向前移动：将中间题目的顺序加1
        db.query(AssignmentQuestion).filter(
            AssignmentQuestion.assignment_id == assignment_id,
            AssignmentQuestion.order >= new_order,
            AssignmentQuestion.order < old_order
        ).update({AssignmentQuestion.order: AssignmentQuestion.order + 1})

    # 更新目标题目的顺序
    question.order = new_order
    db.commit()

    return {"msg": "题目顺序调整成功", "new_order": new_order}


#自动生成考核内容
# 知识点掌握程度评分
class KnowledgePointScore(BaseModel):
    knowledge_point: str
    mastery_score: float  # 0-1之间的掌握程度分数
#选择题目的种类和数量
class QuestionAmount(BaseModel):
    type: str
    amount: int

class AutoAssignmentRequest(BaseModel):
    course_id: int
    knowledge_points: List[KnowledgePointScore]
    question_amount: List[QuestionAmount]
    title: Optional[str] = None
    description: Optional[str] = None
    deadline: datetime

@router.post("/auto-generate")
def auto_generate_assignment(
    request: AutoAssignmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    '''自动生成考核内容'''
    import random  # 添加random模块导入

    # 检查课程是否存在
    course = db.query(Course).filter(Course.id == request.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")

    # 按掌握程度排序并选择最低的3个知识点
    sorted_points = sorted(request.knowledge_points, key=lambda x: x.mastery_score)
    weak_points = sorted_points[:3]
    weak_point_names = [point.knowledge_point for point in weak_points]

    # 根据request.question_amount随机选择题目
    selected_questions = []
    for q_amount in request.question_amount:
        questions = db.query(Question).filter(
            Question.type == q_amount.type,
            Question.key_knowledge.in_(weak_point_names)
        ).all()
        
        if len(questions) >= q_amount.amount:
            # 使用random.sample进行随机选择
            selected_questions.extend(random.sample(questions, q_amount.amount))
        else:
            raise HTTPException(status_code=400, detail=f"{q_amount.type}题数量不足")

    # 生成作业标题和描述（如果未提供）
    if not request.title:
        knowledge_points_str = "、".join(weak_point_names)
        request.title = f"知识点强化练习 - {knowledge_points_str}"
    
    if not request.description:
        request.description = f"本次练习重点针对以下知识点：{', '.join(weak_point_names)}"

    # 创建作业
    assignment = Assignment(
        title=request.title,
        description=request.description,
        deadline=request.deadline,
        course_id=request.course_id,
        creator_id=current_user.id  # 添加creator_id字段
    )
    db.add(assignment)
    db.flush()  # 获取assignment.id

    # 添加题目到作业
    for i, question in enumerate(selected_questions):
        assignment_question = AssignmentQuestion(
            assignment_id=assignment.id,
            question_id=question.id,
            order=i + 1,
            points=question.points
        )
        db.add(assignment_question)

    db.commit()
    db.refresh(assignment)

    return {
        "msg": "考核内容自动生成成功",
        "assignment_id": assignment.id,
        "title": assignment.title,
        "question_count": len(selected_questions),
        "knowledge_points": weak_point_names
    }




# 自动化阅卷
# 用户答案模型
class UserAnswer(BaseModel):
    question_id: int
    answer: str

class AutoGradeRequest(BaseModel):
    answers: List[UserAnswer]

@router.post("/auto-grade/{assignment_id}")
async def auto_grade_assignment(
    assignment_id: int,
    request: AutoGradeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    '''自动化阅卷'''
    # 检查作业是否存在
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="作业不存在")

    # 检查是否已经提交过
    existing_submission = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.assignment_id == assignment_id,
        AssignmentSubmission.student_id == current_user.id
    ).first()
    
    if existing_submission:
        raise HTTPException(status_code=400, detail="该作业已经提交过，不能重复提交")

    # 获取作业的所有题目
    assignment_questions = db.query(AssignmentQuestion).filter(
        AssignmentQuestion.assignment_id == assignment_id
    ).order_by(AssignmentQuestion.order).all()

    # 创建答案字典，方便查找
    answer_dict = {ans.question_id: ans.answer for ans in request.answers}
    
    # 存储评分结果
    grading_results = []
    total_score = 0
    total_points = 0

    # 遍历每个题目进行评分
    for aq in assignment_questions:
        question = db.query(Question).filter(Question.id == aq.question_id).first()
        if not question:
            continue

        user_answer = answer_dict.get(question.id)
        if user_answer is None:
            # 如果用户没有回答这道题
            result = {
                "question_id": question.id,
                "type": question.type,
                "score": 0,
                "max_points": aq.points,
                "feedback": "未作答"
            }
        else:
            # 根据题目类型进行评分
            if question.type in ["选择", "填空"]:
                # 选择题和填空题直接比对答案
                score = aq.points if user_answer.strip() == question.answer.strip() else 0
                feedback = "正确" if score > 0 else "错误"
                result = {
                    "question_id": question.id,
                    "type": question.type,
                    "score": score,
                    "max_points": aq.points,
                    "feedback": feedback
                }
            elif question.type == "简答":
                # 简答题使用AI评分
                try:
                    score, feedback = await score_subjective(
                        #chat_id="cf6fdbd05e3c11f09a2b1a7dbaf3bdd9", 
                        reference=question.answer,
                        student_answer=user_answer,
                        current_user=current_user
                    )
                    # 将0-100的分数转换为题目分值
                    actual_score = (score / 100) * aq.points
                    result = {
                        "question_id": question.id,
                        "type": question.type,
                        "score": actual_score,
                        "max_points": aq.points,
                        "feedback": feedback
                    }
                except Exception as e:
                    result = {
                        "question_id": question.id,
                        "type": question.type,
                        "score": 0,
                        "max_points": aq.points,
                        "feedback": f"AI评分失败: {str(e)}"
                    }
            else:
                # 未知题型
                result = {
                    "question_id": question.id,
                    "type": question.type,
                    "score": 0,
                    "max_points": aq.points,
                    "feedback": "未知题型"
                }

        grading_results.append(result)
        total_score += result["score"]
        total_points += result["max_points"]

    # 计算总分和百分比
    percentage = (total_score / total_points * 100) if total_points > 0 else 0

    # 保存提交记录到数据库
    try:
        submission = AssignmentSubmission(
            assignment_id=assignment_id,
            student_id=current_user.id,
            submit_time=datetime.utcnow(),
            answer=json.dumps(answer_dict, ensure_ascii=False),  # 保存学生答案
            score=total_score,  # 保存总分
            feedback=json.dumps(grading_results, ensure_ascii=False)  # 保存评分详情
        )
        
        db.add(submission)
        db.commit()
        db.refresh(submission)
        
        print(f"✅ 提交记录已保存 - 学生ID: {current_user.id}, 作业ID: {assignment_id}, 总分: {total_score}")
        
    except Exception as e:
        print(f"❌ 保存提交记录失败: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"保存提交记录失败: {str(e)}")

    return {
        "assignment_id": assignment_id,
        "total_score": total_score,
        "total_points": total_points,
        "percentage": percentage,
        "results": grading_results,
        "submission_id": submission.id  # 返回提交记录ID
    }

# 在现有的路由中添加以下编辑题目的接口

# 编辑题目
@router.put("/questions/{question_id}")
def update_question(
    question_id: int,
    question: QuestionItem,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    '''编辑题目'''
    # 检查用户权限
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="仅教师可编辑题目")

    # 检查题目是否存在
    existing_question = db.query(Question).filter(Question.id == question_id).first()
    if not existing_question:
        raise HTTPException(status_code=404, detail="题目不存在")

    # 根据题目类型处理options字段
    options_json = None
    if question.type in ["选择", "单选", "多选"] and question.options:
        options_json = json.dumps(question.options)
    elif question.type in ["选择", "单选", "多选"] and not question.options:
        raise HTTPException(status_code=400, detail="选择题必须提供选项")

    # 更新题目信息
    existing_question.type = question.type
    existing_question.content = question.content
    existing_question.options = options_json
    existing_question.answer = question.answer
    existing_question.points = question.points if question.points is not None else existing_question.points
    existing_question.key_knowledge = question.key_knowledge
    existing_question.difficulty = question.difficulty

    db.commit()
    db.refresh(existing_question)

    return {
        "msg": "题目更新成功",
        "question_id": existing_question.id
    }

#查阅assignmet_submission
@router.get("/{assignment_id}/submissions")
def get_assignment_submissions(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    '''查阅assignmet_submission'''
    # 检查作业是否存在
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="作业不存在")
    
    # 检查用户权限
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="仅教师可查阅作业提交") 
    
    # 获取课程信息和学生总数
    course = db.query(Course).filter(Course.id == assignment.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    
    total_students = len(course.students)
    if total_students == 0:
        return {
            "data": [],
            "statistics": {
                "completion_rate": 0,
                "average_score": 0,
                "total_students": 0,
                "submitted_count": 0
            }
        }

    # 获取作业的提交记录
    submissions = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.assignment_id == assignment_id
    ).all()

    # 获取作业题目信息
    questions = db.query(AssignmentQuestion).filter(
        AssignmentQuestion.assignment_id == assignment_id
    ).order_by(AssignmentQuestion.order).all()

    # 计算总分
    total_points = 0
    for aq in questions:
        total_points += aq.points

    # 统计信息
    submitted_count = len(submissions)
    completion_rate = (submitted_count / total_students) * 100 if total_students > 0 else 0
    
    # 计算平均分
    if submitted_count > 0:
        total_scores = sum(sub.score for sub in submissions)
        average_score = (total_scores / submitted_count) / total_points * 100 if total_points > 0 else 0
    else:
        average_score = 0

    # 格式化提交记录
    submission_list = []
    for sub in submissions:
        # 获取学生信息
        student = db.query(User).filter(User.id == sub.student_id).first()
        
        # 解析答题详情
        answer_details = []
        if sub.feedback:  # 确保feedback字段不为空
            try:
                answer_json = json.loads(sub.feedback)  # 使用feedback字段，因为它包含了每道题的得分和反馈
                for detail in answer_json:
                    # 获取题目信息
                    question = db.query(Question).join(AssignmentQuestion).filter(
                        AssignmentQuestion.assignment_id == assignment_id,
                        Question.id == detail["question_id"]
                    ).first()
                    
                    if question:
                        answer_details.append({
                            "question_id": detail["question_id"],
                            "question_content": question.content,
                            "score": detail["score"],
                            "max_points": detail["max_points"],
                            "feedback": detail["feedback"]
                        })
            except json.JSONDecodeError:
                answer_details = []
                
        submission_list.append({
            "id": sub.id,
            "student_id": sub.student_id,
            "student_name": student.username if student else "未知学生",
            "submit_time": sub.submit_time,
            "score": sub.score,
            "score_percentage": (sub.score / total_points * 100) if total_points > 0 else 0,
            "answer_details": answer_details  # 添加答题详情
        })

    # 按得分率降序排序
    submission_list.sort(key=lambda x: x["score_percentage"], reverse=True)

    return {
        "data": submission_list,
        "statistics": {
            "completion_rate": round(completion_rate, 2),  # 完成率（百分比）
            "average_score": round(average_score, 2),      # 平均得分率（百分比）
            "total_students": total_students,              # 总学生数
            "submitted_count": submitted_count,            # 已提交数量
            "total_points": total_points                   # 总分值
        }
    }

# 学生成绩查询相关接口
from datetime import timedelta

class GradeAnalysisRequest(BaseModel):
    time_range: Optional[int] = 30  # 分析时间范围（天）
    include_suggestions: bool = True  # 是否包含学习建议

# 获取学生所有作业成绩汇总
@router.get("/grades/my-scores")
def get_my_all_scores(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=50, description="每页数量"),
    course_id: Optional[int] = Query(None, description="课程ID筛选"),  # 可选：按课程筛选
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    '''获取学生所有作业成绩记录汇总'''
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="仅学生可查看成绩")
    
    # 参数验证
    if page < 1:
        raise HTTPException(status_code=400, detail="页码必须大于0")
    if page_size < 1 or page_size > 50:
        raise HTTPException(status_code=400, detail="每页大小必须在1-50之间")
    
    offset = (page - 1) * page_size
    
    # 构建查询
    query = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.student_id == current_user.id
    )
    
    # 按课程筛选
    if course_id:
        query = query.join(Assignment).filter(Assignment.course_id == course_id)
    
    # 获取总数
    total_count = query.count()
    
    # 获取分页数据，按提交时间降序排列
    submissions = query.order_by(AssignmentSubmission.submit_time.desc()).offset(offset).limit(page_size).all()
    
    # 格式化返回数据
    score_list = []
    for sub in submissions:
        assignment = sub.assignment
        course = assignment.course if assignment else None
        
        # 计算作业总分
        total_points = 0
        if assignment:
            assignment_questions = db.query(AssignmentQuestion).filter(
                AssignmentQuestion.assignment_id == assignment.id
            ).all()
            total_points = sum(aq.points for aq in assignment_questions)
        
        # 计算得分率
        percentage = (sub.score / total_points * 100) if total_points > 0 else 0
        
        score_list.append({
            "submission_id": sub.id,
            "assignment_id": assignment.id if assignment else None,
            "assignment_title": assignment.title if assignment else "未知作业",
            "course_name": course.title if course else "未知课程",
            "course_id": course.id if course else None,
            "submit_time": sub.submit_time,
            "score": sub.score,
            "total_points": total_points,
            "percentage": round(percentage, 1),
            "deadline": assignment.deadline if assignment else None
        })
    
    return {
        "data": score_list,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total_count,
            "total_pages": (total_count + page_size - 1) // page_size,
            "has_next": page * page_size < total_count,
            "has_prev": page > 1
        }
    }

# 获取最近几次成绩用于图表
@router.get("/grades/recent")
def get_recent_scores(
    limit: int = Query(10, ge=1, le=50, description="返回数量限制"),
    course_id: Optional[int] = Query(None, description="课程ID筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    '''获取学生最近几次作业成绩用于图表展示'''
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="仅学生可查看成绩")
    
    if limit < 1 or limit > 50:
        raise HTTPException(status_code=400, detail="限制数量必须在1-50之间")
    
    # 构建查询
    query = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.student_id == current_user.id
    )
    
    # 按课程筛选
    if course_id:
        query = query.join(Assignment).filter(Assignment.course_id == course_id)
    
    # 获取最近的记录
    recent_submissions = query.order_by(AssignmentSubmission.submit_time.desc()).limit(limit).all()
    
    # 反转顺序，使图表从左到右按时间递增显示
    recent_submissions = recent_submissions[::-1]
    
    # 格式化数据用于图表展示
    chart_data = []
    score_summary = {
        "total_assignments": len(recent_submissions),
        "average_score": 0,
        "highest_score": 0,
        "lowest_score": 100,
        "trend": "stable"  # stable, improving, declining
    }
    
    total_percentage = 0
    percentages = []
    
    for sub in recent_submissions:
        assignment = sub.assignment
        
        # 计算作业总分
        total_points = 0
        if assignment:
            assignment_questions = db.query(AssignmentQuestion).filter(
                AssignmentQuestion.assignment_id == assignment.id
            ).all()
            total_points = sum(aq.points for aq in assignment_questions)
        
        # 计算得分率
        percentage = (sub.score / total_points * 100) if total_points > 0 else 0
        percentages.append(percentage)
        total_percentage += percentage
        
        chart_data.append({
            "assignment_title": assignment.title if assignment else "未知作业",
            "submit_time": sub.submit_time.strftime("%Y-%m-%d"),
            "score": sub.score,
            "total_points": total_points,
            "percentage": round(percentage, 1)
        })
        
        # 更新统计数据
        if percentage > score_summary["highest_score"]:
            score_summary["highest_score"] = round(percentage, 1)
        if percentage < score_summary["lowest_score"]:
            score_summary["lowest_score"] = round(percentage, 1)
    
    # 计算平均分和趋势
    if len(recent_submissions) > 0:
        score_summary["average_score"] = round(total_percentage / len(recent_submissions), 1)
        
        # 简单的趋势分析（比较前半部分和后半部分）
        if len(percentages) >= 3:
            mid_point = len(percentages) // 2
            early_avg = sum(percentages[:mid_point]) / mid_point    # 较早的
            recent_avg = sum(percentages[-mid_point:]) / mid_point  # 较近的
            
            if recent_avg > early_avg + 5:
                score_summary["trend"] = "improving"
            elif recent_avg < early_avg - 5:
                score_summary["trend"] = "declining"
    
    return {
        "chart_data": chart_data,
        "summary": score_summary
    }

# 成绩趋势分析和学习建议
@router.post("/grades/analysis")
async def get_grade_analysis(
    request: GradeAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    '''生成成绩分析报告和学习建议'''
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="仅学生可查看成绩分析")
    
    # 获取指定时间范围内的成绩记录
    time_threshold = datetime.utcnow() - timedelta(days=request.time_range)
    
    submissions = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.student_id == current_user.id,
        AssignmentSubmission.submit_time >= time_threshold
    ).order_by(AssignmentSubmission.submit_time).all()
    
    if not submissions:
        return {
            "analysis": "暂无足够的成绩数据进行分析",
            "suggestions": [],
            "statistics": {
                "total_assignments": 0,
                "average_score": 0,
                "improvement_trend": "无数据"
            }
        }
    
    # 准备分析数据
    analysis_data = []
    weak_knowledge_points = {}
    score_trend = []
    
    for sub in submissions:
        assignment = sub.assignment
        if not assignment:
            continue
            
        # 计算作业总分
        assignment_questions = db.query(AssignmentQuestion).filter(
            AssignmentQuestion.assignment_id == assignment.id
        ).all()
        total_points = sum(aq.points for aq in assignment_questions)
        percentage = (sub.score / total_points * 100) if total_points > 0 else 0
        
        score_trend.append(percentage)
        
        # 分析错误题目的知识点
        if sub.feedback:
            try:
                feedback_data = json.loads(sub.feedback)
                for item in feedback_data:
                    # 如果得分率低于60%，认为是薄弱知识点
                    question_score_rate = (item.get("score", 0) / item.get("max_points", 1)) * 100
                    if question_score_rate < 60:
                        # 获取题目信息
                        question = db.query(Question).filter(Question.id == item.get("question_id")).first()
                        if question and question.key_knowledge:
                            knowledge_point = question.key_knowledge
                            if knowledge_point not in weak_knowledge_points:
                                weak_knowledge_points[knowledge_point] = []
                            weak_knowledge_points[knowledge_point].append({
                                "assignment": assignment.title,
                                "score_rate": question_score_rate,
                                "feedback": item.get("feedback", "")
                            })
            except json.JSONDecodeError:
                continue
        
        analysis_data.append({
            "assignment_title": assignment.title,
            "course_name": assignment.course.title if assignment.course else "未知课程",
            "submit_time": sub.submit_time.strftime("%Y-%m-%d"),
            "score": sub.score,
            "total_points": total_points,
            "percentage": round(percentage, 1)
        })
    
    # 构建分析提示词
    analysis_prompt = f"""
    请分析学生的学习情况并给出建议：
    
    学生姓名：{current_user.username}
    分析时间范围：最近{request.time_range}天
    
    成绩趋势数据：
    {json.dumps(analysis_data, ensure_ascii=False, indent=2)}
    
    薄弱知识点统计：
    {json.dumps(weak_knowledge_points, ensure_ascii=False, indent=2)}
    
    请从以下角度进行分析：
    1. 总体学习表现评价
    2. 成绩变化趋势分析
    3. 薄弱知识点识别
    4. 具体的学习建议和改进措施
    5. 后续学习重点
    
    请以JSON格式返回，包含以下字段：
    {{
        "overall_performance": "总体表现评价",
        "trend_analysis": "趋势分析",
        "weak_points": ["薄弱知识点1", "薄弱知识点2"],
        "suggestions": [
            {{"priority": "high", "suggestion": "重要建议"}},
            {{"priority": "medium", "suggestion": "中等建议"}},
            {{"priority": "low", "suggestion": "一般建议"}}
        ],
        "study_plan": "学习计划建议"
    }}
    """
    
    # 调用大模型进行分析
    try:
        from ai_core.services.session_management_service import chat_with_assistant_once
        
        response = chat_with_assistant_once(
            chat_name="成绩分析助手",
            question=analysis_prompt,
            session_id=None
        )
        
        # 解析AI响应
        ai_answer = response.get("data", {}).get("answer", "")
        
        # 提取JSON字符串
        json_str = ai_answer.replace("```json", "").replace("```", "").strip()
        
        try:
            ai_analysis = json.loads(json_str)
        except json.JSONDecodeError:
            # 如果JSON解析失败，使用默认分析
            ai_analysis = {
                "overall_performance": "系统正在分析中，请稍后再试",
                "trend_analysis": "暂无法生成详细分析",
                "weak_points": list(weak_knowledge_points.keys())[:3],
                "suggestions": [{"priority": "high", "suggestion": "建议重点复习错题和薄弱知识点"}],
                "study_plan": "根据错题情况制定个性化学习计划"
            }
            
    except Exception as e:
        print(f"AI分析失败: {str(e)}")
        # 生成基础统计分析
        average_score = sum(score_trend) / len(score_trend) if score_trend else 0
        trend_direction = "稳定"
        if len(score_trend) >= 3:
            early_scores = score_trend[:len(score_trend)//2]
            recent_scores = score_trend[len(score_trend)//2:]
            early_avg = sum(early_scores) / len(early_scores)
            recent_avg = sum(recent_scores) / len(recent_scores)
            
            if recent_avg > early_avg + 5:
                trend_direction = "上升"
            elif recent_avg < early_avg - 5:
                trend_direction = "下降"
        
        ai_analysis = {
            "overall_performance": f"平均得分 {average_score:.1f}%，成绩趋势{trend_direction}",
            "trend_analysis": f"最近{request.time_range}天完成{len(submissions)}次作业，平均得分{average_score:.1f}%",
            "weak_points": list(weak_knowledge_points.keys())[:5],
            "suggestions": [
                {"priority": "high", "suggestion": "重点复习得分较低的知识点"},
                {"priority": "medium", "suggestion": "保持学习节奏，及时完成作业"},
                {"priority": "low", "suggestion": "多做练习题巩固知识"}
            ],
            "study_plan": "建议制定每日学习计划，重点关注薄弱环节"
        }
    
    # 计算统计数据
    average_score = sum(score_trend) / len(score_trend) if score_trend else 0
    improvement_trend = "稳定"
    if len(score_trend) >= 2:
        if score_trend[-1] > score_trend[0]:
            improvement_trend = "上升"
        elif score_trend[-1] < score_trend[0]:
            improvement_trend = "下降"
    
    return {
        "analysis": ai_analysis,
        "statistics": {
            "total_assignments": len(submissions),
            "average_score": round(average_score, 1),
            "improvement_trend": improvement_trend,
            "weak_knowledge_count": len(weak_knowledge_points),
            "time_range": request.time_range
        },
        "score_trend": [round(score, 1) for score in score_trend],
        "weak_knowledge_points": weak_knowledge_points
    }

# 获取单次作业详细成绩
@router.get("/grades/detail/{submission_id}")
def get_grade_detail(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    '''获取单次作业的详细成绩'''
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="仅学生可查看成绩详情")
    
    # 查找提交记录
    submission = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.id == submission_id,
        AssignmentSubmission.student_id == current_user.id
    ).first()
    
    if not submission:
        raise HTTPException(status_code=404, detail="成绩记录不存在")
    
    assignment = submission.assignment
    if not assignment:
        raise HTTPException(status_code=404, detail="作业信息不存在")
    
    # 获取作业题目信息
    assignment_questions = db.query(AssignmentQuestion).filter(
        AssignmentQuestion.assignment_id == assignment.id
    ).order_by(AssignmentQuestion.order).all()
    
    total_points = sum(aq.points for aq in assignment_questions)
    
    # 解析详细答案和反馈
    detailed_results = []
    if submission.feedback:
        try:
            feedback_data = json.loads(submission.feedback)
            answer_data = json.loads(submission.answer) if submission.answer else {}
            
            for item in feedback_data:
                question_id = item.get("question_id")
                question = db.query(Question).filter(Question.id == question_id).first()
                
                if question:
                    detailed_results.append({
                        "question_id": question_id,
                        "question_type": question.type,
                        "question_content": question.content,
                        "student_answer": answer_data.get(str(question_id), ""),
                        "correct_answer": question.answer,
                        "score": item.get("score", 0),
                        "max_points": item.get("max_points", 0),
                        "feedback": item.get("feedback", ""),
                        "key_knowledge": question.key_knowledge,
                        "difficulty": question.difficulty,
                        "options": json.loads(question.options) if question.options else None
                    })
        except json.JSONDecodeError:
            pass
    
    return {
        "submission_info": {
            "id": submission.id,
            "assignment_title": assignment.title,
            "course_name": assignment.course.title if assignment.course else "未知课程",
            "submit_time": submission.submit_time,
            "deadline": assignment.deadline,
            "score": submission.score,
            "total_points": total_points,
            "percentage": round((submission.score / total_points * 100), 1) if total_points > 0 else 0
        },
        "question_details": detailed_results
    }
