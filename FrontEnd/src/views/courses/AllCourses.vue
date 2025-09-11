<template>
  <div class="all-courses-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="page-title">
        <h2>全部课程</h2>
        <span class="course-count">共 {{ courses.length }} 门课程</span>
      </div>
    </div>

    <!-- 搜索区域 -->
    <div class="search-section">
      <div class="search-wrapper">
        <el-input
          v-model="searchQuery"
          placeholder="搜索课程名称、描述或教师..."
          class="search-input"
          size="large"
          clearable
          @keyup.enter="searchCourses"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button 
          type="primary" 
          size="large"
          @click="searchCourses"
          :loading="loading"
        >
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
      </div>
      <div class="search-tips">
        <span>💡 提示：输入关键词后按回车键或点击搜索按钮</span>
      </div>
    </div>

    <!-- 课程列表 -->
    <div class="course-grid">
      <div v-for="course in filteredCourses" 
           :key="course.id" 
           class="course-item">
        <div class="course-content" @click="showCourseDetail(course)">
          <!-- 课程封面 -->
          <div class="course-cover">
            <el-image
              :src="course.cover || getDefaultCover(course.title)"
              :alt="course.title"
              fit="cover"
              class="cover-image"
              :preview-src-list="[course.cover || getDefaultCover(course.title)]"
            >
              <template #error>
                <div class="cover-placeholder">
                  <el-icon><Picture /></el-icon>
                  <span>{{ course.title.charAt(0) }}</span>
                </div>
              </template>
            </el-image>
          </div>
          
          <div class="course-info">
            <h2 class="course-name">{{ course.title }}</h2>
            <p class="course-description" v-if="course.description">
              {{ course.description }}
            </p>
            <p class="course-id">ID: {{ course.id }}</p>
            <p class="course-teacher" v-if="course.teacher">
              教师: {{ course.teacher }}
            </p>
            <div class="course-status">
              <el-tag v-if="course.is_joined" type="success">已加入</el-tag>
              <el-tag v-else type="info">未加入</el-tag>
            </div>
          </div>
        </div>
        <div class="course-operations">
          <el-button-group>
            <el-button 
              v-if="!course.is_joined"
              type="primary" 
              @click.stop="joinCourse(course)"
            >
              <el-icon><Plus /></el-icon>
              加入课程
            </el-button>
            <el-button 
              v-else
              type="success" 
              @click.stop="enterCourse(course)"
            >
              <el-icon><View /></el-icon>
              进入课程
            </el-button>
          </el-button-group>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <el-empty 
      v-if="!courses.length && !loading"
      description="暂无课程数据，请尝试搜索"
    />

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-loading-directive></el-loading-directive>
    </div>

    <!-- 课程详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      :title="currentCourse?.title"
      width="800px"
      destroy-on-close
    >
      <div class="course-detail" v-if="currentCourse">
        <!-- 课程封面 -->
        <div class="detail-cover">
          <el-image
            :src="currentCourse.cover || getDefaultCover(currentCourse.title)"
            :alt="currentCourse.title"
            fit="cover"
            class="detail-cover-image"
            :preview-src-list="[currentCourse.cover || getDefaultCover(currentCourse.title)]"
          >
            <template #error>
              <div class="detail-cover-placeholder">
                <el-icon><Picture /></el-icon>
                <span>{{ currentCourse.title.charAt(0) }}</span>
              </div>
            </template>
          </el-image>
        </div>
        
        <div class="detail-section">
          <h3>课程描述</h3>
          <p>{{ currentCourse.description || '暂无描述' }}</p>
          <p class="course-id">课程ID: {{ currentCourse.id }}</p>
          <p class="course-teacher" v-if="currentCourse.teacher">
            授课教师: {{ currentCourse.teacher }}
          </p>
          <div class="course-status">
            <el-tag v-if="currentCourse.is_joined" type="success">已加入</el-tag>
            <el-tag v-else type="info">未加入</el-tag>
          </div>
        </div>

        <div class="detail-actions">
          <el-button 
            v-if="!currentCourse.is_joined"
            type="primary" 
            @click="joinCourse(currentCourse)"
          >
            <el-icon><Plus /></el-icon>
            加入课程
          </el-button>
          <el-button 
            v-else
            type="success" 
            @click="enterCourse(currentCourse)"
          >
            <el-icon><View /></el-icon>
            进入课程
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, View, Picture } from '@element-plus/icons-vue'
import request from '@/utils/request'
import { useRouter } from 'vue-router'

const router = useRouter()

// 数据定义
const courses = ref([])
const searchQuery = ref('')
const detailDialogVisible = ref(false)
const currentCourse = ref(null)
const loading = ref(false)

// 计算属性：过滤后的课程列表
const filteredCourses = computed(() => {
  if (!searchQuery.value) return courses.value
  const query = searchQuery.value.toLowerCase()
  return courses.value.filter(course => 
    course.title.toLowerCase().includes(query) ||
    (course.description && course.description.toLowerCase().includes(query)) ||
    (course.teacher && course.teacher.toLowerCase().includes(query))
  )
})

