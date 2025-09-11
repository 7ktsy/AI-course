from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from models import User, AssignmentSubmission
from pydantic import BaseModel
from datetime import datetime, timedelta
from passlib.context import CryptContext
from typing import Optional
from user_routes import get_current_user, UserCreate, UserLogin, UserUpdate, AdminUserCreate, get_password_hash

router = APIRouter()
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.get("/admin/basic-stats", response_model=dict)
def get_admin_basic_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取管理员基础统计数据（仅管理员可访问）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可访问统计数据")
    
    try:
        from models import Course, CourseMaterial, Assignment, AssignmentQuestion, Question, ParseStatus
        
        # 统计用户数据
        total_users = db.query(User).count()
        total_students = db.query(User).filter(User.role == "student").count()
        total_teachers = db.query(User).filter(User.role == "teacher").count()
        
        # 统计课程数据
        total_courses = db.query(Course).count()
        active_courses = db.query(Course).filter(Course.created_at.isnot(None)).count()
        completed_courses = 0  # 这里可以根据实际业务逻辑计算
        new_courses = db.query(Course).filter(
            Course.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        ).count()
        
        return {
            "code": 0,
            "message": "获取统计数据成功",
            "data": {
                "totalUsers": total_users,
                "totalStudents": total_students,
                "totalTeachers": total_teachers,
                "totalCourses": total_courses,
                "activeCourses": active_courses,
                "completedCourses": completed_courses,
                "newCourses": new_courses
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计数据失败: {str(e)}")

@router.get("/admin/users", response_model=dict)
def get_all_users(
    page: int = Query(1, ge=1, description="页码"),
    per_page: int = Query(20, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    role: Optional[str] = Query(None, description="角色筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取所有用户列表（仅管理员可访问）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可访问用户列表")
    
    try:
        from models import Course, CourseMaterial, Assignment, AssignmentQuestion, Question, AssignmentSubmission, ParseStatus
        
        # 构建查询
        query = db.query(User)
        
        # 搜索过滤
        if search:
            query = query.filter(
                User.username.contains(search) |
                User.phone.contains(search) |
                User.university.contains(search)
            )
        
        # 角色过滤
        if role:
            query = query.filter(User.role == role)
        
        # 状态过滤（如果有status字段的话）
        if status:
            # 这里假设User模型有status字段，如果没有需要添加
            query = query.filter(User.status == status)
        
        # 计算总数
        total = query.count()
        
        # 分页
        users = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return {
            "code": 0,
            "message": "获取用户列表成功",
            "data": {
                "users": [
                    {
                        "id": user.id,
                        "username": user.username,
                        "phone": user.phone,
                        "role": user.role,
                        "university": user.university,
                        "title": user.title,
                        "department": user.department,
                        "created_at": user.created_at.isoformat() if user.created_at else None,
                        "last_login": user.last_login.isoformat() if hasattr(user, 'last_login') and user.last_login else None,
                        "status": getattr(user, 'status', 'active')  # 默认状态为active
                    }
                    for user in users
                ],
                "total": total,
                "page": page,
                "per_page": per_page
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户列表失败: {str(e)}")

@router.get("/admin/users/{user_id}", response_model=dict)
def get_user_detail(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户详情（仅管理员可访问）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可访问用户详情")
    
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 获取用户统计信息（根据角色）
        stats = {}
        if user.role == "student":
            # 学生统计信息
            from models import Course, Assignment, AssignmentSubmission
            stats = {
                "courses_enrolled": db.query(Course).join(Course.students).filter(Course.students.any(id=user.id)).count(),
                "assignments_completed": db.query(AssignmentSubmission).filter(AssignmentSubmission.student_id == user.id).count(),
                "total_study_time": 0,  # 需要根据实际业务逻辑计算
                "average_score": 0  # 需要根据实际业务逻辑计算
            }
        elif user.role == "teacher":
            # 教师统计信息
            from models import Course, Assignment
            stats = {
                "courses_created": db.query(Course).filter(Course.teacher_id == user.id).count(),
                "assignments_created": db.query(Assignment).filter(Assignment.creator_id == str(user.id)).count(),
                "total_students": 0,  # 需要根据实际业务逻辑计算
                "lessons_created": 0  # 需要根据实际业务逻辑计算
            }
        
        return {
            "code": 0,
            "message": "获取用户详情成功",
            "data": {
                "id": user.id,
                "username": user.username,
                "phone": user.phone,
                "role": user.role,
                "university": user.university,
                "title": user.title,
                "department": user.department,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "last_login": user.last_login.isoformat() if hasattr(user, 'last_login') and user.last_login else None,
                "status": getattr(user, 'status', 'active'),
                "stats": stats
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户详情失败: {str(e)}")

@router.post("/admin/users", response_model=dict)
def create_user_by_admin(
    user_data: AdminUserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """管理员创建用户"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可创建用户")
    
    try:
        # 检查手机号是否已存在
        existing_user = db.query(User).filter(User.phone == user_data.phone).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="手机号已注册")
        
        # 检查用户名是否已存在
        existing_username = db.query(User).filter(User.username == user_data.username).first()
        if existing_username:
            raise HTTPException(status_code=400, detail="用户名已存在")
        
        # 创建新用户
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            username=user_data.username,
            hashed_password=hashed_password,
            phone=user_data.phone,
            role=user_data.role,
            university=user_data.university,
            title=user_data.title,
            department=user_data.department,
            status=user_data.status if hasattr(User, 'status') else 'active'
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return {
            "code": 0,
            "message": "用户创建成功",
            "data": {
                "id": db_user.id,
                "username": db_user.username,
                "phone": db_user.phone,
                "role": db_user.role
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建用户失败: {str(e)}")

@router.put("/admin/users/{user_id}", response_model=dict)
def update_user_by_admin(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """管理员更新用户信息"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可更新用户信息")
    
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 更新用户信息
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(user, field):
                setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        
        return {
            "code": 0,
            "message": "用户信息更新成功",
            "data": {
                "id": user.id,
                "username": user.username,
                "phone": user.phone,
                "role": user.role
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新用户信息失败: {str(e)}")

@router.delete("/admin/users/{user_id}", response_model=dict)
def delete_user_by_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """管理员删除用户"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可删除用户")
    
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 不能删除管理员账户
        if user.role == "admin":
            raise HTTPException(status_code=400, detail="不能删除管理员账户")
        
        # 不能删除自己
        if user.id == current_user.id:
            raise HTTPException(status_code=400, detail="不能删除自己的账户")
        
        db.delete(user)
        db.commit()
        
        return {
            "code": 0,
            "message": "用户删除成功",
            "data": None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除用户失败: {str(e)}")

@router.get("/admin/users/stats", response_model=dict)
def get_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户统计信息（仅管理员可访问）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可访问用户统计")
    
    try:
        total_users = db.query(User).count()
        total_students = db.query(User).filter(User.role == "student").count()
        total_teachers = db.query(User).filter(User.role == "teacher").count()
        total_admins = db.query(User).filter(User.role == "admin").count()
        
        # 今日新增用户
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        new_users_today = db.query(User).filter(User.created_at >= today).count()
        
        return {
            "code": 0,
            "message": "获取用户统计成功",
            "data": {
                "total_users": total_users,
                "total_students": total_students,
                "total_teachers": total_teachers,
                "total_admins": total_admins,
                "new_users_today": new_users_today
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户统计失败: {str(e)}")

@router.get("/admin/courses", response_model=dict)
def get_all_courses_detail(
    page: int = Query(1, ge=1, description="页码"),
    per_page: int = Query(20, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    teacher_id: Optional[int] = Query(None, description="教师ID筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取所有课程详细信息（仅管理员可访问）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可访问课程详情")
    
    try:
        from models import Course, CourseMaterial, Assignment, AssignmentQuestion, Question, AssignmentSubmission, ParseStatus
        
        # 构建查询
        query = db.query(Course)
        
        # 搜索过滤
        if search:
            query = query.filter(
                Course.title.contains(search) |
                Course.description.contains(search)
            )
        
        # 教师过滤
        if teacher_id:
            query = query.filter(Course.teacher_id == teacher_id)
        
        # 计算总数
        total = query.count()
        
        # 分页
        courses = query.offset((page - 1) * per_page).limit(per_page).all()
        
        course_details = []
        for course in courses:
            # 获取课程资料
            materials = db.query(CourseMaterial).filter(
                CourseMaterial.course_id == course.id
            ).all()
            
            # 获取课程任务
            assignments = db.query(Assignment).filter(
                Assignment.course_id == course.id
            ).all()
            
            # 获取每个任务的题目详情
            assignment_details = []
            for assignment in assignments:
                # 获取任务的题目
                assignment_questions = db.query(AssignmentQuestion).filter(
                    AssignmentQuestion.assignment_id == assignment.id
                ).order_by(AssignmentQuestion.order).all()
                
                questions_detail = []
                for aq in assignment_questions:
                    question = db.query(Question).filter(Question.id == aq.question_id).first()
                    if question:
                        questions_detail.append({
                            "id": question.id,
                            "type": question.type,
                            "content": question.content,
                            "points": aq.points,
                            "key_knowledge": question.key_knowledge,
                            "difficulty": question.difficulty,
                            "options": question.options,
                            "answer": question.answer,
                            "order": aq.order
                        })
                
                # 获取任务提交统计
                submission_count = db.query(AssignmentSubmission).filter(
                    AssignmentSubmission.assignment_id == assignment.id
                ).count()
                
                assignment_details.append({
                    "id": assignment.id,
                    "title": assignment.title,
                    "description": assignment.description,
                    "content": assignment.content,
                    "answer": assignment.answer,
                    "created_at": assignment.created_at.isoformat() if assignment.created_at else None,
                    "deadline": assignment.deadline.isoformat() if assignment.deadline else None,
                    "creator_id": assignment.creator_id,
                    "questions_count": len(questions_detail),
                    "submission_count": submission_count,
                    "questions": questions_detail
                })
            
            # 获取学生数量
            student_count = len(course.students)
            
            # 获取教师信息
            teacher = db.query(User).filter(User.id == course.teacher_id).first()
            
            course_details.append({
                "id": course.id,
                "title": course.title,
                "description": course.description,
                "created_at": course.created_at.isoformat() if course.created_at else None,
                "dataset_id": course.dataset_id,
                "dataset_name": course.dataset_name,
                "chat_id": course.chat_id,
                "teacher": {
                    "id": teacher.id if teacher else None,
                    "username": teacher.username if teacher else None,
                    "phone": teacher.phone if teacher else None,
                    "university": teacher.university if teacher else None,
                    "title": teacher.title if teacher else None,
                    "department": teacher.department if teacher else None
                } if teacher else None,
                "student_count": student_count,
                "materials_count": len(materials),
                "assignments_count": len(assignments),
                "materials": [
                    {
                        "id": material.id,
                        "title": material.title,
                        "description": material.description,
                        "filename": material.filename,
                        "file_path": material.file_path,
                        "uploadtime": material.uploadtime.isoformat() if material.uploadtime else None,
                        "status": material.status.value if material.status else None,
                        "rag_doc_id": material.rag_doc_id,
                        "error_msg": material.error_msg
                    }
                    for material in materials
                ],
                "assignments": assignment_details
            })
        
        return {
            "code": 0,
            "message": "获取课程详情成功",
            "data": {
                "courses": course_details,
                "total": total,
                "page": page,
                "per_page": per_page
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取课程详情失败: {str(e)}")

@router.get("/admin/courses/{course_id}", response_model=dict)
def get_course_detail_by_id(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取指定课程的详细信息（仅管理员可访问）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可访问课程详情")
    
    try:
        from models import Course, CourseMaterial, Assignment, AssignmentQuestion, Question, AssignmentSubmission, ParseStatus
        
        # 获取课程
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="课程不存在")
        
        # 获取课程资料
        materials = db.query(CourseMaterial).filter(
            CourseMaterial.course_id == course.id
        ).all()
        
        # 获取课程任务
        assignments = db.query(Assignment).filter(
            Assignment.course_id == course.id
        ).all()
        
        # 获取每个任务的详细信息
        assignment_details = []
        for assignment in assignments:
            # 获取任务的题目
            assignment_questions = db.query(AssignmentQuestion).filter(
                AssignmentQuestion.assignment_id == assignment.id
            ).order_by(AssignmentQuestion.order).all()
            
            questions_detail = []
            for aq in assignment_questions:
                question = db.query(Question).filter(Question.id == aq.question_id).first()
                if question:
                    questions_detail.append({
                        "id": question.id,
                        "type": question.type,
                        "content": question.content,
                        "points": aq.points,
                        "key_knowledge": question.key_knowledge,
                        "difficulty": question.difficulty,
                        "options": question.options,
                        "answer": question.answer,
                        "order": aq.order
                    })
            
            # 获取任务提交记录
            submissions = db.query(AssignmentSubmission).filter(
                AssignmentSubmission.assignment_id == assignment.id
            ).all()
            
            submission_details = []
            for submission in submissions:
                student = db.query(User).filter(User.id == submission.student_id).first()
                submission_details.append({
                    "id": submission.id,
                    "student": {
                        "id": student.id if student else None,
                        "username": student.username if student else None,
                        "phone": student.phone if student else None
                    } if student else None,
                    "submit_time": submission.submit_time.isoformat() if submission.submit_time else None,
                    "score": submission.score,
                    "feedback": submission.feedback
                })
            
            assignment_details.append({
                "id": assignment.id,
                "title": assignment.title,
                "description": assignment.description,
                "content": assignment.content,
                "answer": assignment.answer,
                "created_at": assignment.created_at.isoformat() if assignment.created_at else None,
                "deadline": assignment.deadline.isoformat() if assignment.deadline else None,
                "creator_id": assignment.creator_id,
                "questions_count": len(questions_detail),
                "submission_count": len(submission_details),
                "questions": questions_detail,
                "submissions": submission_details
            })
        
        # 获取学生列表
        students = course.students
        student_list = [
            {
                "id": student.id,
                "username": student.username,
                "phone": student.phone,
                "university": student.university,
                "created_at": student.created_at.isoformat() if student.created_at else None
            }
            for student in students
        ]
        
        # 获取教师信息
        teacher = db.query(User).filter(User.id == course.teacher_id).first()
        
        return {
            "code": 0,
            "message": "获取课程详情成功",
            "data": {
                "id": course.id,
                "title": course.title,
                "description": course.description,
                "created_at": course.created_at.isoformat() if course.created_at else None,
                "dataset_id": course.dataset_id,
                "dataset_name": course.dataset_name,
                "chat_id": course.chat_id,
                "teacher": {
                    "id": teacher.id if teacher else None,
                    "username": teacher.username if teacher else None,
                    "phone": teacher.phone if teacher else None,
                    "university": teacher.university if teacher else None,
                    "title": teacher.title if teacher else None,
                    "department": teacher.department if teacher else None
                } if teacher else None,
                "students": student_list,
                "student_count": len(students),
                "materials_count": len(materials),
                "assignments_count": len(assignments),
                "materials": [
                    {
                        "id": material.id,
                        "title": material.title,
                        "description": material.description,
                        "filename": material.filename,
                        "file_path": material.file_path,
                        "uploadtime": material.uploadtime.isoformat() if material.uploadtime else None,
                        "status": material.status.value if material.status else None,
                        "rag_doc_id": material.rag_doc_id,
                        "error_msg": material.error_msg
                    }
                    for material in materials
                ],
                "assignments": assignment_details
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取课程详情失败: {str(e)}")