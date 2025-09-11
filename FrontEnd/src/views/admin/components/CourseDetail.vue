<template>
  <div class="course-detail">
    <div class="detail-container">
      <!-- 课程基本信息 -->
      <el-card class="info-card" shadow="never">
        <template #header>
          <div class="card-header">
            <el-icon><Reading /></el-icon>
            <span>课程基本信息</span>
          </div>
        </template>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="课程ID">{{ course.id }}</el-descriptions-item>
          <el-descriptions-item label="课程标题">{{ course.title }}</el-descriptions-item>
          <el-descriptions-item label="课程描述" :span="2">{{ course.description }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(course.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="知识库ID">{{ course.dataset_id || '未设置' }}</el-descriptions-item>
          <el-descriptions-item label="知识库名称">{{ course.dataset_name || '未设置' }}</el-descriptions-item>
          <el-descriptions-item label="聊天助手ID">{{ course.chat_id || '未设置' }}</el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 教师信息 -->
      <el-card class="info-card" shadow="never" v-if="course.teacher">
        <template #header>
          <div class="card-header">
            <el-icon><User /></el-icon>
            <span>教师信息</span>
          </div>
        </template>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="教师ID">{{ course.teacher.id }}</el-descriptions-item>
          <el-descriptions-item label="教师姓名">{{ course.teacher.username }}</el-descriptions-item>
          <el-descriptions-item label="手机号">{{ course.teacher.phone }}</el-descriptions-item>
          <el-descriptions-item label="所属大学">{{ course.teacher.university || '未设置' }}</el-descriptions-item>
          <el-descriptions-item label="职称">{{ course.teacher.title || '未设置' }}</el-descriptions-item>
          <el-descriptions-item label="所属部门">{{ course.teacher.department || '未设置' }}</el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 学生信息 -->
      <el-card class="info-card" shadow="never">
        <template #header>
          <div class="card-header">
            <el-icon><UserFilled /></el-icon>
            <span>学生信息 ({{ course.student_count }}人)</span>
          </div>
        </template>
        <div v-if="course.students && course.students.length > 0">
          <el-table :data="course.students" stripe size="small">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="username" label="姓名" width="120" />
            <el-table-column prop="phone" label="手机号" width="140" />
            <el-table-column prop="university" label="大学" />
            <el-table-column prop="created_at" label="注册时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
          </el-table>
        </div>
        <div v-else class="empty-state">
          <el-empty description="暂无学生加入此课程" />
        </div>
      </el-card>

      <!-- 课程资料概览 -->
      <el-card class="info-card" shadow="never">
        <template #header>
          <div class="card-header">
            <el-icon><Document /></el-icon>
            <span>课程资料概览 ({{ course.materials_count }}个)</span>
          </div>
        </template>
        <div v-if="course.materials && course.materials.length > 0">
          <el-table :data="course.materials" stripe size="small">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="title" label="标题" width="200" />
            <el-table-column prop="filename" label="文件名" width="150" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">
                  {{ getStatusLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="uploadtime" label="上传时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.uploadtime) }}
              </template>
            </el-table-column>
            <el-table-column prop="rag_doc_id" label="RAG文档ID" width="120">
              <template #default="{ row }">
                {{ row.rag_doc_id || '未设置' }}
              </template>
            </el-table-column>
          </el-table>
        </div>
        <div v-else class="empty-state">
          <el-empty description="暂无课程资料" />
        </div>
      </el-card>

      <!-- 课程任务概览 -->
      <el-card class="info-card" shadow="never">
        <template #header>
          <div class="card-header">
            <el-icon><Edit /></el-icon>
            <span>课程任务概览 ({{ course.assignments_count }}个)</span>
          </div>
        </template>
        <div v-if="course.assignments && course.assignments.length > 0">
          <el-table :data="course.assignments" stripe size="small">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="title" label="标题" width="200" />
            <el-table-column prop="description" label="描述" />
            <el-table-column prop="questions_count" label="题目数" width="100" align="center">
              <template #default="{ row }">
                <el-tag size="small">{{ row.questions_count }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="submission_count" label="提交数" width="100" align="center">
              <template #default="{ row }">
                <el-tag size="small" type="success">{{ row.submission_count }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column prop="deadline" label="截止时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.deadline) }}
              </template>
            </el-table-column>
          </el-table>
        </div>
        <div v-else class="empty-state">
          <el-empty description="暂无课程任务" />
        </div>
      </el-card>

      <!-- 统计信息 -->
      <el-card class="info-card" shadow="never">
        <template #header>
          <div class="card-header">
            <el-icon><DataAnalysis /></el-icon>
            <span>统计信息</span>
          </div>
        </template>
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-value">{{ course.student_count }}</div>
            <div class="stat-label">学生数量</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ course.materials_count }}</div>
            <div class="stat-label">资料数量</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ course.assignments_count }}</div>
            <div class="stat-label">任务数量</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ getTotalQuestions() }}</div>
            <div class="stat-label">总题目数</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ getTotalSubmissions() }}</div>
            <div class="stat-label">总提交数</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ getCompletionRate() }}%</div>
            <div class="stat-label">完成率</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 底部操作按钮 -->
    <div class="footer-actions">
      <el-button @click="$emit('close')">关闭</el-button>
      <el-dropdown @command="handleExportCommand">
        <el-button type="primary">
          <el-icon><Download /></el-icon> 导出课程数据
          <el-icon class="el-icon--right"><ArrowDown /></el-icon>
        </el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="all">导出完整数据包</el-dropdown-item>
            <el-dropdown-item command="basic">仅导出基本信息</el-dropdown-item>
            <el-dropdown-item command="students">仅导出学生信息</el-dropdown-item>
            <el-dropdown-item command="materials">仅导出资料信息</el-dropdown-item>
            <el-dropdown-item command="assignments">仅导出任务信息</el-dropdown-item>
            <el-dropdown-item command="summary">仅导出汇总报告</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Reading, User, UserFilled, Document, Edit, DataAnalysis, Download, ArrowDown 
} from '@element-plus/icons-vue'
import { exportToCSV } from '@/utils/exportUtils'

