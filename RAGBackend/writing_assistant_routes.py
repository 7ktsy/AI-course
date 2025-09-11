from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List
import os
import base64
from datetime import datetime
import tempfile
import requests
from PIL import Image
import io
import json
import time

router = APIRouter()

# 配置RunwayML API密钥
RUNWAYML_API_KEY = "key_20537ad741a6fb579fafa8127cfff7fab3831d32c4c1c5359ae4704e9ec29c544f97f24b4d455de131db16a407bfd551a903e5058d3f2f859119d102affa17e5"
RUNWAYML_BASE_URL = "https://api.dev.runwayml.com/v1"

# 参考图像模型
class ReferenceImage(BaseModel):
    uri: str
    tag: Optional[str] = None

# 内容审核模型
class ContentModeration(BaseModel):
    publicFigureThreshold: Optional[str] = "auto"

# 请求模型
class TextToImageRequest(BaseModel):
    promptText: str
    ratio: str = "1920:1080"
    model: str = "gen4_image"
    seed: Optional[int] = None
    referenceImages: Optional[List[ReferenceImage]] = None
    contentModeration: Optional[ContentModeration] = None

# 响应模型
class TextToImageResponse(BaseModel):
    success: bool
    image_url: Optional[str] = None
    image_base64: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime

# 图片转视频请求模型
class ImageToVideoRequest(BaseModel):
    prompt_text: str
    image_url: str
    ratio: str = "1280:720"
    model: str = "gen4_turbo"
    duration: Optional[int] = 5

# 视频响应模型
class VideoResponse(BaseModel):
    success: bool
    video_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime

