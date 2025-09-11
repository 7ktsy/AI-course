from datetime import datetime
import json
from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models import User, Course, Assignment, AssignmentSubmission, CourseChat
from typing import List
from user_routes import get_current_user
from ragflow_client import score_subjective

router = APIRouter(prefix="/student", tags=["学生"])

class AnswerItem(BaseModel):
    question_id: int
    answer: str

class SubmissionRequest(BaseModel):
    answers: List[AnswerItem]

#学生查看作业列表
@router.get("/assignment/list")
def assignment_list(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "student":
        raise HTTPException(403, detail="仅学生可查看作业列表")

    # 如果学生没有加入任何课程，直接返回空列表
    if not current_user.joined_courses:
        return []

    # 获取学生有权限查看的作业创建者ID列表
    # 包括：1.学生自己 2.所加入课程的教师
    allowed_creator_ids = [str(current_user.id)]  # 学生自己
    course_ids = [course.id for course in current_user.joined_courses]
    
    # 添加课程教师的ID
    for course in current_user.joined_courses:
        allowed_creator_ids.append(str(course.teacher_id))

    # 使用JOIN查询优化
    assignments = db.query(Assignment, Course).join(
        Course, Assignment.course_id == Course.id
    ).filter(
        Assignment.course_id.in_(course_ids),
        Assignment.creator_id.in_(allowed_creator_ids)
    ).all()

    return [
        {
            "id": assignment.id,
            "title": assignment.title,
            "course_id": assignment.course_id,
            "course_title": course.title,
            "creator_id": assignment.creator_id,
            "deadline": assignment.deadline.strftime("%Y-%m-%d %H:%M:%S") if assignment.deadline else None
        }
        for assignment, course in assignments
    ]

#学生提交作业
@router.post("/assignment/{assignment_id}/submit")
async def submit_assignment(
    assignment_id: int,
    req: SubmissionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "student":
        raise HTTPException(403, detail="仅学生可提交作业")

    assignment = db.get(Assignment, assignment_id)
    if not assignment:
        raise HTTPException(404, detail="作业不存在")

    if assignment.deadline and assignment.deadline < datetime.utcnow():
        raise HTTPException(400, "已超过截止时间，无法提交")

    # 获取作业批改助手
    grading_chat = db.query(CourseChat).filter(
        CourseChat.course_id == assignment.course_id,
        CourseChat.chat_type == "grading",
        CourseChat.is_active == 1
    ).first()
    
    # 如果没有专门的批改助手，使用第一个可用的聊天助手
    if not grading_chat:
        grading_chat = db.query(CourseChat).filter(
            CourseChat.course_id == assignment.course_id,
            CourseChat.is_active == 1
        ).first()

    
    if not grading_chat:
        raise HTTPException(404, "课程聊天助手未配置，无法批改作业")

    stu_ans_map = {a.question_id: a.answer.strip() for a in req.answers}
    per_q = []
    total_score = 0.0   #学生实际获得分数
    full_score = 0.0    #作业最高分
    # chat_id = grading_chat.chat_id

    for q in assignment.questions:
        points = q.points or 1.0
        full_score += points
        stu_ans = stu_ans_map.get(q.question_id, "")
        ref_ans = (q.question.answer or "").strip()

        if q.question.type == "选择" or q.question.type == "填空":
            q_score = points if stu_ans == ref_ans else 0
            if q_score == 0:
                feedback = "答案不匹配"
            else:
                feedback = ""
        else:
            raw, feedback = await score_subjective(ref_ans, stu_ans, current_user)
            q_score = round(points * raw / 100.0, 2)

        total_score += q_score
        per_q.append({
            "question_id": q.question_id,  # 使用question的真实ID，而不是AssignmentQuestion的ID
            "score": q_score,
            "max_points": points,
            "feedback": feedback,
        })


    sub = AssignmentSubmission(
        assignment_id=assignment_id,
        student_id=current_user.id,
        submit_time=datetime.utcnow(),
        answer=json.dumps(stu_ans_map, ensure_ascii=False),
        score=total_score,
        feedback=json.dumps(per_q, ensure_ascii=False),
    )
    db.add(sub);
    db.commit();
    db.refresh(sub)

    return {
        "submission_id": sub.id,
        "total_score": total_score,
        "full_score": full_score,
        "per_question": per_q,
    }

#学生查看作业成绩
@router.get("/assignment/{assignment_id}/my_result")
def my_assignment_result(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "student":
        raise HTTPException(403, "仅学生可查看成绩")

    sub = (
        db.query(AssignmentSubmission)
        .filter_by(assignment_id=assignment_id, student_id=current_user.id)
        .first()
    )
    if not sub:
        raise HTTPException(404, "尚未提交该作业")

    return {
        "submit_time": sub.submit_time.strftime("%Y-%m-%d %H:%M:%S"),
        "score": sub.score,
        "feedback": sub.feedback,
        "answer": sub.answer,
    }

#学生查看自己加入的课程列表
@router.get("/my_courses")
def my_courses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "student":
        raise HTTPException(403, "仅学生可查看该信息")

    return [
        {
            "id": c.id,
            "title": c.title,
            "cover": c.cover,
            "teacher": c.teacher.username
        }
        for c in current_user.joined_courses
    ]

#学生选课加入课程
@router.post("/course/{course_id}/join")
def join_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "student":
        raise HTTPException(403, "仅学生可加入课程")

    course = db.get(Course, course_id)
    if not course:
        raise HTTPException(404, "课程不存在")

    if current_user in course.students:
        return {"msg": "已在课程中"}

    course.students.append(current_user)
    db.commit()
    return {"msg": f"成功加入《{course.title}》"}