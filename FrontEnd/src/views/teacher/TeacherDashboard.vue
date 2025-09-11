<template>
  <div class="teacher-dashboard">
    <!-- 欢迎卡片 -->
    <el-card class="welcome-card" shadow="hover">
      <div class="welcome-content">
        <div class="welcome-left">
          <h2>👨‍🏫 欢迎回来，{{ userInfo.username }} 老师</h2>
          <p class="welcome-subtitle">📅 今天是 {{ currentDate }}，继续您的教学工作！</p>
          <div class="quick-stats">
            <div class="stat-item">
              <span class="stat-number">{{ statistics.totalCourses }}</span>
              <span class="stat-label">我的课程</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">{{ statistics.totalStudents }}</span>
              <span class="stat-label">学生总数</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">{{ statistics.pendingAssignments }}</span>
              <span class="stat-label">待批改作业</span>
            </div>
          </div>
        </div>
        <!-- <div class="welcome-right">
          <el-avatar :size="80" class="user-avatar">{{ userInfo.username?.charAt(0) }}</el-avatar>
        </div> -->
      </div>
    </el-card>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 左侧：课程管理和学生统计 -->
      <div class="left-panel">
        <el-card class="panel-card" shadow="hover">
          <template #header>
            <div class="panel-header">
              <el-icon><Reading /></el-icon>
              <span>我的课程</span>
            </div>
          </template>
          <div class="courses-list">
            <div 
              v-for="course in myCourses" 
              :key="course.id"
              class="course-item"
              @click="navigateToCourse(course.id)"
            >
              <div class="course-info">
                <h4 class="course-name">{{ course.name }}</h4>
                <p class="course-desc">{{ course.description }}</p>
                <div class="course-meta">
                  <el-tag size="small" :type="course.status === 'active' ? 'success' : 'info'">
                    {{ course.status === 'active' ? '进行中' : '已结束' }}
                  </el-tag>
                  <span class="course-students">{{ course.studentCount }}名学生</span>
                </div>
              </div>
              <div class="course-actions">
                <el-button size="small" @click.stop="navigateToClassManagement(course.id)">
                  班级管理
                </el-button>
                <el-button size="small" type="primary" @click.stop="navigateToPreparation(course.id)">
                  智能备课
                </el-button>
              </div>
            </div>
          </div>
        </el-card>

        <el-card class="panel-card" shadow="hover">
          <template #header>
            <div class="panel-header">
              <el-icon><Document /></el-icon>
              <span>待处理事项</span>
            </div>
          </template>
          <div class="todo-list">
            <div 
              v-for="todo in pendingTodos" 
              :key="todo.id"
              class="todo-item"
              @click="navigateToTodo(todo)"
            >
              <div class="todo-info">
                <h4 class="todo-title">{{ todo.title }}</h4>
                <p class="todo-desc">{{ todo.description }}</p>
                <div class="todo-meta">
                  <el-tag 
                    size="small" 
                    :type="todo.priority === 'high' ? 'danger' : todo.priority === 'medium' ? 'warning' : 'info'"
                  >
                    {{ todo.priority === 'high' ? '紧急' : todo.priority === 'medium' ? '重要' : '普通' }}
                  </el-tag>
                  <span class="todo-deadline">截止: {{ todo.deadline }}</span>
                </div>
              </div>
              <el-icon class="arrow-icon"><ArrowRight /></el-icon>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 右侧：教学统计和快速操作 -->
      <div class="right-panel">
        <el-card class="panel-card" shadow="hover">
          <template #header>
            <div class="panel-header">
              <el-icon><TrendCharts /></el-icon>
              <span>教学统计</span>
            </div>
          </template>
          <div class="teaching-stats">
            <div class="stat-card">
              <div class="stat-icon lesson-count">
                <span class="emoji-icon">📖</span>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ statistics.lessonCount }}</div>
                <div class="stat-label">本周授课</div>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon student-engagement">
                <span class="emoji-icon">🎯</span>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ statistics.studentEngagement }}%</div>
                <div class="stat-label">学生参与度</div>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon satisfaction-rate">
                <span class="emoji-icon">⭐</span>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ statistics.satisfactionRate }}</div>
                <div class="stat-label">满意度评分</div>
              </div>
            </div>
          </div>
        </el-card>

        <el-card class="panel-card" shadow="hover">
          <template #header>
            <div class="panel-header">
              <el-icon><Operation /></el-icon>
              <span>快速操作</span>
            </div>
          </template>
          <div class="quick-actions">
            <el-button 
              type="primary" 
              class="action-btn"
              @click="navigateTo('/dashboard/preparation')"
            >
              <span class="emoji-icon">✏️</span>
              智能备课
            </el-button>
            <el-button 
              class="action-btn"
              @click="navigateTo('/dashboard/ai-question-generator')"
            >
              <span class="emoji-icon">🤖</span>
              AI出题
            </el-button>
            <el-button 
              class="action-btn"
              @click="navigateTo('/dashboard/teaching-plan-board')"
            >
              <span class="emoji-icon">📋</span>
              教学计划看板
            </el-button>
            <el-button 
              class="action-btn"
              @click="navigateTo('/dashboard/homework-list')"
            >
              <span class="emoji-icon">📝</span>
              作业管理
            </el-button>
            <el-button 
              class="action-btn"
              @click="navigateTo('/dashboard/question-bank')"
            >
              <span class="emoji-icon">📚</span>
              题库管理
            </el-button>
          </div>
        </el-card>

        <el-card class="panel-card" shadow="hover">
          <template #header>
            <div class="panel-header">
              <el-icon><Bell /></el-icon>
              <span>教学提醒</span>
            </div>
          </template>
          <div class="reminders-list">
            <div 
              v-for="reminder in teachingReminders" 
              :key="reminder.id"
              class="reminder-item"
            >
              <div class="reminder-icon">
                <span class="emoji-icon">{{ reminder.emoji }}</span>
              </div>
              <div class="reminder-content">
                <div class="reminder-title">{{ reminder.title }}</div>
                <div class="reminder-time">{{ reminder.time }}</div>
              </div>
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { 
  Reading, Document, ArrowRight, TrendCharts, User, Star,
  Operation, Edit, MagicStick, Collection, Bell
} from '@element-plus/icons-vue'