// Props
const props = defineProps({
  course: {
    type: Object,
    required: true
  }
})

// Emits
const emit = defineEmits(['close'])

// 计算属性
const getTotalQuestions = () => {
  if (!props.course.assignments) return 0
  return props.course.assignments.reduce((sum, assignment) => sum + assignment.questions_count, 0)
}

const getTotalSubmissions = () => {
  if (!props.course.assignments) return 0
  return props.course.assignments.reduce((sum, assignment) => sum + assignment.submission_count, 0)
}

const getCompletionRate = () => {
  const totalQuestions = getTotalQuestions()
  const totalSubmissions = getTotalSubmissions()
  if (totalQuestions === 0) return 0
  return Math.round((totalSubmissions / totalQuestions) * 100)
}

// 方法
const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString('zh-CN')
}

const getStatusType = (status) => {
  const types = {
    'pending': 'info',
    'parsing': 'warning',
    'parsed': 'success',
    'failed': 'danger'
  }
  return types[status] || 'info'
}

const getStatusLabel = (status) => {
  const labels = {
    'pending': '待处理',
    'parsing': '解析中',
    'parsed': '已解析',
    'failed': '解析失败'
  }
  return labels[status] || status
}

const handleExportCommand = (command) => {
  try {
    const timestamp = new Date().toLocaleDateString()
    const courseTitle = props.course.title.replace(/[^\w\s]/gi, '_') // 移除特殊字符

    if (command === 'all') {
      // 导出完整数据包
      exportAllData(courseTitle, timestamp)
    } else if (command === 'basic') {
      // 仅导出基本信息
      exportBasicInfo(courseTitle, timestamp)
    } else if (command === 'students') {
      // 仅导出学生信息
      exportStudentsInfo(courseTitle, timestamp)
    } else if (command === 'materials') {
      // 仅导出资料信息
      exportMaterialsInfo(courseTitle, timestamp)
    } else if (command === 'assignments') {
      // 仅导出任务信息
      exportAssignmentsInfo(courseTitle, timestamp)
    } else if (command === 'summary') {
      // 仅导出汇总报告
      exportSummaryReport(courseTitle, timestamp)
    }
    ElMessage.success(`成功导出课程"${props.course.title}"的${command}数据`)
  } catch (error) {
    ElMessage.error(`导出失败: ${error.message}`)
    console.error('Export course data error:', error)
  }
}

