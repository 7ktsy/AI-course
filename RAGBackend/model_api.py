from openai import OpenAI
from typing import List, Dict
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from openai import OpenAI
from models import Course, CourseSession, User
import os

RAG_API_KEY = os.environ.get("RAGFLOW_API_KEY", "replace-me")
RAG_BASE    = os.environ.get("RAGFLOW_BASE_URL", "http://localhost:8080")

def get_client(chat_id: str) -> OpenAI:
    """
    为指定 chat_id 动态生成 OpenAI client
    """
    return OpenAI(
        api_key=RAG_API_KEY,
        base_url=f"{RAG_BASE}/api/v1/chats_openai/{chat_id}"
    )

def chat_with_model(chat_id: str, messages: List[Dict]) -> str:
    """
    调用 RAGflow OpenAI 兼容接口完成一次对话
    """
    client = get_client(chat_id)
    try:
        completion = client.chat.completions.create(
            model="model",
            messages=messages,
            stream=False
        )
        return completion.choices[0].message.content
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"模型调用失败：{e}"

#确保每个学生在每门课只有一个session
def get_or_create_session(course_id: int, current_user: User, db: Session):
    session_obj = db.query(CourseSession).filter_by(
        course_id=course_id, user_id=current_user.id
    ).first()

    if session_obj:
        return session_obj.session_id

    #获取课程的chat_id
    course = db.get(Course, course_id)
    if not course or not course.chat_id:
        raise HTTPException(404, "课程助手未初始化")

    #创建新session
    rag_resp = create_session(chat_name=course.chat_id,
                              name=f"u{current_user.id}",
                              user_id=str(current_user.id))

    new_session_id = rag_resp["session_id"]

    try:
        session_obj = CourseSession(
            course_id=course_id,
            user_id=current_user.id,
            chat_id=course.chat_id,
            session_id=new_session_id,
        )
        db.add(session_obj)
        db.commit()
        return new_session_id
    except IntegrityError:
        #并发时回滚
        db.rollback()
        return (
            db.query(CourseSession)
            .filter_by(course_id=course_id, user_id=current_user.id)
            .first()
            .session_id
        )
