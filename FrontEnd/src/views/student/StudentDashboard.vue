<template>
  <div class="student-dashboard">
    <!-- 欢迎卡片 -->
    <el-card class="welcome-card" shadow="hover">
      <div class="welcome-content">
        <div class="welcome-left">
          <h2>👨‍🎓 欢迎回来，{{ userInfo.username }}</h2>
          <p class="welcome-subtitle">📅 今天是 {{ currentDate }}，继续您的学习之旅！</p>
          <div class="quick-stats">
            <div class="stat-item">
              <span class="stat-number">{{ statistics.totalCourses }}</span>
              <span class="stat-label">我的课程</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">{{ statistics.pendingHomework }}</span>
              <span class="stat-label">待完成作业</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">{{ statistics.completedTasks }}</span>
              <span class="stat-label">已完成任务</span>
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
      <!-- 左侧：课程和进度 -->
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
                    {{ course.status === 'active' ? '进行中' : '已完成' }}
                  </el-tag>
                  <span class="course-progress">进度: {{ course.progress }}%</span>
                </div>
              </div>
              <div class="course-progress-bar">
                <el-progress 
                  :percentage="course.progress" 
                  :color="progressColor"
                  :stroke-width="8"
                />
              </div>
            </div>
          </div>
        </el-card>

        <el-card class="panel-card" shadow="hover">
          <template #header>
            <div class="panel-header">
              <el-icon><Document /></el-icon>
              <span>最近作业</span>
            </div>
          </template>
          <div class="homework-list">
            <div 
              v-for="homework in recentHomework" 
              :key="homework.id"
              class="homework-item"
              @click="navigateToHomework(homework.id)"
            >
              <div class="homework-info">
                <h4 class="homework-title">{{ homework.title }}</h4>
                <p class="homework-course">{{ homework.courseName }}</p>
                <div class="homework-meta">
                  <el-tag 
                    size="small" 
                    :type="homework.status === 'pending' ? 'warning' : 'success'"
                  >
                    {{ homework.status === 'pending' ? '待完成' : '已完成' }}
                  </el-tag>
                  <span class="homework-deadline">截止: {{ homework.deadline }}</span>
                </div>
              </div>
              <el-icon class="arrow-icon"><ArrowRight /></el-icon>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 右侧：学习统计和快速操作 -->
      <div class="right-panel">
        <el-card class="panel-card" shadow="hover">
          <template #header>
            <div class="panel-header">
              <el-icon><TrendCharts /></el-icon>
              <span>学习统计</span>
            </div>
          </template>
          <div class="learning-stats">
            <div class="stat-card">
              <div class="stat-icon study-time">
                <span class="emoji-icon">⏰</span>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ statistics.studyTime }}h</div>
                <div class="stat-label">本周学习时长</div>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon completion-rate">
                <span class="emoji-icon">✅</span>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ statistics.completionRate }}%</div>
                <div class="stat-label">任务完成率</div>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon average-score">
                <span class="emoji-icon">🏆</span>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ statistics.averageScore }}</div>
                <div class="stat-label">平均成绩</div>
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
              @click="navigateTo('/dashboard/student/real-time-practice')"
            >
              <span class="emoji-icon">🎯</span>
              开始练习
            </el-button>
            <el-button 
              class="action-btn"
              @click="navigateTo('/dashboard/learning-assistant')"
            >
              <span class="emoji-icon">🤖</span>
              AI学习助手
            </el-button>
            <el-button 
              class="action-btn"
              @click="navigateTo('/dashboard/my-homework')"
            >
              <span class="emoji-icon">📋</span>
              我的作业
            </el-button>
            <el-button 
              class="action-btn"
              @click="navigateTo('/dashboard/grades')"
            >
              <span class="emoji-icon">📊</span>
              成绩查询
            </el-button>
          </div>
        </el-card>

        <el-card class="panel-card" shadow="hover">
          <template #header>
            <div class="panel-header">
              <el-icon><Bell /></el-icon>
              <span>学习提醒</span>
            </div>
          </template>
          <div class="reminders-list">
            <div 
              v-for="reminder in learningReminders" 
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
  Reading, Document, ArrowRight, TrendCharts, Clock, Check, Star,
  Operation, VideoPlay, ChatDotRound, DataAnalysis, Bell
} from '@element-plus/icons-vue'

