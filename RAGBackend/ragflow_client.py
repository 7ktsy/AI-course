import requests
import httpx
from openai import OpenAI
import os
from typing import List,Dict,Optional
import json
from fastapi import HTTPException
from ai_core.services.session_management_service import chat_with_assistant_once
from models import User
import time

API_KEY  = os.getenv("RAGFLOW_API_KEY", "ragflow-FlNDljYzU0M2UxMTExZjA5NGUxMGU0NW")
BASE_URL = os.getenv("RAGFLOW_BASE_URL", "http://localhost:8080")
RAG_API  = f"{BASE_URL}/api/v1"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}"
}

# # 简单的聊天函数
# async def simple_chat_with_assistant(
#     question: str,
#     # chat_id: Optional[str] = None,
#     chat_name: Optional[str] = None
# ) -> Dict:
#     """简化的直接对话接口"""
#     try:
#         if not chat_name:
#             raise ValueError("必须提供chat_name")
        
#         if not question:
#             raise ValueError("问题不能为空")
        
#         # # 如果只有chat_id，获取chat_name
#         # if chat_id and not chat_name:
#         #     try:
#         #         ragflow_response = list_chats(chat_id=chat_id)
#         #         if ragflow_response.get('code') == 0 and ragflow_response.get('data'):
#         #             chat_name = ragflow_response['data'][0].get('name')
#         #         else:
#         #             raise ValueError(f"未找到ID为 {chat_id} 的聊天助手")
#         #     except Exception as e:
#         #         raise ValueError(f"获取聊天助手信息失败: {str(e)}")
        
#         from ai_core.services.chats_management_service import chat_with_assistant_once
#         response = chat_with_assistant_once(
#             chat_name=chat_name,
#             question=question,
#             session_id=None
#         )
        
#         # 处理响应可能是字符串或字典的情况
#         answer = ""
#         if isinstance(response, str):
#             answer = response
#         elif isinstance(response, dict):
#             answer = response.get('data', {}).get('answer', '')
#         else:
#             answer = str(response)
        
#         return {
#             "code": 0,
#             "message": "对话成功",
#             "data": {
#                 "answer": answer,
#                 "chat_id": chat_id,
#                 "chat_name": chat_name,
#                 "question": question
#             }
#         }
        
#     except Exception as e:
#         print(f"对话失败: {str(e)}")
#         raise ValueError(f"对话失败: {str(e)}")

#检查返回值
def _check_resp(resp: requests.Response | httpx.Response, action: str):
    if isinstance(resp, requests.Response):
        data = resp.json()
    else:
        data = resp.json()
    if resp.status_code != 200 or data.get("code") != 0:
        raise RuntimeError(f"{action} 失败：{data.get('message')}")
    return data

