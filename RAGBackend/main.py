from fastapi import FastAPI
from user_routes import router as user_router
from fastapi.openapi.utils import get_openapi
from teacher.course_routes import router as course_router
from teacher.material_routes import router as material_router
from teacher.assignment_routes import router as assignment_router
from teacher.chat_routes import router as chat_router
from teacher.ppt_routes import router as ppt_router
from captcha_routes import router as captcha_router
from student.student_routes import router as student_router
from admin_routes import router as admin_router
from teacher.preparation_routes import router as prepa_router
from writing_assistant_routes import router as writing_assistant_router
from simple_image_generator import router as simple_image_router
from teaching_board_routes import router as teaching_board_router
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 或指定 ["http://localhost:5173"] 只允许特定来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router, prefix="/user")
app.include_router(course_router)
app.include_router(material_router)
app.include_router(chat_router)
app.include_router(ppt_router)
app.include_router(assignment_router)
app.include_router(captcha_router)
app.include_router(student_router)
app.include_router(admin_router, prefix="/user")
app.include_router(prepa_router)
app.include_router(writing_assistant_router, prefix="/writing-assistant")
app.include_router(simple_image_router, prefix="/image-generator")
app.include_router(teaching_board_router)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="教学实训智能体后端",
        version="1.0.0",
        description="支持 Bearer Token 授权",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization"
        }
    }
    for path in openapi_schema["paths"].values():
        for op in path.values():
            op["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
