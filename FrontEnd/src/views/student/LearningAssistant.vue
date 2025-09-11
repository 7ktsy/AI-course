<template>
  <div class="learning-assistant-page">
    <div class="page-header">
      <h1 class="page-title">
        <el-icon><ChatDotSquare /></el-icon>
        学习助手
      </h1>
      <p class="page-description">选择课程，开启个性化学习辅导</p>
    </div>

    <!-- 课程选择卡片 -->
    <div class="course-selection-container">
      <el-row :gutter="20">
        <el-col 
          v-for="course in courses" 
          :key="course.id" 
          :span="8"
          :xs="24" 
          :sm="12" 
          :md="8"
        >
          <el-card 
            class="course-card" 
            shadow="hover"
            @click="selectCourse(course)"
          >
            <div class="course-content">
              <div class="course-icon">
                <el-icon><Document /></el-icon>
              </div>
              <div class="course-info">
                <h3 class="course-name">{{ course.title }}</h3>
                <p class="course-teacher">{{ course.teacher_name || course.teacher || '未知教师' }}</p>
                <div class="course-meta">
                  <el-tag size="small" type="info">
                    <el-icon><User /></el-icon>
                    {{ course.teacher_name || course.teacher || '未知教师' }}
                  </el-tag>
                </div>
              </div>
              <div class="course-action">
                <el-button type="primary" size="small" round>
                  开始学习
                </el-button>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 空状态 -->
      <div v-if="!loading && courses.length === 0" class="empty-state">
        <el-empty description="暂无课程">
          <template #image>
            <el-icon style="font-size: 60px; color: #ddd;">
              <Document />
            </el-icon>
          </template>
          <el-button type="primary" @click="loadCourses">刷新</el-button>
        </el-empty>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <el-skeleton :rows="3" animated />
      </div>
    </div>

    <!-- 学习助手抽屉 -->
    <el-drawer
      v-model="drawerVisible"
      :title="`${selectedCourseName} - 学习助手`"
      direction="rtl"
      size="70%"
      class="learning-drawer"
    >
      <template #header="{ close, titleId, titleClass }">
        <div class="drawer-header">
          <h2 :id="titleId" :class="titleClass" class="drawer-title">
            <el-icon><ChatDotSquare /></el-icon>
            {{ selectedCourseName }} - 学习助手
          </h2>
          <div class="drawer-actions">
            <el-button 
              type="primary" 
              size="small" 
              @click="changeCourse"
              :icon="RefreshRight"
            >
              切换课程
            </el-button>
            <el-button 
              size="small" 
              @click="close"
              :icon="CloseBold"
            >
              关闭
            </el-button>
          </div>
        </div>
      </template>
      
      <div class="drawer-content">
        <div class="chat-status">
          <el-alert
            :title="`正在为您提供 ${selectedCourseName} 的学习帮助`"
            type="success"
            show-icon
            :closable="false"
          />
        </div>
        
        <div class="chat-iframe-container">
          <iframe
            ref="chatIframe"
            src="http://localhost:8080/chat/share?shared_id=ce6e1698671a11f09dbed225975ede12&from=chat&auth=FlNDlkM2MwM2UxMTExZjA5NGUxMGU0NW"
            class="chat-iframe"
            frameborder="0"
            allow="microphone; camera"
          ></iframe>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ChatDotSquare, Document, User, RefreshRight, CloseBold } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

// 响应式数据
const drawerVisible = ref(false)
const selectedCourse = ref(null)
const courses = ref([])
const loading = ref(false)

// 计算属性
const selectedCourseName = computed(() => {
  return selectedCourse.value ? selectedCourse.value.title : ''
})

// API调用函数
const api = {
  // 获取学生的课程列表
  async getStudentCourses() {
    loading.value = true
    try {
      const token = localStorage.getItem('token')
      if (!token) {
        throw new Error('未找到认证令牌，请重新登录')
      }

      console.log('发起API请求: /student/my_courses')
      
      const response = await request.get('/student/my_courses', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      })
      
      console.log('API响应数据:', response.data)
      
      if (response && response.data) {
        // 根据API返回的数组结构调整
        const coursesData = Array.isArray(response.data) ? response.data : []
        courses.value = coursesData
        console.log('成功获取课程数据:', courses.value.length, '门课程')
        
        if (coursesData.length === 0) {
          ElMessage.info('您还没有加入任何课程')
        } else {
          ElMessage.success(`已加载 ${coursesData.length} 门课程`)
        }
      } else {
        console.warn('课程列表响应格式不正确:', response)
        courses.value = []
      }
    } catch (error) {
      console.error('获取课程列表详细错误:', error)
      
      if (error.response) {
        console.log('错误响应状态:', error.response.status)
        console.log('错误响应数据:', error.response.data)
        
        if (error.response.status === 401) {
          ElMessage.error('认证失败，请重新登录')
          localStorage.removeItem('token')
        } else if (error.response.status === 403) {
          ElMessage.error('权限不足，请确认您的学生身份')
        } else if (error.response.status === 404) {
          ElMessage.error('API接口不存在，请检查后端配置')
        } else {
          ElMessage.error(error.response.data?.detail || `服务器错误 (${error.response.status})`)
        }
      } else if (error.request) {
        console.log('请求已发出但未收到响应:', error.request)
        ElMessage.error('网络连接失败，请检查网络或服务器状态')
      } else {
        ElMessage.error(error.message || '获取课程列表失败')
      }
      
      courses.value = []
    } finally {
      loading.value = false
    }
  }
}

