# 创建课程管理组件
<template>
  <div class="courses-container">
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
    <el-row :gutter="20" class="course-list">
      <el-col :span="8" v-for="course in filteredCourses" :key="course.id">
        <el-card class="course-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <h3>{{ course.name }}</h3>
              <div class="header-actions">
                <el-dropdown trigger="click" @command="(cmd) => handleCommand(cmd, course)">
                  <el-button type="primary" text>
                    <el-icon><More /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="edit">编辑课程</el-dropdown-item>
                      <el-dropdown-item command="students">学生管理</el-dropdown-item>
                      <el-dropdown-item command="delete" divided>删除课程</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>
          </template>
          <div class="course-info">
            <p><el-icon><Calendar /></el-icon> 创建时间：{{ formatDate(course.created_at) }}</p>
            <p><el-icon><User /></el-icon> 教师：{{ course.teacher_name }}</p>
            <p><el-icon><UserFilled /></el-icon> 学生数：{{ course.student_count || 0 }}</p>
            <p class="course-description">{{ course.description }}</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

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

    <!-- 学生管理对话框 -->
    <el-dialog
      v-model="studentsDialogVisible"
      title="学生管理"
      width="600px"
    >
      <div class="students-dialog-content">
        <div class="add-students">
          <el-input
            v-model="newStudents"
            type="textarea"
            rows="4"
            placeholder="请输入学生学号，多个学号用逗号或换行分隔"
          />
          <el-button type="primary" @click="handleAddStudents">添加学生</el-button>
        </div>
        <div class="students-list">
          <h4>当前学生列表</h4>
          <el-table :data="currentCourseStudents" height="250">
            <el-table-column prop="student_id" label="学号" width="120" />
            <el-table-column prop="name" label="姓名" />
            <el-table-column prop="department" label="院系" />
          </el-table>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, More, Calendar, User, UserFilled } from '@element-plus/icons-vue'
import request from '@/utils/request'  // 使用配置好的 axios 实例

// 数据定义
const courses = ref([])
const searchQuery = ref('')
const dialogVisible = ref(false)
const studentsDialogVisible = ref(false)
const isEditing = ref(false)
const currentCourse = ref(null)
const currentCourseStudents = ref([])
const newStudents = ref('')

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

// 计算属性：过滤后的课程列表
const filteredCourses = computed(() => {
  if (!searchQuery.value) return courses.value
  const query = searchQuery.value.toLowerCase()
  return courses.value.filter(course => 
    course.name.toLowerCase().includes(query) ||
    course.description.toLowerCase().includes(query)
  )
})

// API 调用函数
const api = {
  // 获取我的课程列表
  async getMyCourses() {
    try {
      const response = await request.get('/course/my')
      console.log('课程列表响应:', response) // 添加调试日志
      if (response && response.data) {
        courses.value = Array.isArray(response.data) ? response.data : []
      } else {
        console.warn('课程列表响应格式不正确:', response)
        courses.value = []
      }
    } catch (error) {
      console.error('获取课程列表失败:', error)
      ElMessage.error(error.message || '获取课程列表失败')
      courses.value = [] // 出错时设置为空数组
    }
  },

  // 创建课程
  async createCourse(courseData) {
    try {
      const response = await request.post('/course/create', courseData)
      ElMessage.success('创建课程成功')
      return response.data
    } catch (error) {
      console.error('创建课程失败:', error)
      throw error
    }
  },

  // 更新课程
  async updateCourse(courseId, courseData) {
    if (!courseId) {
      throw new Error('课程ID不能为空')
    }
    try {
      const response = await request.put(`/course/course/${courseId}`, courseData)
      ElMessage.success('更新课程成功')
      return response.data
    } catch (error) {
      console.error('更新课程失败:', error)
      throw error
    }
  },

  // 删除课程
  async deleteCourse(courseId) {
    if (!courseId) {
      throw new Error('课程ID不能为空')
    }
    try {
      await request.delete(`/course/${courseId}`)
      ElMessage.success('删除课程成功')
    } catch (error) {
      console.error('删除课程失败:', error)
      throw error
    }
  },

  // 获取课程学生列表
  async getCourseStudents(courseId) {
    if (!courseId) {
      throw new Error('课程ID不能为空')
    }
    try {
      const response = await request.get(`/course/${courseId}/students`)
      return Array.isArray(response.data) ? response.data : []
    } catch (error) {
      console.error('获取学生列表失败:', error)
      throw error
    }
  },

  // 添加学生到课程
  async addStudentsToCourse(courseId, students) {
    if (!courseId) {
      throw new Error('课程ID不能为空')
    }
    try {
      await request.post(`/course/${courseId}/add_students`, { students })
      ElMessage.success('添加学生成功')
    } catch (error) {
      console.error('添加学生失败:', error)
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
    case 'students':
      try {
        currentCourseStudents.value = await api.getCourseStudents(course.id)
        studentsDialogVisible.value = true
      } catch (error) {
        console.error('获取学生列表失败:', error)
        ElMessage.error('获取学生列表失败')
      }
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

const handleAddStudents = async () => {
  if (!newStudents.value.trim()) {
    ElMessage.warning('请输入学生学号')
    return
  }

  if (!currentCourse.value || !currentCourse.value.id) {
    ElMessage.error('当前课程信息不完整')
    return
  }

  try {
    const students = newStudents.value
      .split(/[,\n]/)
      .map(s => s.trim())
      .filter(s => s)
    
    await api.addStudentsToCourse(currentCourse.value.id, students)
    currentCourseStudents.value = await api.getCourseStudents(currentCourse.value.id)
    newStudents.value = ''
  } catch (error) {
    console.error('添加学生失败:', error)
    ElMessage.error('添加学生失败')
  }
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

// 生命周期钩子
onMounted(async () => {
  console.log('组件已挂载，开始获取课程列表')
  await api.getMyCourses()
})
</script>

<style scoped>
.courses-container {
  padding: 20px;
}

.operation-bar {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.search-input {
  width: 300px;
}

.course-list {
  margin-top: 20px;
}

.course-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.course-info {
  color: #606266;
}

.course-info p {
  margin: 8px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.course-description {
  margin-top: 15px;
  color: #909399;
  font-size: 14px;
  line-height: 1.4;
}

.students-dialog-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.add-students {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.students-list h4 {
  margin-bottom: 10px;
}

:deep(.el-card__header) {
  padding: 15px 20px;
  border-bottom: 1px solid #ebeef5;
}

:deep(.el-card__body) {
  padding: 20px;
}
</style> 