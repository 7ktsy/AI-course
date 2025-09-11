<template>
  <div class="course-management">
    <!-- 页面状态提示 -->
    <el-alert
      title="课程管理页面已就绪"
      description="您可以查看所有课程的详细信息，包括课程资料和任务"
      type="success"
      :closable="false"
      show-icon
      style="margin-bottom: 20px;"
    />
    
    <!-- 课程统计信息 -->
    <el-card class="status-card" shadow="hover">
      <template #header>
        <div class="status-header">
          <el-icon><Reading /></el-icon>
          <span>课程统计概览</span>
        </div>
      </template>
      <div class="status-content">
        <div class="status-item">
          <el-icon class="status-icon"><Reading /></el-icon>
          <div class="status-info">
            <div class="status-label">总课程数</div>
            <div class="status-value">{{ courseStats.totalCourses || 0 }}</div>
          </div>
        </div>
        <div class="status-item">
          <el-icon class="status-icon"><User /></el-icon>
          <div class="status-info">
            <div class="status-label">活跃教师</div>
            <div class="status-value">{{ courseStats.activeTeachers || 0 }}人</div>
          </div>
        </div>
        <div class="status-item">
          <el-icon class="status-icon"><Document /></el-icon>
          <div class="status-info">
            <div class="status-label">总资料数</div>
            <div class="status-value">{{ courseStats.totalMaterials || 0 }}个</div>
          </div>
        </div>
        <div class="status-item">
          <el-icon class="status-icon"><Edit /></el-icon>
          <div class="status-info">
            <div class="status-label">总任务数</div>
            <div class="status-value">{{ courseStats.totalAssignments || 0 }}个</div>
          </div>
        </div>
      </div>
    </el-card>
    
    <!-- 顶部导航栏 -->
    <div class="top-nav">
      <div class="nav-left">
        <h1 class="page-title">
          <el-icon class="title-icon"><Reading /></el-icon>
          课程管理
        </h1>
        <p class="page-subtitle">管理系统中的所有课程信息</p>
      </div>
      <div class="nav-right">
        <el-button @click="refreshData">
          <el-icon><Refresh /></el-icon> 刷新
        </el-button>
        <el-button @click="router.push('/dashboard/overallview')">
          <el-icon><Back /></el-icon> 返回总览
        </el-button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <div class="search-section">
      <el-card shadow="never" class="search-card">
        <div class="search-row">
          <el-input
            v-model="searchQuery"
            placeholder="搜索课程标题或描述"
            class="search-input"
            clearable
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          
          <el-select v-model="teacherFilter" placeholder="教师筛选" clearable @change="handleSearch">
            <el-option label="全部教师" value="" />
            <el-option 
              v-for="teacher in teacherList" 
              :key="teacher.id" 
              :label="teacher.username" 
              :value="teacher.id" 
            />
          </el-select>
          
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon> 搜索
          </el-button>
        </div>
      </el-card>
    </div>

    <!-- 课程列表 -->
    <div class="course-list-section">
      <el-card shadow="never" class="list-card">
        <template #header>
          <div class="list-header">
            <span>课程列表 ({{ totalCourses }} 门课程)</span>
            <div class="header-actions">
              <el-dropdown @command="handleExportCommand">
                <el-button size="small">
                  <el-icon><Download /></el-icon> 导出
                  <el-icon class="el-icon--right"><ArrowDown /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="courses">导出课程信息</el-dropdown-item>
                    <el-dropdown-item command="materials">导出所有资料</el-dropdown-item>
                    <el-dropdown-item command="selected">导出选中课程</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </template>

        <el-table
          :data="courses"
          v-loading="loading"
          stripe
          class="course-table"
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="55" />
          
          <el-table-column label="课程信息" min-width="250">
            <template #default="{ row }">
              <div class="course-info">
                <div class="course-title">{{ row.title }}</div>
                <div class="course-description">{{ row.description }}</div>
                <div class="course-meta">
                  <el-tag size="small" type="info">
                    <el-icon><Calendar /></el-icon>
                    {{ formatDate(row.created_at) }}
                  </el-tag>
                </div>
              </div>
            </template>
          </el-table-column>

          <el-table-column label="教师信息" width="180">
            <template #default="{ row }">
              <div class="teacher-info" v-if="row.teacher">
                <div class="teacher-name">{{ row.teacher.username }}</div>
                <div class="teacher-phone">{{ row.teacher.phone }}</div>
                <div class="teacher-university">{{ row.teacher.university }}</div>
              </div>
              <div v-else class="no-teacher">未分配教师</div>
            </template>
          </el-table-column>
          
          <el-table-column label="学生数" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="row.student_count > 0 ? 'success' : 'info'" size="small">
                {{ row.student_count }}人
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column label="资料数" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="row.materials_count > 0 ? 'warning' : 'info'" size="small">
                {{ row.materials_count }}个
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column label="任务数" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="row.assignments_count > 0 ? 'danger' : 'info'" size="small">
                {{ row.assignments_count }}个
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-tooltip content="查看详情" placement="top">
                  <el-button 
                    size="small" 
                    type="primary" 
                    @click="viewCourseDetail(row)"
                    class="action-btn"
                  >
                    <el-icon><View /></el-icon>
                    详情
                  </el-button>
                </el-tooltip>
                <el-tooltip content="查看资料" placement="top">
                  <el-button 
                    size="small" 
                    type="warning" 
                    @click="viewMaterials(row)"
                    class="action-btn"
                  >
                    <el-icon><Document /></el-icon>
                    资料
                  </el-button>
                </el-tooltip>
                <el-tooltip content="查看任务" placement="top">
                  <el-button 
                    size="small" 
                    type="danger" 
                    @click="viewAssignments(row)"
                    class="action-btn"
                  >
                    <el-icon><Edit /></el-icon>
                    任务
                  </el-button>
                </el-tooltip>
              </div>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination-wrapper">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="totalCourses"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </el-card>
    </div>

    <!-- 课程详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="课程详情"
      width="80%"
      :close-on-click-modal="false"
    >
      <CourseDetail 
        v-if="selectedCourse" 
        :course="selectedCourse" 
        @close="detailDialogVisible = false"
      />
    </el-dialog>

    <!-- 资料列表对话框 -->
    <el-dialog
      v-model="materialsDialogVisible"
      title="课程资料"
      width="70%"
      :close-on-click-modal="false"
    >
      <CourseMaterials 
        v-if="selectedCourse" 
        :course="selectedCourse" 
        @close="materialsDialogVisible = false"
      />
    </el-dialog>

    <!-- 任务列表对话框 -->
    <el-dialog
      v-model="assignmentsDialogVisible"
      title="课程任务"
      width="70%"
      :close-on-click-modal="false"
    >
      <CourseAssignments 
        v-if="selectedCourse" 
        :course="selectedCourse" 
        @close="assignmentsDialogVisible = false"
      />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  Reading, Refresh, Back, Search, Download, View, Document, Edit,
  Calendar, User, Plus, Setting, ArrowDown
} from '@element-plus/icons-vue'
import CourseDetail from './components/CourseDetail.vue'
import CourseMaterials from './components/CourseMaterials.vue'
import CourseAssignments from './components/CourseAssignments.vue'
import { exportCourses as exportCoursesData } from '@/utils/exportUtils'

