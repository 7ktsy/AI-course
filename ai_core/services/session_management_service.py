from typing import Optional, Dict, Any, List, Union, Generator
import time
import requests
import json
import re
import os
from ..utils.download import markdown_to_pdf, save_as_markdown
from .chats_management_service import get_chat_id_by_name
API_KEY = "ragflow-FlNDljYzU0M2UxMTExZjA5NGUxMGU0NW"
BASE_URL = "http://localhost:8080"

def create_session(
    chat_name: str,
    name: Optional[str] = "新的会话",
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    创建一个与聊天助手的会话
    Args:
        chat_name (str): 聊天助手的名称
        name (str): 会话的名称
        user_id (Optional[str]): 用户的ID
    Returns:
        Dict[str, Any]: 包含会话信息的响应数据
    Raises:
        requests.exceptions.RequestException: 如果API请求失败
    """
    # 获取聊天助手的ID
    chat_id = get_chat_id_by_name(chat_name)
    # 构建请求URL:http://{address}/api/v1/chats/{chat_id}/sessions
    url = f"{BASE_URL}/api/v1/chats/{chat_id}/sessions"
    
    data = {
        "name": name
    }
    
    if user_id:
        data["user_id"] = user_id
        
    response = requests.post(
        url, 
        headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
        },
        json=data
    )
    # 检查响应
    if response.status_code == 200:
        result = response.json()
        raw_result = result.get('data')
        if result.get('code') == 0:
            return {
                "code": 0,
                "message": "创建新会话成功",
                "data": {
                    "chat_id": raw_result.get('chat_id'),
                    "create_date": raw_result.get('create_date'),
                    "update_date": raw_result.get('update_date'),
                    "session_id": raw_result.get('id'),
                    "name": raw_result.get('name'),
                    "messages": raw_result.get('messages'),
                }
            }
        else:
            error_msg = result.get('message', '未知错误')
            raise Exception(f"创建会话失败: {error_msg}")
        
# 更新会话 (其实也就是重命名...)
def update_session(
    chat_name: str,
    session_id: str,
    name: str,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    # 获取聊天助手的ID
    chat_id = get_chat_id_by_name(chat_name)

    # 构建请求URL:http://{address}/api/v1/chats/{chat_id}/sessions/{session_id}
    url = f"{BASE_URL}/api/v1/chats/{chat_id}/sessions/{session_id}"

    data = {
        "name": name
    }
    
    if user_id:
        data["user_id"] = user_id
        
    response = requests.put(
        url, 
        headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
        },
        json=data
    )
    # 检查响应
    if response.status_code == 200:
        result = response.json()
        if result.get('code') == 0:
            return {
                "code": 0,
                "message": "更新会话成功"
            }
        else:
            error_msg = result.get('message', '未知错误')
            raise Exception(f"更新会话失败: {error_msg}")


# 这个一直报错 其他都是可以的
# 列出与指定聊天助手关联的会话
def list_sessions(
    chat_name: str,
    page: int = 1,
    page_size: int = 30,
    orderby: str = "create_time",
    desc: bool = True,
    session_name: Optional[str] = None,
    session_id: Optional[str] = None,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    列出与指定聊天助手关联的会话
    Args:
        chat_name (str): 聊天助手的名称
        page (int): 页码，默认为1
        page_size (int): 每页显示的会话数，默认为30
        orderby (str): 排序字段，可选 'create_time' 或 'update_time'，默认为'create_time'
        desc (bool): 是否降序排序，默认为True
        session_name (Optional[str]): 按会话名称筛选
        session_id (Optional[str]): 按会话ID筛选
        user_id (Optional[str]): 按用户ID筛选
    Returns:
        Dict[str, Any]: 包含会话列表的响应数据
    """
    try:
        # 获取聊天助手的ID
        try:
            chat_id = get_chat_id_by_name(chat_name)
        except Exception as e:
            print(f"警告: 获取聊天助手ID失败: {str(e)}")
            return {
                "code": 0,
                "message": "获取聊天助手ID失败",
                "data": []
            }
        
        # 构建基础URL
        url = f"{BASE_URL}/api/v1/chats/{chat_id}/sessions"
        
        # 构建查询参数
        params = {
            "page": page,
            "page_size": page_size,
            "orderby": orderby,
            "desc": desc
        }
        
        # 添加可选的过滤参数
        if session_name:
            params["name"] = session_name
        if session_id:
            params["id"] = session_id
        if user_id:
            params["user_id"] = user_id
            
        # 发送请求
        response = requests.get(
            url,
            params=params,
            headers={
                "Authorization": f"Bearer {API_KEY}"
            }
        )
        
        # 检查响应
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 0:
                sessions_data = result.get('data', [])
                
                # 如果是空数据，返回空列表
                if not sessions_data:
                    return {
                        "code": 0,
                        "message": "没有找到任何会话",
                        "data": []
                    }
                
                # 如果是列表，直接返回
                if isinstance(sessions_data, list):
                    return {
                        "code": 0,
                        "message": "获取会话列表成功",
                        "data": sessions_data
                    }
                # 如果是单个会话对象，将其包装成列表
                else:
                    return {
                        "code": 0,
                        "message": "获取会话成功",
                        "data": [sessions_data]
                    }
            else:
                error_msg = result.get('message', '未知错误')
                print(f"警告: {error_msg}")
                return {
                    "code": 0,
                    "message": error_msg,
                    "data": []
                }
        else:
            print(f"警告: API请求失败: HTTP {response.status_code}")
            return {
                "code": 0,
                "message": f"API请求失败: HTTP {response.status_code}",
                "data": []
            }
            
    except Exception as e:
        print(f"警告: 获取会话列表时发生错误: {str(e)}")
        return {
            "code": 0,
            "message": f"获取会话列表时发生错误: {str(e)}",
            "data": []
        }


def delete_sessions(
    chat_name: str,
    session_ids: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    删除指定聊天助手的一个或多个会话
    Args:
        chat_name (str): 聊天助手的名称
        session_ids (Optional[List[str]]): 要删除的会话ID列表，如果为None则删除所有会话
    Returns:
        Dict[str, Any]: API响应数据
    """
    # 获取聊天助手的ID
    chat_id = get_chat_id_by_name(chat_name)
    
    # 构建请求URL
    url = f"{BASE_URL}/api/v1/chats/{chat_id}/sessions"
    
    # 构建请求数据
    data = {}
    if session_ids:
        data["ids"] = session_ids
        
    response = requests.delete(
        url,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        },
        json=data
    )
    
    # 检查响应
    if response.status_code == 200:
        result = response.json()
        if result.get('code') == 0:
            return {
                "code": 0,
                "message": "删除会话成功"
            }
        else:
            error_msg = result.get('message', '未知错误')
            raise Exception(f"删除会话失败: {error_msg}")
    else:
        raise Exception(f"API请求失败: HTTP {response.status_code}")

# 根据对话名称获得对话id    
def get_session_id_by_name(chat_name: str, session_name: str) -> str:
    """
    根据会话名称获取会话ID
    Args:
        chat_name (str): 聊天助手的名称
        session_name (str): 会话名称
    Returns:
        str: 会话ID
    Raises:
        Exception: 如果找不到指定名称的会话
    """
    try:
        # 调用list_sessions来查找指定名称的会话
        result = list_sessions(chat_name, session_name=session_name)
        sessions = result.get('data', [])
        
        # 查找匹配的会话
        for session in sessions:
            if session.get('name') == session_name:
                return session.get('id')
                
        # 如果找不到会话，创建一个新的
        print(f"\n未找到名称为 '{session_name}' 的会话，创建新会话")
        create_result = create_session(chat_name, name=session_name)
        if create_result.get('code') == 0:
            return create_result['data']['session_id']
        else:
            raise Exception(f"创建会话失败: {create_result.get('message', '未知错误')}")
            
    except Exception as e:
        raise Exception(f"获取或创建会话失败: {str(e)}")

def chat_with_assistant(
    chat_name: str,
    question: str,
    stream: bool = True,
    session_id: Optional[str] = None,
    user_id: Optional[str] = None
) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, Dict[str, Any]]]:
    """
    与聊天助手进行对话
    Args:
        chat_name (str): 聊天助手的名称
        question (str): 要问的问题
        stream (bool): 是否使用流式输出，默认为True
        session_id (Optional[str]): 会话ID，如果不提供则创建新会话
        user_id (Optional[str]): 用户自定义ID，仅在不提供session_id时有效
    Returns:
        Union[Dict[str, Any], Generator[Dict[str, Any], None, Dict[str, Any]]]: 
            - 如果stream=False，返回完整的响应数据
            - 如果stream=True，返回响应数据流
    Raises:
        Exception: 如果请求失败则抛出异常
    """
    try:
        # 获取聊天助手的ID
        chat_id = get_chat_id_by_name(chat_name)
        
        # 构建请求URL
        url = f"{BASE_URL}/api/v1/chats/{chat_id}/completions"
        
        # 构建请求数据
        data = {
            "question": question,
            "stream": stream
        }
        
        # 添加可选参数
        if session_id:
            data["session_id"] = session_id
        if user_id and not session_id:  # 仅在不提供session_id时添加user_id
            data["user_id"] = user_id
            
        # 发送请求
        response = requests.post(
            url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_KEY}"
            },
            json=data,
            stream=stream  # 根据stream参数决定是否使用流式传输
        )
        
        # 检查响应
        if response.status_code == 200:
            if stream:
                # 处理流式响应
                for line in response.iter_lines():
                    if line:
                        # 移除 "data:" 前缀
                        if line.startswith(b"data:"):
                            line = line[5:]
                        try:
                            result = json.loads(line)
                            if result.get('code') == 0:
                                # 如果是最后一条消息（data为true）
                                if isinstance(result.get('data'), bool):
                                    yield result  # 传递结束标记
                                    break
                                # 否则返回实际的响应数据
                                yield result
                            else:
                                error_msg = result.get('message', '未知错误')
                                raise Exception(f"聊天请求失败: {error_msg}")
                        except json.JSONDecodeError:
                            print(f"Warning: 无法解析响应: {line}")
            else:
                # 处理非流式响应
                print("非流式响应")
                print(response.json())
                result = response.json()
                if result.get('code') == 0:
                    return result
                else:
                    error_msg = result.get('message', '未知错误')
                    raise Exception(f"聊天请求失败: {error_msg}")
        else:
            error_msg = response.json().get('message', '未知错误') if response.content else '未知错误'
            raise Exception(f"API请求失败: HTTP {response.status_code} - {error_msg}")
            
    except Exception as e:
        raise Exception(f"聊天请求失败: {str(e)}")
    
def chat_with_assistant_once(
        chat_name: str, 
        question: str, 
        session_id: Optional[str] = None, 
        user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    与聊天助手进行一次对话
    """
    try:
        # 获取聊天助手的ID
        chat_id = get_chat_id_by_name(chat_name)
        
        # 构建请求URL
        url = f"{BASE_URL}/api/v1/chats/{chat_id}/completions"
        
        # 构建请求数据
        data = {
            "question": question,
            "stream": False
        }
        
        # 添加可选参数
        if session_id:
            data["session_id"] = session_id
        if user_id and not session_id:  # 仅在不提供session_id时添加user_id
            data["user_id"] = user_id
            
        # 发送请求
        response = requests.post(
            url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_KEY}"
            },
            json=data,
            stream=False  #非流式
        )
        
        # 检查响应
        print("[DEBUG] API status:", response.status_code)
        print("[DEBUG] API response:", response.text)
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 0:
                # 只返回 answer 内容
                data = result.get('data', {})
                if isinstance(data, dict) and 'answer' in data:
                    # 清理特殊标记，确保是干净的 Markdown 格式
                    answer = data['answer']
                    import re
                    # 清理 ##数字$$ 格式的特殊标记
                    answer = re.sub(r'##\d+\$\$', '', answer)
                    # 清理多余的空行
                    answer = re.sub(r'\n\s*\n\s*\n', '\n\n', answer)
                    # 清理行首行尾的空白字符
                    answer = answer.strip()
                    answer = answer.replace("：", ":")
                    
                    return {
                        "code": 0,
                        "message": "对话成功",
                        "data": {
                            "answer": answer
                        }
                    }
                else:
                    return result  # 如果没有 answer，返回原始响应
            else:
                error_msg = result.get('message', '未知错误')
                raise Exception(f"聊天请求失败: {error_msg}, 原始响应: {result}")
        else:
            raise Exception(f"API请求失败: HTTP {response.status_code}, 内容: {response.text}")
    except Exception as e:
        raise Exception(f"聊天请求失败: {str(e)}")

