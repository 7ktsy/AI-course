<template>
  <div class="admin-dashboard">
    <!-- 顶部导航栏 -->
    <div class="top-nav">
      <div class="nav-left">
        <h1 class="dashboard-title">
          <span class="emoji-icon">🏢</span>
          教学实训智能体系统
        </h1>
        <p class="dashboard-subtitle">📊 数据统计总览</p>
      </div>
      <div class="nav-right">
        <el-avatar :size="40" class="user-avatar">👨‍💼</el-avatar>
        <span class="user-name">系统管理员</span>
      </div>
    </div>

    <!-- 快速导航 -->
    <div class="quick-nav">
      <el-button type="primary" class="nav-btn active">
        <el-icon><House /></el-icon> 数据总览
      </el-button>
      <el-button class="nav-btn" @click="navigateTo('/dashboard/users')">
        <el-icon><User /></el-icon> 用户管理
      </el-button>
      <el-button class="nav-btn" @click="navigateTo('/dashboard/admin-courses')">
        <el-icon><Reading /></el-icon> 课程管理
      </el-button>
      <el-button class="nav-btn" @click="navigateTo('/dashboard/chat-management')">
        <el-icon><ChatDotRound /></el-icon> 聊天助手管理
      </el-button>
      <el-button class="nav-btn" @click="navigateTo('/dashboard/model-configuration')">
        <el-icon><Setting /></el-icon> 模型配置
      </el-button>
      <el-button class="nav-btn" @click="navigateTo('/dashboard/overallview')">
        <el-icon><Avatar /></el-icon> 教学管理
      </el-button>
      <el-button class="nav-btn" @click="navigateTo('/dashboard/overallview')">
        <el-icon><UserFilled /></el-icon> 学习效果
      </el-button>
      <el-button class="nav-btn" @click="navigateTo('/dashboard/overallview')">
        <el-icon><TrendCharts /></el-icon> 统计报表
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon users">
            <span class="emoji-icon">👥</span>
          </div>
          <div class="stat-details">
            <div class="stat-number">{{ totalUsers }}</div>
            <div class="stat-label">用户总数</div>
            <div class="stat-trend positive">↗ +{{ userGrowth }} 新增</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon students">
            <span class="emoji-icon">👨‍🎓</span>
          </div>
          <div class="stat-details">
            <div class="stat-number">{{ totalStudents }}</div>
            <div class="stat-label">学生总数</div>
            <div class="stat-trend positive">↗ +{{ studentGrowth }}%</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon teachers">
            <span class="emoji-icon">👨‍🏫</span>
          </div>
          <div class="stat-details">
            <div class="stat-number">{{ totalTeachers }}</div>
            <div class="stat-label">教师总数</div>
            <div class="stat-trend positive">↗ +{{ teacherGrowth }} 新增</div>
          </div>
        </div>
      </el-card>
