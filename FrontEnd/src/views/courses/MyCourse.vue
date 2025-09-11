<template>
  <div class="my-course-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>课程管理</h1>
      <p>查看您的课程并上传资料</p>
    </div>
    <!-- 顶部操作栏 -->
    <div class="operation-bar">
      <el-button type="primary" @click="showCreateDialog">
        <el-icon><Plus /></el-icon>创建课程
      </el-button>
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
            <p class="course-date">{{ formatDate(course.created_at) }}</p>
            <p class="course-id">ID: {{ course.id }}</p>
          </div>
        </div>
        <div class="course-operations">
          <el-button-group>
            <el-button 
              type="primary" 
              link
              @click.stop="handleCommand('edit', course)"
            >
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button 
              type="danger" 
              link
              @click.stop="handleCommand('delete', course)"
            >
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </el-button-group>
        </div>
      </div>
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
          <p>{{ currentCourse.description }}</p>
          <p class="course-id">课程ID: {{ currentCourse.id }}</p>
        </div>
        
        <div class="detail-section">
          <h3>课程资料</h3>
          <div class="dataset-upload">
            <el-upload
              :action="`${baseURL}/material/${currentCourse.id}/upload`"
              :headers="uploadHeaders"
              :on-success="handleUploadSuccess"
              :on-error="handleUploadError"
              :before-upload="handleBeforeUpload"
              :data="uploadData"
              multiple
            >
              <el-button type="primary">上传资料</el-button>
              <template #tip>
                <div class="el-upload__tip">
                  支持任意格式文件，每个文件不超过50MB
                </div>
              </template>
            </el-upload>
          </div>
          
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
                <el-table-column fixed="right" label="操作" width="200">
                  <template #default="scope">
                    <div class="operation-buttons">
                      <el-button 
                        v-if="scope.row.status === 'pending' || scope.row.status === 'failed'"
                        link 
                        type="primary" 
                        @click.stop="handleDocumentAction(scope.row, 'parse')"
                      >
                        开始解析
                      </el-button>
                      <el-button 
                        v-if="scope.row.status === 'parsing'"
                        link 
                        type="warning" 
                        @click.stop="handleDocumentAction(scope.row, 'stop')"
                      >
                        取消解析
                      </el-button>
                      <el-button 
                        link 
                        type="info" 
                        @click.stop="handleDocumentAction(scope.row, 'refresh')"
                      >
                        刷新状态
                      </el-button>
                      <el-tooltip 
                        v-if="scope.row.error_msg" 
                        :content="scope.row.error_msg"
                        placement="top"
                      >
                        <el-icon class="error-icon"><Warning /></el-icon>
                      </el-tooltip>
                    </div>
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

    <!-- 创建/编辑课程对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEditing ? '编辑课程' : '创建课程'"
      width="500px"
    >
      <el-form
        ref="courseFormRef"
        :model="courseForm"
        :rules="courseRules"
        label-width="100px"
      >
        <el-form-item label="课程名称" prop="name">
          <el-input v-model="courseForm.name" placeholder="请输入课程名称" />
        </el-form-item>
        <el-form-item label="课程描述" prop="description">
          <el-input
            v-model="courseForm.description"
            type="textarea"
            rows="3"
            placeholder="请输入课程描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSaveCourse">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Warning, Edit, Delete, Picture } from '@element-plus/icons-vue'
import request from '@/utils/request'

// 基础URL
const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// 数据定义
const courses = ref([])
const searchQuery = ref('')
const dialogVisible = ref(false)
const isEditing = ref(false)
const currentCourse = ref(null)

// 表单相关
const courseFormRef = ref(null)
const courseForm = ref({
  name: '',
  description: ''
})
const courseRules = {
  name: [{ required: true, message: '请输入课程名称', trigger: 'blur' }],
  description: [{ required: true, message: '请输入课程描述', trigger: 'blur' }]
}

// 新增的数据
const detailDialogVisible = ref(false)
const courseDatasets = ref([])
const uploadHeaders = computed(() => ({
  'Authorization': `Bearer ${localStorage.getItem('token')}`,
  'Accept': 'application/json'
}))

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
    course.description.toLowerCase().includes(query)
  )
})

