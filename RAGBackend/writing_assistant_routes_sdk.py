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

# 尝试导入官方SDK
try:
    from runwayml import RunwayML, TaskFailedError
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False
    print("⚠️ RunwayML SDK not available, falling back to REST API")

router = APIRouter()

# 配置RunwayML API密钥
RUNWAYML_API_KEY = "key_20537ad741a6fb579fafa8127cfff7fab3831d32c4c1c5359ae4704e9ec29c544f97f24b4d455de131db16a407bfd551a903e5058d3f2f859119d102affa17e5"
RUNWAYML_BASE_URL = "https://api.dev.runwayml.com/v1"

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

@router.post("/image-url-to-video-sdk", response_model=VideoResponse)
async def image_url_to_video_sdk(request: ImageToVideoRequest):
    """
    使用官方SDK将图片URL转换为视频
    """
    print(f"\n🎬 ===== 开始图片转视频处理 (SDK版本) =====")
    print(f"📝 请求参数: {request}")
    
    if not SDK_AVAILABLE:
        return VideoResponse(
            success=False,
            error_message="RunwayML SDK not available",
            created_at=datetime.utcnow()
        )
    
    try:
        print(f"🎬 使用官方SDK开始图片转视频处理...")
        
        # 创建SDK客户端
        client = RunwayML()
        
        print(f"📤 发送请求到RunwayML SDK...")
        
        # 使用官方SDK创建任务
        task = client.image_to_video.create(
            model=request.model,
            prompt_image=request.image_url,
            prompt_text=request.prompt_text,
            ratio=request.ratio,
            duration=request.duration
        ).wait_for_task_output()
        
        print(f"✅ SDK任务完成: {task}")
        
        # 获取视频URL
        if hasattr(task, 'output') and task.output:
            video_url = task.output[0] if isinstance(task.output, list) else task.output
            print(f"🎬 获取到视频URL: {video_url}")
            
            return VideoResponse(
                success=True,
                video_url=video_url,
                created_at=datetime.utcnow()
            )
        else:
            print(f"❌ 任务输出为空")
            return VideoResponse(
                success=False,
                error_message="任务输出为空",
                created_at=datetime.utcnow()
            )
            
    except TaskFailedError as e:
        print(f"💥 SDK任务失败: {e.task_details}")
        return VideoResponse(
            success=False,
            error_message=f"任务失败: {e.task_details}",
            created_at=datetime.utcnow()
        )
    except Exception as e:
        print(f"💥 SDK处理过程中发生异常: {str(e)}")
        print(f"💥 异常类型: {type(e).__name__}")
        import traceback
        print(f"💥 异常堆栈: {traceback.format_exc()}")
        
        return VideoResponse(
            success=False,
            error_message=str(e),
            created_at=datetime.utcnow()
        )
    finally:
        print(f"🎬 ===== 图片转视频处理结束 (SDK版本) =====")

@router.get("/health")
async def health_check():
    """
    健康检查接口
    """
    return {
        "status": "healthy", 
        "service": "writing_assistant",
        "sdk_available": SDK_AVAILABLE
    } 