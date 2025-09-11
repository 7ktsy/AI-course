<template>
  <div class="class-management-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>班级管理</h1>
      <p>管理您的班级和学生</p>
    </div>

    <!-- 搜索栏 -->
    <div class="search-section">
      <el-input
        v-model="searchQuery"
        placeholder="搜索课程..."
        class="search-input"
        clearable
        @input="filterCourses"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
    </div>

    <!-- 课程列表 -->
    <div class="courses-section">
      <el-card v-if="loading" class="loading-card">
        <div class="loading-content">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>加载中...</span>
        </div>
      </el-card>

      <div v-else-if="filteredCourses.length === 0" class="empty-state">
        <el-empty description="暂无课程">
          <el-button type="primary" @click="goToCreateCourse">创建课程</el-button>
        </el-empty>
      </div>

      <div v-else class="courses-grid">
        <el-card 
          v-for="course in filteredCourses" 
          :key="course.id" 
          class="course-card"
          shadow="hover"
          @click="goToCourseDetail(course)"
        >
          <div class="course-header">
            <h3 class="course-title">{{ course.title }}</h3>
            <el-tag type="info" size="small">ID: {{ course.id }}</el-tag>
          </div>
          
          <div class="course-info">
            <p class="course-description">{{ course.description || '暂无描述' }}</p>
            <div class="course-stats">
              <div class="stat-item">
                <el-icon><User /></el-icon>
                <span>学生人数: {{ course.student_count || 0 }}</span>
              </div>
              <div class="stat-item">
                <el-icon><Calendar /></el-icon>
                <span>创建时间: {{ formatDate(course.created_at) }}</span>
              </div>
            </div>
          </div>

          <div class="course-actions">
            <el-button 
              type="primary" 
              size="small"
              @click.stop="goToCourseDetail(course)"
            >
              <el-icon><Setting /></el-icon>
              管理学生
            </el-button>
            <el-button 
              type="success" 
              size="small"
              @click.stop="viewStudents(course)"
            >
              <el-icon><View /></el-icon>
              查看学生
            </el-button>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 学生查看对话框 -->
    <el-dialog
      v-model="studentsDialogVisible"
      :title="`${currentCourse?.title} - 学生列表`"
      width="600px"
      destroy-on-close
    >
      <div v-if="studentsLoading" class="dialog-loading">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>加载学生列表...</span>
      </div>
      
      <div v-else>
        <div class="students-summary">
          <p>共有 <strong>{{ students.length }}</strong> 名学生</p>
        </div>
        
        <el-table :data="students" style="width: 100%" max-height="400">
          <el-table-column prop="id" label="学号" width="80" />
          <el-table-column prop="username" label="姓名" />
          <el-table-column prop="phone" label="联系方式" />
          <el-table-column label="操作" width="100">
            <template #default="scope">
              <el-button 
                type="danger" 
                size="small" 
                link
                @click="removeStudent(scope.row)"
              >
                移除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <template #footer>
        <el-button @click="studentsDialogVisible = false">关闭</el-button>
        <el-button 
          type="primary" 
          @click="goToCourseDetail(currentCourse)"
        >
          管理学生
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Search, 
  Loading, 
  User, 
  Calendar, 
  Setting, 
  View 
} from '@element-plus/icons-vue'
import request from '@/utils/request'

const router = useRouter()

// 响应式数据
const loading = ref(false)
const studentsLoading = ref(false)
const searchQuery = ref('')
const courses = ref([])
const students = ref([])
const studentsDialogVisible = ref(false)
const currentCourse = ref(null)

// 计算属性：过滤后的课程列表
const filteredCourses = computed(() => {
  if (!searchQuery.value) return courses.value
  const query = searchQuery.value.toLowerCase()
  return courses.value.filter(course => 
    course.title.toLowerCase().includes(query) ||
    (course.description && course.description.toLowerCase().includes(query))
  )
})

