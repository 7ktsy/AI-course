#初始化数据库
from database import engine
from models import Base
from sqlalchemy import text

def drop_all_tables_safely():
    """安全地删除所有表，手动控制删除顺序"""
    with engine.connect() as conn:
        # 禁用外键检查
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        
        # 按照依赖关系手动删除表（从最依赖的表开始删除）
        tables_to_drop = [
            "assignment_submissions",  # 依赖 assignments
            "assignment_questions",    # 依赖 assignments 和 questions
            "course_sessions",         # 依赖 courses 和 users
            "course_chats",           # 依赖 courses 和 users
            "course_materials",        # 依赖 courses 和 users
            "course_students",         # 依赖 courses 和 users
            "assignments",            # 依赖 courses
            "questions",              # 独立表
            "courses",                # 依赖 users
            "users"                   # 基础表
        ]
        
        print("开始删除表...")
        for table in tables_to_drop:
            try:
                conn.execute(text(f"DROP TABLE IF EXISTS `{table}`"))
                print(f"✓ 删除表: {table}")
            except Exception as e:
                print(f"✗ 删除表 {table} 时出错: {e}")
        
        # 重新启用外键检查
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        conn.commit()
        print("所有表删除完成")

def create_all_tables():
    """创建所有表"""
    Base.metadata.create_all(bind=engine)
    print("所有表创建完成")

if __name__ == "__main__":
    print("开始重构数据库...")
    
    # 安全删除所有表
    drop_all_tables_safely()
    
    # 创建所有表
    create_all_tables()
    
    print("数据库重构完成！")