const exportAllData = (courseTitle, timestamp) => {
  const courseBasicInfo = [{
    课程ID: props.course.id,
    课程标题: props.course.title,
    课程描述: props.course.description,
    创建时间: formatDate(props.course.created_at),
    知识库ID: props.course.dataset_id || '未设置',
    知识库名称: props.course.dataset_name || '未设置',
    聊天助手ID: props.course.chat_id || '未设置',
    学生数量: props.course.student_count || 0,
    资料数量: props.course.materials_count || 0,
    任务数量: props.course.assignments_count || 0,
    总题目数: getTotalQuestions(),
    总提交数: getTotalSubmissions(),
    完成率: `${getCompletionRate()}%`
  }]

  const teacherInfo = props.course.teacher ? [{
    教师ID: props.course.teacher.id,
    教师姓名: props.course.teacher.username,
    手机号: props.course.teacher.phone,
    所属大学: props.course.teacher.university || '未设置',
    职称: props.course.teacher.title || '未设置',
    所属部门: props.course.teacher.department || '未设置'
  }] : []

  const studentsInfo = props.course.students ? props.course.students.map(student => ({
    学生ID: student.id,
    学生姓名: student.username,
    手机号: student.phone,
    所属大学: student.university || '未设置',
    注册时间: formatDate(student.created_at)
  })) : []

  const materialsInfo = props.course.materials ? props.course.materials.map(material => ({
    资料ID: material.id,
    标题: material.title,
    描述: material.description || '无描述',
    文件名: material.filename,
    状态: getStatusLabel(material.status),
    上传时间: formatDate(material.uploadtime),
    RAG文档ID: material.rag_doc_id || '未设置'
  })) : []

  const assignmentsInfo = props.course.assignments ? props.course.assignments.map(assignment => ({
    任务ID: assignment.id,
    任务标题: assignment.title,
    任务描述: assignment.description || '无描述',
    题目数量: assignment.questions_count || 0,
    提交数量: assignment.submission_count || 0,
    创建时间: formatDate(assignment.created_at),
    截止时间: formatDate(assignment.deadline)
  })) : []

  // 创建多个CSV文件
  exportToCSV(courseBasicInfo, `${courseTitle}_基本信息_${timestamp}`)
  if (teacherInfo.length > 0) {
    exportToCSV(teacherInfo, `${courseTitle}_教师信息_${timestamp}`)
  }
  if (studentsInfo.length > 0) {
    exportToCSV(studentsInfo, `${courseTitle}_学生信息_${timestamp}`)
  }
  if (materialsInfo.length > 0) {
    exportToCSV(materialsInfo, `${courseTitle}_资料信息_${timestamp}`)
  }
  if (assignmentsInfo.length > 0) {
    exportToCSV(assignmentsInfo, `${courseTitle}_任务信息_${timestamp}`)
  }

  // 创建汇总报告
  const summaryReport = [
    {
      导出时间: new Date().toLocaleString('zh-CN'),
      课程标题: props.course.title,
      课程ID: props.course.id,
      教师姓名: props.course.teacher?.username || '未分配',
      学生数量: studentsInfo.length,
      资料数量: materialsInfo.length,
      任务数量: assignmentsInfo.length,
      总题目数: getTotalQuestions(),
      总提交数: getTotalSubmissions(),
      完成率: `${getCompletionRate()}%`
    }
  ]
  
  exportToCSV(summaryReport, `${courseTitle}_汇总报告_${timestamp}`)
}