#聊天助手创建
async def create_chat(name: str, dataset_names: List[str], llm_config: Dict = None, prompt_config: Dict = None) -> Dict:
    try:
        # 将数据集名称转换为数据集ID
        dataset_ids = []
        for dataset_name in dataset_names:
            try:
                dataset_id = get_dataset_id_by_name(dataset_name)
                dataset_ids.append(dataset_id)
                print(f"找到数据集: {dataset_name} -> {dataset_id}")
            except Exception as e:
                raise RuntimeError(f"获取数据集ID失败: {dataset_name}, 错误: {str(e)}")
        
        # 如果没有找到任何数据集，抛出错误
        if not dataset_ids:
            raise RuntimeError("没有找到任何有效的数据集，无法创建聊天助手")
        
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
        final_llm = {**default_llm, **(llm_config or {})}
        final_prompt = {**default_prompt, **(prompt_config or {})}
        
        payload = {
            "name": name, 
            "dataset_ids": dataset_ids,
            "llm": final_llm,
            "prompt": final_prompt
        }
        
        print(f"创建聊天助手请求: {json.dumps(payload, indent=2, ensure_ascii=False)}")

        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{RAG_API}/chats", headers=HEADERS, json=payload)
            
            # 打印原始响应用于调试
            print(f"RagFlow API 响应状态码: {resp.status_code}")
            print(f"RagFlow API 响应内容: {resp.text}")
            
            data = _check_resp(resp, "创建聊天助手")
            
            # 详细检查响应结构
            print(f"解析后的响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            if "data" not in data:
                raise RuntimeError(f"API响应缺少data字段: {data}")
            
            data_content = data["data"]
            print(f"data字段内容: {json.dumps(data_content, indent=2, ensure_ascii=False)}")
            print(f"data字段的键: {list(data_content.keys())}")
            
            # 检查聊天助手ID字段 - 可能是 chat_id 或 id
            chat_id = None
            if "chat_id" in data_content:
                chat_id = data_content["chat_id"]
            elif "id" in data_content:
                chat_id = data_content["id"]
            else:
                raise RuntimeError(f"API响应data中缺少聊天助手ID字段。可用字段: {list(data_content.keys())}")
            
            print(f"成功创建聊天助手: {name} -> {chat_id}")
            
            return {"chat_id": chat_id, "name": name}
    except Exception as e:
        print(f"创建聊天助手失败: {str(e)}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        raise

#删除聊天助手
async def delete_chat(chat_id: str) -> None:
    async with httpx.AsyncClient() as client:
        resp = await client.delete(f"{RAG_API}/chats/{chat_id}", headers=HEADERS)
        _check_resp(resp, "删除聊天助手")

#创建会话
async def create_session(chat_name: str, name: str, user_id: str) -> Dict:
    payload = {"chat_name": chat_name, "name": name, "user_id": user_id}
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{RAG_API}/sessions", headers=HEADERS, json=payload)
        data = _check_resp(resp, "创建会话")
        return data

"""
#为指定chatId生成问答
def get_openai_client(chat_id: str) -> OpenAI:

    return OpenAI(
        api_key=API_KEY,
        base_url=f"{RAG_API}/chats_openai/{chat_id}",
    )

#通用问答
def ask_assistant(chat_id: str, question: str, history: Optional[List[Dict]] = None, stream=False) -> str:
    if history is None:
        history = []
    messages = history + [{"role": "user", "content": question}]

    client = get_openai_client(chat_id)

    try:
        response = client.chat.completions.create(
            model="model",
            messages=messages,
            stream=True
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"对话失败：{str(e)}"
"""

#将文件上传并解析到指定数据集
def upload_and_parse_to_ragflow(dataset_name: str, file_path: str, original_filename: str = None):
    """
    上传文件到RagFlow并解析
    
    Args:
        dataset_name: 数据集名称
        file_path: 本地文件路径
        original_filename: 原始文件名（可选，如果不提供则使用文件路径的basename）
    """
    dataset_id = get_dataset_id_by_name(dataset_name)

    # 如果没有提供原始文件名，使用文件路径的basename
    if original_filename is None:
        original_filename = os.path.basename(file_path)

    with open(file_path, "rb") as f:
        # 使用原始文件名，而不是文件路径
        files = {"file": (original_filename, f, "application/octet-stream")}
        upload_resp = requests.post(
            f"{RAG_API}/datasets/{dataset_id}/documents",
            headers=HEADERS,
            files=files
        )
    upload_data = upload_resp.json()
    if upload_resp.status_code != 200 or upload_data.get("code") != 0:
        raise Exception("上传文档失败")

    doc_id = upload_data["data"]["ids"][0]

    parse_resp = requests.post(
        f"{RAG_API}/datasets/{dataset_id}/chunks",
        headers={**HEADERS, "Content-Type": "application/json"},
        json={"document_ids": [doc_id]}
    )
    parse_data = parse_resp.json()
    if parse_resp.status_code != 200 or parse_data.get("code") != 0:
        raise Exception("文档解析失败")

    return {"dataset_id": dataset_id, "document_id": doc_id}


def get_dataset_id_by_name(name: str) -> str:
    resp = requests.get(f"{RAG_API}/datasets", headers=HEADERS)
    data = resp.json()
    if resp.status_code != 200 or data.get("code") != 0:
        raise Exception("获取数据集失败")

    for ds in data["data"]:
        if ds["name"] == name:
            return ds["id"]

    raise Exception(f"未找到数据集：{name}")
"""
#教师ai助手
def ask_teacher_chat(course_chat_id: str,question: str,history: Optional[List[Dict]] = None,stream: bool = False) -> str:

    return ask_assistant(
        chat_id=course_chat_id,
        question=question,
        history=history,
        stream=stream,
    )

#作业ai助手，只有老师专用
def ask_assignment_assistant(chat_id: str, question: str, history: Optional[List[Dict]] = None) -> str:
    return ask_assistant(
        chat_id=chat_id,
        question=question,
        history=history or [],
        stream=False
    )
"""

#异步接口
#创建数据集，若已存在直接返回已有ID
async def create_dataset(name: str) -> dict:
    """
    创建数据集，返回标准化的响应格式
    
    Args:
        name (str): 数据集名称
        
    Returns:
        dict: 标准化的响应格式
        {
            "code": 0,
            "message": "创建数据集成功",
            "data": {
                "dataset_id": "xxx",
                "name": "xxx",
                "description": "xxx",
                "document_count": 0,
                "create_date": "xxx",
                "update_date": "xxx"
            }
        }
    """
    try:
        # 先检查数据集是否已存在
        try:
            existing_id = get_dataset_id_by_name(name)
            # 如果存在，返回已有数据集信息
            return {
                "code": 0,
                "message": "数据集已存在",
                "data": {
                    "dataset_id": existing_id,
                    "name": name,
                    "description": None,
                    "document_count": 0,
                    "create_date": None,
                    "update_date": None
                }
            }
        except Exception:
            # 数据集不存在，创建新的
            pass

        # 创建新数据集
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{RAG_API}/datasets", 
                headers=HEADERS,
                json={"name": name}
            )
            
            if resp.status_code == 200:
                result = resp.json()
                if result.get("code") == 0:
                    raw_data = result["data"]
                    return {
                        "code": 0,
                        "message": "创建数据集成功",
                        "data": {
                            "dataset_id": raw_data.get("id"),
                            "name": raw_data.get("name"),
                            "description": raw_data.get("description"),
                            "document_count": raw_data.get("document_count", 0),
                            "create_date": raw_data.get("create_date"),
                            "update_date": raw_data.get("update_date"),
                        }
                    }
                else:
                    return {
                        "code": 1,
                        "message": f"API返回错误: {result.get('message', '未知错误')}",
                        "data": None
                    }
            else:
                return {
                    "code": 1,
                    "message": f"HTTP请求失败，状态码: {resp.status_code}",
                    "data": None
                }
                
    except Exception as e:
        return {
            "code": 1,
            "message": f"创建数据集失败: {str(e)}",
            "data": None
        }


#根据数据集名字删除数据库
async def delete_dataset(name: str):
    """
    删除数据集，返回标准化的响应格式
    Args:
        name (str): 数据集名称
    Returns:
        dict: 标准化的响应格式
        {
            "code": 0,
            "message": "删除数据集成功"
        }
    """
    try:
        ds_id = get_dataset_id_by_name(name)
    except Exception as e:
        return {
            "code": 1,
            "message": f"获取数据集ID失败: {str(e)}"
        }

    try:
        async with httpx.AsyncClient() as client:
            # 使用正确的删除API格式
            resp = await client.delete(
                f"{RAG_API}/datasets", 
                headers=HEADERS,
                data=json.dumps({"ids": [ds_id]})  # 使用data参数并手动序列化JSON
            )
            print(f"删除请求状态码: {resp.status_code}")
            
            if resp.status_code == 200:
                result = resp.json()
                if result.get("code") == 0:
                    return {
                        "code": 0,
                        "message": "删除数据集成功"
                    }
                else:
                    return {
                        "code": 1,
                        "message": f"API返回错误: {result.get('message', '未知错误')}"
                    }
            else:
                return {
                    "code": 1,
                    "message": f"HTTP请求失败，状态码: {resp.status_code}"
                }

    except Exception as e:
        return {
            "code": 1,
            "message": f"删除数据集失败: {str(e)}"
        }

#更新数据库
async def update_dataset_by_name(name: str, new_name: str, description: str):
    """
    更新数据集，返回标准化的响应格式
    
    Args:
        name (str): 原数据集名称
        new_name (str): 新的数据集名称
        description (str): 新的数据集描述
        
    Returns:
        dict: 标准化的响应格式
        {
            "code": 0,
            "message": "更新数据集成功"
        }
    """
    try:
        ds_id = get_dataset_id_by_name(name)
    except Exception as e:
        return {
            "code": 1,
            "message": f"获取数据集ID失败: {str(e)}"
        }
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.put(
                f"{RAG_API}/datasets/{ds_id}",
                headers=HEADERS,
                json={"name": new_name, "description": description}
            )
            
            if resp.status_code == 200:
                result = resp.json()
                if result.get("code") == 0:
                    return {
                        "code": 0,
                        "message": "更新数据集成功"
                    }

    except Exception as e:
        return {
            "code": 1,
            "message": f"更新数据集失败: {str(e)}"
        }

#列出数据集
#这个没太搞懂 是查询语句，查询课程吗？跟rag部分好像没关系就没改了
async def list_datasets(name: Optional[str] = None):
    params = {"name": name} if name else {}
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{RAG_API}/datasets", headers=HEADERS, params=params)
        resp.raise_for_status()
        result = resp.json()
        if result["code"] != 0:
            raise RuntimeError(result["message"])
        return result["data"]["datasets"]

#简答题自动评分
async def score_subjective(
    reference: str,
    student_answer: str,
    current_user: User
) -> tuple[int, str]:
    prompt = (
        "你是阅卷老师，请参考标准答案给学生答案打分，并用指出改进点。注意你的评价需要关系到具体知识点只返回 json，如："
        f"【标准答案】\n{reference}\n\n【学生答案】\n{student_answer}"
    )
    session_id = "6c2d3e745e5911f08afa1a7dbaf3bdd9"
    try:
        response = chat_with_assistant_once(
            chat_name="自动评分助手",
            question=prompt,
            session_id=session_id
        )
        
        answer = response.get("data", {}).get("answer", "")
        
        # 提取JSON字符串（去掉markdown代码块标记）
        json_str = answer.replace("```json", "").replace("```", "").strip()
        result = json.loads(json_str)
        
        # 从JSON中提取分数和评语
        score = int(result.get("score", 0))
        feedback = result.get("comment", "未提供评语")
        
        print(f"分数：{score}")
        print(f"点评：{feedback}")
        
        return score, feedback
    except Exception as e:
        print(f"解析评分结果失败: {str(e)}")
        print(f"原始响应: {response if 'response' in locals() else 'No response'}")
        # 如果解析失败，返回默认值
        return 0, f"评分解析失败: {str(e)}"

    
    


