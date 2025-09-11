<template>
  <div class="student-course-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>我的课程</h1>
      <p>查看您加入的课程并进行学习</p>
    </div>

    <!-- 顶部操作栏 -->
    <div class="operation-bar">
      <div class="page-title">
        <span class="course-count">共 {{ courses.length }} 门课程</span>
      </div>
      <el-input
        v-model="searchQuery"
        placeholder="搜索课程..."
        class="search-input"
        clearable
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
    </div>

    <!-- 课程列表 -->
    <div class="course-grid" v-loading="loading">
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
            <p class="course-date">{{ formatDate(course.created_at) }}</p>
            <p class="course-id">ID: {{ course.id }}</p>
            <p class="course-teacher" v-if="course.teacher">
              教师: {{ course.teacher }}
            </p>
          </div>
        </div>
        <div class="course-operations">
          <el-button-group>
            <el-button 
              type="primary" 
              link
              @click.stop="enterCourse(course)"
            >
              <el-icon><View /></el-icon>
              进入课程
            </el-button>
            <el-button 
              type="danger" 
              link
              @click.stop="leaveCourse(course)"
            >
              <el-icon><Close /></el-icon>
              退出课程
            </el-button>
          </el-button-group>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <el-empty 
      v-if="!courses.length && !loading"
      description="您还没有加入任何课程"
    />

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
          <p>{{ currentCourse.description }}</p>
          <p class="course-id">课程ID: {{ currentCourse.id }}</p>
          <p class="course-teacher" v-if="currentCourse.teacher">
            授课教师: {{ currentCourse.teacher }}
          </p>
        </div>
        
        <div class="detail-section">
          <h3>课程资料</h3>
          <div class="dataset-list">
            <el-empty 
              v-if="!courseDatasets.length"
              description="暂无课程资料"
            />
            <template v-else>
              <el-table :data="courseDatasets" style="width: 100%">
                <el-table-column prop="title" label="文件名" />
                <el-table-column prop="filename" label="原始文件名" />
                <el-table-column prop="uploadtime" label="上传时间" width="180">
                  <template #default="{ row }">
                    {{ formatDate(row.uploadtime) }}
                  </template>
                </el-table-column>
                <el-table-column prop="status" label="状态" width="120">
                  <template #default="{ row }">
                    <el-tag :type="row.status === 'parsing' ? 'success' : 'danger'">
                      {{ row.status === 'parsing' ? '已解析' : '未解析' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column fixed="right" label="操作" width="120">
                  <template #default="scope">
                    <el-button 
                      link 
                      type="primary" 
                      @click.stop="downloadFile(scope.row)"
                    >
                      下载
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>

              <!-- 分页器 -->
              <div class="pagination-container">
                <el-pagination
                  v-model:current-page="pagination.currentPage"
                  v-model:page-size="pagination.pageSize"
                  :page-sizes="[5, 10, 20, 50]"
                  :total="pagination.total"
                  layout="total, sizes, prev, pager, next"
                  @size-change="handleSizeChange"
                  @current-change="handlePageChange"
                />
              </div>
            </template>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, View, Close, Picture } from '@element-plus/icons-vue'
import request from '@/utils/request'
import { useRouter } from 'vue-router'

const router = useRouter()

// 基础URL
const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// 数据定义
const courses = ref([])
const searchQuery = ref('')
const detailDialogVisible = ref(false)
const currentCourse = ref(null)
const courseDatasets = ref([])
const loading = ref(false)

// 分页相关
const pagination = ref({
  currentPage: 1,
  pageSize: 10,
  total: 0,
  totalPages: 0
})

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
  // 获取学生的课程列表
  async getStudentCourses() {
    loading.value = true
    try {
      const token = localStorage.getItem('token')
      if (!token) {
        throw new Error('未找到认证令牌，请重新登录')
      }

      console.log('发起API请求: /student/my_courses')
      console.log('使用token:', token ? token.substring(0, 20) + '...' : 'null')
      
      const response = await request.get('/student/my_courses', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      })
      
      console.log('API响应状态:', response.status)
      console.log('API响应头:', response.headers)
      console.log('API响应数据类型:', typeof response.data)
      console.log('API响应数据内容:', response.data)
      
      // 检查响应是否为HTML（说明可能被重定向）
      if (typeof response.data === 'string') {
        if (response.data.includes('<!DOCTYPE html>') || response.data.includes('<html>')) {
          console.error('收到HTML响应，可能是认证失败或路由错误')
          throw new Error('API请求被重定向到HTML页面，请检查认证状态或API配置')
        }
      }
      
      if (response && response.data) {
        // 根据API返回的数组结构调整
        const coursesData = Array.isArray(response.data) ? response.data : []
        courses.value = coursesData
        console.log('成功解析课程数据:', courses.value.length, '门课程')
        
        if (coursesData.length === 0) {
          ElMessage.info('您还没有加入任何课程')
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
          // 可以考虑跳转到登录页面
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
  },

  // 退出课程 (假设有这个接口)
  async leaveCourse(courseId) {
    try {
      const response = await request.delete(`/student/course/${courseId}/leave`)
      ElMessage.success('退出课程成功')
      return response.data
    } catch (error) {
      console.error('退出课程失败:', error)
      throw error
    }
  },

  // 获取课程资料 (学生视角)
  async getCourseDatasets(courseId, page = 1, pageSize = 10) {
    console.log('调用获取课程资料接口:', {
      courseId,
      page,
      pageSize,
      url: `${baseURL}/material/${courseId}/materials`
    })
    try {
      const response = await request.get(`${baseURL}/material/${courseId}/materials`, {
        params: {
          page,
          page_size: pageSize
        },
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Accept': 'application/json'
        }
      })
      console.log('获取课程资料响应:', response)
      if (response.data) {
        // 更新分页信息
        pagination.value = {
          currentPage: response.data.page,
          pageSize: response.data.page_size,
          total: response.data.total,
          totalPages: response.data.total_pages
        }
        courseDatasets.value = response.data.data || []
        console.log('更新后的课程资料:', courseDatasets.value)
        return response.data.data || []
      }
      return []
    } catch (error) {
      console.error('获取课程资料失败:', error)
      ElMessage.error('获取课程资料失败')
      return []
    }
  }
}

// 事件处理函数
const enterCourse = (course) => {
  // 进入课程学习页面
  router.push(`/dashboard/course/${course.id}/learn`)
}

const leaveCourse = async (course) => {
  try {
    await ElMessageBox.confirm('确定要退出该课程吗？', '警告', {
      type: 'warning'
    })
    await api.leaveCourse(course.id)
    await api.getStudentCourses() // 刷新课程列表
  } catch (error) {
    if (error !== 'cancel') {
      console.error('退出课程失败:', error)
      ElMessage.error('退出课程失败')
    }
  }
}

// 显示课程详情
const showCourseDetail = async (course) => {
  console.log('显示课程详情:', course)
  currentCourse.value = course
  detailDialogVisible.value = true
  try {
    await api.getCourseDatasets(course.id)
  } catch (error) {
    console.error('获取课程资料失败:', error)
    ElMessage.error('获取课程资料失败')
  }
}

// 下载文件
const downloadFile = async (file) => {
  try {
    const response = await request.get(`/material/download/${file.id}`, {
      responseType: 'blob'
    })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', file.filename || file.title)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('下载失败:', error)
    ElMessage.error('下载失败')
  }
}

// 处理分页变化
const handlePageChange = async (newPage) => {
  console.log('页码变化:', newPage)
  if (!currentCourse.value) return
  pagination.value.currentPage = newPage
  await api.getCourseDatasets(
    currentCourse.value.id,
    newPage,
    pagination.value.pageSize
  )
}

const handleSizeChange = async (newSize) => {
  console.log('每页数量变化:', newSize)
  if (!currentCourse.value) return
  pagination.value.pageSize = newSize
  pagination.value.currentPage = 1
  await api.getCourseDatasets(
    currentCourse.value.id,
    1,
    newSize
  )
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
  // 使用一个简单的哈希函数生成一个唯一的标识符
  let hash = 0;
  for (let i = 0; i < title.length; i++) {
    hash = title.charCodeAt(i) + ((hash << 5) - hash);
  }
  const color = `hsl(${hash % 360}, 70%, 50%)`; // 生成一个随机的颜色
  return `https://via.placeholder.com/150?text=${title.substring(0, 2)}&color=${color}`;
};

// 生命周期钩子
onMounted(async () => {
  console.log('学生课程组件已挂载，开始获取课程列表')
  await api.getStudentCourses()
})
</script>

<style scoped>
.student-course-container {
  padding: 20px;
  width: 100%;
  max-width: 1200px; /* 添加最大宽度限制，与 MyCourse 保持一致 */
  margin: 0 auto; /* 居中显示 */
}

.page-header {
  margin-bottom: 30px;
  margin-top: -10px; /* 向上移动标题 */
  text-align: center;
}

.page-header h1 {
  color: #303133;
  margin-bottom: 8px;
  margin-top: 0; /* 移除默认的上边距 */
  font-size: 28px;
  font-weight: 600;
}

.page-header p {
  color: #909399;
  font-size: 16px;
  margin-top: 0; /* 移除默认的上边距 */
}

.operation-bar {
  display: flex;
  justify-content: center; /* 修改为居中对齐 */
  align-items: center;
  margin-bottom: 20px;
  width: 100%;
  gap: 15px;
}

.page-title {
  display: flex;
  align-items: baseline;
  gap: 15px;
}

.course-count {
  color: #909399;
  font-size: 14px;
  background: #f5f7fa;
  padding: 4px 12px;
  border-radius: 12px;
}

.search-input {
  width: 300px;
  max-width: 300px;
  flex-shrink: 0;
}

.course-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 30px;
  margin-top: 20px;
  width: 90%; /* 使用90%，减少右侧空白但保留一些边距 */
  margin: 20px auto 0; /* 居中显示 */
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
  width: 90%; /* 卡片充满网格单元 */
}

