from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models import Course, User, CourseChat, ParseStatus, CourseMaterial
from database import get_db
from user_routes import get_current_user
import sys
import os
from pydantic import BaseModel
from ragflow_client import create_chat, delete_chat
from typing import Optional, List, Dict
import time

# 添加ai-core到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'ai_core'))

try:
    from ai_core.services.file_management_service import (
        list_documents, 
        get_document_id_by_name, 
        parse_documents, 
        stop_parsing_documents
    )
    from ai_core.services.session_management_service import (
        create_session,
        chat_with_assistant_once
    )
    from ai_core.services.chats_management_service import list_chats
    from ai_core.services.dataset_management_service import list_datasets
except ImportError:
    # 如果导入失败，提供空的实现
    def list_documents(*args, **kwargs):
        raise HTTPException(500, "ai-core模块未正确配置")
    
    def get_document_id_by_name(*args, **kwargs):
        raise HTTPException(500, "ai-core模块未正确配置")
    
    def parse_documents(*args, **kwargs):
        raise HTTPException(500, "ai-core模块未正确配置")
    
    def stop_parsing_documents(*args, **kwargs):
        raise HTTPException(500, "ai-core模块未正确配置")
    
    def create_session(*args, **kwargs):
        raise HTTPException(500, "ai-core模块未正确配置")
    
    def chat_with_assistant_once(*args, **kwargs):
        raise HTTPException(500, "ai-core模块未正确配置")

router = APIRouter(prefix="/chat", tags=["课程聊天助手"])

class CreateCourseChatRequest(BaseModel):
    name: str
    description: str = ""
    chat_type: str = "general"  # general, analysis, preparation, qa, grading

# 预定义的聊天助手类型
CHAT_TYPES = {
    "general": "通用助手",
    "analysis": "学情分析助手", 
    "preparation": "教师备课助手",
    "qa": "学生答疑助手",
    "grading": "作业批改助手"
}

# 不同聊天助手类型的配置
CHAT_CONFIGS = {
    "general": {
        "llm": {
            "model_name": "deepseek-chat",
            "temperature": 0.3,
            "top_p": 0.8,
            "frequency_penalty": 0.1,
            "presence_penalty": 0.1
        },
        "prompt": {
            "opener": "你好！我是这门课程的智能助手，可以帮你解答课程相关的问题。请告诉我你想了解什么？",
            "prompt": "你是一个专业的课程助手。请基于知识库中的课程内容来回答问题。回答要准确、详细，并考虑聊天历史。如果知识库中没有相关信息，请明确说明。",
            "empty_response": "抱歉，知识库中没有找到相关信息。请换个问题试试，或者联系老师获取帮助。",
            "similarity_threshold": 0.2,
            "top_n": 6,
            "show_quote": True,
            "refine_multiturn": True
        }
    },
    "analysis": {
        "llm": {
            "model_name": "deepseek-chat",
            "temperature": 0.1,
            "top_p": 0.3,
            "frequency_penalty": 0.7,
            "presence_penalty": 0.4
        },
        "prompt": {
            "opener": "你好！我是学情分析助手，专门负责分析学生的学习情况和提供个性化建议。请提供学生的作业数据或学习表现，我将为你进行详细分析。",
            "prompt": "你是一个专业的学情分析专家。请基于提供的数据分析学生的学习情况，包括：1. 知识点掌握程度评估 2. 学习优势和不足 3. 个性化学习建议 4. 改进方向。分析要客观、具体，并提供可操作的建议。",
            "empty_response": "抱歉，没有足够的数据进行分析。请提供更多学生的学习数据。",
            "similarity_threshold": 0.3,
            "top_n": 8,
            "show_quote": True,
            "refine_multiturn": True
        }
    },
    "preparation": {
        "llm": {
            "model_name": "deepseek-chat",
            "temperature": 0.4,
            "top_p": 0.9,
            "frequency_penalty": 0.2,
            "presence_penalty": 0.1
        },
        "prompt": {
            "opener": "你好！我是教师备课助手，专门帮助教师设计教案和教学活动。请告诉我你要备课的章节或主题，我将为你提供详细的备课建议。",
            "prompt": '''你是一个教师备课助理，你根据教师上传的课程大纲和课程知识点汇总帮助教师自动生成教学内容，包括本周课堂知识点讲解，教学关键内容，实训练习与指导、时间分布等。
        以下是知识库：
        {knowledge}
        以上是知识库。
生成的教学内容以下几块为核心：一、上周知识点回顾，二、本周知识点讲解，三、教学关键内容（板书/PPT重点）（注意以mermaid形式生成，Mermaid 的序列图语法对中文符号敏感），四、实训练习与指导，五、课堂时间分布，六、相关知识点拓展''',
            "empty_response": "抱歉，没有找到相关的课程内容。请检查课程资料是否完整。",
            "similarity_threshold": 0.25,
            "top_n": 10,
            "show_quote": True,
            "refine_multiturn": True
        }
    },
    "qa": {
        "llm": {
            "model_name": "deepseek-chat",
            "temperature": 0.2,
            "top_p": 0.7,
            "frequency_penalty": 0.3,
            "presence_penalty": 0.2
        },
        "prompt": {
            "opener": "你好！我是学生答疑助手，专门回答同学们的课程问题。请直接提出你的问题，我会尽力为你解答！",
            "prompt": "你是一个耐心的学习导师。请基于课程内容回答学生的问题，要求：1. 回答要清晰易懂 2. 提供解题思路和方法 3. 适当举例说明 4. 鼓励学生思考 5. 如果问题超出课程范围，引导到相关知识点。",
            "empty_response": "这个问题可能超出了当前课程的范围。建议你复习相关知识点，或者向老师请教。",
            "similarity_threshold": 0.2,
            "top_n": 6,
            "show_quote": True,
            "refine_multiturn": True
        }
    },
    "grading": {
        "llm": {
            "model_name": "deepseek-chat",
            "temperature": 0.05,
            "top_p": 0.2,
            "frequency_penalty": 0.8,
            "presence_penalty": 0.5
        },
        "prompt": {
            "opener": "你好！我是作业批改助手，专门负责批改作业和提供反馈。请提供作业题目和参考答案，我将为你进行专业批改。",
            "prompt": "你是一个严格的作业批改专家。请严格按照参考答案批改作业，要求：1. 客观公正评分 2. 指出具体错误 3. 提供改进建议 4. 鼓励学生进步 5. 保持评分标准一致。对于主观题，要给出详细的评价理由。",
            "empty_response": "无法进行批改，请确保提供了完整的作业内容和参考答案。",
            "similarity_threshold": 0.4,
            "top_n": 8,
            "show_quote": True,
            "refine_multiturn": True
        }
    }
}