const exportBasicInfo = (courseTitle, timestamp) => {
  const courseBasicInfo = [{
    课程ID: props.course.id,
    课程标题: props.course.title,
    课程描述: props.course.description,
    创建时间: formatDate(props.course.created_at),
    知识库ID: props.course.dataset_id || '未设置',
    知识库名称: props.course.dataset_name || '未设置',
    聊天助手ID: props.course.chat_id || '未设置',
    学生数量: props.course.student_count || 0,
    资料数量: props.course.materials_count || 0,
    任务数量: props.course.assignments_count || 0,
    总题目数: getTotalQuestions(),
    总提交数: getTotalSubmissions(),
    完成率: `${getCompletionRate()}%`
  }]
  exportToCSV(courseBasicInfo, `${courseTitle}_基本信息_${timestamp}`)
}

const exportStudentsInfo = (courseTitle, timestamp) => {
  const studentsInfo = props.course.students ? props.course.students.map(student => ({
    学生ID: student.id,
    学生姓名: student.username,
    手机号: student.phone,
    所属大学: student.university || '未设置',
    注册时间: formatDate(student.created_at)
  })) : []
  exportToCSV(studentsInfo, `${courseTitle}_学生信息_${timestamp}`)
}

const exportMaterialsInfo = (courseTitle, timestamp) => {
  const materialsInfo = props.course.materials ? props.course.materials.map(material => ({
    资料ID: material.id,
    标题: material.title,
    描述: material.description || '无描述',
    文件名: material.filename,
    状态: getStatusLabel(material.status),
    上传时间: formatDate(material.uploadtime),
    RAG文档ID: material.rag_doc_id || '未设置'
  })) : []
  exportToCSV(materialsInfo, `${courseTitle}_资料信息_${timestamp}`)
}

const exportAssignmentsInfo = (courseTitle, timestamp) => {
  const assignmentsInfo = props.course.assignments ? props.course.assignments.map(assignment => ({
    任务ID: assignment.id,
    任务标题: assignment.title,
    任务描述: assignment.description || '无描述',
    题目数量: assignment.questions_count || 0,
    提交数量: assignment.submission_count || 0,
    创建时间: formatDate(assignment.created_at),
    截止时间: formatDate(assignment.deadline)
  })) : []
  exportToCSV(assignmentsInfo, `${courseTitle}_任务信息_${timestamp}`)
}

const exportSummaryReport = (courseTitle, timestamp) => {
  const summaryReport = [
    {
      导出时间: new Date().toLocaleString('zh-CN'),
      课程标题: props.course.title,
      课程ID: props.course.id,
      教师姓名: props.course.teacher?.username || '未分配',
      学生数量: props.course.students?.length || 0,
      资料数量: props.course.materials?.length || 0,
      任务数量: props.course.assignments?.length || 0,
      总题目数: getTotalQuestions(),
      总提交数: getTotalSubmissions(),
      完成率: `${getCompletionRate()}%`
    }
  ]
  exportToCSV(summaryReport, `${courseTitle}_汇总报告_${timestamp}`)
}
</script>

<style scoped>
.course-detail {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.detail-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 20px;
}

.info-card {
  border: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #303133;
}

.card-header .el-icon {
  color: #409eff;
}

.empty-state {
  padding: 40px 0;
  text-align: center;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 20px;
  padding: 20px 0;
}

.stat-item {
  text-align: center;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  transition: all 0.3s ease;
}

.stat-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #409eff;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.footer-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  padding: 20px 0;
  border-top: 1px solid #e4e7ed;
  background: white;
  position: sticky;
  bottom: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .course-detail {
    padding: 10px;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }
  
  .stat-item {
    padding: 15px;
  }
  
  .stat-value {
    font-size: 20px;
  }
  
  .footer-actions {
    flex-direction: column;
    align-items: center;
  }
}
</style> 