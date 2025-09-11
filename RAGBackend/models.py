#数据库建模

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey,Text,Table,Index,Float,UniqueConstraint
from sqlalchemy.orm import relationship
import enum
from sqlalchemy.types import Enum
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=True)
    hashed_password = Column(String(128), nullable=False)
    role = Column(String(20), default="student")  # 支持student/teacher/admin
    university = Column(String(100), nullable=True)
    phone = Column(String(20), unique=True, index=True, nullable=False)
    status = Column(String(20), default="active")  # 用户状态：active/inactive
    created_at = Column(DateTime, default=datetime.utcnow)  # 注册时间
    last_login = Column(DateTime, nullable=True)  # 最后登录时间

    #教师专属字段
    title = Column(String(50), nullable=True)
    department = Column(String(100), nullable=True)
    materials = relationship("CourseMaterial", back_populates="teacher")
    courses = relationship("Course", back_populates="teacher")
    joined_courses = relationship("Course", secondary="course_students", back_populates="students")
    created_chats = relationship("CourseChat", back_populates="teacher")

class ParseStatus(enum.Enum):
    pending   = "pending"      # 刚上传，还没发送到 RagFlow
    parsing   = "parsing"      # RagFlow 接收成功，正在拆页/向量化
    parsed    = "parsed"       # 成功
    failed    = "failed"       # 解析或向量化失败


class CourseMaterial(Base):
    __tablename__ = "course_materials"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(String(1000), nullable=False)
    filename = Column(String(100), nullable=False)
    file_path = Column(Text, nullable=False)
    uploadtime = Column(DateTime, default=datetime.utcnow)

    status = Column(Enum(ParseStatus), default=ParseStatus.pending)
    rag_doc_id = Column(String(64), nullable=True)  # RagFlow返回的docId
    error_msg = Column(Text, nullable=True)  # 解析失败原因

    teacher_id = Column(Integer, ForeignKey("users.id"))
    teacher = relationship("User", back_populates="materials")

    course_id = Column(Integer, ForeignKey("courses.id"))
    course = relationship("Course", back_populates="materials")

    __table_args__ = (
        Index("ix_material_course_status", "course_id", "status"),
    )

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    cover = Column(String(255), nullable=True)  # 课程封面图片URL
    teacher_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    dataset_id = Column(String(64), nullable=True)
    dataset_name = Column(String(256), nullable=True)
    chat_id = Column(String(64), nullable=True)  # 允许为null，创建课程时可能暂时为空

    teacher = relationship("User", back_populates="courses")
    students = relationship("User", secondary="course_students", back_populates="joined_courses")

    materials = relationship("CourseMaterial",
                             back_populates="course",
                             cascade="all, delete-orphan")
    
    chats = relationship("CourseChat", back_populates="course", cascade="all, delete-orphan")


course_students = Table(
    "course_students",
    Base.metadata,
    Column("course_id", Integer, ForeignKey("courses.id")),
    Column("student_id", Integer, ForeignKey("users.id"))
)


class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)  # 教学目标、章节说明
    content = Column(Text, nullable=True)      # 生成的题目（JSON字符串或纯文本）
    answer = Column(Text, nullable=True)       # 参考答案
    course_id = Column(Integer, ForeignKey("courses.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    deadline = Column(DateTime, default=datetime.utcnow)
    creator_id = Column(String(10))

    course = relationship("Course", backref="assignments")
    questions = relationship("AssignmentQuestion", back_populates="assignment", cascade="all, delete")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(20))  # 选择题、主观题、填空题、编码
    content = Column(Text)
    points = Column(Float, default=1.0) #每道题的小分
    options = Column(Text)     # JSON string
    answer = Column(Text)      # 正确答案
    key_knowledge = Column(Text)  # 关键知识点
    difficulty = Column(String(10), default='medium')
    
    assignments = relationship("AssignmentQuestion", back_populates="question")

#作业题目关联表
class AssignmentQuestion(Base):
    __tablename__ = "assignment_questions"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    order = Column(Integer)  # 题目在作业中的顺序
    points = Column(Float, default=1.0) #每道题的小分（可以覆盖题目库中的分值）

    assignment = relationship("Assignment", back_populates="questions")
    question = relationship("Question", back_populates="assignments")

class AssignmentSubmission(Base):
    __tablename__ = "assignment_submissions"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"))
    student_id = Column(Integer, ForeignKey("users.id"))
    submit_time = Column(DateTime, default=datetime.utcnow)
    answer = Column(Text)  # 学生提交的答案
    score = Column(Float, nullable=True)  # 作业的总分
    feedback = Column(Text, nullable=True)  # AI返回的建议或错误点

    assignment = relationship("Assignment", backref="submissions")
    student = relationship("User")
    __table_args__ = (
        UniqueConstraint("student_id", "assignment_id", name="uq_sub_once"),
    )

#为每个用户在对应的课程里面创建一个单独的会话/
class CourseSession(Base):
    __tablename__ = "course_sessions"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    chat_id = Column(String(64), nullable=True)       #RAGflow创建聊天助手时返回
    session_id = Column(String(64), nullable=False)    #RAGflow创建session时返回
    created_at = Column(DateTime, default=datetime.utcnow)

    course = relationship("Course")
    user = relationship("User")

    __table_args__ = (
        UniqueConstraint("course_id", "user_id", name="uq_course_user"),
    )

#课程聊天助手模型
class CourseChat(Base):
    __tablename__ = "course_chats"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # 聊天助手名称
    description = Column(Text, nullable=True)   # 聊天助手描述
    chat_id = Column(String(64), nullable=False)  # RagFlow返回的chat_id
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 创建者ID
    chat_type = Column(String(50), nullable=False, default="general")  # 聊天助手类型
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Integer, default=1)  # 是否激活，1为激活，0为禁用

    course = relationship("Course", back_populates="chats")
    teacher = relationship("User", back_populates="created_chats")

    __table_args__ = (
        UniqueConstraint("course_id", "chat_type", name="uq_course_chat_type"),
    )