def handle_stream_response(generator: Generator[Dict[str, Any], None, Dict[str, Any]], max_retries: int = 3) -> List[Dict[str, Any]]:
    """
    处理流式响应的内容，支持重试
    Args:
        generator: 响应生成器
        max_retries: 最大重试次数
    Returns:
        List[Dict[str, Any]]: 所有响应数据的列表
    """
    retries = 0
    responses = []
    while retries < max_retries:
        try:
            print("Assistant: ", end="", flush=True)
            answer_so_far = ""
            for response in generator:
                if isinstance(response, dict):
                    responses.append(response)  # 保存每个响应
                    if 'data' in response:
                        data = response['data']
                        if isinstance(data, bool):
                            break
                        if data.get('answer'):
                            current_answer = data['answer']
                            new_content = current_answer[len(answer_so_far):]
                            if new_content:  # 只在有新内容时打印
                                print(new_content, end="", flush=True)
                                answer_so_far = current_answer
            print("\n")  # 回答结束后换行
            return responses  # 返回所有响应数据
        except Exception as e:
            retries += 1
            if retries >= max_retries:
                print(f"\n响应处理失败（已重试{retries}次）: {e}")
                return responses
            print(f"\n响应处理出错，正在重试（{retries}/{max_retries}）...")
            time.sleep(1)  # 等待1秒后重试

