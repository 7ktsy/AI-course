from typing import Optional, Dict, Any, List
import requests
import json
API_KEY = "ragflow-FlNDljYzU0M2UxMTExZjA5NGUxMGU0NW"
BASE_URL = "http://localhost:8080"

def create_dataset(dataset_name: str) -> Dict[str, Any]:
    """
    创建数据集
    Args:
        dataset_name (str): 数据集名称
    Returns:
        Dict[str, Any]: 创建的数据集信息
    Raises:
        Exception: 当API调用失败时抛出异常
    """
    try:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {API_KEY}'
        }
        
        data = {
            "name": dataset_name
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/datasets",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 0:
                raw_data=result["data"]
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
                raise Exception(f"API返回错误: {result.get('message', '未知错误')}")
        else:
            raise Exception(f"HTTP请求失败，状态码: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"网络请求错误: {str(e)}")
    except json.JSONDecodeError as e:
        raise Exception(f"JSON解析错误: {str(e)}")
    except Exception as e:
        raise Exception(f"创建数据集失败: {str(e)}")

def get_dataset_id_by_name(dataset_name: str) -> str:
    """
    通过数据集名称获取数据集ID
    
    Args:
        dataset_name (str): 数据集名称
        
    Returns:
        str: 数据集ID
        
    Raises:
        Exception: 当找不到数据集或API调用失败时抛出异常
    """
    try:
        headers = {
            'Authorization': f'Bearer {API_KEY}'
        }
        
        # 获取所有数据集列表
        response = requests.get(
            f"{BASE_URL}/api/v1/datasets",
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 0:
                datasets = result.get("data", [])
                # 查找匹配名称的数据集
                for dataset in datasets:
                    if dataset.get("name") == dataset_name:
                        return dataset.get("id")
                raise Exception(f"未找到名称为 '{dataset_name}' 的数据集")
            else:
                raise Exception(f"API返回错误: {result.get('message', '未知错误')}")
        else:
            raise Exception(f"HTTP请求失败，状态码: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"网络请求错误: {str(e)}")
    except json.JSONDecodeError as e:
        raise Exception(f"JSON解析错误: {str(e)}")
    except Exception as e:
        raise Exception(f"获取数据集ID失败: {str(e)}")

def delete_datasets(dataset_ids: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    删除指定ID的数据集
    Args:
        dataset_ids (Optional[List[str]]): 要删除的数据集ID列表，如果为None则删除所有数据集
    Raises:
        Exception: 当API调用失败时抛出异常
    """
    try:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {API_KEY}'
        }
        data = {
            "ids": dataset_ids
        }
        response = requests.delete(
            f"{BASE_URL}/api/v1/datasets",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("code") != 0:
                raise Exception(f"API返回错误: {result.get('message', '未知错误')}")
        else:
            raise Exception(f"HTTP请求失败，状态码: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"网络请求错误: {str(e)}")
    except json.JSONDecodeError as e:
        raise Exception(f"JSON解析错误: {str(e)}")
    except Exception as e:
        raise Exception(f"删除数据集失败: {str(e)}")



def delete_dataset_by_name(dataset_name: str) -> None:
    """
    通过数据集名称删除数据集
    Args:
        dataset_name (str): 要删除的数据集名称
    Raises:
        Exception: 当找不到数据集或API调用失败时抛出异常
    """
    try:
        # 先获取数据集ID
        dataset_id = get_dataset_id_by_name(dataset_name)
        # 删除数据集
        delete_datasets([dataset_id])
        return {
            "code": 0,
            "message": "删除数据集成功"
        }
    except Exception as e:
        raise Exception(f"通过名称删除数据集失败: {str(e)}")
    

def update_dataset(
    dataset_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    permission: Optional[str] = None,
    chunk_method: Optional[str] = None,
    pagerank: Optional[int] = None,
    parser_config: Optional[Dict] = None,
    embedding_model: Optional[str] = None,
    avatar: Optional[str] = None
) -> None:
    """
    更新数据集配置
    
    Args:
        dataset_id (str): 要更新的数据集ID
        name (Optional[str]): 新的数据集名称
        description (Optional[str]): 新的数据集描述
        permission (Optional[str]): 权限设置 ('me' 或 'team')
        chunk_method (Optional[str]): 分块方法
        pagerank (Optional[int]): 页面排名 (0-100)
        parser_config (Optional[Dict]): 解析器配置
        embedding_model (Optional[str]): 嵌入模型名称
        avatar (Optional[str]): Base64编码的头像
        
    Raises:
        Exception: 当API调用失败时抛出异常
    """
    try:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {API_KEY}'
        }
        
        # 构建更新数据，只包含非None的值
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description
        if permission is not None:
            update_data["permission"] = permission
        if chunk_method is not None:
            update_data["chunk_method"] = chunk_method
        if pagerank is not None:
            update_data["pagerank"] = pagerank
        if parser_config is not None:
            update_data["parser_config"] = parser_config
        if embedding_model is not None:
            update_data["embedding_model"] = embedding_model
        if avatar is not None:
            update_data["avatar"] = avatar
            
        response = requests.put(
            f"{BASE_URL}/api/v1/datasets/{dataset_id}",
            headers=headers,
            json=update_data
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("code") != 0:
                raise Exception(f"API返回错误: {result.get('message', '未知错误')}")
        else:
            raise Exception(f"HTTP请求失败，状态码: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"网络请求错误: {str(e)}")
    except json.JSONDecodeError as e:
        raise Exception(f"JSON解析错误: {str(e)}")
    except Exception as e:
        raise Exception(f"更新数据集失败: {str(e)}")

def list_datasets(
    page: int = 1,
    page_size: int = 30,
    orderby: str = "create_time",
    desc: bool = True,
    name: Optional[str] = None,
    dataset_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    列出数据集
    
    Args:
        page (int): 页码，默认为1
        page_size (int): 每页数量，默认为30
        orderby (str): 排序字段，可选 'create_time' 或 'update_time'
        desc (bool): 是否降序排序，默认为True
        name (Optional[str]): 按名称筛选
        dataset_id (Optional[str]): 按ID筛选
        
    Returns:
        List[Dict[str, Any]]: 数据集列表
        
    Raises:
        Exception: 当API调用失败时抛出异常
    """
    try:
        headers = {
            'Authorization': f'Bearer {API_KEY}'
        }
        
        # 构建查询参数
        params = {
            'page': page,
            'page_size': page_size,
            'orderby': orderby,
            'desc': str(desc).lower()
        }
        if name:
            params['name'] = name
        if dataset_id:
            params['id'] = dataset_id
            
        response = requests.get(
            f"{BASE_URL}/api/v1/datasets",
            headers=headers,
            params=params
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 0:
                raw_data = result["data"]
                # 处理每个数据集，只保留需要的字段
                formatted_datasets = [{
                    "dataset_id": dataset.get("id"),
                    "name": dataset.get("name"),
                    "description": dataset.get("description"),
                    "document_count": dataset.get("document_count", 0),
                    "create_date": dataset.get("create_date"),
                    "update_date": dataset.get("update_date"),
                } for dataset in raw_data]

                return {
                    "code": 0,
                    "message": "获取数据集列表成功",
                    "data": {
                        "datasets": formatted_datasets
                    }
                }
            else:
                raise Exception(f"API返回错误: {result.get('message', '未知错误')}")
        else:
            raise Exception(f"HTTP请求失败，状态码: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"网络请求错误: {str(e)}")
    except json.JSONDecodeError as e:
        raise Exception(f"JSON解析错误: {str(e)}")
    except Exception as e:
        raise Exception(f"获取数据集列表失败: {str(e)}")


def update_dataset_by_name(
    dataset_name: str,
    new_name: Optional[str] = None,
    **kwargs
) -> None:
    """
    通过数据集名称更新数据集
    Args:
        dataset_name (str): 要更新的数据集名称
        new_name (Optional[str]): 新的数据集名称
        **kwargs: 其他要更新的参数
    Raises:
        Exception: 当找不到数据集或API调用失败时抛出异常
    """
    try:
        # 先获取数据集ID
        dataset_id = get_dataset_id_by_name(dataset_name)
        # 更新数据集
        if new_name is not None:
            kwargs['name'] = new_name
        update_dataset(dataset_id, **kwargs)
        return {
            "code": 0,
            "message": "更新数据集成功"
        }
    except Exception as e:
        raise Exception(f"通过名称更新数据集失败: {str(e)}")
    

