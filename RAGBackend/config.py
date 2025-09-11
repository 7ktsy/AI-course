import os
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

# 获取RunwayML API密钥
def get_runwayml_api_key():
    """安全地获取RunwayML API密钥"""
    api_key = os.getenv('RUNWAYML_API_SECRET')
    if not api_key:
        raise ValueError("RUNWAYML_API_SECRET 环境变量未设置")
    return api_key

# 其他配置
RUNWAYML_BASE_URL = "https://api.dev.runwayml.com/v1" 