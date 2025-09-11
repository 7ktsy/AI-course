<template>
  <div class="class-manage-detail-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-button 
          type="primary" 
          link 
          @click="goBack"
          class="back-button"
        >
          <el-icon><ArrowLeft /></el-icon>
          返回班级管理
        </el-button>
        <div class="course-info">
          <h1>{{ course?.title || '加载中...' }}</h1>
          <p v-if="course?.description">{{ course.description }}</p>
          <div class="course-meta">
            <el-tag size="small">课程ID: {{ courseId }}</el-tag>
            <el-tag type="info" size="small">学生总数: {{ students.length }}</el-tag>
          </div>
        </div>
      </div>
    </div>

    <!-- 操作栏 -->
    <div class="action-bar">
      <div class="action-left">
        <el-input
          v-model="searchQuery"
          placeholder="搜索学生..."
          class="search-input"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
      <div class="action-right">
        <el-button 
          type="primary" 
          @click="showAddStudentsDialog"
        >
          <el-icon><Plus /></el-icon>
          添加学生
        </el-button>
        <el-button 
          type="success" 
          @click="refreshStudents"
          :loading="loading"
        >
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <!-- 学生列表 -->
    <div class="students-section">
      <el-card v-if="loading" class="loading-card">
        <div class="loading-content">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>加载学生列表...</span>
        </div>
      </el-card>

      <div v-else-if="filteredStudents.length === 0" class="empty-state">
        <el-empty :description="searchQuery ? '未找到匹配的学生' : '暂无学生'">
          <el-button 
            v-if="!searchQuery" 
            type="primary" 
            @click="showAddStudentsDialog"
          >
            添加学生
          </el-button>
        </el-empty>
      </div>

      <el-table 
        v-else
        :data="filteredStudents" 
        style="width: 100%"
        v-loading="loading"
      >
        <el-table-column 
          prop="id" 
          label="学号" 
          width="100"
          sortable
        />
        <el-table-column 
          prop="username" 
          label="姓名" 
          min-width="120"
          sortable
        />
        <el-table-column 
          prop="phone" 
          label="联系方式" 
          min-width="130"
        />
        <el-table-column 
          prop="university" 
          label="学校" 
          min-width="150"
          show-overflow-tooltip
        />
        <el-table-column 
          prop="department" 
          label="院系" 
          min-width="120"
          show-overflow-tooltip
        />
        <!-- <el-table-column 
          label="加入时间" 
          min-width="120"
        >
          <template #default="scope">
            <span>{{ formatJoinDate(scope.row) }}</span>
          </template>
        </el-table-column> -->
        <el-table-column 
          label="操作" 
          width="120" 
          fixed="right"
        >
          <template #default="scope">
            <el-button 
              type="danger" 
              size="small" 
              link
              @click="removeStudent(scope.row)"
            >
              <el-icon><Delete /></el-icon>
              移除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div v-if="!loading && filteredStudents.length > 0" class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.currentPage"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="filteredStudents.length"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- 添加学生对话框 -->
    <el-dialog
      v-model="addStudentsDialogVisible"
      title="添加学生到课程"
      width="800px"
      destroy-on-close
    >
      <div class="add-students-content">
        <!-- 搜索所有学生 -->
        <div class="search-section">
          <el-input
            v-model="allStudentsSearchQuery"
            placeholder="搜索学生..."
            class="search-input"
            clearable
            @input="searchAllStudents"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>

        <!-- 可添加的学生列表 -->
        <div class="available-students">
          <h4>可添加的学生 ({{ availableStudents.length }})</h4>
          
          <el-table 
            :data="paginatedAvailableStudents"
            @selection-change="handleSelectionChange"
            v-loading="allStudentsLoading"
            max-height="400"
          >
            <el-table-column type="selection" width="55" />
            <el-table-column prop="id" label="学号" width="80" />
            <el-table-column prop="username" label="姓名" min-width="100" />
            <el-table-column prop="phone" label="联系方式" min-width="120" />
            <el-table-column prop="university" label="学校" min-width="120" show-overflow-tooltip />
          </el-table>

          <!-- 分页 -->
          <el-pagination
            v-if="availableStudents.length > 10"
            v-model:current-page="availableStudentsPagination.currentPage"
            :page-size="10"
            layout="prev, pager, next"
            :total="availableStudents.length"
            small
            style="margin-top: 15px; text-align: center;"
          />
        </div>

        <!-- 选中的学生 -->
        <div v-if="selectedStudents.length > 0" class="selected-students">
          <h4>已选择的学生 ({{ selectedStudents.length }})</h4>
          <div class="selected-tags">
            <el-tag
              v-for="student in selectedStudents"
              :key="student.id"
              closable
              @close="removeFromSelection(student)"
              type="success"
            >
              {{ student.username }} ({{ student.id }})
            </el-tag>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="addStudentsDialogVisible = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="addSelectedStudents"
          :disabled="selectedStudents.length === 0"
          :loading="addingStudents"
        >
          添加选中学生 ({{ selectedStudents.length }})
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  ArrowLeft, 
  Search, 
  Plus, 
  Refresh, 
  Loading, 
  Delete 
} from '@element-plus/icons-vue'
import request from '@/utils/request'