.course-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.2);
}

.course-content {
  flex-grow: 1;
  margin-bottom: 10px;
  display: flex; /* 使用flex布局 */
  align-items: center; /* 垂直居中 */
  gap: 15px; /* 封面和信息之间的间距 */
}

.course-cover {
  flex-shrink: 0; /* 封面不缩放 */
  width: 100px; /* 固定封面宽度 */
  height: 100px; /* 固定封面高度 */
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.1);
}

.cover-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
  border-radius: 8px;
  color: #c0c4cc;
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

.course-date {
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

.course-detail {
  padding: 20px;
}

.detail-cover {
  width: 100%;
  height: 200px;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 20px;
  background-color: #f0f0f0;
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

.dataset-list {
  margin-top: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.el-empty {
  padding: 40px 0;
}

.course-id {
  color: #909399;
  font-size: 12px;
  margin-top: 5px;
}

/* 响应式设计 */
@media (max-width: 1400px) {
  .course-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 25px; /* 从18px增加到25px */
  }
}

@media (max-width: 1200px) {
  .course-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 25px; /* 从16px增加到25px */
  }
}

@media (max-width: 768px) {
  .student-course-container {
    padding: 15px;
  }
  
  .operation-bar {
    flex-direction: column;
    gap: 15px;
    align-items: center; /* 在移动端也保持居中 */
  }
  
  .search-input {
    width: 100%;
  }
  
  .course-grid {
    grid-template-columns: 1fr;
    gap: 20px; /* 从15px增加到20px */
  }
  
  .page-header h1 {
    font-size: 24px;
  }
}

@media (max-width: 480px) {
  .course-item {
    padding: 12px;
    min-height: 140px;
  }
  
  .course-name {
    font-size: 16px;
  }
}
</style>
