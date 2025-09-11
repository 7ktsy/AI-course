
from fastapi import APIRouter, HTTPException
from redis import Redis
import random

router = APIRouter(prefix="/captcha", tags=["验证码"])

redis_client = Redis(host="localhost", port=6379, decode_responses=True)

@router.post("/send")
def send_captcha(phone: str):
    code = str(random.randint(100000, 999999))
    redis_client.setex(f"captcha:{phone}", 300, code)
    print(f"[模拟短信] 向 {phone} 发送验证码: {code}")
    return {
        "msg": "验证码已发送",
        "captcha": code
    }