const router = useRouter()
const route = useRoute()
const courseId = route.params.course_id

// 响应式数据
const loading = ref(false)
const allStudentsLoading = ref(false)
const addingStudents = ref(false)
const course = ref(null)
const students = ref([])
const allStudents = ref([])
const searchQuery = ref('')
const allStudentsSearchQuery = ref('')
const addStudentsDialogVisible = ref(false)
const selectedStudents = ref([])

// 分页数据
const pagination = ref({
  currentPage: 1,
  pageSize: 20
})

const availableStudentsPagination = ref({
  currentPage: 1
})

// 计算属性
const filteredStudents = computed(() => {
  if (!searchQuery.value) return students.value
  const query = searchQuery.value.toLowerCase()
  return students.value.filter(student => 
    student.username.toLowerCase().includes(query) ||
    student.phone.includes(query) ||
    student.id.toString().includes(query) ||
    (student.university && student.university.toLowerCase().includes(query)) ||
    (student.department && student.department.toLowerCase().includes(query))
  )
})

const availableStudents = computed(() => {
  // 过滤掉已经在课程中的学生
  const currentStudentIds = students.value.map(s => s.id)
  let available = allStudents.value.filter(student => 
    !currentStudentIds.includes(student.id)
  )

  // 根据搜索条件过滤
  if (allStudentsSearchQuery.value) {
    const query = allStudentsSearchQuery.value.toLowerCase()
    available = available.filter(student => 
      student.username.toLowerCase().includes(query) ||
      student.phone.includes(query) ||
      student.id.toString().includes(query) ||
      (student.university && student.university.toLowerCase().includes(query))
    )
  }

  return available
})

const paginatedAvailableStudents = computed(() => {
  const start = (availableStudentsPagination.value.currentPage - 1) * 10
  return availableStudents.value.slice(start, start + 10)
})

