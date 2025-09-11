import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from typing import Optional, Dict, Any, List, Union
import requests
import json
import os
import time
import httpx
from .dataset_management_service import get_dataset_id_by_name

API_KEY = "ragflow-FlNDljYzU0M2UxMTExZjA5NGUxMGU0NW"
BASE_URL = "http://localhost:8080"

def create_chat(
    name: str,
    dataset_names: Optional[List[str]] = None,
    avatar: Optional[str] = None,
    llm: Optional[Dict] = None,
    prompt: Optional[Dict] = None
) -> Dict:
    """
    创建一个聊天助手
    Args:
        name (str): 聊天助手名称
        dataset_names (List[str]): 数据集名称列表
        avatar (Optional[str]): 聊天头像的Base64编码
        llm (Optional[Dict]): LLM设置, 包含model_name, temperature等参数
        prompt (Optional[Dict]): 提示词设置, 包含similarity_threshold等参数
    Returns:
        Dict: API响应数据
    Raises:
        Exception: 如果创建失败则抛出异常
    """
    try:
        # 获取数据集ID列表
        dataset_ids = []
        if dataset_names:  # 添加判断，只有当dataset_names不为None时才处理
            for dataset_name in dataset_names:
                dataset_id = get_dataset_id_by_name(dataset_name)
                dataset_ids.append(dataset_id)
            
        # 准备默认的LLM配置
        default_llm = {
            "model_name": "deepseek-chat",
            "temperature": 0.1,
            "top_p": 0.3,
            "presence_penalty": 0.4,
            "frequency_penalty": 0.7
        }
        
        # 准备默认的prompt配置
        default_prompt = {
            "similarity_threshold": 0.2,
            "keywords_similarity_weight": 0.7,
            "top_n": 6,
            "variables": [
                {"key": "knowledge", "optional": True}
            ],
            "empty_response": "抱歉, 知识库中没有找到你想要的信息, 换个问题试试呢?",
            "opener": "你好, 我是你的助手, 有什么可以帮你的吗?",
            "show_quote": True,
            "prompt": "你是一个智能助手. 请总结知识库的内容以回答问题. 请列出知识库中的数据并详细回答. 当所有知识库内容与问题无关时, 你的回答必须包含句子'抱歉, 知识库中没有找到你想要的信息, 换个问题试试呢?' 回答需要考虑聊天历史.\n"
        }
        
        # 合并用户提供的配置和默认配置
        final_llm = {**default_llm, **(llm or {})}
        final_prompt = {**default_prompt, **(prompt or {})}
        
        # 准备请求数据
        data = {
            "name": name,
            "dataset_ids": dataset_ids,
            "llm": final_llm,
            "prompt": final_prompt
        }
        
        # 如果提供了头像, 添加到请求数据中
        if avatar:
            data["avatar"] = avatar
            
        # 发送创建请求
        response = requests.post(
            f"{BASE_URL}/api/v1/chats",
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {API_KEY}'
            },
            json=data
        )
        
        # 检查响应
        if response.status_code == 200:
            result = response.json()
            raw_data = result["data"]
            if result.get('code') == 0:
                return {
                    "code": 0,
                    "message": "创建聊天助手成功",
                    "data": {
                        "chat_id": raw_data["id"],
                        "name": raw_data["name"],
                        "dataset_ids": raw_data["dataset_ids"],
                        "description": raw_data["description"],
                        "create_date": raw_data["create_date"],
                        "update_date": raw_data["update_date"],
                        "llm": raw_data["llm"],
                        "prompt": raw_data["prompt"]
                    }
                }
            else:
                error_msg = result.get('message', '未知错误')
                raise Exception(f"创建聊天助手失败: {error_msg}")
        else:
            error_msg = response.json().get('message', '未知错误') if response.content else '未知错误'
            raise Exception(f"创建聊天助手失败: {error_msg}")
            
    except Exception as e:
        raise Exception(f"创建聊天助手失败: {str(e)}")


def update_chat(
    chat_id: str,
    name: Optional[str] = None,
    dataset_names: Optional[List[str]] = None,
    avatar: Optional[str] = None,
    llm: Optional[Dict] = None,
    prompt: Optional[Dict] = None
) -> Dict:
    """
    更新指定聊天助手的配置
    Args:
        chat_id (str): 聊天助手ID
        name (Optional[str]): 修改后的聊天助手名称
        dataset_names (Optional[List[str]]): 数据集名称列表
        avatar (Optional[str]): 聊天头像的Base64编码
        llm (Optional[Dict]): LLM设置, 包含model_name, temperature等参数
        prompt (Optional[Dict]): 提示词设置, 包含similarity_threshold等参数
    Returns:
        Dict: API响应数据
    Raises:
        Exception: 如果更新失败则抛出异常
    """
    try:
        # 准备请求数据
        data = {}
        
        # 添加基本信息
        if name is not None:
            data["name"] = name
        if avatar is not None:
            data["avatar"] = avatar
            
        # 获取当前配置
        try:
            result = list_chats(chat_id=chat_id)
            if result.get('code') == 0:
                chats = result.get('data', [])
                if chats:  # 如果找到了聊天助手
                    current_config = chats[0]  # 获取第一个（也是唯一的）聊天助手的配置
                else:
                    raise Exception(f"找不到ID为 '{chat_id}' 的聊天助手")
            else:
                raise Exception(result.get('message', '未知错误'))
                
        except Exception as e:
            raise Exception(f"获取聊天助手配置失败: {str(e)}")
            
        # 如果提供了数据集名称, 转换为数据集ID并合并
        if dataset_names is not None:
            # 获取当前的数据集ID列表
            current_dataset_ids = set(current_config.get("dataset_ids", []))
            
            # 转换新的数据集名称为ID
            new_dataset_ids = set()
            for dataset_name in dataset_names:
                dataset_id = get_dataset_id_by_name(dataset_name)
                new_dataset_ids.add(dataset_id)
            
            # 合并数据集ID
            merged_dataset_ids = list(current_dataset_ids.union(new_dataset_ids))
            data["dataset_ids"] = merged_dataset_ids
            
        # 如果提供了LLM配置, 合并配置
        if llm is not None:
            data["llm"] = {**(current_config.get("llm", {})), **llm}
            
        # 如果提供了prompt配置, 合并配置
        if prompt is not None:
            data["prompt"] = {**(current_config.get("prompt", {})), **prompt}
            
        # 发送更新请求
        response = requests.put(
            f"{BASE_URL}/api/v1/chats/{chat_id}",
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {API_KEY}'
            },
            json=data
        )
        
        # 检查响应
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 0:
                return {
                    "code": 0,
                    "message": "更新聊天助手成功"
                }
            else:
                error_msg = result.get('message', '未知错误')
                raise Exception(f"更新聊天助手失败: {error_msg}")
        else:
            error_msg = response.json().get('message', '未知错误') if response.content else '未知错误'
            raise Exception(f"更新聊天助手失败: {error_msg}")
            
    except Exception as e:
        raise Exception(f"更新聊天助手失败: {str(e)}")


