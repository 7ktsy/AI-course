from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import requests
import base64
from datetime import datetime
import json
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

router = APIRouter()

# 直接硬编码API密钥和基础URL
RUNWAYML_API_KEY = "key_20537ad741a6fb579fafa8127cfff7fab3831d32c4c1c5359ae4704e9ec29c544f97f24b4d455de131db16a407bfd551a903e5058d3f2f859119d102affa17e5"
RUNWAYML_BASE_URL = "https://api.dev.runwayml.com/v1"

# 创建带有重试机制的session
def create_session():
    session = requests.Session()
    
    # 配置重试策略
    retry_strategy = Retry(
        total=3,  # 总重试次数
        backoff_factor=1,  # 重试间隔
        status_forcelist=[429, 500, 502, 503, 504],  # 需要重试的HTTP状态码
    )
    
    # 配置适配器
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # 设置超时
    session.timeout = (10, 30)  # (连接超时, 读取超时)
    
    return session

# 请求模型 - 简化的版本
class SimpleTextToImageRequest(BaseModel):
    promptText: str
    ratio: str = "1920:1080"
    model: str = "gen4_image"
    seed: Optional[int] = None

# 响应模型
class SimpleTextToImageResponse(BaseModel):
    success: bool
    image_url: Optional[str] = None
    image_base64: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    task_id: Optional[str] = None

