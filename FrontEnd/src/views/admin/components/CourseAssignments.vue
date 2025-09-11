<template>
  <div class="course-assignments">
    <div class="assignments-header">
      <h2>{{ course.title }} - 课程任务</h2>
      <p class="subtitle">共 {{ course.assignments?.length || 0 }} 个任务</p>
    </div>

    <div class="assignments-content">
      <div v-if="course.assignments && course.assignments.length > 0">
        <el-table :data="course.assignments" stripe class="assignments-table">
          <el-table-column prop="id" label="ID" width="80" />
          
          <el-table-column label="任务信息" min-width="300">
            <template #default="{ row }">
              <div class="assignment-info">
                <div class="assignment-title">{{ row.title }}</div>
                <div class="assignment-description">{{ row.description }}</div>
                <div class="assignment-meta">
                  <el-tag size="small" type="info">
                    <el-icon><Calendar /></el-icon>
                    创建: {{ formatDate(row.created_at) }}
                  </el-tag>
                  <el-tag size="small" type="warning">
                    <el-icon><Clock /></el-icon>
                    截止: {{ formatDate(row.deadline) }}
                  </el-tag>
                </div>
              </div>
            </template>
          </el-table-column>

          <el-table-column prop="questions_count" label="题目数" width="100" align="center">
            <template #default="{ row }">
              <el-tag size="small" type="primary">{{ row.questions_count }}</el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="submission_count" label="提交数" width="100" align="center">
            <template #default="{ row }">
              <el-tag size="small" type="success">{{ row.submission_count }}</el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="creator_id" label="创建者" width="120" align="center">
            <template #default="{ row }">
              <span>{{ row.creator_id }}</span>
            </template>
          </el-table-column>

          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-tooltip content="查看详情" placement="top">
                  <el-button 
                    size="small" 
                    type="primary" 
                    text
                    @click="viewAssignmentDetail(row)"
                  >
                    <el-icon><View /></el-icon>
                  </el-button>
                </el-tooltip>
                <el-tooltip content="查看题目" placement="top">
                  <el-button 
                    size="small" 
                    type="warning" 
                    text
                    @click="viewQuestions(row)"
                  >
                    <el-icon><Edit /></el-icon>
                  </el-button>
                </el-tooltip>
                <el-tooltip content="查看提交" placement="top">
                  <el-button 
                    size="small" 
                    type="success" 
                    text
                    @click="viewSubmissions(row)"
                  >
                    <el-icon><Document /></el-icon>
                  </el-button>
                </el-tooltip>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <div v-else class="empty-state">
        <el-empty description="暂无课程任务" />
      </div>
    </div>

    <!-- 任务详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="任务详情"
      width="800px"
      :close-on-click-modal="false"
    >
      <div v-if="selectedAssignment" class="assignment-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="任务ID">{{ selectedAssignment.id }}</el-descriptions-item>
          <el-descriptions-item label="标题">{{ selectedAssignment.title }}</el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">{{ selectedAssignment.description }}</el-descriptions-item>
          <el-descriptions-item label="内容" :span="2">
            <div class="content-display">{{ selectedAssignment.content || '无内容' }}</div>
          </el-descriptions-item>
          <el-descriptions-item label="参考答案" :span="2">
            <div class="content-display">{{ selectedAssignment.answer || '无参考答案' }}</div>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(selectedAssignment.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="截止时间">{{ formatDate(selectedAssignment.deadline) }}</el-descriptions-item>
          <el-descriptions-item label="创建者ID">{{ selectedAssignment.creator_id }}</el-descriptions-item>
          <el-descriptions-item label="题目数量">{{ selectedAssignment.questions_count }}</el-descriptions-item>
          <el-descriptions-item label="提交数量">{{ selectedAssignment.submission_count }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>

    <!-- 题目列表对话框 -->
    <el-dialog
      v-model="questionsDialogVisible"
      title="任务题目"
      width="900px"
      :close-on-click-modal="false"
    >
      <div v-if="selectedAssignment && selectedAssignment.questions">
        <el-table :data="selectedAssignment.questions" stripe size="small">
          <el-table-column prop="order" label="序号" width="80" align="center" />
          <el-table-column prop="type" label="类型" width="100" align="center">
            <template #default="{ row }">
              <el-tag size="small" :type="getQuestionTypeColor(row.type)">
                {{ row.type }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="content" label="题目内容" min-width="300">
            <template #default="{ row }">
              <div class="question-content">{{ row.content }}</div>
            </template>
          </el-table-column>
          <el-table-column prop="points" label="分值" width="80" align="center">
            <template #default="{ row }">
              <el-tag size="small" type="warning">{{ row.points }}分</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="difficulty" label="难度" width="100" align="center">
            <template #default="{ row }">
              <el-tag size="small" :type="getDifficultyColor(row.difficulty)">
                {{ row.difficulty }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="key_knowledge" label="知识点" width="150">
            <template #default="{ row }">
              <div class="knowledge-point">{{ row.key_knowledge || '无' }}</div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>

    <!-- 提交记录对话框 -->
    <el-dialog
      v-model="submissionsDialogVisible"
      title="提交记录"
      width="800px"
      :close-on-click-modal="false"
    >
      <div v-if="selectedAssignment && selectedAssignment.submissions">
        <el-table :data="selectedAssignment.submissions" stripe size="small">
          <el-table-column prop="id" label="提交ID" width="80" />
          <el-table-column label="学生信息" width="200">
            <template #default="{ row }">
              <div v-if="row.student" class="student-info">
                <div class="student-name">{{ row.student.username }}</div>
                <div class="student-phone">{{ row.student.phone }}</div>
              </div>
              <span v-else>未知学生</span>
            </template>
          </el-table-column>
          <el-table-column prop="submit_time" label="提交时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.submit_time) }}
            </template>
          </el-table-column>
          <el-table-column prop="score" label="得分" width="100" align="center">
            <template #default="{ row }">
              <el-tag size="small" :type="getScoreColor(row.score)">
                {{ row.score || 0 }}分
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="feedback" label="反馈" min-width="200">
            <template #default="{ row }">
              <div class="feedback-content">{{ row.feedback || '无反馈' }}</div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>

    <!-- 底部操作按钮 -->
    <div class="footer-actions">
      <el-button @click="$emit('close')">关闭</el-button>
      <el-button type="primary" @click="exportAssignments">导出任务列表</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Edit, View, Document, Calendar, Clock 
} from '@element-plus/icons-vue'

// Props
const props = defineProps({
  course: {
    type: Object,
    required: true
  }
})

// Emits
const emit = defineEmits(['close'])

// 响应式数据
const detailDialogVisible = ref(false)
const questionsDialogVisible = ref(false)
const submissionsDialogVisible = ref(false)
const selectedAssignment = ref(null)

// 方法
const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString('zh-CN')
}

const getQuestionTypeColor = (type) => {
  const colors = {
    '选择': 'primary',
    '填空': 'success',
    '主观题': 'warning',
    '编码': 'danger'
  }
  return colors[type] || 'info'
}

const getDifficultyColor = (difficulty) => {
  const colors = {
    'easy': 'success',
    'medium': 'warning',
    'hard': 'danger'
  }
  return colors[difficulty] || 'info'
}

const getScoreColor = (score) => {
  if (score >= 90) return 'success'
  if (score >= 80) return 'warning'
  if (score >= 60) return 'info'
  return 'danger'
}

const viewAssignmentDetail = (assignment) => {
  selectedAssignment.value = assignment
  detailDialogVisible.value = true
}

const viewQuestions = (assignment) => {
  selectedAssignment.value = assignment
  questionsDialogVisible.value = true
}

const viewSubmissions = (assignment) => {
  selectedAssignment.value = assignment
  submissionsDialogVisible.value = true
}

const exportAssignments = () => {
  ElMessage.info('导出功能开发中...')
}
</script>

<style scoped>
.course-assignments {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.assignments-header {
  margin-bottom: 20px;
  text-align: center;
}

.assignments-header h2 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 20px;
  font-weight: 600;
}

.subtitle {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.assignments-content {
  margin-bottom: 20px;
}

.assignments-table {
  margin-bottom: 20px;
}

.assignments-table :deep(.el-table__header) {
  background-color: #f8f9fa;
}

.assignments-table :deep(.el-table__header th) {
  background-color: #f8f9fa;
  color: #606266;
  font-weight: 600;
  border-bottom: 2px solid #e4e7ed;
}

.assignment-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.assignment-title {
  font-weight: 600;
  color: #303133;
  font-size: 14px;
}

.assignment-description {
  color: #606266;
  font-size: 12px;
  line-height: 1.4;
}

.assignment-meta {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.empty-state {
  padding: 60px 0;
  text-align: center;
}

.action-buttons {
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: center;
}

.assignment-detail {
  padding: 20px 0;
}

.content-display {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 4px;
  font-size: 12px;
  line-height: 1.5;
  color: #606266;
  max-height: 100px;
  overflow-y: auto;
  white-space: pre-wrap;
}

.question-content {
  font-size: 12px;
  line-height: 1.4;
  color: #303133;
}

.knowledge-point {
  font-size: 12px;
  color: #606266;
}

.student-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.student-name {
  font-weight: 600;
  color: #303133;
  font-size: 12px;
}

.student-phone {
  color: #909399;
  font-size: 11px;
}

.feedback-content {
  font-size: 12px;
  color: #606266;
  line-height: 1.4;
  max-height: 60px;
  overflow-y: auto;
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
  .course-assignments {
    padding: 10px;
  }
  
  .assignments-table {
    font-size: 12px;
  }
  
  .assignment-meta {
    flex-direction: column;
    gap: 4px;
  }
  
  .footer-actions {
    flex-direction: column;
    align-items: center;
  }
}
</style> 