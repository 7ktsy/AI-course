from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from models import User
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
from typing import Optional

router = APIRouter()
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT配置
SECRET_KEY = "your-secret-key-here"  # 在生产环境中应该使用环境变量
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class UserCreate(BaseModel):
    username: str
    password: str
    phone: str
    role: str = "student"
    university: str = ""
    title: str = ""
    department: str = ""

class UserLogin(BaseModel):
    phone: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    university: Optional[str] = None
    title: Optional[str] = None
    department: Optional[str] = None
    status: Optional[str] = None

class AdminUserCreate(BaseModel):
    username: str
    password: str
    phone: str
    role: str = "student"
    university: str = ""
    title: str = ""
    department: str = ""
    status: str = "active"

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user

@router.post("/register", response_model=dict)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # 检查手机号是否已存在
    existing_user = db.query(User).filter(User.phone == user_data.phone).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="手机号已注册")
    
    # 创建新用户
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        hashed_password=hashed_password,
        phone=user_data.phone,
        role=user_data.role,
        university=user_data.university,
        title=user_data.title,
        department=user_data.department
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {
        "code": 0,
        "message": "注册成功",
        "data": {
            "id": db_user.id,
            "username": db_user.username,
            "phone": db_user.phone,
            "role": db_user.role
        }
    }

@router.post("/login", response_model=dict)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    # 查找用户
    user = db.query(User).filter(User.phone == user_data.phone).first()
    if not user:
        raise HTTPException(status_code=400, detail="用户不存在")
    
    # 验证密码
    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="密码错误")
    
    # 验证码验证已被禁用
    # if not check_captcha(user_data.phone, user_data.captcha):
    #     raise HTTPException(status_code=400, detail="验证码错误")
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return {
        "code": 0,
        "message": "登录成功",
        "data": {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "phone": user.phone,
                "role": user.role,
                "university": user.university,
                "title": user.title,
                "department": user.department
            }
        }
    }

@router.get("/me", response_model=dict)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return {
        "code": 0,
        "message": "获取成功",
        "data": {
            "id": current_user.id,
            "username": current_user.username,
            "phone": current_user.phone,
            "role": current_user.role,
            "university": current_user.university,
            "title": current_user.title,
            "department": current_user.department
        }
    }

@router.get("/students", response_model=dict)
def get_all_students(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取所有学生列表（仅教师可访问）"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="仅教师可查看学生列表")
    
    students = db.query(User).filter(User.role == "student").all()
    return {
        "code": 0,
        "message": "获取成功",
        "data": {
            "students": [
                {
                    "id": student.id,
                    "username": student.username,
                    "phone": student.phone,
                    "university": student.university,
                    "department": student.department,
                    "title": student.title
                }
                for student in students
            ]
        }
    }

@router.get("/teachers", response_model=dict)
def get_all_teachers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取所有教师列表（仅教师可访问）"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="仅教师可查看教师列表")
    
    teachers = db.query(User).filter(User.role == "teacher").all()
    return {
        "code": 0,
        "message": "获取成功",
        "data": {
            "teachers": [
                {
                    "id": teacher.id,
                    "username": teacher.username,
                    "phone": teacher.phone,
                    "university": teacher.university,
                    "title": teacher.title,
                    "department": teacher.department
                }
                for teacher in teachers
            ]
        }
    }