def chat_loop(chat_name: str, session_id: str, initial_prompt: str = None) -> List[Dict[str, Any]]:
    """
    主对话循环
    Args:
        chat_name: 聊天助手名称
        session_id: 会话ID
        initial_prompt: 初始提示信息（可选）
    Returns:
        List[Dict[str, Any]]: 所有响应数据的列表
    """
    responses = []  # 用于存储所有响应
    last_response = ""  # 用于存储助手的最后一次回答
    
    try:
        # 如果有初始提示信息，先发送给AI
        if initial_prompt:
            print("\n系统: 正在分析学习情况...\n")
            stream_response = chat_with_assistant(
                chat_name=chat_name,
                question=initial_prompt,
                session_id=session_id,
                stream=True
            )
            
            # 处理AI的回答
            initial_responses = handle_stream_response(stream_response)
            if initial_responses:
                responses.extend(initial_responses)
                
    except Exception as e:
        print(f"\n处理初始提示时出错: {e}")
    
    while True:
        try:
            # 获取用户输入
            user_input = input("\n你: ").strip()
            
            # 检查是否退出
            if user_input.lower() == 'exit':
                print("再见！")
                break

            # 检查是否需要下载文件
            if user_input == '下载文件':
                if not last_response:
                    print("没有可下载的内容。请先与助手进行对话。")
                    continue
                    
                try:
                    # 获取用户输入的文件名
                    file_name = input("请输入要保存的文件名（不需要输入后缀）: ").strip()
                    if not file_name:
                        print("文件名不能为空")
                        continue
                    
                    # 清理文件名中的非法字符
                    import re
                    # 替换Windows文件名中的非法字符
                    file_name = re.sub(r'[<>:"/\\|?*]', '_', file_name)
                    
                    # 选择下载格式
                    print("\n请选择下载格式：")
                    print("1. Markdown文件 (.md)")
                    print("2. PDF文件 (.pdf)")
                    format_choice = input("请输入选项编号 (1 或 2): ").strip()
                    
                    # 清理特殊标记
                    cleaned_response = last_response
                    cleaned_response = re.sub(r'##\d+\$\$', '', cleaned_response)
                    
                    if format_choice == "1":
                        output_path = save_as_markdown(cleaned_response, file_name)
                        print(f"Markdown文件已保存到: {output_path}")
                    elif format_choice == "2":
                        output_path = markdown_to_pdf(cleaned_response, file_name)
                        print(f"PDF文件已保存到: {output_path}")
                    else:
                        print("无效的选项，请重试")
                        
                except Exception as e:
                    print(f"保存文件时出错: {e}")
                continue

            # 检查是否为空输入
            if not user_input:
                continue
            
            # 发送问题并获取流式响应
            stream_response = chat_with_assistant(
                chat_name=chat_name,
                question=user_input,
                session_id=session_id,
                stream=True
            )
            
            # 处理AI的回答并收集响应
            chat_responses = handle_stream_response(stream_response)
            if chat_responses:
                responses.extend(chat_responses)
                # 更新最后的回答用于文件下载
                last_data = chat_responses[-1].get('data', {})
                if isinstance(last_data, dict) and last_data.get('answer'):
                    last_response = last_data['answer']
            
        except Exception as e:
            print(f"\n对话过程中出错: {e}")
            print("你可以继续输入问题，或输入 'exit' 退出。")
            continue
    
    return responses  # 返回所有收集到的响应数据