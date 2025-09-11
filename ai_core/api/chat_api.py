# from fastapi import FastAPI, WebSocket
# from typing import Optional, Dict, Any
# from services.session_management_service import (
#     create_session,
#     chat_with_assistant,
#     get_session_id_by_name
# )
# from fastapi.responses import StreamingResponse
# import json
# import asyncio

# app = FastAPI()

# @app.post("/api/chat")
# async def chat(
#     question: str,
#     chat_name: str,
#     session_name: Optional[str] = None,
#     session_id: Optional[str] = None
# ):
#     """
#     普通的HTTP聊天接口
#     """
#     try:
#         # 如果没有session_id但有session_name，尝试获取或创建session
#         if not session_id and session_name:
#             try:
#                 session_id = get_session_id_by_name(chat_name, session_name)
#             except Exception:
#                 # 如果获取失败，创建新的session
#                 create_result = create_session(chat_name, name=session_name)
#                 session_id = create_result['data']['session_id']
        
#         # 获取AI响应
#         response = chat_with_assistant(
#             chat_name=chat_name,
#             question=question,
#             session_id=session_id,
#             stream=False
#         )
#         return response
        
#     except Exception as e:
#         return {
#             "code": 1,
#             "message": str(e),
#             "data": None
#         }

# async def stream_chat_generator(
#     chat_name: str,
#     question: str,
#     session_id: Optional[str] = None
# ):
#     """
#     生成流式响应
#     """
#     try:
#         # 获取流式响应
#         stream_response = chat_with_assistant(
#             chat_name=chat_name,
#             question=question,
#             session_id=session_id,
#             stream=True
#         )
        
#         # 逐个yield响应数据
#         for response in stream_response:
#             yield f"data: {json.dumps(response, ensure_ascii=False)}\n\n"
            
#     except Exception as e:
#         error_response = {
#             "code": 1,
#             "message": str(e),
#             "data": None
#         }
#         yield f"data: {json.dumps(error_response, ensure_ascii=False)}\n\n"

# @app.get("/api/chat/stream")
# async def stream_chat(
#     question: str,
#     chat_name: str,
#     session_name: Optional[str] = None,
#     session_id: Optional[str] = None
# ):
#     """
#     流式聊天接口（Server-Sent Events）
#     """
#     try:
#         # 如果没有session_id但有session_name，尝试获取或创建session
#         if not session_id and session_name:
#             try:
#                 session_id = get_session_id_by_name(chat_name, session_name)
#             except Exception:
#                 # 如果获取失败，创建新的session
#                 create_result = create_session(chat_name, name=session_name)
#                 session_id = create_result['data']['session_id']
        
#         return StreamingResponse(
#             stream_chat_generator(chat_name, question, session_id),
#             media_type="text/event-stream"
#         )
        
#     except Exception as e:
#         return {
#             "code": 1,
#             "message": str(e),
#             "data": None
#         }

# @app.websocket("/ws/chat")
# async def websocket_chat(websocket: WebSocket):
#     """
#     WebSocket聊天接口
#     """
#     await websocket.accept()
    
#     try:
#         while True:
#             # 接收消息
#             data = await websocket.receive_json()
#             question = data.get("question")
#             chat_name = data.get("chat_name")
#             session_id = data.get("session_id")
#             session_name = data.get("session_name")
            
#             if not question or not chat_name:
#                 await websocket.send_json({
#                     "code": 1,
#                     "message": "Missing required parameters",
#                     "data": None
#                 })
#                 continue
            
#             # 如果没有session_id但有session_name，尝试获取或创建session
#             if not session_id and session_name:
#                 try:
#                     session_id = get_session_id_by_name(chat_name, session_name)
#                 except Exception:
#                     # 如果获取失败，创建新的session
#                     create_result = create_session(chat_name, name=session_name)
#                     session_id = create_result['data']['session_id']
            
#             # 获取流式响应
#             stream_response = chat_with_assistant(
#                 chat_name=chat_name,
#                 question=question,
#                 session_id=session_id,
#                 stream=True
#             )
            
#             # 发送响应
#             for response in stream_response:
#                 await websocket.send_json(response)
#                 await asyncio.sleep(0)  # 让出控制权
                
#     except Exception as e:
#         await websocket.send_json({
#             "code": 1,
#             "message": str(e),
#             "data": None
#         })
#     finally:
#         await websocket.close() 