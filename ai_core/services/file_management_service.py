import os

from typing import Optional, Dict, Any, List, Union
from ai_core.services.dataset_management_service import get_dataset_id_by_name
import requests
API_KEY = "ragflow-FlNDljYzU0M2UxMTExZjA5NGUxMGU0NW"
BASE_URL = "http://localhost:8080"


def upload_documents_to_dataset(dataset_name: str, file_paths: Union[str, List[str]]) -> Dict:
    """
    上传一个或多个文档到指定的数据集
    Args:
        dataset_id (str): 目标数据集的ID
        file_paths (Union[str, List[str]]): 要上传的文件路径，可以是单个字符串或字符串列表
    Returns:
        Dict: API响应数据
    Raises:
        Exception: 如果上传失败则抛出异常
    """
    try:
        # 列表上传
        if isinstance(file_paths, str):
            file_paths = [file_paths]
            
        # 准备文件
        files = []
        for file_path in file_paths:
            if not os.path.exists(file_path):
                raise Exception(f"文件不存在: {file_path}")
            files.append(('file', open(file_path, 'rb')))
        
        dataset_id = get_dataset_id_by_name(dataset_name)
        # 发送请求
        response = requests.post(
            f"{BASE_URL}/api/v1/datasets/{dataset_id}/documents",
            headers={
                'Authorization': f'Bearer {API_KEY}'
            },
            files=files
        )
        
        # 关闭所有打开的文件
        for _, file_obj in files:
            file_obj.close()
            
        # 检查响应
        if response.status_code == 200:
            result = response.json()
            raw_data = result["data"]
            formatted_result = [{
                "dataset_id": file.get("dataset_id"),
                "id": file.get("id"),
                "name": file.get("name"),
                "type": file.get("type"),
                "size": file.get("size"),
                "run": file.get("run") #状态 不太清楚有什么用
            } for file in raw_data]
            return {
                "code": 0,
                "message": "上传文档成功",
                "data": formatted_result
            }
        else:
            error_msg = response.json().get('detail', '未知错误') if response.content else '未知错误'
            raise Exception(f"上传文档失败: {error_msg}")
            
    except Exception as e:
        raise Exception(f"上传文档失败: {str(e)}")


def download_document_from_dataset(dataset_name: str, document_id: str, output_path: str) -> str:
    """
    从指定的数据集下载文档
    Args:
        dataset_name (str): 数据集名称
        document_id (str): 文档ID
        output_path (str): 输出文件路径
    Returns:
        str: 下载文件的路径
    Raises:
        Exception: 如果下载失败则抛出异常
    """
    try:
        dataset_id = get_dataset_id_by_name(dataset_name)
        
        # 发送下载请求
        response = requests.get(
            f"{BASE_URL}/api/v1/datasets/{dataset_id}/documents/{document_id}",
            headers={
                'Authorization': f'Bearer {API_KEY}'
            },
            stream=True  # 使用流式下载
        )
        
        # 检查响应
        if response.status_code == 200:
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 写入文件
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return {
                "code": 0,
                "message": "下载文档成功",
                "data": output_path
            }
        else:
            # 如果是错误响应，尝试解析错误信息
            try:
                error_data = response.json()
                error_msg = error_data.get('message', '未知错误')
            except:
                error_msg = f"下载失败，状态码: {response.status_code}"
            raise Exception(f"下载文档失败: {error_msg}")
            
    except Exception as e:
        raise Exception(f"下载文档失败: {str(e)}")