// API 调用函数
const api = {
  // 获取教师的所有课程
  async getCourses() {
    try {
      loading.value = true
      const response = await request.get('/course/my')
      
      if (response?.data?.code === 0 && response?.data?.data?.courses) {
        // 为每个课程获取学生数量
        const coursesWithStudentCount = await Promise.all(
          response.data.data.courses.map(async (course) => {
            try {
              const studentsResponse = await request.get(`/course/${course.id}/students`)
              const studentCount = studentsResponse?.data?.data?.students?.length || 0
              return {
                ...course,
                student_count: studentCount
              }
            } catch (error) {
              console.warn(`获取课程 ${course.id} 学生数量失败:`, error)
              return {
                ...course,
                student_count: 0
              }
            }
          })
        )
        
        courses.value = coursesWithStudentCount
        console.log('获取到的课程列表:', courses.value)
      } else {
        courses.value = []
      }
    } catch (error) {
      console.error('获取课程列表失败:', error)
      ElMessage.error('获取课程列表失败')
      courses.value = []
    } finally {
      loading.value = false
    }
  },

  // 获取课程学生列表
  async getCourseStudents(courseId) {
    try {
      studentsLoading.value = true
      const response = await request.get(`/course/${courseId}/students`)
      
      if (response?.data?.code === 0 && response?.data?.data?.students) {
        students.value = response.data.data.students
        console.log('获取到的学生列表:', students.value)
      } else {
        students.value = []
      }
    } catch (error) {
      console.error('获取学生列表失败:', error)
      ElMessage.error('获取学生列表失败')
      students.value = []
    } finally {
      studentsLoading.value = false
    }
  },

  // 从课程中移除学生
  async removeStudentFromCourse(courseId, studentId) {
    try {
      const response = await request.delete(`/course/${courseId}/students/${studentId}`)
      if (response?.data?.code === 0) {
        ElMessage.success('移除学生成功')
        return true
      } else {
        throw new Error(response?.data?.message || '移除学生失败')
      }
    } catch (error) {
      console.error('移除学生失败:', error)
      ElMessage.error('移除学生失败')
      return false
    }
  }
}

// 事件处理函数
const goToCourseDetail = (course) => {
  console.log('跳转到课程详情页:', course)
  router.push(`/dashboard/class-management/${course.id}`)
}

const goToCreateCourse = () => {
  router.push('/dashboard/courses')
}

const viewStudents = async (course) => {
  console.log('查看学生列表:', course)
  currentCourse.value = course
  studentsDialogVisible.value = true
  await api.getCourseStudents(course.id)
}

const removeStudent = async (student) => {
  if (!currentCourse.value) return

  try {
    await ElMessageBox.confirm(
      `确定要从课程"${currentCourse.value.title}"中移除学生"${student.username}"吗？`,
      '确认移除',
      { type: 'warning' }
    )

    const success = await api.removeStudentFromCourse(currentCourse.value.id, student.id)
    if (success) {
      // 重新获取学生列表
      await api.getCourseStudents(currentCourse.value.id)
      // 更新课程的学生数量
      const courseIndex = courses.value.findIndex(c => c.id === currentCourse.value.id)
      if (courseIndex !== -1) {
        courses.value[courseIndex].student_count = Math.max(0, courses.value[courseIndex].student_count - 1)
      }
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('移除学生失败:', error)
      ElMessage.error('移除学生失败')
    }
  }
}

const filterCourses = () => {
  // 搜索功能通过计算属性实现，这里可以添加其他逻辑
}

const formatDate = (dateString) => {
  if (!dateString) return '未知'
  try {
    return new Date(dateString).toLocaleDateString('zh-CN')
  } catch (error) {
    return '未知'
  }
}

// 生命周期
onMounted(() => {
  api.getCourses()
})
</script>

<style scoped>
.class-management-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
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

.search-section {
  margin-bottom: 30px;
  display: flex;
  justify-content: center;
}

.search-input {
  max-width: 400px;
}

.courses-section {
  min-height: 400px;
}

.loading-card {
  text-align: center;
  padding: 40px;
}

.loading-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  font-size: 16px;
  color: #909399;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}

.courses-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.course-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 12px;
}

.course-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.course-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.course-title {
  color: #303133;
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  flex: 1;
  margin-right: 10px;
}

.course-info {
  margin-bottom: 20px;
}

.course-description {
  color: #606266;
  font-size: 14px;
  margin-bottom: 15px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.course-stats {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #909399;
}

.course-actions {
  display: flex;
  gap: 10px;
  padding-top: 15px;
  border-top: 1px solid #f0f0f0;
}

.dialog-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 40px;
  font-size: 16px;
  color: #909399;
}

.students-summary {
  margin-bottom: 15px;
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 6px;
  text-align: center;
}

.students-summary strong {
  color: #409eff;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .courses-grid {
    grid-template-columns: 1fr;
  }
  
  .course-actions {
    flex-direction: column;
  }
  
  .course-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>
