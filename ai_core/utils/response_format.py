from typing import Any, Dict, Optional, List
from datetime import datetime
import re

class APIResponse:
    """API响应格式化工具类"""
    
    @staticmethod
    def success(message: str = "操作成功", data: Any = None) -> Dict[str, Any]:
        """
        成功响应
        Args:
            message: 成功信息
            data: 返回数据
        """
        return {
            "code": 0,
            "message": message,
            "data": data
        }
    
    @staticmethod
    def error(message: str = "操作失败", code: int = 1, data: Any = None) -> Dict[str, Any]:
        """
        错误响应
        Args:
            message: 错误信息
            code: 错误码（非0）
            data: 额外的错误数据
        """
        return {
            "code": code,
            "message": message,
            "data": data
        }

    @staticmethod
    def parse_analysis_text(text: str) -> Dict[str, Any]:
        """
        解析AI的分析文本，提取结构化信息
        Args:
            text: AI的原始回答文本
        Returns:
            解析后的结构化数据
        """
        # 初始化结果
        result = {
            "summary": "",
            "strengths": [],
            "weaknesses": [],
            "suggestions": []
        }
        
        # 尝试提取总结部分（第一段通常是总结）
        paragraphs = text.split('\n\n')
        if paragraphs:
            result["summary"] = paragraphs[0].strip()
        
        # 提取优势（通常在"优势"、"优点"、"掌握良好"等关键词后）
        strength_matches = re.findall(r'(?:优势|优点|掌握良好|掌握情况好)[:：](.*?)(?=\n|$)', text, re.MULTILINE)
        for match in strength_matches:
            points = [p.strip() for p in match.split('、') if p.strip()]
            result["strengths"].extend(points)
        
        # 提取劣势（通常在"劣势"、"不足"、"需要改进"等关键词后）
        weakness_matches = re.findall(r'(?:劣势|不足|薄弱|需要改进)[:：](.*?)(?=\n|$)', text, re.MULTILINE)
        for match in weakness_matches:
            points = [p.strip() for p in match.split('、') if p.strip()]
            result["weaknesses"].extend(points)
        
        # 提取建议（通常在"建议"、"推荐"等关键词后）
        suggestion_matches = re.findall(r'(?:建议|推荐|可以|应该)[:：](.*?)(?=\n|$)', text, re.MULTILINE)
        for match in suggestion_matches:
            points = [p.strip() for p in match.split('、') if p.strip()]
            result["suggestions"].extend(points)
        
        return result

    @staticmethod
    def format_analysis_result(raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        格式化AI分析结果
        Args:
            raw_data: AI返回的原始数据
        Returns:
            整理后的分析数据
        """
        # 如果只有answer字段，尝试解析文本
        if "answer" in raw_data:
            parsed_data = APIResponse.parse_analysis_text(raw_data["answer"])
            return {
                "original_answer": raw_data["answer"],  # 保留原始回答
                "structured_data": parsed_data          # 添加解析后的结构化数据
            }
        return raw_data

    @staticmethod
    def format_chat_result(raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        格式化对话结果
        Args:
            raw_data: AI返回的原始对话数据
        Returns:
            整理后的对话数据
        """
        return {
            "answer": raw_data.get("answer", ""),
            "created_at": raw_data.get("created_at", datetime.now().isoformat())
        }

    @staticmethod
    def format_dataset_info(raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        格式化数据集信息
        Args:
            raw_data: 原始数据集信息
        Returns:
            整理后的数据集信息
        """
        return {
            "dataset_id": raw_data.get("id"),
            "name": raw_data.get("name"),
            "description": raw_data.get("description"),
            "document_count": raw_data.get("document_count", 0),
            "created_at": raw_data.get("created_at"),
            "updated_at": raw_data.get("updated_at"),
            # 只返回前端需要的配置信息
            "config": {
                "language": raw_data.get("language"),
                "permission": raw_data.get("permission")
            }
        }

    @staticmethod
    def format_user_progress(
        user_id: str,
        username: str,
        course_name: str,
        progress_data: list,
        ai_analysis: Dict[str, Any],
        last_updated: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        格式化用户学习进度数据
        Args:
            user_id: 用户ID
            username: 用户名
            course_name: 课程名称
            progress_data: 进度数据
            ai_analysis: AI分析结果
            last_updated: 最后更新时间
        """
        # 使用format_analysis_result处理AI分析结果
        formatted_analysis = APIResponse.format_analysis_result(ai_analysis)
        
        return {
            "user_info": {
                "user_id": user_id,
                "username": username,
                "course_name": course_name
            },
            "progress_data": progress_data,
            "ai_analysis": formatted_analysis,
            "last_updated": last_updated.isoformat() if last_updated else datetime.now().isoformat()
        }
    
    @staticmethod
    def format_chat_response(
        session_id: str,
        question: str,
        raw_response: Dict[str, Any],
        chat_name: str,
        created_at: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        格式化对话响应
        Args:
            session_id: 会话ID
            question: 问题
            raw_response: AI的原始响应
            chat_name: 对话助手名称
            created_at: 创建时间
        """
        # 使用format_chat_result处理AI响应
        formatted_response = APIResponse.format_chat_result(raw_response)
        
        return {
            "session_info": {
                "session_id": session_id,
                "chat_name": chat_name
            },
            "message": {
                "question": question,
                "answer": formatted_response["answer"],
                "created_at": created_at.isoformat() if created_at else formatted_response["created_at"]
            }
        }
    
    @staticmethod
    def format_knowledge_point(
        point_id: str,
        point_name: str,
        mastery_level: float,
        description: Optional[str] = None,
        last_review: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        格式化知识点数据
        Args:
            point_id: 知识点ID
            point_name: 知识点名称
            mastery_level: 掌握程度
            description: 描述
            last_review: 最后复习时间
        """
        return {
            "point_id": point_id,
            "point_name": point_name,
            "mastery_level": mastery_level,
            "description": description,
            "last_review": last_review.isoformat() if last_review else None
        } 