def list_documents(
    dataset_name: str,
    page: int = 1,
    page_size: int = 30,
    orderby: str = "create_time",
    desc: bool = True,
    keywords: Optional[str] = None,
    document_id: Optional[str] = None,
    document_name: Optional[str] = None
) -> Dict:
    """
    列出指定数据集中的文档
    Args:
        dataset_name (str): 数据集名称
        page (int): 页码，默认为1
        page_size (int): 每页数量，默认为30
        orderby (str): 排序字段，可选 create_time 或 update_time
        desc (bool): 是否降序排序，默认为True
        keywords (Optional[str]): 搜索关键词
        document_id (Optional[str]): 文档ID
        document_name (Optional[str]): 文档名称
    Returns:
        Dict: API响应数据
    Raises:
        Exception: 如果获取失败则抛出异常
    """
    try:
        dataset_id = get_dataset_id_by_name(dataset_name)
        
        # 构建查询参数
        params = {
            'page': page,
            'page_size': page_size,
            'orderby': orderby,
            'desc': str(desc).lower()
        }
        
        # 添加可选参数
        if keywords:
            params['keywords'] = keywords
        if document_id:
            params['id'] = document_id
        if document_name:
            params['name'] = document_name
            
        # 发送请求
        response = requests.get(
            f"{BASE_URL}/api/v1/datasets/{dataset_id}/documents",
            headers={
                'Authorization': f'Bearer {API_KEY}',
                'Content-Type': 'application/json'
            },
            params=params
        )
        # 检查响应
        if response.status_code == 200:
            result = response.json()
            raw_data = result["data"]["docs"]
            formatted_result = [{
                "dataset_id": file.get("dataset_id"),
                "id": file.get("id"),
                "name": file.get("name"),
                "type": file.get("type"),
                "size": file.get("size"),
                "run": file.get("run") #状态
            } for file in raw_data]
            return {
                "code": 0,
                "message": "获取文档列表成功",
                "data": {
                    "docs": formatted_result,
                    "total": result["data"]["total"] #总文档的数量，用于前端分页
                }
            }
        
        else:
            error_msg = response.json().get('message', '未知错误') if response.content else '未知错误'
            raise Exception(f"获取文档列表失败: {error_msg}")
            
    except Exception as e:
        raise Exception(f"获取文档列表失败: {str(e)}")
    
# 根据文档名称获取文档ID
def get_document_id_by_name(dataset_name: str, document_name: str) -> str:
    """
    根据文档名称获取文档ID
    Args:
        dataset_name (str): 数据集名称
        document_name (str): 文档名称
    Returns:
        str: 文档ID
    """
    try:
        dataset_id = get_dataset_id_by_name(dataset_name)
        response = requests.get(
            f"{BASE_URL}/api/v1/datasets/{dataset_id}/documents",
            headers={
                'Authorization': f'Bearer {API_KEY}'
            }
        )
        if response.status_code == 200:
            docs = response.json().get('data', {}).get('docs', [])
            for doc in docs:
                if doc['name'] == document_name:
                    return doc['id']
        raise Exception(f"未找到名称为 '{document_name}' 的文档")
    except Exception as e:
        raise Exception(f"获取文档ID失败: {str(e)}")
    
def delete_documents(dataset_name: str, document_ids: List[str]) -> Dict:
    """
    从指定的数据集删除文档
    Args:
        dataset_name (str): 数据集名称
        document_ids (List[str]): 要删除的文档ID列表
    Returns:
        Dict: API响应数据
    Raises:
        Exception: 如果删除失败则抛出异常
    """
    try:
        # 获取数据集ID
        dataset_id = get_dataset_id_by_name(dataset_name)
        
        # 准备请求头和数据
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {API_KEY}'
        }
        data = {
            "ids": document_ids
        }
        
        # 发送删除请求
        response = requests.delete(
            f"{BASE_URL}/api/v1/datasets/{dataset_id}/documents",
            headers=headers,
            json=data
        )
        # 检查响应
        if response.status_code == 200:
            return {
                "code": 0,
                "message": "删除文档成功",
            }
        else:
            error_msg = response.json().get('message', '未知错误') if response.content else '未知错误'
            print(f"删除失败: {error_msg}")
            raise Exception(f"删除文档失败: {error_msg}")
            
    except Exception as e:
        print(f"删除过程中发生错误: {str(e)}")
        raise Exception(f"删除文档失败: {str(e)}")


