from fastapi import APIRouter, UploadFile,Depends, File, Form, HTTPException
import os
import sys
from sqlalchemy.orm import Session
from datetime import datetime
from models import CourseMaterial, User,Course,ParseStatus
from database import get_db
from user_routes import get_current_user
from uuid import uuid4
from pydantic import BaseModel
from ragflow_client import upload_and_parse_to_ragflow, create_dataset, delete_dataset,update_dataset_by_name,create_chat,delete_chat
from typing import List,Dict
from model_api import get_or_create_session


#调用ai-core封装层自己添加的
# 添加ai-core到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'ai_core'))

try:
    from ai_core.services.file_management_service import (
        parse_documents, 
        stop_parsing_documents, 
        list_documents,
        get_document_id_by_name
    )
except ImportError:
    # 如果导入失败，提供空的实现
    def parse_documents(*args, **kwargs):
        raise HTTPException(500, "ai-core模块未正确配置")
    
    def stop_parsing_documents(*args, **kwargs):
        raise HTTPException(500, "ai-core模块未正确配置")
    
    def list_documents(*args, **kwargs):
        raise HTTPException(500, "ai-core模块未正确配置")
    
    def get_document_id_by_name(*args, **kwargs):
        raise HTTPException(500, "ai-core模块未正确配置")

router = APIRouter(prefix="/course", tags=["课程"])

class ChatRequest(BaseModel):
    question: str
    history: List[Dict] = []

class CourseCreate(BaseModel):
    title: str
    description: str = ""
    cover: str = None  # 课程封面URL

class AddStudentsRequest(BaseModel):
    student_ids: List[int]

class ParseDocumentsRequest(BaseModel):
    document_name: str

# class CreateCourseChatRequest(BaseModel):
#     name: str
#     description: str = ""

#通过RAG回调信息（目前还没这个功能？？）
@router.post("/notify_parse_success")
def notify_success(data: dict, db: Session = Depends(get_db)):
    doc_id = data.get("rag_doc_id")
    material = db.query(CourseMaterial).filter_by(rag_doc_id=doc_id).first()
    if material:
        material.status = ParseStatus.parsed
        db.commit()
    return {"msg": "success"}

"""
#与智能ai对话
@router.post("/assistant")
async def teacher_assistant_chat(
    course_id: int,
    req: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    course = db.get(Course, course_id)
    if not course or course.teacher_id != current_user.id:
        raise HTTPException(403, "无权访问该课程")

    session_id = await get_or_create_session(course_id, current_user, db)
    answer = ask_teacher_chat(course_chat_id=course.chat_id,question=req.question,history=req.history)
    return {
        "session_id": session_id,
        "question": req.question,
        "answer": answer
    }
"""

#创建课程
@router.post("/create")
async def create_course(
    data: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="仅教师可创建课程")

    course = Course(
        title=data.title,
        description=data.description,
        cover=data.cover,  # 添加封面字段
        teacher_id=current_user.id,
        dataset_id=None,  # 初始化为None
        dataset_name=None,  # 初始化为None
        chat_id=None  # 初始化为None
    )
    db.add(course)
    db.commit()
    db.refresh(course)

    # 以course_{course.id}_{title}作为知识库数据集名
    # 改成只有title 便于删除查找
    dataset_name = data.title
    try:
        rag_resp = await create_dataset(dataset_name)  # 返回标准化的响应格式
        
        # 检查响应状态
        if rag_resp.get("code") != 0:
            # 数据集创建失败，回滚课程创建
            db.delete(course)
            db.commit()
            raise HTTPException(status_code=500, detail=f"知识库创建失败：{rag_resp.get('message')}")
        
        # 数据集创建成功，更新课程信息
        course.dataset_id = rag_resp["data"]["dataset_id"]
        course.dataset_name = dataset_name
        db.commit()
        
    except Exception as e:
        # 发生异常，回滚课程创建
        db.delete(course)
        db.commit()
        raise HTTPException(status_code=500, detail=f"知识库创建失败：{str(e)}")

    # #课程专属的chat助手，对应课程的知识库
    # try:
    #     rag_chat = await create_chat(
    #         name=f"chat_course_{course.id}",
    #         dataset_names=[dataset_name]
    #     )
    #     course.chat_id = rag_chat["chat_id"]
    #     db.commit()
    # except Exception as e:
    #     # Chat创建失败，但课程和数据集已创建，记录错误但不回滚
    #     print(f"Chat创建失败：{e}")

    return {
        "msg": "课程创建成功",
        "course": {
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "cover": course.cover,  # 添加封面字段
            "created_at": course.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "dataset_name": course.dataset_name,
            "dataset_id": course.dataset_id
        }
    }