class PreparationStatus(enum.Enum):
    draft = "draft"           # 草稿
    completed = "completed"   # 已完成
    used = "used"            # 已使用

class Preparation(Base):
    __tablename__ = "preparations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)  # 教案标题
    content = Column(Text, nullable=False)       # 教案内容（Markdown格式）
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(PreparationStatus), default=PreparationStatus.draft)
    is_public = Column(Integer, default=0)       # 是否公开分享，0私有，1公开
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联关系
    course = relationship("Course", backref="preparations")
    teacher = relationship("User", backref="preparations")
    shares = relationship("PreparationShare", back_populates="preparation", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_preparation_course_teacher", "course_id", "teacher_id"),
        Index("ix_preparation_status", "status"),
        Index("ix_preparation_public", "is_public"),
    )

class PreparationShare(Base):
    __tablename__ = "preparation_shares"

    id = Column(Integer, primary_key=True, index=True)
    preparation_id = Column(Integer, ForeignKey("preparations.id"), nullable=False)
    from_teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 分享者
    to_teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)    # 接收者
    message = Column(String(500), nullable=True)  # 分享留言
    is_read = Column(Integer, default=0)          # 是否已读，0未读，1已读
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关联关系
    preparation = relationship("Preparation", back_populates="shares")
    from_teacher = relationship("User", foreign_keys=[from_teacher_id], backref="shared_preparations")
    to_teacher = relationship("User", foreign_keys=[to_teacher_id], backref="received_preparations")

    __table_args__ = (
        UniqueConstraint("preparation_id", "to_teacher_id", name="uq_preparation_share_once"),
        Index("ix_share_to_teacher", "to_teacher_id"),
        Index("ix_share_read", "is_read"),
    )

class PreparationLike(Base):
    __tablename__ = "preparation_likes"

    id = Column(Integer, primary_key=True, index=True)
    preparation_id = Column(Integer, ForeignKey("preparations.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关联关系
    preparation = relationship("Preparation")
    teacher = relationship("User")

    __table_args__ = (
        UniqueConstraint("preparation_id", "teacher_id", name="uq_preparation_like_once"),
    )


# 教学计划看板相关模型
class TeachingEvent(Base):
    __tablename__ = "teaching_events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)  # 事件标题
    description = Column(Text, nullable=True)    # 事件描述
    event_type = Column(String(50), nullable=False)  # 事件类型：lecture, lab, discussion, exam, homework, other
    duration = Column(Integer, nullable=False)   # 持续时间（分钟）
    color = Column(String(7), nullable=False)    # 事件颜色（十六进制）
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)  # 可选，关联课程
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联关系
    teacher = relationship("User", backref="teaching_events")
    course = relationship("Course", backref="teaching_events")
    placed_events = relationship("PlacedEvent", back_populates="event", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_teaching_event_teacher", "teacher_id"),
        Index("ix_teaching_event_course", "course_id"),
    )


class PlacedEvent(Base):
    __tablename__ = "placed_events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("teaching_events.id"), nullable=False)
    board_id = Column(Integer, ForeignKey("teaching_boards.id"), nullable=False)
    start_hour = Column(Float, nullable=False)   # 开始时间（小时，如8.5表示8:30）
    duration = Column(Integer, nullable=False)   # 持续时间（分钟）
    board_date = Column(DateTime, nullable=False)  # 事件发生的日期
    position_x = Column(Float, nullable=True)    # 在看板中的X位置（百分比）
    position_y = Column(Float, nullable=True)    # 在看板中的Y位置（百分比）
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联关系
    event = relationship("TeachingEvent", back_populates="placed_events")
    board = relationship("TeachingBoard", back_populates="placed_events")

    __table_args__ = (
        Index("ix_placed_event_board", "board_id"),
        Index("ix_placed_event_start_time", "board_id", "start_hour"),
        Index("ix_placed_event_date", "board_date"),
    )


class TeachingBoard(Base):
    __tablename__ = "teaching_boards"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)  # 看板标题
    description = Column(Text, nullable=True)    # 看板描述
    board_date = Column(DateTime, nullable=False)  # 看板日期
    view_type = Column(String(20), default="day")  # 视图类型：day, week, month
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联关系
    placed_events = relationship("PlacedEvent", back_populates="board", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_teaching_board_date", "board_date"),
    )