#有点奇怪，不知道获取的是对的还是错的
#应该用不上
def get_document_info(document_name: str) -> Dict:
    """
    获取文档的详细信息，包括所属数据集
    Args:
        document_name (str): 文档名称
    Returns:
        Dict: 文档信息，包含数据集ID等
    Raises:
        Exception: 如果获取失败则抛出异常
    """
    try:
        # 获取所有数据集
        response = requests.get(
            f"{BASE_URL}/api/v1/datasets",
            headers={
                'Authorization': f'Bearer {API_KEY}'
            }
        )
        
        if response.status_code != 200:
            raise Exception("获取数据集列表失败")
            
        datasets = response.json().get('data', [])
        
        # 遍历每个数据集查找文档
        for dataset in datasets:
            dataset_id = dataset['id']
            # 获取数据集中的文档
            docs_response = requests.get(
                f"{BASE_URL}/api/v1/datasets/{dataset_id}/documents",
                headers={
                    'Authorization': f'Bearer {API_KEY}'
                }
            )
            
            if docs_response.status_code == 200:
                docs = docs_response.json().get('data', {}).get('docs', [])
                # 查找指定ID的文档
                for doc in docs:
                    if doc['name'] == document_name:
                        # 找到文档，返回完整信息
                        return {
                            'document': doc,
                            'dataset': dataset
                        }
                        
        raise Exception(f"未找到名称为 {document_name} 的文档")
        
    except Exception as e:
        raise Exception(f"获取文档信息失败: {str(e)}")
    

def parse_documents(dataset_name: str, document_ids: List[str]) -> Dict:
    """
    解析指定数据集中的文档
    Args:
        dataset_name (str): 数据集名称
        document_ids (List[str]): 要解析的文档ID列表
    Returns:
        Dict: API响应数据
    Raises:
        Exception: 如果解析失败则抛出异常
    """
    try:
        # 获取数据集ID
        dataset_id = get_dataset_id_by_name(dataset_name)
        
        # 准备请求头和数据
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {API_KEY}'
        }
        data = {
            "document_ids": document_ids
        }
        
        # 发送解析请求
        response = requests.post(
            f"{BASE_URL}/api/v1/datasets/{dataset_id}/chunks",
            headers=headers,
            json=data
        )
        
        # 检查响应
        if response.status_code == 200:
            return {
                "code": 0,
                "message": "发送解析请求成功",
            }
        else:
            error_msg = response.json().get('message', '未知错误') if response.content else '未知错误'
            raise Exception(f"解析文档失败: {error_msg}")
            
    except Exception as e:
        raise Exception(f"解析文档失败: {str(e)}")


def stop_parsing_documents(dataset_name: str, document_ids: List[str]) -> Dict:
    """
    停止解析指定的文档
    Args:
        dataset_name (str): 数据集名称
        document_ids (List[str]): 要停止解析的文档ID列表
    Returns:
        Dict: API响应数据
    Raises:
        Exception: 如果停止解析失败则抛出异常
    """
    try:
        # 获取数据集ID
        dataset_id = get_dataset_id_by_name(dataset_name)
        
        # 准备请求头和数据
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {API_KEY}'
        }
        data = {
            "document_ids": document_ids
        }
        
        # 发送停止解析请求
        response = requests.delete(
            f"{BASE_URL}/api/v1/datasets/{dataset_id}/chunks",
            headers=headers,
            json=data
        )
        
        # 检查响应
        if response.status_code == 200:
            return {
                "code": 0,
                "message": "停止解析文档成功",
            }
        else:
            error_msg = response.json().get('message', '未知错误') if response.content else '未知错误'
            raise Exception(f"停止解析文档失败: {error_msg}")
            
    except Exception as e:
        raise Exception(f"停止解析文档失败: {str(e)}")