@router.post("/generate-image", response_model=SimpleTextToImageResponse)
async def generate_image_from_text(request: SimpleTextToImageRequest):
    """
    根据文字描述生成图片 - 简化版本，不需要参考图片
    """
    print(f"🚀 开始处理图片生成请求: {request.promptText[:50]}...")
    session = create_session()
    
    try:
        # 准备请求数据
        payload = {
            "promptText": request.promptText,
            "ratio": request.ratio,
            "model": request.model
        }
        
        # 添加可选的种子参数
        if request.seed is not None:
            payload["seed"] = request.seed
        
        # 设置请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {RUNWAYML_API_KEY}",
            "X-Runway-Version": "2024-11-06"
        }
        
        print(f"📤 发送请求到RunwayML API: {payload}")
        
        # 发送请求到RunwayML API，使用session
        try:
            response = session.post(
                f"{RUNWAYML_BASE_URL}/text_to_image",
                json=payload,
                headers=headers,
                timeout=(10, 30)  # 连接超时10秒，读取超时30秒
            )
        except requests.exceptions.SSLError as ssl_error:
            print(f"❌ SSL错误: {ssl_error}")
            return SimpleTextToImageResponse(
                success=False,
                error_message=f"SSL连接错误，请检查网络连接或稍后重试: {str(ssl_error)}",
                created_at=datetime.now()
            )
        except requests.exceptions.ConnectionError as conn_error:
            print(f"❌ 连接错误: {conn_error}")
            return SimpleTextToImageResponse(
                success=False,
                error_message=f"网络连接错误，请检查网络连接: {str(conn_error)}",
                created_at=datetime.now()
            )
        except requests.exceptions.Timeout as timeout_error:
            print(f"❌ 超时错误: {timeout_error}")
            return SimpleTextToImageResponse(
                success=False,
                error_message=f"请求超时，请稍后重试: {str(timeout_error)}",
                created_at=datetime.now()
            )
        except requests.exceptions.RequestException as req_error:
            print(f"❌ 请求错误: {req_error}")
            return SimpleTextToImageResponse(
                success=False,
                error_message=f"请求失败: {str(req_error)}",
                created_at=datetime.now()
            )
        
        print(f"📥 RunwayML API响应状态码: {response.status_code}")
        print(f"📥 RunwayML API响应内容: {response.text}")
        
        if response.status_code == 200:
            # 获取任务ID
            task_data = response.json()
            task_id = task_data.get("id")
            
            if task_id:
                print(f"🆔 任务ID: {task_id}")
                
                # 轮询任务状态直到完成
                max_attempts = 60  # 最多等待5分钟
                attempt = 0
                
                while attempt < max_attempts:
                    try:
                        status_response = session.get(
                            f"{RUNWAYML_BASE_URL}/tasks/{task_id}",
                            headers=headers,
                            timeout=(10, 30)
                        )
                        
                        if status_response.status_code == 200:
                            task_status = status_response.json()
                            status = task_status.get("status")
                            
                            print(f"🔄 任务状态: {status}")
                            
                            if status == "SUCCEEDED" or status == "completed":
                                # 任务完成，获取结果
                                output = task_status.get("output", [])
                                if output and len(output) > 0:
                                    image_url = output[0]
                                    
                                    # 尝试获取base64图像数据
                                    try:
                                        image_response = session.get(image_url, timeout=(10, 30))
                                        if image_response.status_code == 200:
                                            image_base64 = base64.b64encode(image_response.content).decode('utf-8')
                                        else:
                                            image_base64 = None
                                    except Exception as e:
                                        print(f"获取图像数据失败: {e}")
                                        image_base64 = None
                                    
                                    print(f"✅ 图片生成成功，URL: {image_url}")
                                    result = SimpleTextToImageResponse(
                                        success=True,
                                        image_url=image_url,
                                        image_base64=image_base64,
                                        created_at=datetime.now(),
                                        task_id=task_id
                                    )
                                    print(f"📤 返回结果: {result}")
                                    return result
                                else:
                                    print("❌ 任务完成但没有输出图像")
                                    return SimpleTextToImageResponse(
                                        success=False,
                                        error_message="任务完成但没有输出图像",
                                        created_at=datetime.now(),
                                        task_id=task_id
                                    )
                                    
                            elif status == "failed" or status == "FAILED":
                                error_details = task_status.get("error", {})
                                error_message = error_details.get("message", "任务失败")
                                print(f"❌ 任务失败: {error_message}")
                                return SimpleTextToImageResponse(
                                    success=False,
                                    error_message=error_message,
                                    created_at=datetime.now(),
                                    task_id=task_id
                                )
                            
                            # 等待5秒后再次检查
                            import asyncio
                            await asyncio.sleep(5)
                            attempt += 1
                        else:
                            print(f"获取任务状态失败: {status_response.status_code}")
                            return SimpleTextToImageResponse(
                                success=False,
                                error_message=f"获取任务状态失败: {status_response.status_code}",
                                created_at=datetime.now(),
                                task_id=task_id
                            )
                    except requests.exceptions.RequestException as e:
                        print(f"轮询任务状态时出错: {e}")
                        # 继续重试，不要立即失败
                        await asyncio.sleep(5)
                        attempt += 1
                
                # 超时
                print("⏰ 任务超时")
                return SimpleTextToImageResponse(
                    success=False,
                    error_message="任务超时",
                    created_at=datetime.now(),
                    task_id=task_id
                )
            else:
                print("❌ 未获取到任务ID")
                return SimpleTextToImageResponse(
                    success=False,
                    error_message="未获取到任务ID",
                    created_at=datetime.now()
                )
        else:
            error_message = f"API请求失败: {response.status_code}"
            try:
                error_data = response.json()
                error_message += f" - {error_data.get('error', {}).get('message', '')}"
            except:
                error_message += f" - {response.text}"
            
            print(f"❌ {error_message}")
            return SimpleTextToImageResponse(
                success=False,
                error_message=error_message,
                created_at=datetime.now()
            )
            
    except Exception as e:
        print(f"❌ 生成图像时发生错误: {e}")
        return SimpleTextToImageResponse(
            success=False,
            error_message=f"服务器内部错误: {str(e)}",
            created_at=datetime.now()
        )
    finally:
        session.close()
        print("🏁 图片生成请求处理完成")

@router.get("/health")
async def health_check():
    """
    健康检查接口
    """
    return {
        "status": "healthy",
        "service": "simple-image-generator",
        "timestamp": datetime.now().isoformat()
    } 