<!-- 
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon health">
            <el-icon size="24"><CircleCheck /></el-icon>
          </div>
          <div class="stat-details">
            <div class="stat-number">{{ systemHealth }}%</div>
            <div class="stat-label">系统健康度</div>
            <div class="stat-trend success">— 优秀</div>
          </div>
        </div>
      </el-card> -->
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 左侧：教师和学生统计 -->
      <div class="left-panel">
        <el-card class="panel-card" shadow="hover">
          <template #header>
            <div class="panel-header">
              <el-icon><Avatar /></el-icon>
              <span>教师使用统计</span>
            </div>
          </template>
          <div class="stats-panel">
            <div class="stat-row">
              <div class="stat-item">
                <div class="stat-title">今日活跃</div>
                <div class="stat-value">{{ teacherStats.todayActive }}</div>
                <div class="stat-desc">登录次数</div>
              </div>
              <div class="stat-item">
                <div class="stat-title">本周活跃</div>
                <div class="stat-value">{{ teacherStats.weeklyActive }}</div>
                <div class="stat-desc">登录次数</div>
              </div>
            </div>
            <div class="stat-details">
              <div class="detail-item">
                <span class="label">教案创建:</span>
                <span class="value">{{ teacherStats.todayLessons }}</span>
              </div>
              <div class="detail-item">
                <span class="label">学生互动:</span>
                <span class="value">{{ teacherStats.todayInteractions }}</span>
              </div>
            </div>
          </div>
        </el-card>

        <el-card class="panel-card" shadow="hover">
          <template #header>
            <div class="panel-header">
              <el-icon><UserFilled /></el-icon>
              <span>学生使用统计</span>
            </div>
          </template>
          <div class="stats-panel">
            <div class="stat-row">
              <div class="stat-item">
                <div class="stat-title">今日活跃</div>
                <div class="stat-value">{{ studentStats.todayActive }}</div>
                <div class="stat-desc">登录次数</div>
              </div>
              <div class="stat-item">
                <div class="stat-title">本周活跃</div>
                <div class="stat-value">{{ studentStats.weeklyActive }}</div>
                <div class="stat-desc">登录次数</div>
              </div>
            </div>
            <div class="stat-details">
              <div class="detail-item">
                <span class="label">完成练习:</span>
                <span class="value">{{ studentStats.todayExercises }}时</span>
              </div>
              <div class="detail-item">
                <span class="label">AI问答:</span>
                <span class="value">{{ studentStats.todayQuestions }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 右侧：系统状态和实时活动 -->
      <div class="right-panel">
        <el-card class="panel-card" shadow="hover">
          <template #header>
            <div class="panel-header">
              <el-icon><CircleCheck /></el-icon>
              <span>系统健康状态</span>
            </div>
          </template>
          <div class="health-panel">
            <div class="health-circle">
              <el-progress 
                type="circle" 
                :percentage="systemHealth" 
                :color="healthColor"
                :width="100"
              />
            </div>
            <div class="health-metrics">
              <div class="metric-item">
                <span class="metric-label">API响应时间</span>
                <span class="metric-value">{{ apiResponseTime }}ms</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">并发用户数</span>
                <span class="metric-value">{{ concurrentUsers }} 用户</span>
              </div>
              <div class="metric-item error">
                <span class="metric-label">错误次数</span>
                <span class="metric-value">{{ errorCount }}</span>
              </div>
            </div>
            <el-button type="primary" @click="refreshSystemStatus" size="small">
              <el-icon><Refresh /></el-icon> 刷新状态
            </el-button>
          </div>
        </el-card>

        <el-card class="panel-card" shadow="hover">
          <template #header>
            <div class="panel-header">
              <el-icon><Bell /></el-icon>
              <span>实时活动</span>
            </div>
          </template>
          <div class="activity-list">
            <div 
              v-for="activity in realtimeActivities" 
              :key="activity.id"
              class="activity-item"
              :class="activity.type"
            >
              <div class="activity-content">
                <div class="activity-user">{{ activity.user }}</div>
                <div class="activity-action">{{ activity.action }}</div>
              </div>
              <div class="activity-time">{{ activity.time }}</div>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 底部：教学效果和课程统计 -->
    <div class="bottom-panel">
      <el-card class="panel-card" shadow="hover">
        <template #header>
          <div class="panel-header">
            <el-icon><Trophy /></el-icon>
            <span>教学效果分析</span>
          </div>
        </template>
        <div class="effectiveness-panel">
          <div class="effectiveness-score">
            <el-progress 
              type="circle" 
              :percentage="teachingEfficiency" 
              :color="efficiencyColor"
              :width="80"
            />
            <div class="score-label">综合评分</div>
          </div>
          <div class="effectiveness-metrics">
            <div class="metric">
              <span class="metric-name">课程完成率</span>
              <el-progress 
                :percentage="courseCompletionRate" 
                :color="progressColor"
                :stroke-width="8"
              />
            </div>
            <div class="metric">
              <span class="metric-name">学生满意度</span>
              <el-progress 
                :percentage="studentSatisfaction" 
                :color="progressColor"
                :stroke-width="8"
              />
            </div>
            <div class="metric">
              <span class="metric-name">教师活跃度</span>
              <el-progress 
                :percentage="teacherActivity" 
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
            <el-icon><Reading /></el-icon>
            <span>课程统计</span>
          </div>
        </template>
        <div class="course-stats">
          <div class="course-overview">
            <div class="course-item">
              <div class="course-number">{{ totalCourses }}</div>
              <div class="course-label">课程总数</div>
            </div>
            <div class="course-item">
              <div class="course-number">{{ activeCourses }}</div>
              <div class="course-label">活跃课程</div>
            </div>
            <div class="course-item">
              <div class="course-number">{{ completedCourses }}</div>
              <div class="course-label">已完成</div>
            </div>
            <div class="course-item">
              <div class="course-number">{{ newCourses }}</div>
              <div class="course-label">新增课程</div>
            </div>
          </div>
          <div class="popular-courses">
            <h4>热门课程排行</h4>
            <div 
              v-for="(course, index) in popularCourses" 
              :key="course.id"
              class="popular-course"
            >
              <el-tag :type="index < 3 ? 'success' : 'info'" size="small" class="course-rank">
                {{ index + 1 }}
              </el-tag>
              <span class="course-title">{{ course.name }}</span>
              <span class="course-students">{{ course.studentCount }}人学习</span>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { 
  DataBoard, House, User, Reading, Avatar, UserFilled, TrendCharts,
  CircleCheck, Refresh, Bell, Trophy, Star, ChatDotRound, Setting
} from '@element-plus/icons-vue'

export default {
  name: 'OverallView',
  components: {
    DataBoard, House, User, Reading, Avatar, UserFilled, TrendCharts,
    CircleCheck, Refresh, Bell, Trophy, Star, ChatDotRound, Setting
  },
  setup() {
    const router = useRouter()

    // 基础统计数据（从数据库获取）
    const totalUsers = ref(0)
    const totalStudents = ref(0)
    const totalTeachers = ref(0)
    const totalCourses = ref(0)

    // 增长数据
    const userGrowth = ref(12)
    const studentGrowth = ref(8.5)
    const teacherGrowth = ref(3)
    const systemHealth = ref(99.2)

    // 教师使用统计（模拟数据）
    const teacherStats = ref({
      todayActive: 28,
      todayLessons: 5,
      todayInteractions: 3,
      weeklyActive: 156,
      weeklyLessons: 23,
      weeklyInteractions: 15
    })

    // 学生使用统计（模拟数据）
    const studentStats = ref({
      todayActive: 67,
      todayExercises: 34,
      todayQuestions: 34,
      weeklyActive: 445,
      weeklyExercises: 567,
      weeklyQuestions: 234
    })

    // 系统健康数据
    const apiResponseTime = ref(156)
    const concurrentUsers = ref(45)
    const errorCount = ref(3)

    // 教学效果数据
    const teachingEfficiency = ref(92)
    const courseCompletionRate = ref(87)
    const studentSatisfaction = ref(94)
    const teacherActivity = ref(89)

    // 学习效果数据
    const averageScore = ref(85.3)
    const improvementRate = ref(76)
    const passRate = ref(92)

    // 学科表现数据
    const subjectPerformance = ref([
      { name: '数学', score: 88 },
      { name: '英语', score: 92 },
      { name: '物理', score: 84 },
      { name: '化学', score: 87 },
      { name: '生物', score: 90 }
    ])

    // 课程统计数据
    const activeCourses = ref(0)
    const completedCourses = ref(0)
    const newCourses = ref(0)

    // 热门课程数据
    const popularCourses = ref([
      { id: 1, name: '计算机网络', studentCount: 156 },
      { id: 2, name: '数据库管理', studentCount: 142 },
      { id: 3, name: '操作系统', studentCount: 128 },
      { id: 4, name: '数据结构', studentCount: 115 },
      { id: 5, name: '计算机组成原理', studentCount: 98 }
    ])

    // 实时活动数据
    const realtimeActivities = ref([
      { id: 1, user: '张老师', action: '创建了新教案', time: '1分钟前', type: 'teacher' },
      { id: 2, user: '李同学', action: '完成了练习', time: '2分钟前', type: 'student' },
      { id: 3, user: '王老师', action: '发布了考试', time: '3分钟前', type: 'teacher' }
    ])

    // 计算属性
    const healthColor = computed(() => {
      if (systemHealth.value >= 90) return '#67C23A'
      if (systemHealth.value >= 70) return '#E6A23C'
      return '#F56C6C'
    })

    const efficiencyColor = computed(() => {
      if (teachingEfficiency.value >= 90) return '#67C23A'
      if (teachingEfficiency.value >= 70) return '#E6A23C'
      return '#F56C6C'
    })

    const progressColor = computed(() => {
      return ['#67C23A', '#409EFF', '#E6A23C']
    })

    const subjectColor = computed(() => {
      return ['#FF9800', '#FF5722', '#9C27B0', '#2196F3', '#4CAF50']
    })

    // 从数据库获取基础统计数据
    const fetchBasicStats = async () => {
      try {
        console.log('开始获取统计数据...')
        
        // 检查token是否存在
        const token = localStorage.getItem('token')
        if (!token) {
          console.error('未找到token，使用默认值')
          setDefaultValues()
          return
        }
        
        console.log('Token存在，开始调用API...')
        
        // 调用实际的API接口
        const response = await fetch('/user/admin/basic-stats', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        })
        
        console.log('API响应状态:', response.status)
        console.log('API响应头:', response.headers)
        
        if (response.ok) {
          const data = await response.json()
          console.log('API返回数据:', data)
          
          if (data.code === 0) {
            totalUsers.value = data.data.totalUsers || 156
            totalStudents.value = data.data.totalStudents || 128
            totalTeachers.value = data.data.totalTeachers || 24
            totalCourses.value = data.data.totalCourses || 45
            activeCourses.value = data.data.activeCourses || 38
            completedCourses.value = data.data.completedCourses || 7
            newCourses.value = data.data.newCourses || 5
            console.log('统计数据更新成功')
          } else {
            console.error('API返回错误:', data.message)
            setDefaultValues()
          }
        } else {
          const errorText = await response.text()
          console.error('API请求失败:', response.status, errorText)
          setDefaultValues()
        }
      } catch (error) {
        console.error('获取统计数据失败:', error)
        setDefaultValues()
      }
    }

    // 设置默认值
    const setDefaultValues = () => {
      totalUsers.value = 156
      totalStudents.value = 128
      totalTeachers.value = 24
      totalCourses.value = 45
      activeCourses.value = 38
      completedCourses.value = 7
      newCourses.value = 5
    }

    // 刷新系统状态
    const refreshSystemStatus = () => {
      // 模拟刷新数据
      systemHealth.value = Math.floor(Math.random() * 5) + 95
      apiResponseTime.value = Math.floor(Math.random() * 50) + 120
      concurrentUsers.value = Math.floor(Math.random() * 20) + 35
      errorCount.value = Math.floor(Math.random() * 5)
    }

    // 导航到指定页面
    const navigateTo = (path) => {
      router.push(path)
    }

    onMounted(() => {
      fetchBasicStats()
    })

    return {
      totalUsers,
      totalStudents,
      totalTeachers,
      totalCourses,
      userGrowth,
      studentGrowth,
      teacherGrowth,
      systemHealth,
      teacherStats,
      studentStats,
      apiResponseTime,
      concurrentUsers,
      errorCount,
      teachingEfficiency,
      courseCompletionRate,
      studentSatisfaction,
      teacherActivity,
      averageScore,
      improvementRate,
      passRate,
      subjectPerformance,
      activeCourses,
      completedCourses,
      newCourses,
      popularCourses,
      realtimeActivities,
      healthColor,
      efficiencyColor,
      progressColor,
      subjectColor,
      refreshSystemStatus,
      navigateTo
    }
  }
}
</script>