export default {
  name: 'StudentDashboard',
  components: {
    Reading, Document, ArrowRight, TrendCharts, Clock, Check, Star,
    Operation, VideoPlay, ChatDotRound, DataAnalysis, Bell
  },
  setup() {
    const router = useRouter()
    const userInfo = ref({})

    // 统计数据
    const statistics = ref({
      totalCourses: 5,
      pendingHomework: 3,
      completedTasks: 12,
      studyTime: 24,
      completionRate: 85,
      averageScore: 88.5
    })

    // 我的课程
    const myCourses = ref([
      {
        id: 1,
        name: '计算机网络',
        description: '计算机网络基础知识，包括物理层、数据链路层、网络层、传输层、应用层等',
        status: 'active',
        progress: 85
      },
      {
        id: 2,
        name: '软件工程导论',
        description: '软件工程导论基础知识，包括软件工程概述、软件生命周期、软件开发模型等',
        status: 'active',
        progress: 65
      },
      {
        id: 3,
        name: '数据库系统原理',
        description: '数据库系统原理基础知识，包括关系数据库、SQL语言、数据库设计等',
        status: 'active',
        progress: 55
      }
    ])

    // 最近作业
    const recentHomework = ref([
      {
        id: 1,
        title: '计算机网络作业第三章',
        courseName: '计算机网络',
        status: 'pending',
        deadline: '2025-07-25'
      },
      {
        id: 2,
        title: '软件工程导论作业第二章',
        courseName: '软件工程导论',
        status: 'completed',
        deadline: '2025-07-25'
      },
      {
        id: 3,
        title: '数据库系统原理作业第三章',
        courseName: '数据库系统原理',
        status: 'pending',
        deadline: '2025-07-25'
      }
    ])

    // 学习提醒
    const learningReminders = ref([
      {
        id: 1,
        title: '计算机网络作业即将截止',
        time: '2小时后',
        emoji: '⏰'
      },
      {
        id: 2,
        title: '软件工程导论作业即将截止',
        time: '明天 14:00',
        emoji: '📝'
      },
      {
        id: 3,
        title: '编程项目提交提醒',
        time: '3天后',
        emoji: '💻'
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

    const progressColor = computed(() => {
      return ['#67C23A', '#409EFF', '#E6A23C']
    })

    // 方法
    const navigateTo = (path) => {
      router.push(path)
    }

    const navigateToCourse = (courseId) => {
      router.push(`/dashboard/courses/${courseId}`)
    }

    const navigateToHomework = (homeworkId) => {
      router.push(`/dashboard/homework-detail/${homeworkId}`)
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
      recentHomework,
      learningReminders,
      currentDate,
      progressColor,
      navigateTo,
      navigateToCourse,
      navigateToHomework
    }
  }
}
</script>

<style scoped>
.student-dashboard {
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

/* .user-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: 600;
} */

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
  margin-bottom: 12px;
}

.course-progress {
  color: #909399;
  font-size: 12px;
}

.course-progress-bar {
  margin-top: 8px;
}

/* 作业列表 */
.homework-list {
  padding: 24px;
}

.homework-item {
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

.homework-item:hover {
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.homework-title {
  color: #303133;
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 4px 0;
}

.homework-course {
  color: #606266;
  font-size: 12px;
  margin: 0 0 8px 0;
}

.homework-meta {
  display: flex;
  gap: 12px;
  align-items: center;
}

.homework-deadline {
  color: #909399;
  font-size: 12px;
}

.arrow-icon {
  color: #c0c4cc;
  font-size: 16px;
}

/* 学习统计 */
.learning-stats {
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

.stat-icon.study-time {
  background: #f8f9fa;
  border: 2px solid #e9ecef;
}

.stat-icon.completion-rate {
  background: #f8f9fa;
  border: 2px solid #e9ecef;
}

.stat-icon.average-score {
  background: #f8f9fa;
  border: 2px solid #e9ecef;
}

.stat-icon .emoji-icon {
  font-size: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
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

.action-btn .emoji-icon {
  font-size: 18px;
  margin-right: 8px;
}

/* 学习提醒 */
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

.reminder-icon .emoji-icon {
  font-size: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
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
  .student-dashboard {
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
  
  .panel-header {
    padding: 16px 20px;
  }
  
  .courses-list, .homework-list, .learning-stats, .quick-actions, .reminders-list {
    padding: 20px;
  }
}
</style> 