// API 调用函数
const api = {
  // 获取我的课程列表
  async getMyCourses() {
    try {
      const response = await request.get('/course/my')
      console.log('课程列表响应:', response)
      if (response?.data?.code === 0 && response?.data?.data?.courses) {
        courses.value = response.data.data.courses
      } else {
        console.warn('课程列表响应格式不正确:', response)
        courses.value = []
      }
    } catch (error) {
      console.error('获取课程列表失败:', error)
      ElMessage.error(error.message || '获取课程列表失败')
      courses.value = []
    }
  },

  // 创建新课程
  async createCourse(courseData) {
    try {
      const response = await request.post('/course/create', {
        title: courseData.name,
        description: courseData.description
      })
      if (response?.data?.code === 0) {
        ElMessage.success('创建课程成功')
        return response.data.data
      } else {
        throw new Error(response?.data?.message || '创建课程失败')
      }
    } catch (error) {
      console.error('创建课程失败:', error)
      throw error
    }
  },

  // 更新课程
  async updateCourse(courseId, courseData) {
    try {
      const response = await request.put(`/course/${courseId}`, {
        title: courseData.name,
        description: courseData.description
      })
      if (response?.data?.code === 0) {
        ElMessage.success('更新课程成功')
        return response.data.data
      } else {
        throw new Error(response?.data?.message || '更新课程失败')
      }
    } catch (error) {
      console.error('更新课程失败:', error)
      throw error
    }
  },

  // 删除课程
  async deleteCourse(courseId) {
    try {
      const response = await request.delete(`/course/${courseId}`)
      if (response?.data?.code === 0) {
        ElMessage.success('删除课程成功')
      } else {
        throw new Error(response?.data?.message || '删除课程失败')
      }
    } catch (error) {
      console.error('删除课程失败:', error)
      throw error
    }
  },

  // 获取课程资料
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
  },

  // 上传课程资料
  async uploadDataset(courseId, file) {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('title', file.name)
    formData.append('description', '课程资料')
    try {
      const response = await request.post(`/material/${courseId}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      return response.data
    } catch (error) {
      console.error('上传资料失败:', error)
      throw error
    }
  },

  // 开始解析文档
  async parseDocument(courseId, documentName) {
    try {
      const response = await request.post(`/material/${courseId}/documents/${documentName}/parse`)
      ElMessage.success('开始解析文档')
      return response.data
    } catch (error) {
      console.error('开始解析文档失败:', error)
      throw error
    }
  },

  // 停止解析文档
  async stopParseDocument(courseId, documentName) {
    try {
      await request.delete(`/material/${courseId}/documents/${documentName}/parse`)
      ElMessage.success('已停止解析文档')
    } catch (error) {
      console.error('停止解析文档失败:', error)
      throw error
    }
  },

  // 获取文档解析状态
  async getDocumentStatus(courseId, documentName) {
    try {
      const response = await request.get(`/material/${courseId}/documents/${documentName}/status`)
      return response.data
    } catch (error) {
      console.error('获取文档状态失败:', error)
      throw error
    }
  }
}

// 事件处理函数
const showCreateDialog = () => {
  isEditing.value = false
  courseForm.value = { name: '', description: '' }
  dialogVisible.value = true
}

const handleCommand = async (command, course) => {
  if (!course || !course.id) {
    ElMessage.error('课程信息不完整')
    return
  }
  
  currentCourse.value = course
  switch (command) {
    case 'edit':
      isEditing.value = true
      courseForm.value = { ...course }
      dialogVisible.value = true
      break
    case 'delete':
      try {
        await ElMessageBox.confirm('确定要删除该课程吗？', '警告', {
          type: 'warning'
        })
        await api.deleteCourse(course.id)
        await api.getMyCourses() // 刷新课程列表
      } catch (error) {
        if (error !== 'cancel') {
          console.error('删除课程失败:', error)
          ElMessage.error('删除课程失败')
        }
      }
      break
  }
}

const handleSaveCourse = async () => {
  if (!courseFormRef.value) return
  
  try {
    await courseFormRef.value.validate()
    if (isEditing.value) {
      if (!currentCourse.value || !currentCourse.value.id) {
        throw new Error('当前编辑的课程信息不完整')
      }
      await api.updateCourse(currentCourse.value.id, courseForm.value)
    } else {
      await api.createCourse(courseForm.value)
    }
    dialogVisible.value = false
    await api.getMyCourses() // 刷新课程列表
  } catch (error) {
    console.error('保存课程失败:', error)
    ElMessage.error(error.message || '保存课程失败')
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

const loadCourseDatasets = async (courseId) => {
  try {
    const response = await request.get(`/course/${courseId}/datasets`)
    courseDatasets.value = response.data.datasets || []
  } catch (error) {
    console.error('获取课程资料失败:', error)
    ElMessage.error('获取课程资料失败')
  }
}

const handleUploadSuccess = async (response, file) => {
  console.log('上传成功:', response)
  ElMessage.success('上传成功')
  if (currentCourse.value) {
    await api.getCourseDatasets(currentCourse.value.id)
  }
}

const uploadData = ref({
  title: '',
  description: '课程资料'
})

const handleBeforeUpload = (file) => {
  // 使用文件名作为标题
  uploadData.value.title = file.name
  return true
}

const handleUploadError = (error) => {
  console.error('上传失败:', error)
  let errorMessage = '上传失败'
  if (error.message) {
    try {
      const errorData = JSON.parse(error.message)
      if (errorData.detail) {
        errorMessage = Array.isArray(errorData.detail) 
          ? errorData.detail.map(err => err.msg).join(', ')
          : errorData.detail
      }
    } catch (e) {
      errorMessage = error.message
    }
  }
  ElMessage.error(errorMessage)
}

const downloadFile = async (file) => {
  try {
    const response = await request.get(`/course/dataset/${file.id}/download`, {
      responseType: 'blob'
    })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', file.name)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (error) {
    console.error('下载失败:', error)
    ElMessage.error('下载失败')
  }
}

const deleteFile = async (file) => {
  try {
    await ElMessageBox.confirm('确定要删除该文件吗？', '警告', {
      type: 'warning'
    })
    await request.delete(`/course/dataset/${file.id}`)
    ElMessage.success('删除成功')
    await loadCourseDatasets(currentCourse.value.id)
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除文件失败:', error)
      ElMessage.error('删除文件失败')
    }
  }
}

// 处理文档操作
const handleDocumentAction = async (row, action) => {
  if (!currentCourse.value) return
  
  try {
    switch (action) {
      case 'parse':
        await api.parseDocument(currentCourse.value.id, row.filename)
        break
      case 'stop':
        await api.stopParseDocument(currentCourse.value.id, row.filename)
        break
      case 'refresh':
        const status = await api.getDocumentStatus(currentCourse.value.id, row.filename)
        // 更新当前文档的状态
        const index = courseDatasets.value.findIndex(item => item.id === row.id)
        if (index !== -1) {
          courseDatasets.value[index] = { ...courseDatasets.value[index], ...status }
        }
        break
    }
  } catch (error) {
    ElMessage.error(error.message || '操作失败')
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
  // 可以根据课程标题生成一个默认封面图片的URL
  // 例如，使用一个简单的文本或图标作为默认封面
  const defaultCoverUrl = 'https://via.placeholder.com/150x100?text=Course+Cover';
  return defaultCoverUrl;
}

// 生命周期钩子
onMounted(async () => {
  console.log('组件已挂载，开始获取课程列表')
  await api.getMyCourses()
})
</script>

<style scoped>
.my-course-container {
  padding: 20px;
  width: 100%;
  max-width: 1200px; /* 添加最大宽度限制，与 ClassManagement 保持一致 */
  margin: 0 auto; /* 居中显示 */
}

/* 添加页面标题样式，与 ClassManagement 保持一致 */
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
  width: 90%; /* 使用95%，减少右侧空白但保留一些边距 */
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
  gap: 15px; /* 图片和文字之间的间距 */
}

.course-cover {
  width: 100px; /* 固定封面图片宽度 */
  height: 70px; /* 固定封面图片高度 */
  flex-shrink: 0; /* 防止图片缩小 */
  border-radius: 4px;
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
  color: #c0c4cc;
  font-size: 24px;
}

.course-info {
  flex-grow: 1;
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

.course-operations {
  flex-shrink: 0;
  display: flex;
  justify-content: flex-end;
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
  margin-top: auto;
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

.dataset-upload {
  margin-bottom: 20px;
}

.dataset-list {
  margin-top: 20px;
}

.operation-buttons {
  display: flex;
  align-items: center;
  gap: 8px;
}

.error-icon {
  color: #f56c6c;
  cursor: help;
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
  .my-course-container {
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
  
  /* 添加移动端页面标题样式调整 */
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