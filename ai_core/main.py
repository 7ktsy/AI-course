from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from api.chat_api import app as chat_api
import uvicorn

app = FastAPI()

# 挂载聊天API
app.mount("/api", chat_api)

# 挂载静态文件
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 