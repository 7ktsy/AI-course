from redis_client import r
import random
def set_captcha(phone: str, code: str, expire_seconds: int = 300):
    key = f"captcha:{phone}"
    r.set(key, code, ex=expire_seconds)

def check_captcha(phone: str, code: str) -> bool:
    key = f"captcha:{phone}"
    stored_code = r.get(key)
    return stored_code == code

def generate_captcha(length=6):
    return ''.join(random.choices("0123456789", k=length))

def send_captcha_to_phone(phone: str) -> str:
    code = generate_captcha()
    redis_key = f"captcha:{phone}"
    r.setex(redis_key, 300, code)  # 设置 5 分钟过期
    print(f"[模拟短信] 向 {phone} 发送验证码: {code}")  # 实际部署时换成短信服务
    return code