// 获取router实例
const router = useRouter()

// 获取用户信息和token
const token = localStorage.getItem('token')
const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')

// 响应式数据
const loading = ref(false)
const courses = ref([])
const teacherList = ref([])
const selectedCourse = ref(null)
const detailDialogVisible = ref(false)
const materialsDialogVisible = ref(false)
const assignmentsDialogVisible = ref(false)
const selectedCourses = ref([]) // 添加选中课程数组

// 搜索和筛选
const searchQuery = ref('')
const teacherFilter = ref('')

// 分页
const currentPage = ref(1)
const pageSize = ref(20)
const totalCourses = ref(0)

// 统计信息
const courseStats = ref({
  totalCourses: 0,
  activeTeachers: 0,
  totalMaterials: 0,
  totalAssignments: 0
})

// API调用函数
const apiCall = async (url, options = {}) => {
  const token = localStorage.getItem('token')
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    }
  }
  
  const response = await fetch(`http://127.0.0.1:8000${url}`, {
    ...defaultOptions,
    ...options
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || '请求失败')
  }
  
  return response.json()
}

// 方法
const loadCourses = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams({
      page: currentPage.value.toString(),
      per_page: pageSize.value.toString()
    })
    
    if (searchQuery.value) params.append('search', searchQuery.value)
    if (teacherFilter.value) params.append('teacher_id', teacherFilter.value)
    
    const response = await apiCall(`/user/admin/courses?${params}`)
    courses.value = response.data.courses || []
    totalCourses.value = response.data.total || 0
    
    // 更新统计信息
    updateCourseStats()
  } catch (error) {
    ElMessage.error('加载课程列表失败')
    console.error('Load courses error:', error)
  } finally {
    loading.value = false
  }
}

const loadTeachers = async () => {
  try {
    // 使用更简单的API调用，避免复杂的查询参数
    const response = await apiCall('/user/admin/users?per_page=1000')
    // 在前端过滤教师角色
    teacherList.value = (response.data.users || []).filter(user => user.role === 'teacher')
  } catch (error) {
    console.error('Load teachers error:', error)
    // 如果加载失败，设置为空数组，避免页面崩溃
    teacherList.value = []
    //ElMessage.warning('教师列表加载失败，筛选功能可能受限')
  }
}

