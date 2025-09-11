from fastapi import APIRouter, HTTPException, Depends, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from models import User, Course, CourseChat, Preparation, PreparationShare, PreparationStatus
from database import get_db
from user_routes import get_current_user
from pydantic import BaseModel
from typing import Optional, Dict, List
import json
import os
import sys
import re

# 添加ai-core到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'ai_core'))

try:
    from ai_core.utils.ppt_generate import create_presentation
except ImportError:
    def create_presentation(*args, **kwargs):
        raise HTTPException(500, "ai-core模块未正确配置")

def clean_markdown_content(content: str) -> str:
    """
    清理Markdown格式，转换为纯文本
    """
    if not content:
        return ""
    
    # 移除Markdown标记
    cleaned = content
    
    # 移除标题标记
    cleaned = re.sub(r'^#{1,6}\s+', '', cleaned, flags=re.MULTILINE)
    
    # 移除粗体和斜体标记
    cleaned = re.sub(r'\*\*(.*?)\*\*', r'\1', cleaned)  # **粗体**
    cleaned = re.sub(r'\*(.*?)\*', r'\1', cleaned)      # *斜体*
    cleaned = re.sub(r'__(.*?)__', r'\1', cleaned)      # __粗体__
    cleaned = re.sub(r'_(.*?)_', r'\1', cleaned)        # _斜体_
    
    # 移除代码块标记
    cleaned = re.sub(r'```[\s\S]*?```', '', cleaned)    # ```代码块```
    cleaned = re.sub(r'`([^`]+)`', r'\1', cleaned)      # `行内代码`
    
    # 移除链接标记，保留链接文本
    cleaned = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', cleaned)  # [文本](链接)
    
    # 移除图片标记
    cleaned = re.sub(r'!\[([^\]]*)\]\([^)]+\)', '', cleaned)    # ![alt](图片链接)
    
    # 移除列表标记
    cleaned = re.sub(r'^[\s]*[-*+]\s+', '', cleaned, flags=re.MULTILINE)  # 无序列表
    cleaned = re.sub(r'^[\s]*\d+\.\s+', '', cleaned, flags=re.MULTILINE)  # 有序列表
    
    # 移除引用标记
    cleaned = re.sub(r'^>\s+', '', cleaned, flags=re.MULTILINE)  # > 引用
    
    # 移除水平线
    cleaned = re.sub(r'^[\s]*[-*_]{3,}[\s]*$', '', cleaned, flags=re.MULTILINE)
    
    # 移除表格标记
    cleaned = re.sub(r'\|.*\|', '', cleaned)  # 简单移除表格行
    
    # 清理多余的空行
    cleaned = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned)
    
    # 清理行首行尾空白
    cleaned = '\n'.join(line.strip() for line in cleaned.split('\n'))
    
    # 移除HTML标签（如果有的话）
    cleaned = re.sub(r'<[^>]+>', '', cleaned)
    
    return cleaned.strip()

router = APIRouter(prefix="/ppt", tags=["PPT生成"])

class PPTGenerateRequest(BaseModel):
    title: str
    content_dict: Dict[str, List[str]]
    course_id: Optional[int] = None
    theme: Optional[str] = "professional"  # 颜色主题
    font_config: Optional[str] = "default"  # 字体配置
    include_animations: Optional[bool] = False  # 是否包含动画

class PPTOutlineRequest(BaseModel):
    course_id: int
    topic: str
    chat_name: Optional[str] = None
    preparation_id: Optional[int] = None  # 参考的教案ID