export default {
  name: 'TeacherDashboard',
  components: {
    Reading, Document, ArrowRight, TrendCharts, User, Star,
    Operation, Edit, MagicStick, Collection, Bell
  },
  setup() {
    const router = useRouter()
    const userInfo = ref({})

    // 统计数据
    const statistics = ref({
      totalCourses: 4,
      totalStudents: 156,
      pendingAssignments: 8,
      lessonCount: 12,
      studentEngagement: 92,
      satisfactionRate: 4.8
    })

    // 我的课程
    const myCourses = ref([
      {
        id: 1,
        name: '计算机网络',
        description: '计算机网络基础知识，包括物理层、数据链路层、网络层、传输层、应用层等',
        status: 'active',
        studentCount: 44
      },
      {
        id: 2,
        name: '软件工程导论',
        description: '软件工程导论基础知识，包括软件工程概述、软件生命周期、软件开发模型等',
        status: 'active',
        studentCount: 38
      },
      {
        id: 3,
        name: '英语口语提升',
        description: '实用英语口语训练',
        status: 'active',
        studentCount: 32
      },
      {
        id: 4,
        name: '物理实验课程',
        description: '基础物理实验操作',
        status: 'active',
        studentCount: 41
      }
    ])

    // 待处理事项
    const pendingTodos = ref([
      {
        id: 1,
        title: '批改微积分作业',
        description: '第三章导数应用作业，共45份',
        priority: 'high',
        deadline: '2024-03-20',
        type: 'homework'
      },
      {
        id: 2,
        title: '准备编程课程教案',
        description: 'Python面向对象编程章节',
        priority: 'medium',
        deadline: '2024-03-22',
        type: 'preparation'
      },
      {
        id: 3,
        title: '英语口语考试安排',
        description: '期中口语测试时间安排',
        priority: 'medium',
        deadline: '2024-03-25',
        type: 'exam'
      }
    ])

    // 教学提醒
    const teachingReminders = ref([
      {
        id: 1,
        title: '微积分课程即将开始',
        time: '30分钟后',
        emoji: '📚'
      },
      {
        id: 2,
        title: '编程作业截止提醒',
        time: '明天 18:00',
        emoji: '⏰'
      },
      {
        id: 3,
        title: '教学研讨会',
        time: '后天 14:00',
        emoji: '👥'
      }
    ])

    // 计算属性
    const currentDate = computed(() => {
      return new Date().toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        weekday: 'long'
      })
    })

    // 方法
    const navigateTo = (path) => {
      router.push(path)
    }

    const navigateToCourse = (courseId) => {
      router.push(`/dashboard/courses/${courseId}`)
    }

    const navigateToClassManagement = (courseId) => {
      router.push(`/dashboard/class-management/${courseId}`)
    }

    const navigateToPreparation = (courseId) => {
      router.push('/dashboard/preparation')
    }

    const navigateToTodo = (todo) => {
      switch (todo.type) {
        case 'homework':
          router.push('/dashboard/homework-list')
          break
        case 'preparation':
          router.push('/dashboard/preparation')
          break
        case 'exam':
          router.push('/dashboard/ai-question-generator')
          break
        default:
          break
      }
    }

    onMounted(() => {
      const storedUserInfo = localStorage.getItem('userInfo')
      if (storedUserInfo) {
        userInfo.value = JSON.parse(storedUserInfo)
      }
    })

    return {
      userInfo,
      statistics,
      myCourses,
      pendingTodos,
      teachingReminders,
      currentDate,
      navigateTo,
      navigateToCourse,
      navigateToClassManagement,
      navigateToPreparation,
      navigateToTodo
    }
  }
}
</script>