<style scoped>
.admin-dashboard {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* 顶部导航栏 */
.top-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 30px;
  background: white;
  border-radius: 12px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid #e4e7ed;
}

.nav-left {
  flex: 1;
}

.dashboard-title {
  color: #303133;
  font-size: 24px;
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.title-icon {
  color: #409eff;
  font-size: 28px;
}

.dashboard-subtitle {
  color: #909399;
  font-size: 14px;
  margin-top: 8px;
  font-weight: 400;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #303133;
}

.user-avatar {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
  font-weight: 600;
}

.user-name {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

/* 快速导航 */
.quick-nav {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  flex-wrap: wrap;
  padding: 0 4px;
}

.nav-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  border-radius: 8px;
  font-weight: 500;
  padding: 10px 16px;
}

.nav-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.nav-btn.active {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  border-color: transparent;
  color: white;
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  transition: all 0.3s ease;
  border-radius: 12px;
  overflow: hidden;
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 24px;
}

.stat-icon {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 28px;
}

.stat-icon.users {
  background: #f8f9fa;
  border: 2px solid #e9ecef;
}

.stat-icon.students {
  background: #f8f9fa;
  border: 2px solid #e9ecef;
}

.stat-icon.teachers {
  background: #f8f9fa;
  border: 2px solid #e9ecef;
}

.stat-icon.health {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-details {
  text-align: left;
  flex: 1;
}

.stat-number {
  font-size: 32px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 8px;
  line-height: 1;
}

.stat-label {
  font-size: 16px;
  color: #606266;
  margin-bottom: 8px;
  font-weight: 500;
}

.stat-trend {
  font-size: 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 4px;
}

.stat-trend.positive {
  color: #67c23a;
}

.stat-trend.success {
  color: #67c23a;
}

/* 主要内容区域 */
.main-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

.left-panel, .right-panel {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.panel-card {
  transition: all 0.3s ease;
  border-radius: 12px;
  overflow: hidden;
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  background: white;
}

.panel-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
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

.stats-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 24px;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  gap: 20px;
}

.stat-item {
  text-align: center;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
  flex: 1;
  border: 1px solid #e9ecef;
}

.stat-title {
  color: #606266;
  font-size: 14px;
  margin-bottom: 8px;
  font-weight: 500;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #409eff;
  margin-bottom: 6px;
  line-height: 1;
}

.stat-desc {
  color: #909399;
  font-size: 12px;
  font-weight: 400;
}

.stat-details {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-top: 20px;
  border-top: 1px solid #e9ecef;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  padding: 8px 0;
  align-items: center;
}

.detail-item .label {
  color: #606266;
  font-weight: 500;
}

.detail-item .value {
  color: #303133;
  font-weight: 600;
}

/* 系统健康状态 */
.health-panel {
  text-align: center;
  padding: 24px;
}

.health-circle {
  margin-bottom: 24px;
}

.health-metrics {
  margin-bottom: 24px;
}

.metric-item {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
  align-items: center;
}

.metric-item:last-child {
  border-bottom: none;
}

.metric-item.error .metric-value {
  color: #f56c6c;
}

.metric-label {
  color: #606266;
  font-size: 14px;
  font-weight: 500;
}

.metric-value {
  color: #303133;
  font-weight: 600;
}

/* 实时活动 */
.activity-list {
  max-height: 320px;
  overflow-y: auto;
  padding: 0 24px 24px;
}

.activity-item {
  padding: 16px;
  border-radius: 12px;
  margin-bottom: 12px;
  background: #f8f9fa;
  border-left: 4px solid #409eff;
  transition: all 0.3s ease;
  border: 1px solid #e9ecef;
}

.activity-item:hover {
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.activity-item.teacher {
  border-left-color: #9c27b0;
  background: #f3e5f5;
}

.activity-item.student {
  border-left-color: #4caf50;
  background: #e8f5e8;
}

.activity-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.activity-user {
  font-weight: 600;
  color: #303133;
  font-size: 14px;
}

.activity-action {
  color: #606266;
  font-size: 13px;
}

.activity-time {
  color: #909399;
  font-size: 12px;
  text-align: right;
}

/* 底部面板 */
.bottom-panel {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

/* 教学效果分析 */
.effectiveness-panel {
  text-align: center;
  padding: 24px;
}

.effectiveness-score {
  margin-bottom: 24px;
}

.score-label {
  color: #606266;
  font-size: 14px;
  margin-top: 12px;
  font-weight: 500;
}

.effectiveness-metrics {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.metric {
  text-align: left;
}

.metric-name {
  display: block;
  color: #606266;
  font-size: 14px;
  margin-bottom: 10px;
  font-weight: 500;
}

/* 课程统计 */
.course-stats {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 24px;
}

.course-overview {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.course-item {
  text-align: center;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
  border: 1px solid #e9ecef;
}

.course-number {
  font-size: 28px;
  font-weight: 700;
  color: #9c27b0;
  margin-bottom: 8px;
  line-height: 1;
}

.course-label {
  color: #606266;
  font-size: 14px;
  font-weight: 500;
}

.popular-courses h4 {
  color: #303133;
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
}

.popular-course {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.popular-course:last-child {
  border-bottom: none;
}

.course-rank {
  min-width: 28px;
  text-align: center;
  font-weight: 600;
}

.course-title {
  flex: 1;
  color: #303133;
  font-size: 14px;
  font-weight: 500;
}

.course-students {
  color: #909399;
  font-size: 12px;
  font-weight: 400;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .main-content, .bottom-panel {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .admin-dashboard {
    padding: 16px;
  }
  
  .top-nav {
    flex-direction: column;
    gap: 16px;
    text-align: center;
    padding: 16px 20px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .course-overview {
    grid-template-columns: 1fr;
  }
  
  .quick-nav {
    justify-content: center;
  }
  
  .stat-row {
    flex-direction: column;
  }
  
  .stat-content {
    padding: 20px;
  }
  
  .panel-header {
    padding: 16px 20px;
  }
  
  .stats-panel, .course-stats, .health-panel, .effectiveness-panel {
    padding: 20px;
  }
}

/* 滚动条样式 */
.activity-list::-webkit-scrollbar {
  width: 6px;
}

.activity-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.activity-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.activity-list::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 卡片内容样式优化 */
.el-card__body {
  padding: 0;
}

.el-card__header {
  padding: 0;
  border-bottom: none;
}

/* Emoji样式 */
.dashboard-title .emoji-icon {
  font-size: 28px;
  margin-right: 12px;
}

.stat-icon .emoji-icon {
  font-size: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}
</style>