@router.get("/preparations/{course_id}")
async def get_course_preparations(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取课程的教案列表，用于PPT生成时选择参考"""
    try:
        # 验证课程权限
        course = db.get(Course, course_id)
        if not course:
            raise HTTPException(404, "课程不存在")
        
        # 获取该课程的所有教案（包括自己创建的和别人分享的）
        # 构建查询：包括自己创建的和别人分享给我的教案
        shared_preparation_ids = db.query(PreparationShare.preparation_id).filter(
            PreparationShare.to_teacher_id == current_user.id
        ).subquery()
        
        query = db.query(Preparation).filter(
            and_(
                Preparation.course_id == course_id,
                or_(
                    Preparation.teacher_id == current_user.id,  # 我创建的
                    Preparation.id.in_(shared_preparation_ids)  # 分享给我的
                )
            )
        )
        
        # 只获取已完成的教案
        query = query.filter(Preparation.status == PreparationStatus.completed)
        
        preparations = query.order_by(Preparation.updated_at.desc()).all()
        
        result = []
        for prep in preparations:
            # 清理教案内容，移除Markdown格式
            cleaned_content = clean_markdown_content(prep.content)
            preview_content = cleaned_content[:200] + "..." if len(cleaned_content) > 200 else cleaned_content
            
            result.append({
                "id": prep.id,
                "title": prep.title,
                "content": preview_content,  # 使用清理后的内容
                "teacher_name": prep.teacher.username if prep.teacher else "未知教师",
                "created_at": prep.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": prep.updated_at.strftime("%Y-%m-%d %H:%M:%S")
            })
        
        return {
            "code": 0,
            "message": "获取教案列表成功",
            "data": {
                "preparations": result,
                "total": len(result)
            }
        }
        
    except Exception as e:
        import traceback
        print(f"获取教案列表时发生错误: {str(e)}")
        print(f"错误详情: {traceback.format_exc()}")
        raise HTTPException(500, f"获取教案列表失败: {str(e)}")

@router.get("/themes")
async def get_available_themes():
    """获取可用的PPT主题列表"""
    try:
        from ai_core.utils.ppt_generate import get_available_themes
        themes = get_available_themes()
        return {
            "code": 0,
            "message": "获取主题列表成功",
            "data": {
                "themes": themes,
                "theme_descriptions": {
                    "professional": "专业商务风格，适合正式场合",
                    "modern": "现代简约风格，适合技术展示",
                    "elegant": "优雅精致风格，适合学术报告",
                    "tech": "科技感风格，适合技术主题"
                }
            }
        }
    except Exception as e:
        raise HTTPException(500, f"获取主题列表失败: {str(e)}")

@router.get("/fonts")
async def get_available_fonts():
    """获取可用的字体配置列表"""
    try:
        from ai_core.utils.ppt_generate import get_available_fonts
        fonts = get_available_fonts()
        return {
            "code": 0,
            "message": "获取字体配置列表成功",
            "data": {
                "fonts": fonts,
                "font_descriptions": {
                    "default": "微软雅黑，清晰易读",
                    "modern": "思源黑体，现代简约",
                    "elegant": "华文细黑，优雅精致"
                }
            }
        }
    except Exception as e:
        raise HTTPException(500, f"获取字体配置列表失败: {str(e)}")

@router.post("/generate-outline")
async def generate_ppt_outline(
    request: PPTOutlineRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """通过教师备课助手生成PPT大纲"""
    try:
        # 验证课程权限
        course = db.get(Course, request.course_id)
        if not course:
            raise HTTPException(404, "课程不存在")
        
        # 获取教师备课助手
        preparation_chat = db.query(CourseChat).filter(
            CourseChat.course_id == request.course_id,
            CourseChat.chat_type == "preparation",
            CourseChat.is_active == 1
        ).first()
        
        if not preparation_chat:
            raise HTTPException(404, "未找到教师备课助手，请先创建备课助手")
        
        # 构建问题
        question = f"""请为"{request.topic}"这个主题生成一个详细的PPT大纲。

要求：
1. 返回格式必须是JSON格式
2. 包含PPT标题和内容结构
3. 每个章节包含具体的要点
4. 适合课堂教学使用"""

        # 如果有选择参考教案，添加教案内容到问题中
        if request.preparation_id:
            preparation = db.get(Preparation, request.preparation_id)
            if preparation:
                # 验证教案权限
                has_access = (
                    preparation.teacher_id == current_user.id or
                    preparation.is_public == 1 or
                    db.query(PreparationShare).filter(
                        and_(
                            PreparationShare.preparation_id == request.preparation_id,
                            PreparationShare.to_teacher_id == current_user.id
                        )
                    ).first() is not None
                )
                
                if has_access:
                    # 清理教案内容，移除Markdown格式
                    cleaned_content = clean_markdown_content(preparation.content)
                    
                    question += f"""

参考教案信息：
标题：{preparation.title}
内容：{cleaned_content}

请基于以上教案内容，为PPT大纲提供更详细和准确的内容结构。"""
                else:
                    raise HTTPException(403, "无权访问该教案")

        question += f"""

请按照以下JSON格式返回：
{{
    "title": "PPT标题",
    "content_dict": {{
        "第一章标题": ["要点1", "要点2", "要点3"],
        "第二章标题": ["要点1", "要点2", "要点3"],
        ...
    }}
}}

主题：{request.topic}"""

        # 调用simple chat接口
        from teacher.chat_routes import simple_chat_with_assistant
        
        response = await simple_chat_with_assistant(
            question=question,
            chat_name=f"course_{request.course_id}_preparation_{preparation_chat.name}",
            current_user=current_user
        )
        
        if response.get("code") != 0:
            raise HTTPException(500, f"生成大纲失败: {response.get('message', '未知错误')}")
        
        answer = response.get("data", {}).get("answer", "")
        
        # 尝试解析JSON格式的答案
        try:
            # 查找JSON内容
            import re
            json_match = re.search(r'\{.*\}', answer, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                outline_data = json.loads(json_str)
                
                # 验证数据结构
                if "title" not in outline_data or "content_dict" not in outline_data:
                    raise ValueError("返回的数据格式不正确")
                
                return {
                    "code": 0,
                    "message": "PPT大纲生成成功",
                    "data": outline_data
                }
            else:
                # 如果没有找到JSON，返回原始答案
                return {
                    "code": 0,
                    "message": "PPT大纲生成成功",
                    "data": {
                        "title": request.topic,
                        "content_dict": {
                            "原始回答": [answer]
                        }
                    }
                }
                
        except (json.JSONDecodeError, ValueError) as e:
            # JSON解析失败，返回原始答案
            return {
                "code": 0,
                "message": "PPT大纲生成成功（格式解析失败，请手动调整）",
                "data": {
                    "title": request.topic,
                    "content_dict": {
                        "原始回答": [answer]
                    }
                }
            }
            
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"生成PPT大纲时发生错误: {str(e)}")
        print(f"错误详情: {traceback.format_exc()}")
        raise HTTPException(500, f"生成PPT大纲失败: {str(e)}")

@router.post("/generate")
async def generate_ppt(
    request: PPTGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """根据大纲生成PPT文件"""
    try:
        # 验证数据
        if not request.title or not request.content_dict:
            raise HTTPException(400, "标题和内容不能为空")
        
        # 验证主题和字体配置
        from ai_core.utils.ppt_generate import get_available_themes, get_available_fonts
        
        available_themes = get_available_themes()
        available_fonts = get_available_fonts()
        
        if request.theme not in available_themes:
            raise HTTPException(400, f"不支持的主题: {request.theme}")
        
        if request.font_config not in available_fonts:
            raise HTTPException(400, f"不支持的字体配置: {request.font_config}")
        
        # 生成PPT文件
        file_path = create_presentation(
            request.title, 
            request.content_dict,
            theme=request.theme,
            font_config=request.font_config,
            include_animations=request.include_animations
        )
        
        # 获取文件名
        file_name = os.path.basename(file_path)
        
        return {
            "code": 0,
            "message": "PPT生成成功",
            "data": {
                "file_path": file_path,
                "file_name": file_name,
                "download_url": f"/ppt/download/{file_name}",
                "theme": request.theme,
                "font_config": request.font_config,
                "slide_count": len(request.content_dict) + 2  # 内容页 + 封面页 + 结束页
            }
        }
        
    except Exception as e:
        import traceback
        print(f"生成PPT时发生错误: {str(e)}")
        print(f"错误详情: {traceback.format_exc()}")
        raise HTTPException(500, f"生成PPT失败: {str(e)}")

@router.get("/download/{file_name}")
async def download_ppt(file_name: str):
    """下载PPT文件"""
    try:
        # 构建文件路径
        save_dir = "D:\\Download"
        file_path = os.path.join(save_dir, file_name)
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise HTTPException(404, "文件不存在")
        
        # 返回文件
        return FileResponse(
            path=file_path,
            filename=file_name,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"下载文件失败: {str(e)}") 