// API 调用函数
const api = {
  // 搜索全部课程
  async searchAllCourses(query = '') {
    try {
      loading.value = true
      console.log('发起课程搜索请求:', '/course/listall', '查询参数:', query)
      
      const response = await request.get('/course/listall', {
        params: query ? { q: query } : {}
      })
      
      console.log('课程搜索响应:', response)
      console.log('响应数据类型:', typeof response.data)
      console.log('响应数据:', response.data)
      
      if (response && response.data) {
        // 后端返回格式: {code: 0, data: {courses: [...]}, message: "获取成功"}
        let coursesData = response.data.data?.courses || response.data.courses || response.data
        
        if (Array.isArray(coursesData)) {
          // 转换字段名以匹配前端期望
          courses.value = coursesData.map(course => ({
            ...course,
            teacher: course.teacher_name || course.teacher, // 统一字段名
            is_joined: course.is_enrolled || course.is_joined // 统一字段名
          }))
          console.log('解析后的课程数据:', courses.value)
          ElMessage.success(`找到 ${courses.value.length} 门课程`)
        } else {
          console.error('API返回的courses不是数组:', coursesData)
          courses.value = []
          ElMessage.warning('课程数据格式异常')
        }
      } else {
        console.warn('API响应数据为空')
        courses.value = []
        ElMessage.info('未找到课程数据')
      }
    } catch (error) {
      console.error('搜索课程失败:', error)
      
      if (error.response) {
        console.log('错误响应状态:', error.response.status)
        console.log('错误响应数据:', error.response.data)
        
        if (error.response.status === 401) {
          ElMessage.error('认证失败，请重新登录')
        } else if (error.response.status === 403) {
          ElMessage.error('权限不足，无法访问课程列表')
        } else {
          ElMessage.error(error.response.data?.detail || `服务器错误 (${error.response.status})`)
        }
      } else if (error.request) {
        ElMessage.error('网络连接失败，请检查网络或服务器状态')
      } else {
        ElMessage.error(error.message || '搜索课程失败')
      }
      
      courses.value = []
    } finally {
      loading.value = false
    }
  },

  // 获取全部课程（不带搜索参数）
  async getAllCourses() {
    try {
      loading.value = true
      console.log('获取全部课程列表...')
      
      const response = await request.get('/course/listall')
      console.log('全部课程响应:', response)
      
      if (response && response.data) {
        let coursesData = response.data.data?.courses || response.data.courses || response.data
        
        if (Array.isArray(coursesData)) {
          courses.value = coursesData.map(course => ({
            ...course,
            teacher: course.teacher_name || course.teacher,
            is_joined: course.is_enrolled || course.is_joined
          }))
          console.log('获取到的全部课程:', courses.value.length, '门')
        } else {
          courses.value = []
        }
      } else {
        courses.value = []
      }
    } catch (error) {
      console.error('获取全部课程失败:', error)
      ElMessage.error('获取课程列表失败')
      courses.value = []
    } finally {
      loading.value = false
    }
  },

  // 加入课程
  async joinCourse(courseId) {
    try {
      const response = await request.post(`/student/course/${courseId}/join`)
      ElMessage.success('加入课程成功')
      return response.data
    } catch (error) {
      console.error('加入课程失败:', error)
      throw error
    }
  },

  // 获取我加入的课程ID列表（用于标记状态）
  async getMyCoursesIds() {
    try {
      console.log('获取我的课程ID列表...')
      const response = await request.get('/student/my_courses')
      console.log('我的课程响应:', response)
      
      if (response && response.data && Array.isArray(response.data)) {
        const myCoursesIds = response.data.map(course => course.id)
        console.log('我加入的课程ID列表:', myCoursesIds)
        return myCoursesIds
      }
      return []
    } catch (error) {
      console.error('获取我的课程失败:', error)
      return []
    }
  }
}

// 事件处理函数
const searchCourses = async () => {
  console.log('开始搜索课程:', searchQuery.value)
  await api.searchAllCourses(searchQuery.value)
  // 注意：后端已经在返回数据中包含了 is_enrolled 字段，无需额外调用
}

const loadAllCourses = async () => {
  console.log('加载全部课程...')
  await api.getAllCourses()
}

const joinCourse = async (course) => {
  try {
    await ElMessageBox.confirm(`确定要加入课程"${course.title}"吗？`, '确认', {
      type: 'info'
    })
    
    console.log('正在加入课程:', course.id)
    await api.joinCourse(course.id)
    
    // 更新课程状态
    course.is_joined = true
    if (currentCourse.value && currentCourse.value.id === course.id) {
      currentCourse.value.is_joined = true
    }
    
    ElMessage.success(`成功加入课程: ${course.title}`)
  } catch (error) {
    if (error !== 'cancel') {
      console.error('加入课程失败:', error)
      
      if (error.response) {
        if (error.response.status === 400) {
          ElMessage.warning('您已经加入了该课程')
          // 即使提示已加入，也更新状态
          course.is_joined = true
          if (currentCourse.value && currentCourse.value.id === course.id) {
            currentCourse.value.is_joined = true
          }
        } else {
          ElMessage.error(error.response.data?.detail || '加入课程失败')
        }
      } else {
        ElMessage.error(error.message || '加入课程失败')
      }
    }
  }
}

