from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models import CourseMaterial, User, Course
from database import get_db
from user_routes import get_current_user
from fastapi import UploadFile, File, Form
from datetime import datetime
import os
import sys
from uuid import uuid4 
from ragflow_client import upload_and_parse_to_ragflow
from models import ParseStatus

# 添加ai-core到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'ai_core'))

try:
    from ai_core.services.file_management_service import (
        list_documents, 
        get_document_id_by_name, 
        parse_documents, 
        stop_parsing_documents
    )
except ImportError:
    # 如果导入失败，提供空的实现
    def list_documents(*args, **kwargs):
        raise HTTPException(500, "ai-core模块未正确配置")
    
    def get_document_id_by_name(*args, **kwargs):
        raise HTTPException(500, "ai-core模块未正确配置")
    
    def parse_documents(*args, **kwargs):
        raise HTTPException(500, "ai-core模块未正确配置")
    
    def stop_parsing_documents(*args, **kwargs):
        raise HTTPException(500, "ai-core模块未正确配置")

router = APIRouter(prefix="/material", tags=["课程资料"])

UPLOAD_DIR = "uploaded_materials"
os.makedirs(UPLOAD_DIR, exist_ok=True)

#教师上传课程大纲文件或课程关键词,同时同步RAG知识库
@router.post("/{course_id}/upload")
def upload_material(
    course_id: int,
    title: str = Form(...),
    description: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        course = db.get(Course, course_id)
        if not course or course.teacher_id != current_user.id or current_user.role != "teacher":
            raise HTTPException(status_code=403, detail="权限不足，仅限教师上传资料")

        filename = f"{uuid4().hex}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)

        with open(file_path, "wb") as f:
            f.write(file.file.read())

        material = CourseMaterial(
            title=title,
            filename=file.filename,
            description=description,
            file_path=file_path,
            teacher_id=current_user.id,
            uploadtime=datetime.utcnow(),
            course_id=course_id
        )
        db.add(material)
        db.commit()
        db.refresh(material)

        try:
            upload_and_parse_to_ragflow(course.dataset_name, file_path, file.filename)
            material.status = ParseStatus.parsing
            db.commit()
        except Exception as e:
            material.status = ParseStatus.failed
            material.error_msg = str(e)[:800]
            db.commit()
            print("知识库同步失败：", e)

        return {
            "msg": "上传成功",
            "material": {
                "id": material.id,
                "title": material.title,
                "filename": material.filename,
                "uploadtime": material.uploadtime.strftime("%Y-%m-%d %H:%M:%S")
            }
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"服务器内部错误：{str(e)}")
    
    
#获取上传资料的状态
@router.get("/{course_id}/materials")
def get_course_materials(
    course_id: int, 
    page: int = 1, 
    page_size: int = 10,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    course = db.get(Course, course_id)
    if not course or course.teacher_id != current_user.id:
        raise HTTPException(403, "无权查看")

    # 计算总数
    total = db.query(CourseMaterial).filter_by(course_id=course_id).count()
    
    # 分页查询
    offset = (page - 1) * page_size
    materials = db.query(CourseMaterial).filter_by(course_id=course_id)\
        .order_by(CourseMaterial.uploadtime.desc())\
        .offset(offset).limit(page_size).all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
        "data": [
            {
                "id": m.id,
                "title": m.title,
                "status": m.status.value,
                "uploadtime": m.uploadtime.strftime("%Y-%m-%d %H:%M:%S"),
                "filename": m.filename,
                "error_msg": m.error_msg
            } for m in materials
        ]
    }


# 解析指定文档
@router.post("/{course_id}/documents/{document_name}/parse")
async def parse_course_document(
    course_id: int,
    document_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """解析课程中的指定文档"""
    course = db.get(Course, course_id)
    if not course or course.teacher_id != current_user.id:
        raise HTTPException(403, "无权操作")
    
    if not course.dataset_name:
        raise HTTPException(404, "课程没有关联的知识库")
    
    try:
        # 先获取数据集中的所有文档列表，用于调试
        try:
            docs_result = list_documents(course.dataset_name)
            if docs_result.get("code") == 0:
                available_docs = docs_result.get("data", {}).get("docs", [])
                print(f"数据集 '{course.dataset_name}' 中的可用文档:")
                for doc in available_docs:
                    print(f"  - '{doc.get('name')}' (ID: {doc.get('id')})")
            else:
                print(f"获取文档列表失败: {docs_result.get('message')}")
        except Exception as e:
            print(f"获取文档列表异常: {e}")
        
        # 获取文档ID
        try:
            print(f"尝试查找文档: '{document_name}'")
            doc_id = get_document_id_by_name(course.dataset_name, document_name)
            print(f"✅ 找到文档ID: {doc_id}")
        except Exception as e:
            # 尝试自动添加常见扩展名
            extensions = ['.pdf', '.docx', '.doc', '.txt', '.md']
            found = False
            
            for ext in extensions:
                try:
                    full_name = document_name + ext
                    print(f"尝试查找文档: '{full_name}'")
                    doc_id = get_document_id_by_name(course.dataset_name, full_name)
                    print(f"✅ 找到文档ID: {doc_id} (使用扩展名 {ext})")
                    found = True
                    break
                except:
                    continue
            
            if not found:
                error_msg = f"文档 '{document_name}' 不存在: {str(e)}"
                print(f"❌ {error_msg}")
                raise HTTPException(400, error_msg)
        
        # 调用ai-core的解析接口
        result = parse_documents(course.dataset_name, [doc_id])
        
        # 更新数据库中对应材料的状态
        material = db.query(CourseMaterial).filter(
            CourseMaterial.course_id == course_id,
            CourseMaterial.filename == document_name
        ).first()
        if material:
            material.status = ParseStatus.parsing
            db.commit()
        
        return result
    except Exception as e:
        raise HTTPException(500, f"解析文档失败: {str(e)}")

# 停止解析指定文档
@router.delete("/{course_id}/documents/{document_name}/parse")
async def stop_parse_course_document(
    course_id: int,
    document_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """停止解析课程中的指定文档"""
    course = db.get(Course, course_id)
    if not course or course.teacher_id != current_user.id:
        raise HTTPException(403, "无权操作")
    
    if not course.dataset_name:
        raise HTTPException(404, "课程没有关联的知识库")
    
    try:
        # 获取文档ID
        try:
            doc_id = get_document_id_by_name(course.dataset_name, document_name)
        except Exception as e:
            raise HTTPException(400, f"文档 '{document_name}' 不存在: {str(e)}")
        
        # 调用ai-core的停止解析接口
        result = stop_parsing_documents(course.dataset_name, [doc_id])
        
        # 更新数据库中对应材料的状态
        material = db.query(CourseMaterial).filter(
            CourseMaterial.course_id == course_id,
            CourseMaterial.filename == document_name
        ).first()
        if material:
            material.status = ParseStatus.pending
            db.commit()
        
        return result
    except Exception as e:
        raise HTTPException(500, f"停止解析失败: {str(e)}")

# 查询文档解析状态
@router.get("/{course_id}/documents/{document_name}/status")
async def get_document_parse_status(
    course_id: int,
    document_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """查询指定文档的解析状态"""
    course = db.get(Course, course_id)
    if not course or course.teacher_id != current_user.id:
        raise HTTPException(403, "无权查看")
    
    # 查询数据库中的状态
    material = db.query(CourseMaterial).filter(
        CourseMaterial.course_id == course_id,
        CourseMaterial.filename == document_name
    ).first()
    
    if not material:
        raise HTTPException(404, "文档不存在")
    
    return {
        "document_name": document_name,
        "status": material.status.value,
        "error_msg": material.error_msg,
        "upload_time": material.uploadtime.strftime("%Y-%m-%d %H:%M:%S")
    }