const updateCourseStats = () => {
  courseStats.value = {
    totalCourses: totalCourses.value,
    activeTeachers: new Set(courses.value.map(c => c.teacher?.id).filter(Boolean)).size,
    totalMaterials: courses.value.reduce((sum, c) => sum + c.materials_count, 0),
    totalAssignments: courses.value.reduce((sum, c) => sum + c.assignments_count, 0)
  }
}

const refreshData = () => {
  loadCourses()
  loadTeachers()
}

const handleSearch = () => {
  currentPage.value = 1
  loadCourses()
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  loadCourses()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  loadCourses()
}

const viewCourseDetail = async (course) => {
  try {
    const response = await apiCall(`/user/admin/courses/${course.id}`)
    selectedCourse.value = response.data
    detailDialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取课程详情失败')
    console.error('Get course detail error:', error)
  }
}

const viewMaterials = (course) => {
  selectedCourse.value = course
  materialsDialogVisible.value = true
}

const viewAssignments = (course) => {
  selectedCourse.value = course
  assignmentsDialogVisible.value = true
}

const handleExportCommand = (command) => {
  try {
    if (command === 'courses') {
      const count = exportCoursesData(courses.value, '课程管理')
      ElMessage.success(`成功导出 ${count} 门课程信息`)
    } else if (command === 'materials') {
      // 导出所有资料的逻辑
      ElMessage.info('导出所有资料功能待实现')
    } else if (command === 'selected') {
      // 导出选中课程
      if (selectedCourses.value.length === 0) {
        ElMessage.warning('请先选择要导出的课程')
        return
      }
      const count = exportCoursesData(selectedCourses.value, '选中课程')
      ElMessage.success(`成功导出 ${count} 门选中课程信息`)
    }
  } catch (error) {
    ElMessage.error('导出失败：' + error.message)
  }
}

const handleSelectionChange = (selection) => {
  selectedCourses.value = selection
  console.log('Selected courses:', selection)
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('zh-CN')
}

// 生命周期
onMounted(() => {
  loadCourses()
  loadTeachers()
})
</script>

<style scoped>
.course-management {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.top-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.nav-left {
  display: flex;
  flex-direction: column;
}

.page-title {
  display: flex;
  align-items: center;
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.title-icon {
  margin-right: 8px;
  color: #409eff;
}

.page-subtitle {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.nav-right {
  display: flex;
  gap: 12px;
}

.search-section {
  margin-bottom: 20px;
}

.search-card {
  border: none;
}

.search-row {
  display: flex;
  gap: 16px;
  align-items: center;
}

.search-input {
  flex: 1;
  max-width: 300px;
}

.course-list-section {
  margin-bottom: 20px;
}

.list-card {
  border: none;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.course-table {
  margin-bottom: 20px;
}

.course-table :deep(.el-table__header) {
  background-color: #f8f9fa;
}

.course-table :deep(.el-table__header th) {
  background-color: #f8f9fa;
  color: #606266;
  font-weight: 600;
  border-bottom: 2px solid #e4e7ed;
}

.course-table :deep(.el-table__row:hover) {
  background-color: #f5f7fa;
}

.course-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.course-title {
  font-weight: 600;
  color: #303133;
  font-size: 16px;
}

.course-description {
  color: #606266;
  font-size: 14px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.course-meta {
  display: flex;
  gap: 8px;
}

.teacher-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.teacher-name {
  font-weight: 600;
  color: #303133;
}

.teacher-phone {
  font-size: 12px;
  color: #909399;
}

.teacher-university {
  font-size: 12px;
  color: #909399;
}

.no-teacher {
  color: #909399;
  font-style: italic;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

/* 状态卡片样式 */
.status-card {
  margin-bottom: 20px;
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.status-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #303133;
}

.status-header .el-icon {
  color: #409eff;
}

.status-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  transition: all 0.3s ease;
}

.status-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.status-icon {
  font-size: 20px;
  color: #409eff;
  background: #e6f7ff;
  padding: 8px;
  border-radius: 6px;
}

.status-info {
  flex: 1;
}

.status-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
  font-weight: 500;
}

.status-value {
  font-size: 18px;
  color: #303133;
  font-weight: 600;
}

/* 操作按钮样式 */
.action-buttons {
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: center;
}

.action-btn {
  padding: 6px 12px;
  border-radius: 6px;
  transition: all 0.3s ease;
  min-width: 60px;
  height: 32px;
}

.action-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.action-btn .el-icon {
  font-size: 14px;
  margin-right: 4px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .course-management {
    padding: 10px;
  }
  
  .top-nav {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .search-row {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-input {
    max-width: none;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 4px;
  }
}
</style> 