// 方法
const loadCourses = async () => {
  await api.getStudentCourses()
}

const selectCourse = (course) => {
  selectedCourse.value = course
  drawerVisible.value = true
  ElMessage.success(`已启动 ${course.title} 学习助手`)
}

const changeCourse = () => {
  drawerVisible.value = false
  selectedCourse.value = null
  setTimeout(() => {
    // 可以滚动到课程选择区域
    const coursesContainer = document.querySelector('.course-selection-container')
    if (coursesContainer) {
      coursesContainer.scrollIntoView({ behavior: 'smooth' })
    }
  }, 300)
}

// 生命周期钩子
onMounted(async () => {
  console.log('学习助手组件已挂载，开始获取课程列表')
  await loadCourses()
})
</script>

<style scoped>
.learning-assistant-page {
  padding: 24px;
  background: #ffffff;
  min-height: calc(100vh - 140px);
}

.page-header {
  text-align: center;
  margin-bottom: 40px;
  color: #2c3e50;
}

.page-title {
  font-size: 32px;
  font-weight: 600;
  margin: 0 0 12px 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: #2c3e50;
}

.page-title .el-icon {
  font-size: 36px;
  color: #74b9ff;
}

.page-description {
  font-size: 16px;
  margin: 0;
  color: #7f8c8d;
}

.course-selection-container {
  max-width: 1200px;
  margin: 0 auto;
}

.course-card {
  margin-bottom: 20px;
  border-radius: 16px;
  transition: all 0.3s ease;
  cursor: pointer;
  border: 1px solid #e1e8ed;
  background: #ffffff;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.course-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(116, 185, 255, 0.15);
  border-color: #74b9ff;
}

.course-content {
  padding: 24px;
  text-align: center;
}

.course-icon {
  margin-bottom: 16px;
}

.course-icon .el-icon {
  font-size: 48px;
  color: #74b9ff;
  background: linear-gradient(135deg, #74b9ff, #0984e3);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.course-info {
  margin-bottom: 20px;
}

.course-name {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: #2c3e50;
}

.course-teacher {
  font-size: 14px;
  color: #7f8c8d;
  margin: 0 0 12px 0;
}

.course-meta {
  display: flex;
  justify-content: center;
  gap: 8px;
  flex-wrap: wrap;
}

.course-action {
  margin-top: 16px;
}

.course-action .el-button {
  background: linear-gradient(135deg, #74b9ff, #0984e3);
  border: none;
  padding: 8px 24px;
  font-weight: 500;
  color: white;
}

.course-action .el-button:hover {
  background: linear-gradient(135deg, #5faff9, #0770c7);
  transform: translateY(-2px);
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
  background: #f8f9fa;
  border-radius: 16px;
  border: 2px dashed #e1e8ed;
}

.loading-state {
  padding: 40px;
  background: #f8f9fa;
  border-radius: 16px;
  border: 1px solid #e1e8ed;
}

.learning-drawer {
  border-radius: 16px 0 0 16px;
  overflow: hidden;
}

:deep(.el-drawer__header) {
  padding: 0;
  margin-bottom: 0;
  border-bottom: 1px solid #f0f0f0;
}

.drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: linear-gradient(135deg, #74b9ff, #0984e3);
  color: white;
}

.drawer-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.drawer-actions {
  display: flex;
  gap: 8px;
}

.drawer-actions .el-button {
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
}

.drawer-actions .el-button:hover {
  background: rgba(255, 255, 255, 0.25);
  border-color: rgba(255, 255, 255, 0.5);
}

.drawer-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 0;
}

.chat-status {
  padding: 16px 24px;
  flex-shrink: 0;
}

.chat-iframe-container {
  flex: 1;
  padding: 0 24px 24px 24px;
  display: flex;
  flex-direction: column;
}

.chat-iframe {
  width: 100%;
  height: 100%;
  min-height: 600px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background: #f8f9fa;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .learning-assistant-page {
    padding: 16px;
  }
  
  .page-title {
    font-size: 24px;
  }
  
  .course-content {
    padding: 16px;
  }
  
  .course-icon .el-icon {
    font-size: 36px;
  }
  
  .course-name {
    font-size: 16px;
  }
  
  :deep(.el-drawer) {
    width: 95% !important;
  }
  
  .drawer-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  .drawer-actions {
    width: 100%;
    justify-content: flex-end;
  }
}

/* 美化滚动条 */
:deep(.el-drawer__body) {
  padding: 0;
}

:deep(.el-drawer__body)::-webkit-scrollbar {
  width: 6px;
}

:deep(.el-drawer__body)::-webkit-scrollbar-track {
  background: #f1f1f1;
}

:deep(.el-drawer__body)::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

:deep(.el-drawer__body)::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style> 