# #获取课程助手的chatId
# @router.get("/{course_id}/chat")
# def get_course_chat(
#         course_id: int,
#         db: Session = Depends(get_db),
#         current_user: User = Depends(get_current_user)
# ):
#     course = db.get(Course, course_id)
#     if not course: raise HTTPException(404, "课程不存在")
#     # 权限检查（老师或已选课学生）
#     if current_user.role == "teacher" and course.teacher_id != current_user.id:
#         raise HTTPException(403, "无权访问")
#     if current_user.role == "student" and course not in current_user.joined_courses:
#         raise HTTPException(403, "未加入课程")
#     return {"chat_id": course.chat_id}


# #生成sessionId返回给前端
# @router.post("/{course_id}/session")
# async def get_session_id(
#         course_id: int,
#         db: Session = Depends(get_db),
#         current_user: User = Depends(get_current_user)
# ):
#     course = db.get(Course, course_id)
#     if not course:
#         raise HTTPException(404, "课程不存在")

#     if current_user.role == "student" and course not in current_user.joined_courses:
#         raise HTTPException(403, "未加入课程")
#     if current_user.role == "teacher" and course.teacher_id != current_user.id:
#         raise HTTPException(403, "无权访问")

#     session_id = await get_or_create_session(course_id, current_user, db)
#     return {"chat_id": course.chat_id, "session_id": session_id}


#获取当前教师的所有课程信息
@router.get("/my")
def get_my_courses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="仅教师可查看课程")

    courses = db.query(Course).filter(Course.teacher_id == current_user.id).all()
    return {
        "code": 0,
        "message": "获取成功",
        "data": {
            "courses": [
                {
                    "id": c.id,
                    "title": c.title,
                    "description": c.description,
                    "created_at": c.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "cover": c.cover,
                    "dataset_name":c.dataset_name
                }
                for c in courses
            ]
        }
    }


#删除课程
@router.delete("/{course_id}")
async def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    course = db.get(Course, course_id)

    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    if course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权删除该课程")

    # 删除知识库
    if course.dataset_name:
        try:
            delete_result = await delete_dataset(course.dataset_name)
            if delete_result.get("code") != 0:
                print(f"删除知识库失败：{delete_result.get('message')}")
        except Exception as e:
            print(f"删除知识库失败：{e}")

    # 删除Chat助手
    if course.chat_id:
        try:
            await delete_chat(course.chat_id)
        except Exception as e:
            print(f"删除Chat失败：{e}")

    db.delete(course)
    db.commit()
    return {"msg": f"课程《{course.title}》已删除"}

#向课程添加学生
@router.post("/{course_id}/add_students")
def add_students_to_course(
    course_id: int,
    req: AddStudentsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    if course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作该课程")

    added_count = 0
    # 查找学生并添加
    for student_id in req.student_ids:
        student = db.query(User).filter(User.id == student_id, User.role == "student").first()
        if not student:
            continue
        if student not in course.students:
            course.students.append(student)
            added_count += 1

    db.commit()
    return {
        "code": 0,
        "message": f"成功添加 {added_count} 名学生",
        "data": {
            "added_count": added_count
        }
    }


#查看课程学生名单
@router.get("/{course_id}/students")
def get_course_students(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    if course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权查看该课程")

    return {
        "code": 0,
        "message": "获取成功",
        "data": {
            "students": [
                {
                    "id": student.id,
                    "username": student.username,
                    "phone": student.phone,
                    "university": student.university,
                    "department": student.department,
                    "title": student.title
                }
                for student in course.students
            ]
        }
    }

#从课程中移除学生
@router.delete("/{course_id}/students/{student_id}")
def remove_student_from_course(
    course_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    if course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作该课程")

    student = db.query(User).filter(User.id == student_id, User.role == "student").first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    
    if student in course.students:
        course.students.remove(student)
        db.commit()
        return {
            "code": 0,
            "message": f"学生 {student.username} 已从课程中移除",
            "data": {}
        }
    else:
        raise HTTPException(status_code=400, detail="学生未在该课程中")

#更改课程信息
@router.put("/course/{course_id}")
async def update_course(
    course_id: int,
    new_title: str = Form(...),
    new_description: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    course = db.get(Course, course_id)
    if not course or course.teacher_id != current_user.id:
        raise HTTPException(403, "无权修改")

    old_dataset = course.dataset_name
    new_dataset = new_title

    course.title = new_title
    course.description = new_description
    course.dataset_name = new_dataset
    db.commit()

    # 更新知识库
    if old_dataset:
        try:
            update_result = await update_dataset_by_name(old_dataset, new_dataset, new_description)
            if update_result.get("code") != 0:
                print(f"知识库更新失败：{update_result.get('message')}")
        except Exception as e:
            print(f"知识库更新失败：{e}")

    return {"msg": "课程已更新"}

#获取全部课程
@router.get("/listall")
def get_all_courses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    courses = db.query(Course).all()
    return {
        "code": 0,
        "message": "获取成功",
        "data": {
            "courses": [
                {
                    "id": c.id,
                    "title": c.title,
                    "description": c.description,
                    "cover": c.cover,  # 添加封面字段
                    "teacher_name": c.teacher.username,
                    "created_at": c.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "is_enrolled": current_user in c.students  # 添加是否已加入字段
                }
                for c in courses
            ]
        }
    }