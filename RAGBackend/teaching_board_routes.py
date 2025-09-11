from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime, date
import json

from database import get_db
from models import (
    User, TeachingEvent, PlacedEvent, TeachingBoard, Course
)
from user_routes import get_current_user

router = APIRouter(prefix="/api/teaching-board", tags=["教学计划看板"])


# 获取当前用户的教学事件库
@router.get("/events")
async def get_teaching_events(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的教学事件库"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="只有教师可以访问教学事件")
    
    events = db.query(TeachingEvent).filter(
        TeachingEvent.teacher_id == current_user.id
    ).all()
    
    return {
        "success": True,
        "data": [
            {
                "id": event.id,
                "title": event.title,
                "description": event.description,
                "type": event.event_type,
                "duration": event.duration,
                "color": event.color,
                "teacherName": current_user.username,
                "course_id": event.course_id,
                "created_at": event.created_at.isoformat() if event.created_at else None
            }
            for event in events
        ]
    }


# 创建教学事件
@router.post("/events")
async def create_teaching_event(
    event_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建教学事件"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="只有教师可以创建教学事件")
    
    try:
        new_event = TeachingEvent(
            title=event_data["title"],
            description=event_data.get("description", ""),
            event_type=event_data["type"],
            duration=event_data["duration"],
            color=event_data["color"],
            teacher_id=current_user.id,
            course_id=event_data.get("course_id")
        )
        
        db.add(new_event)
        db.commit()
        db.refresh(new_event)
        
        return {
            "success": True,
            "data": {
                "id": new_event.id,
                "title": new_event.title,
                "description": new_event.description,
                "type": new_event.event_type,
                "duration": new_event.duration,
                "color": new_event.color,
                "teacherName": current_user.username,
                "course_id": new_event.course_id
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"创建事件失败: {str(e)}")


# 更新教学事件
@router.put("/events/{event_id}")
async def update_teaching_event(
    event_id: int,
    event_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新教学事件"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="只有教师可以更新教学事件")
    
    event = db.query(TeachingEvent).filter(
        and_(
            TeachingEvent.id == event_id,
            TeachingEvent.teacher_id == current_user.id
        )
    ).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="事件不存在或无权限")
    
    try:
        event.title = event_data["title"]
        event.description = event_data.get("description", "")
        event.event_type = event_data["type"]
        event.duration = event_data["duration"]
        event.color = event_data["color"]
        event.course_id = event_data.get("course_id")
        event.updated_at = datetime.utcnow()
        
        db.commit()
        
        return {
            "success": True,
            "data": {
                "id": event.id,
                "title": event.title,
                "description": event.description,
                "type": event.event_type,
                "duration": event.duration,
                "color": event.color,
                "teacherName": current_user.username,
                "course_id": event.course_id
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"更新事件失败: {str(e)}")


# 删除教学事件
@router.delete("/events/{event_id}")
async def delete_teaching_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除教学事件"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="只有教师可以删除教学事件")
    
    event = db.query(TeachingEvent).filter(
        and_(
            TeachingEvent.id == event_id,
            TeachingEvent.teacher_id == current_user.id
        )
    ).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="事件不存在或无权限")
    
    try:
        # 同时删除相关的已放置事件
        db.query(PlacedEvent).filter(PlacedEvent.event_id == event_id).delete()
        db.delete(event)
        db.commit()
        
        return {"success": True, "message": "事件已删除"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"删除事件失败: {str(e)}")


# 获取教学计划看板（所有教师共用）
@router.get("/boards")
async def get_teaching_boards(
    board_date: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取教学计划看板（所有教师共用）"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="只有教师可以访问教学计划看板")
    
    query = db.query(TeachingBoard)
    
    if board_date:
        try:
            target_date = datetime.strptime(board_date, "%Y-%m-%d").date()
            query = query.filter(
                TeachingBoard.board_date >= target_date,
                TeachingBoard.board_date < target_date.replace(day=target_date.day + 1)
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="日期格式错误")
    
    boards = query.all()
    
    return {
        "success": True,
        "data": [
            {
                "id": board.id,
                "title": board.title,
                "description": board.description,
                "board_date": board.board_date.isoformat() if board.board_date else None,
                "view_type": board.view_type,
                "created_at": board.created_at.isoformat() if board.created_at else None
            }
            for board in boards
        ]
    }


# 创建教学计划看板（所有教师共用）
@router.post("/boards")
async def create_teaching_board(
    board_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建教学计划看板（所有教师共用）"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="只有教师可以创建教学计划看板")
    
    try:
        board_date = datetime.strptime(board_data["board_date"], "%Y-%m-%d")
        
        new_board = TeachingBoard(
            title=board_data["title"],
            description=board_data.get("description", ""),
            board_date=board_date,
            view_type=board_data.get("view_type", "day")
        )
        
        db.add(new_board)
        db.commit()
        db.refresh(new_board)
        
        return {
            "success": True,
            "data": {
                "id": new_board.id,
                "title": new_board.title,
                "description": new_board.description,
                "board_date": new_board.board_date.isoformat() if new_board.board_date else None,
                "view_type": new_board.view_type
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"创建看板失败: {str(e)}")


# 获取看板详情（包含已放置的事件）
@router.get("/boards/{board_id}")
async def get_board_detail(
    board_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取看板详情（所有教师共用）"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="只有教师可以访问教学计划看板")
    
    board = db.query(TeachingBoard).filter(
        TeachingBoard.id == board_id
    ).first()
    
    if not board:
        raise HTTPException(status_code=404, detail="看板不存在")
    
    # 获取已放置的事件
    placed_events = db.query(PlacedEvent).filter(
        PlacedEvent.board_id == board_id
    ).all()
    
    placed_events_data = []
    for placed in placed_events:
        event = placed.event
        teacher = event.teacher
        placed_events_data.append({
            "id": placed.id,
            "title": event.title,
            "description": event.description,
            "type": event.event_type,
            "duration": placed.duration,
            "startHour": placed.start_hour,
            "color": event.color,
            "teacherName": teacher.username,
            "board_date": placed.board_date.strftime("%Y-%m-%d") if placed.board_date else None,
            "position_x": placed.position_x,
            "position_y": placed.position_y
        })
    
    return {
        "success": True,
        "data": {
            "board": {
                "id": board.id,
                "title": board.title,
                "description": board.description,
                "board_date": board.board_date.isoformat() if board.board_date else None,
                "view_type": board.view_type
            },
            "placed_events": placed_events_data
        }
    }


# 放置事件到看板（所有教师共用）
@router.post("/boards/{board_id}/events")
async def place_event_on_board(
    board_id: int,
    event_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """放置事件到看板（所有教师共用）"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="只有教师可以操作看板")
    
    # 检查看板是否存在
    board = db.query(TeachingBoard).filter(
        TeachingBoard.id == board_id
    ).first()
    
    if not board:
        raise HTTPException(status_code=404, detail="看板不存在")
    
    # 检查事件是否存在
    event = db.query(TeachingEvent).filter(
        TeachingEvent.id == event_data["event_id"]
    ).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="事件不存在")
    
    # 解析日期
    board_date = None
    if "board_date" in event_data:
        try:
            board_date = datetime.strptime(event_data["board_date"], "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="日期格式错误")
    else:
        # 如果没有提供日期，使用看板的日期
        board_date = board.board_date
    
    # 检查时间冲突
    start_hour = event_data["startHour"]
    duration = event_data["duration"]
    end_hour = start_hour + duration / 60
    
    conflict = db.query(PlacedEvent).filter(
        and_(
            PlacedEvent.board_id == board_id,
            PlacedEvent.board_date == board_date,
            PlacedEvent.id != event_data.get("id"),  # 排除当前编辑的事件
            or_(
                and_(
                    PlacedEvent.start_hour < end_hour,
                    PlacedEvent.start_hour + PlacedEvent.duration / 60 > start_hour
                )
            )
        )
    ).first()
    
    if conflict:
        raise HTTPException(status_code=400, detail="该时间段已有其他事件安排")
    
    try:
        if "id" in event_data:
            # 更新已放置的事件
            placed_event = db.query(PlacedEvent).filter(
                PlacedEvent.id == event_data["id"]
            ).first()
            
            if placed_event:
                placed_event.start_hour = start_hour
                placed_event.duration = duration
                placed_event.board_date = board_date
                placed_event.position_x = event_data.get("position_x")
                placed_event.position_y = event_data.get("position_y")
                placed_event.updated_at = datetime.utcnow()
            else:
                raise HTTPException(status_code=404, detail="已放置的事件不存在")
        else:
            # 创建新的已放置事件
            placed_event = PlacedEvent(
                event_id=event_data["event_id"],
                board_id=board_id,
                start_hour=start_hour,
                duration=duration,
                board_date=board_date,
                position_x=event_data.get("position_x"),
                position_y=event_data.get("position_y")
            )
            db.add(placed_event)
        
        db.commit()
        db.refresh(placed_event)
        
        return {
            "success": True,
            "data": {
                "id": placed_event.id,
                "title": event.title,
                "description": event.description,
                "type": event.event_type,
                "duration": placed_event.duration,
                "startHour": placed_event.start_hour,
                "color": event.color,
                "teacherName": event.teacher.username,
                "board_date": placed_event.board_date.strftime("%Y-%m-%d") if placed_event.board_date else None,
                "position_x": placed_event.position_x,
                "position_y": placed_event.position_y
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"放置事件失败: {str(e)}")


# 删除已放置的事件
@router.delete("/boards/{board_id}/events/{placed_event_id}")
async def remove_event_from_board(
    board_id: int,
    placed_event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """从看板中删除已放置的事件"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="只有教师可以操作看板")
    
    placed_event = db.query(PlacedEvent).filter(
        and_(
            PlacedEvent.id == placed_event_id,
            PlacedEvent.board_id == board_id
        )
    ).first()
    
    if not placed_event:
        raise HTTPException(status_code=404, detail="已放置的事件不存在")
    
    try:
        db.delete(placed_event)
        db.commit()
        
        return {"success": True, "message": "事件已从看板中删除"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"删除事件失败: {str(e)}") 