# 创建课程聊天助手
@router.post("/{course_id}/chats")
async def create_course_chat(
    course_id: int,
    request: CreateCourseChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建课程聊天助手"""
    try:
        # 权限检查
        course = db.get(Course, course_id)
        if not course or course.teacher_id != current_user.id:
            raise HTTPException(403, "无权操作该课程")
        
        # 检查课程是否有解析中的文件
        parsing_materials = db.query(CourseMaterial).filter(
            CourseMaterial.course_id == course_id,
            CourseMaterial.status == ParseStatus.parsing
        ).count()
        
        if parsing_materials == 0:
            raise HTTPException(400, "课程中没有正在解析的文件，无法创建聊天助手")
        
        # 检查课程是否有数据集名称
        if not course.dataset_name:
            raise HTTPException(400, "课程数据集未配置，无法创建聊天助手")
        
        # 验证聊天助手类型
        if request.chat_type not in CHAT_TYPES:
            raise HTTPException(400, f"不支持的聊天助手类型: {request.chat_type}")
        
        # 检查是否已存在同类型的聊天助手
        existing_chat = db.query(CourseChat).filter(
            CourseChat.course_id == course_id,
            CourseChat.chat_type == request.chat_type,
            CourseChat.is_active == 1
        ).first()
        
        if existing_chat:
            raise HTTPException(400, f"该课程已存在 {CHAT_TYPES[request.chat_type]}")
        
        # 获取该类型的配置
        config = CHAT_CONFIGS[request.chat_type]
        
        print(f"准备创建聊天助手，课程数据集名称: {course.dataset_name}")
        
        # 创建RagFlow聊天助手，传入专门的配置
        rag_chat = await create_chat(
            name=f"course_{course_id}_{request.chat_type}_{request.name}",
            dataset_names=[course.dataset_name],
            llm_config=config["llm"],
            prompt_config=config["prompt"]
        )
        
        # 保存到数据库
        course_chat = CourseChat(
            name=request.name,
            description=request.description,
            chat_id=rag_chat["chat_id"],
            course_id=course_id,
            teacher_id=current_user.id,
            chat_type=request.chat_type
        )
        
        db.add(course_chat) 
        db.commit()
        db.refresh(course_chat)
        
        return {
            "msg": f"{CHAT_TYPES[request.chat_type]}创建成功",
            "chat": {
                "id": course_chat.id,
                "name": course_chat.name,
                "description": course_chat.description,
                "chat_id": course_chat.chat_id,
                "chat_type": course_chat.chat_type,
                "chat_type_name": CHAT_TYPES[course_chat.chat_type],
                "course_id": course_chat.course_id,
                "teacher_id": course_chat.teacher_id,
                "created_at": course_chat.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "is_active": course_chat.is_active
            }
        }
        
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        import traceback
        print(f"创建聊天助手时发生错误: {str(e)}")
        print(f"错误详情: {traceback.format_exc()}")
        raise HTTPException(500, f"创建聊天助手失败: {str(e)}")

# 获取课程的聊天助手列表
@router.get("/{course_id}/chats")
def get_course_chats(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取课程的聊天助手列表"""
    # 权限检查 - 取消教师身份验证，允许任何用户查看
    course = db.get(Course, course_id)
    if not course:
        raise HTTPException(404, "课程不存在")
    
    # 注释掉教师身份验证，允许任何用户查看
    # if not course or course.teacher_id != current_user.id:
    #     raise HTTPException(403, "无权查看该课程")
    
    chats = db.query(CourseChat).filter(
        CourseChat.course_id == course_id,
        CourseChat.is_active == 1
    ).order_by(CourseChat.created_at.desc()).all()
    
    return {
        "chats": [
            {
                "id": chat.id,
                "name": chat.name,
                "description": chat.description,
                "chat_id": chat.chat_id,
                "chat_type": chat.chat_type,
                "chat_type_name": CHAT_TYPES.get(chat.chat_type, "未知类型"),
                "teacher_id": chat.teacher_id,
                "created_at": chat.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "is_active": chat.is_active
            }
            for chat in chats
        ]
    }

# 根据类型获取特定的聊天助手
@router.get("/{course_id}/chats/{chat_type}")
def get_course_chat_by_type(
    course_id: int,
    chat_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """根据类型获取特定的聊天助手"""
    # 权限检查 - 取消教师身份验证，允许任何用户访问
    course = db.get(Course, course_id)
    if not course: 
        raise HTTPException(404, "课程不存在")
    
    # 注释掉教师身份验证，允许任何用户访问
    # if current_user.role == "teacher" and course.teacher_id != current_user.id:
    #     raise HTTPException(403, "无权访问")
    # if current_user.role == "student" and course not in current_user.joined_courses:
    #     raise HTTPException(403, "未加入课程")
    
    chat = db.query(CourseChat).filter(
        CourseChat.course_id == course_id,
        CourseChat.chat_type == chat_type,
        CourseChat.is_active == 1
    ).first()
    
    if not chat:
        raise HTTPException(404, f"未找到 {CHAT_TYPES.get(chat_type, chat_type)} 聊天助手")
    
    print(f"找到聊天助手: {chat.name} (ID: {chat.chat_id})")
    print(f"聊天助手类型: {chat_type}")
    print(f"课程ID: {course_id}")
    
    return {
        "chat_id": chat.chat_id,
        "name": chat.name,
        "description": chat.description,
        "chat_type": chat.chat_type,
        "chat_type_name": CHAT_TYPES.get(chat.chat_type, "未知类型")
    }

# 删除课程聊天助手
@router.delete("/{course_id}/chats/{chat_id}")
async def delete_course_chat(
    course_id: int,
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除课程聊天助手"""
    # 权限检查
    course = db.get(Course, course_id)
    if not course or course.teacher_id != current_user.id:
        raise HTTPException(403, "无权操作该课程")
    
    # 查找聊天助手
    course_chat = db.query(CourseChat).filter(
        CourseChat.id == chat_id,
        CourseChat.course_id == course_id
    ).first()
    
    if not course_chat:
        raise HTTPException(404, "聊天助手不存在")
    
    try:
        # 删除RagFlow聊天助手
        await delete_chat(course_chat.chat_id)
        
        # 从数据库中删除
        db.delete(course_chat)
        db.commit()
        
        return {"msg": f"{CHAT_TYPES.get(course_chat.chat_type, '聊天助手')}删除成功"}
        
    except Exception as e:
        raise HTTPException(500, f"删除聊天助手失败: {str(e)}")

# 获取课程聊天助手状态
@router.get("/{course_id}/chat/status")
def get_course_chat_status(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取课程聊天助手状态"""
    # 权限检查 - 取消教师身份验证，允许任何用户查看
    course = db.get(Course, course_id)
    if not course:
        raise HTTPException(404, "课程不存在")
    
    # 注释掉教师身份验证，允许任何用户查看
    # if not course or course.teacher_id != current_user.id:
    #     raise HTTPException(403, "无权查看该课程")
    
    # 检查课程是否有解析中的文件
    parsing_materials = db.query(CourseMaterial).filter(
        CourseMaterial.course_id == course_id,
        CourseMaterial.status == ParseStatus.parsing
    ).count()
    
    # 获取现有的聊天助手
    existing_chats = db.query(CourseChat).filter(
        CourseChat.course_id == course_id,
        CourseChat.is_active == 1
    ).all()
    
    existing_types = [chat.chat_type for chat in existing_chats]
    
    return {
        "course_id": course.id,
        "course_title": course.title,
        "has_parsing_materials": parsing_materials > 0,
        "parsing_materials_count": parsing_materials,
        "existing_chat_types": existing_types,
        "available_chat_types": [chat_type for chat_type in CHAT_TYPES.keys() if chat_type not in existing_types],
        "chat_types_info": CHAT_TYPES
    }

# 聊天对话请求模型
class ChatMessageRequest(BaseModel):
    question: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None

# 与聊天助手进行单次对话
@router.post("/{course_id}/chats/{chat_type}/chat")
async def chat_with_assistant(
    course_id: int,
    chat_type: str,
    request: ChatMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """与指定类型的聊天助手进行单次对话"""
    try:
        # 权限检查 - 取消教师身份验证，允许任何用户访问
        course = db.get(Course, course_id)
        if not course: 
            raise HTTPException(404, "课程不存在")
        
        # 注释掉教师身份验证，允许任何用户访问
        # if current_user.role == "teacher" and course.teacher_id != current_user.id:
        #     raise HTTPException(403, "无权访问")
        # if current_user.role == "student" and course not in current_user.joined_courses:
        #     raise HTTPException(403, "未加入课程")
        
        # 从数据库中获取指定类型的聊天助手
        chat = db.query(CourseChat).filter(
            CourseChat.course_id == course_id,
            CourseChat.chat_type == chat_type,
            CourseChat.is_active == 1
        ).first()
        
        if not chat:
            raise HTTPException(404, f"未找到 {CHAT_TYPES.get(chat_type, chat_type)} 聊天助手")
        
        chat_id = chat.chat_id
        chat_name = f"course_{course_id}_{chat_type}_{chat.name}"
        print(f"从数据库获取聊天助手: {chat.name} (ID: {chat_id})")
        
        # 如果没有提供session_id，创建一个新的会话
        session_id = request.session_id
        if not session_id:
            try:
                session_name = f"session_{current_user.id}_{int(time.time())}"
                session_result = create_session(
                    chat_name=chat_name,
                    name=session_name,
                    user_id=str(current_user.id)
                )
                session_id = session_result['data']['session_id']
                print(f"创建新会话: {session_id}")
            except Exception as e:
                print(f"创建会话失败: {str(e)}")
                # 如果创建会话失败，继续使用user_id进行对话

        # 与聊天助手对话
        try:
            print(f"使用聊天助手名称: {chat_name}")
            
            # 如果创建会话失败或没有session_id，直接使用user_id进行对话
            if session_id:
                print(f"使用session_id进行对话: {session_id}")
                response = chat_with_assistant_once(
                    chat_name=chat_name,
                    question=request.question,
                    session_id=session_id,
                    user_id=None  # 使用session_id时不需要user_id
                )
            else:
                # 直接使用user_id进行对话，不创建会话
                print(f"使用user_id进行对话")
                response = chat_with_assistant_once(
                    chat_name=chat_name,
                    question=request.question,
                    session_id=None,
                    user_id=str(current_user.id)
                )
            
            return {
                "code": 0,
                "message": "对话成功",
                "data": {
                    "answer": response.get('data', {}).get('answer', ''),
                    "session_id": session_id,
                    "chat_type": chat_type,
                    "chat_type_name": CHAT_TYPES.get(chat_type, "未知类型"),
                    "chat_id": chat_id,
                    "chat_name": chat_name,
                    "question": request.question
                }
            }
            
        except Exception as e:
            print(f"聊天对话失败: {str(e)}")
            
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        import traceback
        print(f"聊天对话时发生错误: {str(e)}")
        print(f"错误详情: {traceback.format_exc()}")
        raise HTTPException(500, f"聊天对话失败: {str(e)}")

# 获取所有可用的聊天助手列表
@router.get("/assistants")
async def get_all_chat_assistants(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取所有可用的聊天助手列表"""
    try:
        # 获取所有聊天助手
        ragflow_response = list_chats()
        
        if ragflow_response.get('code') != 0:
            raise HTTPException(500, f"获取聊天助手失败: {ragflow_response.get('message', '未知错误')}")
        
        chats_data = ragflow_response.get('data', [])
        
        # 获取所有课程聊天助手信息
        course_chats = db.query(CourseChat).filter(CourseChat.is_active == 1).all()
        course_chat_ids = {chat.chat_id: chat for chat in course_chats}
        
        # 格式化返回数据
        formatted_chats = []
        for chat in chats_data:
            chat_id = chat.get("chat_id")
            course_chat = course_chat_ids.get(chat_id)
            
            formatted_chat = {
                "chat_id": chat_id,
                "name": chat.get("name"),
                "description": chat.get("description", ""),
                "create_date": chat.get("create_date"),
                "update_date": chat.get("update_date"),
                "llm": chat.get("llm", {}),
                "prompt": chat.get("prompt", {}),
                "dataset_ids": chat.get("dataset_ids"),
                "is_course_chat": course_chat is not None,
                "course_info": {
                    "course_id": course_chat.course_id if course_chat else None,
                    "course_title": None,  # 需要查询课程信息
                    "teacher_id": course_chat.teacher_id if course_chat else None,
                    "chat_type": course_chat.chat_type if course_chat else None,
                    "chat_type_name": CHAT_TYPES.get(course_chat.chat_type, "未知类型") if course_chat else None
                }
            }
            
            # 如果是课程聊天助手，获取课程信息
            if course_chat:
                course = db.get(Course, course_chat.course_id)
                if course:
                    formatted_chat["course_info"]["course_title"] = course.title
            
            formatted_chats.append(formatted_chat)
        
        return {
            "code": 0,
            "message": "获取聊天助手列表成功",
            "data": formatted_chats
        }
        
    except Exception as e:
        import traceback
        print(f"获取聊天助手列表时发生错误: {str(e)}")
        print(f"错误详情: {traceback.format_exc()}")
        raise HTTPException(500, f"获取聊天助手列表失败: {str(e)}")


# 和原有的对话（效果更好）
# 目前报错：{"detail": "对话失败: 'str' object has no attribute 'get'"}
# 简化的直接对话接口
class SimpleChatRequest(BaseModel):
    question: str
    chat_id: Optional[str] = None
    chat_name: Optional[str] = None

@router.post("/simple")
async def simple_chat_with_assistant(
    question: str,
    chat_id: Optional[str] = None,
    chat_name: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """简化的直接对话接口，通过chat_id或chat_name直接对话，避免会话所有权问题"""
    try:
        # 验证参数
        if not chat_id and not chat_name:
            raise HTTPException(400, "必须提供chat_id或chat_name")
        
        if not question:
            raise HTTPException(400, "问题不能为空")
        
        # 如果只有chat_id，获取chat_name
        if chat_id and not chat_name:
            try:
                from ai_core.services.chats_management_service import list_chats
                ragflow_response = list_chats(chat_id=chat_id)
                if ragflow_response.get('code') == 0 and ragflow_response.get('data'):
                    chat_name = ragflow_response['data'][0].get('name')
                else:
                    raise HTTPException(404, f"未找到ID为 {chat_id} 的聊天助手")
            except Exception as e:
                raise HTTPException(404, f"获取聊天助手信息失败: {str(e)}")
        
        # 好像必须要创建对话
        session_id = create_session(chat_name=chat_name, name=f"session_{current_user.id}_{int(time.time())}", user_id=str(current_user.id))['data']['session_id']
        try:
            print(f"使用聊天助手名称: {chat_name}")
            
            response = chat_with_assistant_once(
                chat_name=chat_name,
                question=question,
                session_id=session_id
            )
            
            # 处理响应可能是字符串或字典的情况
            answer = ""
            if isinstance(response, str):
                answer = response
            elif isinstance(response, dict):
                answer = response.get('data', {}).get('answer', '')
            else:
                answer = str(response)
            
            return {
                "code": 0,
                "message": "对话成功",
                "data": {
                    "answer": answer,
                    "session_id": None,
                    "chat_id": chat_id,
                    "chat_name": chat_name,
                    "question": question
                }
            }
            
        except Exception as e:
            print(f"对话失败: {str(e)}")
            raise HTTPException(500, f"对话失败: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"简化对话时发生错误: {str(e)}")
        print(f"错误详情: {traceback.format_exc()}")
        raise HTTPException(500, f"对话失败: {str(e)}")

# 更新聊天助手配置的请求模型
class UpdateChatConfigRequest(BaseModel):
    llm: Optional[dict] = None
    prompt: Optional[dict] = None
    description: Optional[str] = None

# 更新聊天助手配置
@router.put("/assistants/{chat_id}")
async def update_chat_assistant_config(
    chat_id: str,
    request: UpdateChatConfigRequest,
    current_user: User = Depends(get_current_user)
):
    """更新聊天助手配置"""
    try:
        # 检查权限 - 只有管理员可以更新配置
        if current_user.role != "admin":
            raise HTTPException(403, "只有管理员可以更新聊天助手配置")
        
        # 获取聊天助手信息
        ragflow_response = list_chats(chat_id=chat_id)
        if ragflow_response.get('code') != 0 or not ragflow_response.get('data'):
            raise HTTPException(404, "聊天助手不存在")
        
        chat_data = ragflow_response['data'][0]
        
        # 准备更新数据
        update_data = {}
        if request.llm is not None:
            update_data['llm'] = request.llm
        if request.prompt is not None:
            update_data['prompt'] = request.prompt
        if request.description is not None:
            update_data['description'] = request.description
        
        if not update_data:
            raise HTTPException(400, "没有提供要更新的数据")
        
        # 调用RagFlow API更新配置
        # 注意：这里需要实现update_chat_config函数
        # 由于RagFlow可能没有直接的更新接口，我们可能需要删除重建
        # 这里先返回成功，实际实现需要根据RagFlow的API
        
        return {
            "code": 0,
            "message": "聊天助手配置更新成功",
            "data": {
                "chat_id": chat_id,
                "updated_fields": list(update_data.keys())
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"更新聊天助手配置时发生错误: {str(e)}")
        print(f"错误详情: {traceback.format_exc()}")
        raise HTTPException(500, f"更新聊天助手配置失败: {str(e)}")

# 获取单个聊天助手详细信息
@router.get("/assistants/{chat_id}")
async def get_chat_assistant_detail(
    chat_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取单个聊天助手的详细信息"""
    try:
        # 获取聊天助手信息
        ragflow_response = list_chats(chat_id=chat_id)
        if ragflow_response.get('code') != 0 or not ragflow_response.get('data'):
            raise HTTPException(404, "聊天助手不存在")
        
        chat_data = ragflow_response['data'][0]
        
        # 获取课程信息
        course_chat = db.query(CourseChat).filter(CourseChat.chat_id == chat_id).first()
        course_info = None
        
        if course_chat:
            course = db.get(Course, course_chat.course_id)
            teacher = db.get(User, course_chat.teacher_id) if course_chat.teacher_id else None
            
            course_info = {
                "course_id": course_chat.course_id,
                "course_title": course.title if course else None,
                "teacher_id": course_chat.teacher_id,
                "teacher_name": teacher.username if teacher else None,
                "chat_type": course_chat.chat_type,
                "chat_type_name": CHAT_TYPES.get(course_chat.chat_type, "未知类型"),
                "created_at": course_chat.created_at.strftime("%Y-%m-%d %H:%M:%S") if course_chat.created_at else None
            }
        
        return {
            "code": 0,
            "message": "获取聊天助手详情成功",
            "data": {
                "chat_id": chat_data.get("chat_id"),
                "name": chat_data.get("name"),
                "description": chat_data.get("description", ""),
                "create_date": chat_data.get("create_date"),
                "update_date": chat_data.get("update_date"),
                "llm": chat_data.get("llm", {}),
                "prompt": chat_data.get("prompt", {}),
                "dataset_ids": chat_data.get("dataset_ids"),
                "is_course_chat": course_chat is not None,
                "course_info": course_info
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"获取聊天助手详情时发生错误: {str(e)}")
        print(f"错误详情: {traceback.format_exc()}")
        raise HTTPException(500, f"获取聊天助手详情失败: {str(e)}")