const enterCourse = (course) => {
  // 进入课程学习页面
  router.push(`/dashboard/course/${course.id}/learn`)
}

// 显示课程详情
const showCourseDetail = (course) => {
  console.log('显示课程详情:', course)
  currentCourse.value = course
  detailDialogVisible.value = true
}

// 工具函数
const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// 默认封面图片
const getDefaultCover = (title) => {
  // 使用一个简单的哈希函数来生成一个基础的背景色
  let hash = 0;
  for (let i = 0; i < title.length; i++) {
    hash = title.charCodeAt(i) + ((hash << 5) - hash);
  }
  const hue = Math.abs(hash) % 360; // 0-360 之间的色调
  return `https://via.placeholder.com/150x100?text=${title.substring(0, 2).toUpperCase()}&hue=${hue}`;
}

// 生命周期钩子
onMounted(async () => {
  console.log('全部课程组件已挂载，开始加载课程列表')
  await loadAllCourses()
})
</script>

<style scoped>
.all-courses-container {
  padding: 20px;
  width: 100%;
  max-width: none;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-title {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 15px;
}

.page-title h2 {
  margin: 0;
  color: #303133;
  font-size: 28px;
  font-weight: 600;
}

.course-count {
  color: #909399;
  font-size: 14px;
  background: #f5f7fa;
  padding: 4px 12px;
  border-radius: 12px;
}

.search-section {
  background: #f8f9fa;
  padding: 25px;
  border-radius: 12px;
  margin-bottom: 30px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.search-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  margin-bottom: 15px;
}

.search-input {
  width: 500px;
  max-width: 500px;
}

.search-tips {
  text-align: center;
  color: #909399;
  font-size: 13px;
}

.search-tips span {
  background: #fff;
  padding: 6px 15px;
  border-radius: 15px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.course-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-top: 20px;
  width: 90%;
}

.course-item {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  min-height: 160px;
  width: 90%;
}

.course-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.2);
}

.course-content {
  display: flex;
  gap: 15px;
  align-items: center;
  flex-grow: 1;
  margin-bottom: 10px;
}

.course-cover {
  width: 100px;
  height: 70px;
  border-radius: 6px;
  overflow: hidden;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f0f0f0; /* 默认背景色 */
}

.cover-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  background-color: #f0f0f0;
  color: #606266;
  font-size: 24px;
  font-weight: bold;
}

.course-info {
  flex-grow: 1;
}

.course-operations {
  flex-shrink: 0;
  display: flex;
  justify-content: flex-end;
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
  margin-top: auto;
}

.course-name {
  font-size: 18px;
  margin: 0 0 8px 0;
  color: #303133;
  line-height: 1.4;
}

.course-description {
  font-size: 13px;
  color: #606266;
  margin: 0 0 8px 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.course-id {
  font-size: 12px;
  color: #909399;
  margin: 0 0 4px 0;
}

.course-teacher {
  font-size: 12px;
  color: #67C23A;
  margin: 4px 0;
  font-weight: 500;
}

.course-status {
  margin-top: 8px;
}

.course-detail {
  padding: 20px;
}

.detail-cover {
  width: 100%;
  height: 150px; /* 固定高度 */
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 20px;
  background-color: #f0f0f0; /* 默认背景色 */
}

.detail-cover-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.detail-cover-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  background-color: #f0f0f0;
  color: #606266;
  font-size: 24px;
  font-weight: bold;
}

.detail-section {
  margin-bottom: 30px;
}

.detail-section h3 {
  margin-bottom: 15px;
  color: #303133;
  font-size: 18px;
}

.detail-actions {
  display: flex;
  justify-content: center;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
}

.el-empty {
  padding: 60px 0;
}

/* 响应式设计 */
@media (max-width: 1400px) {
  .course-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 18px;
  }
}

@media (max-width: 1200px) {
  .course-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }
  
  .search-input {
    width: 400px;
  }
}

@media (max-width: 768px) {
  .all-courses-container {
    padding: 15px;
  }
  
  .page-title {
    flex-direction: column;
    gap: 10px;
    align-items: center;
  }
  
  .page-title h2 {
    font-size: 24px;
  }
  
  .search-section {
    padding: 20px;
  }
  
  .search-wrapper {
    flex-direction: column;
    gap: 12px;
  }
  
  .search-input {
    width: 100%;
  }
  
  .course-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }
}

@media (max-width: 480px) {
  .search-section {
    padding: 15px;
    margin-bottom: 20px;
  }
  
  .course-item {
    padding: 12px;
    min-height: 180px;
  }
  
  .course-name {
    font-size: 16px;
  }
  
  .page-title h2 {
    font-size: 22px;
  }
}
</style>