// API 调用函数
const api = {
  // 获取课程信息
  async getCourseInfo() {
    try {
      const response = await request.get('/course/my')
      if (response?.data?.code === 0 && response?.data?.data?.courses) {
        course.value = response.data.data.courses.find(c => c.id.toString() === courseId)
        console.log('获取到的课程信息:', course.value)
      }
    } catch (error) {
      console.error('获取课程信息失败:', error)
      ElMessage.error('获取课程信息失败')
    }
  },

  // 获取课程学生列表
  async getCourseStudents() {
    try {
      loading.value = true
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
      loading.value = false
    }
  },

  // 获取所有学生（用于添加）
  async getAllStudents() {
    try {
      allStudentsLoading.value = true
      const response = await request.get('/user/students')
      
      if (response?.data?.code === 0 && response?.data?.data?.students) {
        allStudents.value = response.data.data.students
        console.log('获取到的所有学生:', allStudents.value)
      } else {
        allStudents.value = []
      }
    } catch (error) {
      console.error('获取所有学生失败:', error)
      ElMessage.error('获取学生数据失败')
      allStudents.value = []
    } finally {
      allStudentsLoading.value = false
    }
  },

  // 添加学生到课程
  async addStudentsToCourse(studentIds) {
    try {
      addingStudents.value = true
      console.log('开始添加学生到课程:', { courseId, studentIds })
      
      const response = await request.post(`/course/${courseId}/add_students`, {
        student_ids: studentIds
      })
      
      console.log('添加学生API响应:', response)
      
      if (response?.data?.code === 0) {
        ElMessage.success('添加学生成功')
        return true
      } else {
        const errorMsg = response?.data?.message || '添加学生失败'
        console.error('API返回错误:', response?.data)
        throw new Error(errorMsg)
      }
    } catch (error) {
      console.error('添加学生失败:', error)
      console.error('错误详情:', {
        message: error.message,
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        config: error.config
      })
      // 显示具体的错误信息，而不是固定的"添加学生失败"
      const errorMessage = error.message || '添加学生失败'
      ElMessage.error(errorMessage)
      return false
    } finally {
      addingStudents.value = false
    }
  },

  // 从课程中移除学生
  async removeStudentFromCourse(studentId) {
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
const goBack = () => {
  router.push('/dashboard/class-management')
}

const refreshStudents = () => {
  api.getCourseStudents()
}

const showAddStudentsDialog = () => {
  addStudentsDialogVisible.value = true
  if (allStudents.value.length === 0) {
    api.getAllStudents()
  }
}

const handleSelectionChange = (selection) => {
  selectedStudents.value = selection
}

const removeFromSelection = (student) => {
  const index = selectedStudents.value.findIndex(s => s.id === student.id)
  if (index > -1) {
    selectedStudents.value.splice(index, 1)
  }
}

const addSelectedStudents = async () => {
  if (selectedStudents.value.length === 0) {
    ElMessage.warning('请选择要添加的学生')
    return
  }

  const studentIds = selectedStudents.value.map(s => s.id)
  const success = await api.addStudentsToCourse(studentIds)
  
  if (success) {
    addStudentsDialogVisible.value = false
    selectedStudents.value = []
    await api.getCourseStudents() // 刷新学生列表
  }
}

const removeStudent = async (student) => {
  try {
    await ElMessageBox.confirm(
      `确定要从课程"${course.value?.title}"中移除学生"${student.username}"吗？`,
      '确认移除',
      { type: 'warning' }
    )

    const success = await api.removeStudentFromCourse(student.id)
    if (success) {
      await api.getCourseStudents() // 刷新学生列表
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('移除学生失败:', error)
    }
  }
}

const searchAllStudents = () => {
  availableStudentsPagination.value.currentPage = 1
}

const handleSizeChange = (size) => {
  pagination.value.pageSize = size
}

const handleCurrentChange = (page) => {
  pagination.value.currentPage = page
}

const formatJoinDate = (student) => {
  // 这里可以根据实际数据结构调整
  return '未知'
}

// 监听路由参数变化
watch(() => route.params.course_id, (newCourseId) => {
  if (newCourseId) {
    api.getCourseInfo()
    api.getCourseStudents()
  }
})

// 生命周期
onMounted(() => {
  api.getCourseInfo()
  api.getCourseStudents()
})
</script>

<style scoped>
.class-manage-detail-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e4e7ed;
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.back-button {
  align-self: flex-start;
  font-size: 14px;
}

.course-info h1 {
  color: #303133;
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
}

.course-info p {
  color: #606266;
  margin: 0 0 15px 0;
  font-size: 14px;
  line-height: 1.5;
}

.course-meta {
  display: flex;
  gap: 10px;
}

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.action-left .search-input {
  width: 300px;
}

.action-right {
  display: flex;
  gap: 10px;
}

.students-section {
  background-color: white;
  border-radius: 8px;
  overflow: hidden;
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

.pagination-container {
  display: flex;
  justify-content: center;
  padding: 20px;
  background-color: #f8f9fa;
}

.add-students-content {
  max-height: 600px;
  overflow-y: auto;
}

.search-section {
  margin-bottom: 20px;
}

.available-students {
  margin-bottom: 20px;
}

.available-students h4 {
  margin: 0 0 15px 0;
  color: #303133;
  font-size: 16px;
}

.selected-students h4 {
  margin: 0 0 15px 0;
  color: #303133;
  font-size: 16px;
}

.selected-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .action-bar {
    flex-direction: column;
    gap: 15px;
  }
  
  .action-left .search-input {
    width: 100%;
  }
  
  .action-right {
    width: 100%;
    justify-content: center;
  }
  
  .header-left {
    gap: 10px;
  }
  
  .course-meta {
    flex-direction: column;
    gap: 5px;
  }
}
</style>