@router.post("/text-to-image", response_model=TextToImageResponse)
async def text_to_image(request: TextToImageRequest):
    """
    将文本转换为图像
    """
    try:
        # 准备请求数据
        payload = {
            "promptText": request.promptText,
            "ratio": request.ratio,
            "model": request.model
        }
        
        # 添加可选参数
        if request.seed is not None:
            payload["seed"] = request.seed
            
        if request.referenceImages:
            payload["referenceImages"] = [
                {"uri": img.uri, "tag": img.tag} for img in request.referenceImages
            ]
            
        if request.contentModeration:
            payload["contentModeration"] = {
                "publicFigureThreshold": request.contentModeration.publicFigureThreshold
            }
        
        # 设置请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {RUNWAYML_API_KEY}",
            "X-Runway-Version": "2024-11-06"
        }
        
        # 发送请求到RunwayML API
        response = requests.post(
            f"{RUNWAYML_BASE_URL}/text_to_image",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 200:
            # 获取任务ID
            task_data = response.json()
            task_id = task_data.get("id")
            
            if task_id:
                # 轮询任务状态直到完成
                while True:
                    status_response = requests.get(
                        f"{RUNWAYML_BASE_URL}/tasks/{task_id}",
                        headers=headers
                    )
                    
                    if status_response.status_code == 200:
                        task_status = status_response.json()
                        status = task_status.get("status")
                        
                        if status == "completed":
                            # 任务完成，获取结果
                            output = task_status.get("output", {})
                            image_url = output.get("image_url") or output.get("url")
                            
                            if image_url:
                                # 下载图像并转换为base64
                                image_response = requests.get(image_url)
                                if image_response.status_code == 200:
                                    image_base64 = base64.b64encode(image_response.content).decode('utf-8')
                                    
                                    return TextToImageResponse(
                                        success=True,
                                        image_url=image_url,
                                        image_base64=image_base64,
                                        created_at=datetime.utcnow()
                                    )
                                else:
                                    raise HTTPException(status_code=500, detail="无法下载生成的图像")
                            else:
                                raise HTTPException(status_code=500, detail="生成的图像URL为空")
                        elif status == "failed":
                            error_msg = task_status.get("error", "图像生成失败")
                            raise HTTPException(status_code=500, detail=error_msg)
                        elif status in ["pending", "running", "PENDING", "RUNNING"]:
                            # 继续等待
                            import time
                            time.sleep(2)
                            continue
                        else:
                            raise HTTPException(status_code=500, detail=f"未知任务状态: {status}")
                    else:
                        raise HTTPException(status_code=500, detail="无法获取任务状态")
            else:
                raise HTTPException(status_code=500, detail="未获取到任务ID")
        else:
            error_msg = response.text
            raise HTTPException(status_code=response.status_code, detail=error_msg)
            
    except Exception as e:
        return TextToImageResponse(
            success=False,
            error_message=str(e),
            created_at=datetime.utcnow()
        )

@router.post("/image-to-video", response_model=TextToImageResponse)
async def image_to_video(
    prompt_text: str,
    prompt_image: UploadFile = File(...),
    ratio: str = "1280:720",
    model: str = "gen4_turbo"
):
    """
    将图像转换为视频
    """
    try:
        # 读取上传的图像文件
        image_content = await prompt_image.read()
        
        # 保存图像到临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            temp_file.write(image_content)
            temp_image_path = temp_file.name
        
        # 准备请求数据
        payload = {
            "prompt_text": prompt_text,
            "prompt_image": temp_image_path,
            "ratio": ratio,
            "model": model
        }
        
        # 设置请求头
        headers = {
            "Authorization": f"Bearer {RUNWAYML_API_KEY}",
            "X-Runway-Version": "2024-11-06"
        }
        
        # 发送请求到RunwayML API
        response = requests.post(
            f"{RUNWAYML_BASE_URL}/image_to_video",
            json=payload,
            headers=headers
        )
        
        # 清理临时文件
        os.unlink(temp_image_path)
        
        if response.status_code == 200:
            # 获取任务ID
            task_data = response.json()
            task_id = task_data.get("id")
            
            if task_id:
                # 轮询任务状态直到完成
                while True:
                    status_response = requests.get(
                        f"{RUNWAYML_BASE_URL}/tasks/{task_id}",
                        headers=headers
                    )
                    
                    if status_response.status_code == 200:
                        task_status = status_response.json()
                        status = task_status.get("status")
                        
                        if status == "completed":
                            # 任务完成，获取结果
                            output = task_status.get("output", {})
                            video_url = output.get("video_url") or output.get("url")
                            
                            if video_url:
                                return TextToImageResponse(
                                    success=True,
                                    image_url=video_url,  # 这里实际上是视频URL
                                    created_at=datetime.utcnow()
                                )
                            else:
                                raise HTTPException(status_code=500, detail="生成的视频URL为空")
                        elif status == "failed":
                            error_msg = task_status.get("error", "视频生成失败")
                            raise HTTPException(status_code=500, detail=error_msg)
                        elif status in ["pending", "running", "PENDING", "RUNNING"]:
                            # 继续等待
                            import time
                            time.sleep(2)
                            continue
                        else:
                            raise HTTPException(status_code=500, detail=f"未知任务状态: {status}")
                    else:
                        raise HTTPException(status_code=500, detail="无法获取任务状态")
            else:
                raise HTTPException(status_code=500, detail="未获取到任务ID")
        else:
            error_msg = response.text
            raise HTTPException(status_code=response.status_code, detail=error_msg)
            
    except Exception as e:
        return TextToImageResponse(
            success=False,
            error_message=str(e),
            created_at=datetime.utcnow()
        )

@router.post("/image-url-to-video", response_model=VideoResponse)
async def image_url_to_video(request: ImageToVideoRequest):
    """
    将图片URL转换为视频
    """
    print(f"\n🎬 ===== 开始图片转视频处理 =====")
    print(f"📝 请求参数: {request}")
    
    try:
        print(f"🎬 开始图片转视频处理...")
        print(f"📝 请求参数: {request}")
        
        # 准备请求数据
        payload = {
            "promptText": request.prompt_text,  # API期望的格式
            "promptImage": request.image_url,   # API期望的格式
            "ratio": request.ratio,
            "model": request.model
        }
        
        # 添加可选参数
        if request.duration is not None:
            payload["duration"] = request.duration
        
        print(f"📤 发送到RunwayML的payload: {payload}")
        
        # 设置请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {RUNWAYML_API_KEY}",
            "X-Runway-Version": "2024-11-06"
        }
        
        print(f"🔗 请求URL: {RUNWAYML_BASE_URL}/image_to_video")
        
        # 发送请求到RunwayML API
        print(f"📤 正在发送请求到RunwayML...")
        response = requests.post(
            f"{RUNWAYML_BASE_URL}/image_to_video",
            json=payload,
            headers=headers
        )
        
        print(f"📥 RunwayML响应状态码: {response.status_code}")
        print(f"📥 RunwayML响应内容: {response.text}")
        
        if response.status_code == 200:
            # 获取任务ID
            task_data = response.json()
            task_id = task_data.get("id")
            
            print(f"🆔 获取到任务ID: {task_id}")
            
            if task_id:
                print(f"🔄 开始轮询任务状态...")
                # 轮询任务状态直到完成
                max_wait_time = 300  # 最大等待5分钟
                start_time = time.time()
                
                while True:
                    # 检查是否超时
                    if time.time() - start_time > max_wait_time:
                        print(f"⏰ 任务执行超时")
                        raise HTTPException(status_code=500, detail="任务执行超时，请稍后重试")
                    
                    print(f"📊 正在查询任务状态...")
                    status_response = requests.get(
                        f"{RUNWAYML_BASE_URL}/tasks/{task_id}",
                        headers=headers
                    )
                    
                    print(f"📊 任务状态响应: {status_response.status_code}")
                    
                    if status_response.status_code == 200:
                        task_status = status_response.json()
                        status = task_status.get("status")
                        
                        print(f"📊 任务状态: {status}")
                        print(f"📊 完整任务状态: {task_status}")
                        
                        if status == "completed" or status == "SUCCEEDED":
                            # 任务完成，获取结果
                            output = task_status.get("output", {})
                            
                            # 处理不同的输出格式
                            if isinstance(output, list) and len(output) > 0:
                                # 输出是列表格式，取第一个元素
                                video_url = output[0]
                            elif isinstance(output, dict):
                                # 输出是字典格式
                                video_url = output.get("video_url") or output.get("url")
                            else:
                                video_url = None
                            
                            print(f"🎬 获取到视频URL: {video_url}")
                            
                            if video_url:
                                print(f"✅ 视频生成成功，返回结果")
                                return VideoResponse(
                                    success=True,
                                    video_url=video_url,
                                    created_at=datetime.utcnow()
                                )
                            else:
                                print(f"❌ 生成的视频URL为空")
                                raise HTTPException(status_code=500, detail="生成的视频URL为空")
                        elif status == "failed":
                            error_msg = task_status.get("error", "视频生成失败")
                            print(f"❌ 任务失败: {error_msg}")
                            raise HTTPException(status_code=500, detail=error_msg)
                        elif status in ["pending", "running", "PENDING", "RUNNING"]:
                            # 继续等待
                            print(f"⏳ 任务状态: {status}，继续等待...")
                            time.sleep(2)
                            continue
                        else:
                            print(f"❌ 未知任务状态: {status}")
                            raise HTTPException(status_code=500, detail=f"未知任务状态: {status}")
                    else:
                        print(f"❌ 获取任务状态失败: {status_response.status_code}")
                        print(f"❌ 错误响应: {status_response.text}")
                        raise HTTPException(status_code=500, detail="无法获取任务状态")
            else:
                print(f"❌ 未获取到任务ID")
                raise HTTPException(status_code=500, detail="未获取到任务ID")
        else:
            error_msg = response.text
            print(f"❌ RunwayML API请求失败: {response.status_code}")
            print(f"❌ 错误信息: {error_msg}")
            raise HTTPException(status_code=response.status_code, detail=error_msg)
            
    except HTTPException as e:
        print(f"💥 HTTP异常: {e.detail}")
        return VideoResponse(
            success=False,
            error_message=e.detail,
            created_at=datetime.utcnow()
        )
    except Exception as e:
        print(f"💥 图片转视频过程中发生异常: {str(e)}")
        print(f"💥 异常类型: {type(e).__name__}")
        import traceback
        print(f"💥 异常堆栈: {traceback.format_exc()}")
        
        return VideoResponse(
            success=False,
            error_message=str(e),
            created_at=datetime.utcnow()
        )
    finally:
        print(f"🎬 ===== 图片转视频处理结束 =====")

@router.get("/health")
async def health_check():
    """
    健康检查接口
    """
    return {"status": "healthy", "service": "writing_assistant"} 