<style scoped>
.teacher-dashboard {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* 欢迎卡片 */
.welcome-card {
  margin-bottom: 24px;
  border-radius: 12px;
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.welcome-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 0;
}

.welcome-left h2 {
  color: #303133;
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 8px 0;
}

.welcome-subtitle {
  color: #606266;
  font-size: 14px;
  margin: 0 0 20px 0;
}

.quick-stats {
  display: flex;
  gap: 24px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 24px;
  font-weight: 700;
  color: #409eff;
  line-height: 1;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.user-avatar {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
  font-weight: 600;
}

/* 主要内容区域 */
.main-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
}

.left-panel, .right-panel {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.panel-card {
  border-radius: 12px;
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  background: white;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  padding: 20px 24px;
  border-bottom: 1px solid #f0f0f0;
  background: #fafbfc;
}

.panel-header .el-icon {
  color: #409eff;
  font-size: 20px;
}

/* 课程列表 */
.courses-list {
  padding: 24px;
}

.course-item {
  padding: 20px;
  border: 1px solid #e9ecef;
  border-radius: 12px;
  margin-bottom: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #f8f9fa;
}

.course-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.course-info {
  margin-bottom: 16px;
}

.course-name {
  color: #303133;
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 8px 0;
}

.course-desc {
  color: #606266;
  font-size: 14px;
  margin: 0 0 12px 0;
}

.course-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.course-students {
  color: #909399;
  font-size: 12px;
}

.course-actions {
  display: flex;
  gap: 8px;
}

/* 待处理事项 */
.todo-list {
  padding: 24px;
}

.todo-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border: 1px solid #e9ecef;
  border-radius: 12px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #f8f9fa;
}

.todo-item:hover {
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.todo-title {
  color: #303133;
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 4px 0;
}

.todo-desc {
  color: #606266;
  font-size: 12px;
  margin: 0 0 8px 0;
}

.todo-meta {
  display: flex;
  gap: 12px;
  align-items: center;
}

.todo-deadline {
  color: #909399;
  font-size: 12px;
}

.arrow-icon {
  color: #c0c4cc;
  font-size: 16px;
}

/* 教学统计 */
.teaching-stats {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 12px;
  border: 1px solid #e9ecef;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
}

.stat-icon.lesson-count {
  background: #f8f9fa;
  border: 2px solid #e9ecef;
}

.stat-icon.student-engagement {
  background: #f8f9fa;
  border: 2px solid #e9ecef;
}

.stat-icon.satisfaction-rate {
  background: #f8f9fa;
  border: 2px solid #e9ecef;
}

.stat-content {
  flex: 1;
}

.stat-content .stat-number {
  font-size: 20px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 4px;
}

.stat-content .stat-label {
  font-size: 12px;
  color: #606266;
}

/* 快速操作 */
.quick-actions {
  padding: 24px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px;
  height: auto;
  border-radius: 12px;
  font-weight: 500;
}

.action-btn .el-icon {
  font-size: 20px;
}

/* 教学提醒 */
.reminders-list {
  padding: 24px;
}

.reminder-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.reminder-item:last-child {
  border-bottom: none;
}

.reminder-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.reminder-content {
  flex: 1;
}

.reminder-title {
  color: #303133;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 4px;
}

.reminder-time {
  color: #909399;
  font-size: 12px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .main-content {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .teacher-dashboard {
    padding: 16px;
  }
  
  .welcome-content {
    flex-direction: column;
    text-align: center;
    gap: 20px;
  }
  
  .quick-stats {
    justify-content: center;
  }
  
  .quick-actions {
    grid-template-columns: 1fr;
  }
  
  .course-actions {
    flex-direction: column;
  }
  
  .panel-header {
    padding: 16px 20px;
  }
  
  .courses-list, .todo-list, .teaching-stats, .quick-actions, .reminders-list {
    padding: 20px;
  }
}

.stat-icon .emoji-icon {
  font-size: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

.action-btn .emoji-icon {
  font-size: 18px;
  margin-right: 8px;
}

.reminder-icon .emoji-icon {
  font-size: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}
</style> 