from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from models import (
    Preparation, PreparationShare, PreparationLike, PreparationStatus,
    Course, User
)
from database import get_db
from user_routes import get_current_user
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import json

router = APIRouter(prefix="/preparation", tags=["教案管理"])

# 请求模型
class PreparationCreate(BaseModel):
    title: str
    content: str
    course_id: int
    status: str = "draft"

class PreparationUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    status: Optional[str] = None
    is_public: Optional[int] = None

class PreparationShareRequest(BaseModel):
    to_teacher_ids: List[int]
    message: Optional[str] = None

class AIOptimizeRequest(BaseModel):
    optimization_type: str  # "grammar", "structure", "content", "pedagogy"
    custom_prompt: Optional[str] = None

# 创建教案
@router.post("/create")
async def create_preparation(
    data: PreparationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建教案"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="仅教师可创建教案")
    
    # 验证课程权限
    course = db.query(Course).filter(Course.id == data.course_id).first()
    if not course or course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作该课程")
    
    # 验证状态
    try:
        status = PreparationStatus(data.status)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的状态值")
    
    preparation = Preparation(
        title=data.title,
        content=data.content,
        course_id=data.course_id,
        teacher_id=current_user.id,
        status=status
    )
    
    db.add(preparation)
    db.commit()
    db.refresh(preparation)
    
    return {
        "code": 0,
        "message": "教案创建成功",
        "data": {
            "preparation": {
                "id": preparation.id,
                "title": preparation.title,
                "status": preparation.status.value,
                "created_at": preparation.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }
        }
    }

# 获取我的教案列表（包括自己的和别人分享给我的）
@router.get("/my")
async def get_my_preparations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    course_id: Optional[int] = None,
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    source: Optional[str] = Query(None, description="筛选来源: own(我创建的), shared(分享给我的), all(全部)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取我的教案列表（包括自己创建的和别人分享给我的）"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="仅教师可访问")
    
    # 构建查询：包括自己创建的和别人分享给我的教案
    if source == "own":
        # 只显示我创建的
        query = db.query(Preparation).filter(Preparation.teacher_id == current_user.id)
    elif source == "shared":
        # 只显示分享给我的
        shared_preparation_ids = db.query(PreparationShare.preparation_id).filter(
            PreparationShare.to_teacher_id == current_user.id
        ).subquery()
        
        query = db.query(Preparation).filter(
            Preparation.id.in_(shared_preparation_ids)
        )
    else:
        # 默认显示全部：我创建的 + 分享给我的
        shared_preparation_ids = db.query(PreparationShare.preparation_id).filter(
            PreparationShare.to_teacher_id == current_user.id
        ).subquery()
        
        query = db.query(Preparation).filter(
            or_(
                Preparation.teacher_id == current_user.id,  # 我创建的
                Preparation.id.in_(shared_preparation_ids)  # 分享给我的
            )
        )
    
    # 筛选条件
    if course_id:
        query = query.filter(Preparation.course_id == course_id)
    
    if status:
        try:
            status_enum = PreparationStatus(status)
            query = query.filter(Preparation.status == status_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail="无效的状态值")
    
    if keyword:
        query = query.filter(
            or_(
                Preparation.title.contains(keyword),
                Preparation.content.contains(keyword)
            )
        )
    
    # 总数
    total = query.count()
    
    # 分页
    preparations = query.order_by(Preparation.updated_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    # 关联查询课程信息和分享信息
    result = []
    for prep in preparations:
        course = db.query(Course).filter(Course.id == prep.course_id).first()
        teacher = db.query(User).filter(User.id == prep.teacher_id).first()
        
        # 检查这个教案是否是分享给我的
        is_shared_to_me = db.query(PreparationShare).filter(
            and_(
                PreparationShare.preparation_id == prep.id,
                PreparationShare.to_teacher_id == current_user.id
            )
        ).first()
        
        # 检查我是否可以编辑（创建者或被分享者）
        can_edit = (
            prep.teacher_id == current_user.id or
            is_shared_to_me is not None
        )
        
        result.append({
            "id": prep.id,
            "title": prep.title,
            "course_id": prep.course_id,
            "course_name": course.title if course else "未知课程",
            "teacher_id": prep.teacher_id,
            "teacher_name": teacher.username if teacher else "未知教师",
            "status": prep.status.value,
            "is_public": prep.is_public,
            "is_owner": prep.teacher_id == current_user.id,  # 是否是我创建的
            "is_shared": is_shared_to_me is not None,  # 是否是分享给我的
            "can_edit": can_edit,  # 是否可以编辑
            "share_message": is_shared_to_me.message if is_shared_to_me else None,  # 分享留言
            "shared_at": is_shared_to_me.created_at.strftime("%Y-%m-%d %H:%M:%S") if is_shared_to_me else None,  # 分享时间
            "created_at": prep.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": prep.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        })
    
    return {
        "code": 0,
        "message": "获取成功",
        "data": {
            "preparations": result,
            "total": total,
            "page": page,
            "page_size": page_size,
            "source": source or "all"
        }
    }

# 获取教案详情
@router.get("/{preparation_id}")
async def get_preparation_detail(
    preparation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取教案详情"""
    preparation = db.query(Preparation).filter(Preparation.id == preparation_id).first()
    if not preparation:
        raise HTTPException(status_code=404, detail="教案不存在")
    
    # 权限检查：创建者、被分享者或公开教案可以查看
    has_access = (
        preparation.teacher_id == current_user.id or
        preparation.is_public == 1 or
        db.query(PreparationShare).filter(
            and_(
                PreparationShare.preparation_id == preparation_id,
                PreparationShare.to_teacher_id == current_user.id
            )
        ).first() is not None
    )
    
    if not has_access:
        raise HTTPException(status_code=403, detail="无权访问该教案")
    
    course = db.query(Course).filter(Course.id == preparation.course_id).first()
    teacher = db.query(User).filter(User.id == preparation.teacher_id).first()
    
    # 检查是否已点赞
    is_liked = db.query(PreparationLike).filter(
        and_(
            PreparationLike.preparation_id == preparation_id,
            PreparationLike.teacher_id == current_user.id
        )
    ).first() is not None
    
    # 检查是否可以编辑（创建者或被分享者）
    can_edit = (
        preparation.teacher_id == current_user.id or
        db.query(PreparationShare).filter(
            and_(
                PreparationShare.preparation_id == preparation_id,
                PreparationShare.to_teacher_id == current_user.id
            )
        ).first() is not None
    )
    
    return {
        "code": 0,
        "message": "获取成功",
        "data": {
            "id": preparation.id,
            "title": preparation.title,
            "content": preparation.content,
            "course_id": preparation.course_id,
            "course_name": course.title if course else "未知课程",
            "teacher_id": preparation.teacher_id,
            "teacher_name": teacher.username if teacher else "未知教师",
            "status": preparation.status.value,
            "is_public": preparation.is_public,
            "is_liked": is_liked,
            "can_edit": can_edit,
            "created_at": preparation.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": preparation.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        }
    }

# 更新教案
@router.put("/{preparation_id}")
async def update_preparation(
    preparation_id: int,
    data: PreparationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新教案（创建者或被分享者都可以修改）"""
    preparation = db.query(Preparation).filter(Preparation.id == preparation_id).first()
    if not preparation:
        raise HTTPException(status_code=404, detail="教案不存在")
    
    # 权限检查：创建者或被分享者可以修改
    can_edit = (
        preparation.teacher_id == current_user.id or
        db.query(PreparationShare).filter(
            and_(
                PreparationShare.preparation_id == preparation_id,
                PreparationShare.to_teacher_id == current_user.id
            )
        ).first() is not None
    )
    
    if not can_edit:
        raise HTTPException(status_code=403, detail="无权修改该教案")
    
    # 更新字段
    update_data = data.dict(exclude_unset=True)
    
    # 处理状态字段
    if "status" in update_data:
        try:
            update_data["status"] = PreparationStatus(update_data["status"])
        except ValueError:
            raise HTTPException(status_code=400, detail="无效的状态值")
    
    for field, value in update_data.items():
        setattr(preparation, field, value)
    
    preparation.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(preparation)
    
    return {
        "code": 0,
        "message": "教案更新成功",
        "data": {}
    }

# AI优化教案建议
@router.post("/{preparation_id}/ai-optimize")
async def get_ai_optimization_suggestions(
    preparation_id: int,
    data: AIOptimizeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取AI优化建议"""
    preparation = db.query(Preparation).filter(Preparation.id == preparation_id).first()
    if not preparation:
        raise HTTPException(status_code=404, detail="教案不存在")
    
    # 权限检查：创建者或被分享者可以获取AI建议
    can_access = (
        preparation.teacher_id == current_user.id or
        db.query(PreparationShare).filter(
            and_(
                PreparationShare.preparation_id == preparation_id,
                PreparationShare.to_teacher_id == current_user.id
            )
        ).first() is not None
    )
    
    if not can_access:
        raise HTTPException(status_code=403, detail="无权操作该教案")
    
    # 构建AI提示词
    optimization_prompts = {
        "grammar": "请检查并优化这份教案的语法表达和文字流畅度，保持原有结构，重点改进语言表达。请按以下格式返回：\n\n## 语法优化建议\n\n### 主要问题\n- 问题1\n- 问题2\n\n### 具体修改建议\n1. **建议1**：具体修改内容\n2. **建议2**：具体修改内容\n\n### 优化后的内容\n（提供优化后的完整内容）",
        "structure": "请分析并优化这份教案的结构逻辑和层次安排，提供更合理的组织方式。请按以下格式返回：\n\n## 结构优化建议\n\n### 当前结构分析\n- 优点：...\n- 不足：...\n\n### 改进建议\n1. **建议1**：具体改进方案\n2. **建议2**：具体改进方案\n\n### 优化后的结构\n（提供重新组织后的内容）",
        "content": "请评估并建议如何丰富这份教案的教学内容，增加实用的教学元素。请按以下格式返回：\n\n## 内容优化建议\n\n### 内容分析\n- 当前内容特点：...\n- 需要改进的地方：...\n\n### 具体改进建议\n1. **建议1**：具体改进内容\n2. **建议2**：具体改进内容\n3. **建议3**：具体改进内容\n\n### 补充内容\n（提供需要补充的具体内容）",
        "pedagogy": "请从教学法角度分析并建议如何改进这份教案的教学方法和策略。请按以下格式返回：\n\n## 教学法优化建议\n\n### 教学方法分析\n- 当前方法：...\n- 适用性：...\n\n### 改进建议\n1. **建议1**：具体教学方法改进\n2. **建议2**：具体教学方法改进\n\n### 实施建议\n（提供具体的实施步骤和注意事项）"
    }
    
    prompt = optimization_prompts.get(data.optimization_type, "请对这份教案提出优化建议：")
    if data.custom_prompt:
        prompt = data.custom_prompt
    
    # 构建完整的问题，包含教案标题和内容
    full_question = f"""
{prompt}

教案标题：{preparation.title}

教案内容：
{preparation.content}

请提供具体的优化建议和改进方案。
"""
    
    try:
        # 调用simple_chat_with_assistant获取AI回答
        from teacher.chat_routes import simple_chat_with_assistant
        
        # 调用聊天接口
        response = await simple_chat_with_assistant(
            question=full_question,
            chat_name="教案改进助手",
            current_user=current_user
        )
        
        # 提取AI回答
        ai_answer = response.get("data", {}).get("answer", "")
        
        # 解析AI回答，提取建议和优化内容
        ai_suggestions = {
            "optimized_content": preparation.content,  # 保持原内容，用户可以选择应用
            "optimization_type": data.optimization_type,
            "ai_response": ai_answer # AI的详细分析和建议
        }
        
        return {
            "code": 0,
            "message": "AI建议生成成功",
            "data": {
                "suggestions": ai_suggestions
            }
        }
        
    except Exception as e:
        print(f"AI优化建议生成失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI建议生成失败: {str(e)}")

# 应用AI优化建议
@router.post("/{preparation_id}/apply-ai-suggestions")
async def apply_ai_suggestions(
    preparation_id: int,
    optimized_content: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """应用AI优化建议"""
    preparation = db.query(Preparation).filter(Preparation.id == preparation_id).first()
    if not preparation:
        raise HTTPException(status_code=404, detail="教案不存在")
    
    # 权限检查
    can_edit = (
        preparation.teacher_id == current_user.id or
        db.query(PreparationShare).filter(
            and_(
                PreparationShare.preparation_id == preparation_id,
                PreparationShare.to_teacher_id == current_user.id
            )
        ).first() is not None
    )
    
    if not can_edit:
        raise HTTPException(status_code=403, detail="无权修改该教案")
    
    # 如果optimized_content为空，则请求AI生成优化内容
    if not optimized_content or optimized_content.strip() == "":
        try:
            from teacher.chat_routes import simple_chat_with_assistant
            
            # 构建请求AI优化内容的提示词
            question = f"请直接优化这份教案的内容，返回优化后的完整教案：\n{preparation.content}"
            chat_name = "教案改进助手"
            
            # 调用聊天接口获取优化后的内容
            response = await simple_chat_with_assistant(
                question=question,
                chat_name=chat_name,
                current_user=current_user
            )
            
            # 提取AI优化后的内容
            optimized_content = response.get("data", {}).get("answer", preparation.content)
            
        except Exception as e:
            print(f"AI内容优化失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"AI内容优化失败: {str(e)}")
    
    # 更新教案内容
    preparation.content = optimized_content
    preparation.updated_at = datetime.utcnow()
    db.commit()
    
    return {
        "code": 0,
        "message": "AI建议应用成功",
        "data": {}
    }

# 删除教案
@router.delete("/{preparation_id}")
async def delete_preparation(
    preparation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除教案（仅创建者可删除）"""
    preparation = db.query(Preparation).filter(Preparation.id == preparation_id).first()
    if not preparation:
        raise HTTPException(status_code=404, detail="教案不存在")
    
    if preparation.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="仅创建者可删除该教案")
    
    db.delete(preparation)
    db.commit()
    
    return {
        "code": 0,
        "message": "教案删除成功",
        "data": {}
    }

# 分享教案给其他教师
@router.post("/{preparation_id}/share")
async def share_preparation(
    preparation_id: int,
    data: PreparationShareRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """分享教案给其他教师"""
    preparation = db.query(Preparation).filter(Preparation.id == preparation_id).first()
    if not preparation:
        raise HTTPException(status_code=404, detail="教案不存在")
    
    if preparation.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权分享该教案")
    
    success_count = 0
    # 验证接收者
    for teacher_id in data.to_teacher_ids:
        if teacher_id == current_user.id:
            continue
        
        teacher = db.query(User).filter(
            and_(User.id == teacher_id, User.role == "teacher")
        ).first()
        if not teacher:
            continue
        
        # 检查是否已经分享过
        existing_share = db.query(PreparationShare).filter(
            and_(
                PreparationShare.preparation_id == preparation_id,
                PreparationShare.to_teacher_id == teacher_id
            )
        ).first()
        
        if existing_share:
            continue
        
        # 创建分享记录
        share = PreparationShare(
            preparation_id=preparation_id,
            from_teacher_id=current_user.id,
            to_teacher_id=teacher_id,
            message=data.message
        )
        db.add(share)
        success_count += 1
    
    db.commit()
    
    return {
        "code": 0,
        "message": f"教案已分享给 {success_count} 位教师",
        "data": {}
    }

# 获取分享给我的教案
@router.get("/shared/to-me")
async def get_shared_preparations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    is_read: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取分享给我的教案"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="仅教师可访问")
    
    query = db.query(PreparationShare).filter(PreparationShare.to_teacher_id == current_user.id)
    
    if is_read is not None:
        query = query.filter(PreparationShare.is_read == is_read)
    
    total = query.count()
    shares = query.order_by(PreparationShare.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    result = []
    for share in shares:
        preparation = db.query(Preparation).filter(Preparation.id == share.preparation_id).first()
        from_teacher = db.query(User).filter(User.id == share.from_teacher_id).first()
        course = db.query(Course).filter(Course.id == preparation.course_id).first() if preparation else None
        
        result.append({
            "share_id": share.id,
            "preparation_id": share.preparation_id,
            "preparation_title": preparation.title if preparation else "教案已删除",
            "course_name": course.title if course else "未知课程",
            "from_teacher_name": from_teacher.username if from_teacher else "未知教师",
            "message": share.message,
            "is_read": share.is_read,
            "created_at": share.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })
    
    return {
        "code": 0,
        "message": "获取成功",
        "data": {
            "shares": result,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    }

# 标记分享的教案为已读
@router.put("/share/{share_id}/read")
async def mark_share_as_read(
    share_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """标记分享的教案为已读"""
    share = db.query(PreparationShare).filter(
        and_(
            PreparationShare.id == share_id,
            PreparationShare.to_teacher_id == current_user.id
        )
    ).first()
    
    if not share:
        raise HTTPException(status_code=404, detail="分享记录不存在")
    
    share.is_read = 1
    db.commit()
    
    return {
        "code": 0,
        "message": "已标记为已读",
        "data": {}
    }

# 获取公开教案列表
@router.get("/public/list")
async def get_public_preparations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    course_id: Optional[int] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取公开教案列表"""
    query = db.query(Preparation).filter(Preparation.is_public == 1)
    
    if course_id:
        query = query.filter(Preparation.course_id == course_id)
    
    if keyword:
        query = query.filter(
            or_(
                Preparation.title.contains(keyword),
                Preparation.content.contains(keyword)
            )
        )
    
    total = query.count()
    preparations = query.order_by(Preparation.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    result = []
    for prep in preparations:
        course = db.query(Course).filter(Course.id == prep.course_id).first()
        teacher = db.query(User).filter(User.id == prep.teacher_id).first()
        
        result.append({
            "id": prep.id,
            "title": prep.title,
            "course_name": course.title if course else "未知课程",
            "teacher_name": teacher.username if teacher else "未知教师",
            "created_at": prep.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })
    
    return {
        "code": 0,
        "message": "获取成功",
        "data": {
            "preparations": result,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    }

# 点赞/取消点赞教案
@router.post("/{preparation_id}/like")
async def toggle_preparation_like(
    preparation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """点赞/取消点赞教案"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="仅教师可操作")
    
    preparation = db.query(Preparation).filter(Preparation.id == preparation_id).first()
    if not preparation:
        raise HTTPException(status_code=404, detail="教案不存在")
    
    # 检查是否已点赞
    existing_like = db.query(PreparationLike).filter(
        and_(
            PreparationLike.preparation_id == preparation_id,
            PreparationLike.teacher_id == current_user.id
        )
    ).first()
    
    if existing_like:
        # 取消点赞
        db.delete(existing_like)
        message = "已取消点赞"
    else:
        # 添加点赞
        like = PreparationLike(
            preparation_id=preparation_id,
            teacher_id=current_user.id
        )
        db.add(like)
        message = "点赞成功"
    
    db.commit()
    
    # 获取最新点赞数
    like_count = db.query(PreparationLike).filter(PreparationLike.preparation_id == preparation_id).count()
    
    return {
        "code": 0,
        "message": message,
        "data": {
            "like_count": like_count
        }
    }

# 复制教案到我的教案中
@router.post("/{preparation_id}/duplicate")
async def duplicate_preparation(
    preparation_id: int,
    new_title: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """复制教案到我的教案中"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="仅教师可操作")
    
    original = db.query(Preparation).filter(Preparation.id == preparation_id).first()
    if not original:
        raise HTTPException(status_code=404, detail="教案不存在")
    
    # 权限检查：创建者、被分享者或公开教案可以复制
    can_access = (
        original.teacher_id == current_user.id or
        original.is_public == 1 or
        db.query(PreparationShare).filter(
            and_(
                PreparationShare.preparation_id == preparation_id,
                PreparationShare.to_teacher_id == current_user.id
            )
        ).first() is not None
    )
    
    if not can_access:
        raise HTTPException(status_code=403, detail="无权复制该教案")
    
    # 创建副本
    duplicate_title = new_title or f"{original.title}（副本）"
    
    duplicate = Preparation(
        title=duplicate_title,
        content=original.content,
        course_id=original.course_id,
        teacher_id=current_user.id,
        status=PreparationStatus.draft,
        is_public=0
    )
    
    db.add(duplicate)
    db.commit()
    db.refresh(duplicate)
    
    return {
        "code": 0,
        "message": "教案复制成功",
        "data": {
            "preparation_id": duplicate.id,
            "title": duplicate.title
        }
    }