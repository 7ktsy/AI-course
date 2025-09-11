#!/usr/bin/env python3
"""
教学计划看板功能测试脚本
"""

import requests
import json
from datetime import datetime, date

# 配置
BASE_URL = "http://localhost:8000"
API_BASE_URL = f"{BASE_URL}/api/teaching-board"

def login_and_get_token():
    """登录并获取token"""
    login_data = {
        "phone": "13800138000",  # 使用测试账号
        "password": "123456"
    }
    
    response = requests.post(f"{BASE_URL}/user/login", json=login_data)
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            return data["data"]["access_token"]
    
    print("登录失败")
    return None

def test_teaching_board_api():
    """测试教学计划看板API"""
    # 登录获取token
    token = login_and_get_token()
    if not token:
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("=== 教学计划看板API测试 ===")
    
    # 1. 创建教学事件
    print("\n1. 创建教学事件...")
    event_data = {
        "title": "数学基础理论课",
        "description": "讲解数学基础概念和公式推导",
        "type": "lecture",
        "duration": 45,
        "color": "#409EFF"
    }
    
    response = requests.post(f"{API_BASE_URL}/events", json=event_data, headers=headers)
    print(f"创建事件响应: {response.status_code}")
    if response.status_code == 200:
        print(f"事件创建成功: {response.json()}")
        event_id = response.json()["data"]["id"]
    else:
        print(f"创建事件失败: {response.text}")
        return
    
    # 2. 获取教学事件列表
    print("\n2. 获取教学事件列表...")
    response = requests.get(f"{API_BASE_URL}/events", headers=headers)
    print(f"获取事件列表响应: {response.status_code}")
    if response.status_code == 200:
        print(f"事件列表: {response.json()}")
    
    # 3. 创建教学计划看板（所有教师共用）
    print("\n3. 创建教学计划看板...")
    today = date.today().isoformat()
    board_data = {
        "title": f"{today} 教学计划",
        "description": "今日教学计划看板（所有教师共用）",
        "board_date": today,
        "view_type": "day"
    }
    
    response = requests.post(f"{API_BASE_URL}/boards", json=board_data, headers=headers)
    print(f"创建看板响应: {response.status_code}")
    if response.status_code == 200:
        print(f"看板创建成功: {response.json()}")
        board_id = response.json()["data"]["id"]
    else:
        print(f"创建看板失败: {response.text}")
        return
    
    # 4. 放置事件到看板
    print("\n4. 放置事件到看板...")
    place_data = {
        "event_id": event_id,
        "startHour": 8.0,
        "duration": 45,
        "position_x": 33.33,
        "position_y": 0
    }
    
    response = requests.post(f"{API_BASE_URL}/boards/{board_id}/events", json=place_data, headers=headers)
    print(f"放置事件响应: {response.status_code}")
    if response.status_code == 200:
        print(f"事件放置成功: {response.json()}")
        placed_event_id = response.json()["data"]["id"]
    else:
        print(f"放置事件失败: {response.text}")
        return
    
    # 5. 获取看板详情
    print("\n5. 获取看板详情...")
    response = requests.get(f"{API_BASE_URL}/boards/{board_id}", headers=headers)
    print(f"获取看板详情响应: {response.status_code}")
    if response.status_code == 200:
        print(f"看板详情: {response.json()}")
    
    # 6. 更新已放置的事件
    print("\n6. 更新已放置的事件...")
    update_data = {
        "id": placed_event_id,
        "event_id": event_id,
        "startHour": 9.0,
        "duration": 60,
        "position_x": 37.5,
        "position_y": 0
    }
    
    response = requests.post(f"{API_BASE_URL}/boards/{board_id}/events", json=update_data, headers=headers)
    print(f"更新事件响应: {response.status_code}")
    if response.status_code == 200:
        print(f"事件更新成功: {response.json()}")
    
    # 7. 获取看板列表
    print("\n7. 获取看板列表...")
    response = requests.get(f"{API_BASE_URL}/boards", headers=headers)
    print(f"获取看板列表响应: {response.status_code}")
    if response.status_code == 200:
        print(f"看板列表: {response.json()}")
    
    # 8. 删除已放置的事件
    print("\n8. 删除已放置的事件...")
    response = requests.delete(f"{API_BASE_URL}/boards/{board_id}/events/{placed_event_id}", headers=headers)
    print(f"删除已放置事件响应: {response.status_code}")
    if response.status_code == 200:
        print(f"已放置事件删除成功: {response.json()}")
    
    # 9. 删除教学事件
    print("\n9. 删除教学事件...")
    response = requests.delete(f"{API_BASE_URL}/events/{event_id}", headers=headers)
    print(f"删除事件响应: {response.status_code}")
    if response.status_code == 200:
        print(f"事件删除成功: {response.json()}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_teaching_board_api() 