def get_chat_id_by_name(chat_name: str) -> str:
    """
    根据聊天助手名称获取其ID
    Args:
        chat_name (str): 聊天助手名称
    Returns:
        str: 聊天助手ID
    Raises:
        Exception: 如果获取失败或未找到对应的聊天助手则抛出异常
    """
    try:
        # 发送请求获取聊天助手列表
        response = requests.get(
            f"{BASE_URL}/api/v1/chats",
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {API_KEY}'
            }
        )
        
        # 检查响应
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 0:
                chats = result.get('data', [])  # 直接获取data列表
                # 查找匹配的聊天助手
                for chat in chats:
                    if chat.get('name') == chat_name:
                        return chat['id']
                raise Exception(f"未找到名称为 '{chat_name}' 的聊天助手")
            else:
                error_msg = result.get('message', '未知错误')
                raise Exception(f"获取聊天助手列表失败: {error_msg}")
        else:
            error_msg = response.json().get('message', '未知错误') if response.content else '未知错误'
            raise Exception(f"获取聊天助手列表失败: {error_msg}")
            
    except Exception as e:
        raise Exception(f"获取聊天助手ID失败: {str(e)}")
    
    
def list_chats(
    page: int = 1,
    page_size: int = 30,
    orderby: str = "create_time",
    desc: bool = True,
    chat_id: Optional[str] = None,
    chat_name: Optional[str] = None
) -> Dict:
    """
    列出聊天助手
    Args:
        page (int): 页码, 默认为1
        page_size (int): 每页数量, 默认为30
        orderby (str): 排序字段, 可选 create_time 或 update_time
        desc (bool): 是否降序排序, 默认为True
        chat_id (Optional[str]): 聊天助手ID
        chat_name (Optional[str]): 聊天助手名称
    Returns:
        Dict: API响应数据
    Raises:
        Exception: 如果获取失败则抛出异常
    """
    try:
        # 构建查询参数
        params = {
            'page': page,
            'page_size': page_size,
            'orderby': orderby,
            'desc': str(desc).lower()
        }
        
        # 添加可选参数
        if chat_id:
            params['id'] = chat_id
        if chat_name:
            params['name'] = chat_name
            
        # 发送请求
        response = requests.get(
            f"{BASE_URL}/api/v1/chats",
            headers={
                'Authorization': f'Bearer {API_KEY}'
            },
            params=params
        )
        
        # 检查响应
        if response.status_code == 200:
            result = response.json()
            raw_data = result["data"]
            formatted_result = [{
                "chat_id": chat.get("id"),
                "name": chat.get("name"),
                "dataset_ids": chat.get("dataset_ids"),
                "description": chat.get("description"),
                "create_date": chat.get("create_date"),
                "update_date": chat.get("update_date"),
                "llm": chat.get("llm"),
                "prompt": chat.get("prompt")
            } for chat in raw_data]
            
            if result.get('code') == 0:
                return {
                    "code": 0,
                    "message": "获取聊天助手列表成功",
                    "data": formatted_result
                }
            else:
                error_msg = result.get('message', '未知错误')
                raise Exception(f"获取聊天助手列表失败: {error_msg}")
        else:
            error_msg = response.json().get('message', '未知错误') if response.content else '未知错误'
            raise Exception(f"获取聊天助手列表失败: {error_msg}")
            
    except Exception as e:
        raise Exception(f"获取聊天助手列表失败: {str(e)}")

def delete_chats(chat_ids: List[str]) -> Dict:
    """
    删除指定的聊天助手
    Args:
        chat_ids (List[str]): 要删除的聊天助手ID列表
    Returns:
        Dict: API响应数据
    Raises:
        Exception: 如果删除失败则抛出异常
    """
    try:
        # 准备请求数据
        data = {
            "ids": chat_ids
        }
        
        # 发送删除请求
        response = requests.delete(
            f"{BASE_URL}/api/v1/chats",
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {API_KEY}'
            },
            json=data
        )
        
        # 检查响应
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 0:
                return {
                    "code": 0,
                    "message": "删除聊天助手成功"
                }
            else:
                error_msg = result.get('message', '未知错误')
                raise Exception(f"删除聊天助手失败: {error_msg}")
        else:
            error_msg = response.json().get('message', '未知错误') if response.content else '未知错误'
            raise Exception(f"删除聊天助手失败: {error_msg}")
            
    except Exception as e:
        raise Exception(f"删除聊天助手失败: {str(e)}")
    

    