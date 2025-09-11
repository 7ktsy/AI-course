<template>
  <div class="my-homework-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="page-title">
        <h2>我的作业</h2>
        <span class="homework-count">共 {{ assignments.length }} 项作业</span>
      </div>
    </div>

    <!-- 筛选和搜索区域 -->
    <div class="filter-section">
      <div class="filter-wrapper">
        <el-input
          v-model="searchQuery"
          placeholder="搜索作业标题..."
          class="search-input"
          size="large"
          clearable
          @input="filterAssignments"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select
          v-model="filterType"
          placeholder="作业类型"
          size="large"
          style="width: 200px"
          @change="filterAssignments"
        >
          <el-option label="全部作业" value="all" />
          <el-option label="教师布置" value="teacher" />
          <el-option label="实时测评" value="self" />
        </el-select>
        
        <el-select
          v-model="filterStatus"
          placeholder="完成状态"
          size="large"
          style="width: 150px"
          @change="filterAssignments"
        >
          <el-option label="全部状态" value="all" />
          <el-option label="未完成" value="pending" />
          <el-option label="已完成" value="completed" />
          <el-option label="已过期" value="overdue" />
        </el-select>
      </div>
    </div>

    <!-- 作业列表 -->
    <div class="homework-list" v-loading="loading">
      <div v-if="filteredAssignments.length === 0" class="empty-state">
        <el-empty description="暂无作业" />
      </div>
      
      <div v-else class="homework-grid">
        <div 
          v-for="assignment in filteredAssignments" 
          :key="assignment.id" 
          class="homework-item"
          :class="{ 
            'overdue': isOverdue(assignment.deadline) && getSubmissionStatus(assignment.id) !== 'completed' && !isSelfGenerated(assignment.creator_id),
            'completed': getSubmissionStatus(assignment.id) === 'completed' && !isSelfGenerated(assignment.creator_id),
            'self-generated': isSelfGenerated(assignment.creator_id)
          }"
          @click="goToHomeworkDetail(assignment)"
        >
          <!-- 作业类型标签 -->
          <div class="assignment-tag">
            <el-tag 
              :type="isSelfGenerated(assignment.creator_id) ? 'success' : 'primary'" 
              size="small"
            >
              {{ isSelfGenerated(assignment.creator_id) ? '实时测评' : '教师布置' }}
            </el-tag>
            <el-tag 
              v-if="getSubmissionStatus(assignment.id) === 'completed'" 
              type="success" 
              size="small"
            >
              已完成
            </el-tag>
            <el-tag 
              v-else-if="isOverdue(assignment.deadline)" 
              type="danger" 
              size="small"
            >
              已过期
            </el-tag>
          </div>

          <!-- 作业内容 -->
          <div class="homework-content">
            <h3 class="homework-title">{{ assignment.title }}</h3>
            <div class="homework-meta">
              <div class="meta-item">
                <el-icon><School /></el-icon>
                <span>{{ assignment.course_title }}</span>
              </div>
              <div class="meta-item" v-if="assignment.deadline">
                <el-icon><Clock /></el-icon>
                <span>截止：{{ formatDate(assignment.deadline) }}</span>
              </div>
              <div class="meta-item" v-if="getSubmissionInfo(assignment.id)">
                <el-icon><DocumentChecked /></el-icon>
                <span>分数：{{ getSubmissionInfo(assignment.id).score }} 分</span>
              </div>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="homework-actions">
            <el-button 
              v-if="getSubmissionStatus(assignment.id) === 'completed'"
              type="success" 
              size="small"
              @click.stop="viewResult(assignment)"
            >
              查看结果
            </el-button>
            <el-button 
              v-else
              :type="isOverdue(assignment.deadline) ? 'info' : 'primary'"
              size="small"
              @click.stop="goToHomeworkDetail(assignment)"
            >
              {{ isOverdue(assignment.deadline) ? '查看详情' : '开始答题' }}
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, School, Clock, DocumentChecked } from '@element-plus/icons-vue'
import request from '@/utils/request'

const router = useRouter()

// 数据定义
const assignments = ref([])
const submissions = ref([]) // 学生提交记录
const loading = ref(false)
const searchQuery = ref('')
const filterType = ref('all')
const filterStatus = ref('all')

// 当前用户信息
const currentUser = JSON.parse(localStorage.getItem('userInfo') || '{}')

// 计算属性：过滤后的作业列表
const filteredAssignments = computed(() => {
  let filtered = assignments.value

  // 按搜索关键词过滤
  if (searchQuery.value) {
    filtered = filtered.filter(assignment => 
      assignment.title.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  }

  // 按作业类型过滤
  if (filterType.value !== 'all') {
    filtered = filtered.filter(assignment => {
      const isSelf = isSelfGenerated(assignment.creator_id)
      return filterType.value === 'self' ? isSelf : !isSelf
    })
  }

  // 按完成状态过滤
  if (filterStatus.value !== 'all') {
    filtered = filtered.filter(assignment => {
      const status = getSubmissionStatus(assignment.id)
      if (filterStatus.value === 'completed') return status === 'completed'
      if (filterStatus.value === 'pending') return status === 'pending'
      if (filterStatus.value === 'overdue') return isOverdue(assignment.deadline) && status !== 'completed'
      return true
    })
  }

  return filtered.sort((a, b) => {
    // 先按完成状态排序，未完成的在前
    const statusA = getSubmissionStatus(a.id)
    const statusB = getSubmissionStatus(b.id)
    if (statusA !== statusB) {
      return statusA === 'pending' ? -1 : 1
    }
    
    // 再按截止时间排序
    if (a.deadline && b.deadline) {
      return new Date(a.deadline) - new Date(b.deadline)
    }
    return 0
  })
})

// API 调用
const api = {
  // 获取作业列表
  async getAssignments() {
    try {
      loading.value = true
      const response = await request.get('/student/assignment/list')
      console.log('作业列表响应:', response)
      if (response && response.data) {
        assignments.value = response.data
        // 获取所有作业的提交状态
        await api.getSubmissionsStatus()
      }
    } catch (error) {
      console.error('获取作业列表失败:', error)
      ElMessage.error('获取作业列表失败')
    } finally {
      loading.value = false
    }
  },

  // 获取所有作业的提交状态
  async getSubmissionsStatus() {
    try {
      // 为每个作业检查提交状态
      const submissionPromises = assignments.value.map(async (assignment) => {
        try {
          const response = await request({
            method: 'get',
            url: `/student/assignment/${assignment.id}/my_result`,
            silentNotFound: true  // 静默处理404错误
          })
          if (response && response.data) {
            return {
              assignment_id: assignment.id,
              ...response.data
            }
          }
        } catch (error) {
          // 如果返回404，说明该作业未提交，这是正常情况，不需要报错
          if (error.response?.status === 404) {
            return null
          }
          // 其他错误才记录日志
          console.warn(`获取作业${assignment.id}提交状态失败:`, error.message)
          return null
        }
      })

      const results = await Promise.all(submissionPromises)
      // 过滤掉null值，只保留已提交的作业记录
      submissions.value = results.filter(result => result !== null)
      console.log('已提交作业数量:', submissions.value.length)
    } catch (error) {
      console.error('获取提交状态失败:', error)
    }
  }
}

// 工具函数
const isSelfGenerated = (creatorId) => {
  return creatorId === String(currentUser.id)
}

const isOverdue = (deadline) => {
  if (!deadline) return false
  return new Date(deadline) < new Date()
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getSubmissionStatus = (assignmentId) => {
  const submission = submissions.value.find(s => s.assignment_id === assignmentId)
  return submission ? 'completed' : 'pending'
}

const getSubmissionInfo = (assignmentId) => {
  return submissions.value.find(s => s.assignment_id === assignmentId)
}

const filterAssignments = () => {
  // 触发computed重新计算
}

// 页面跳转
const goToHomeworkDetail = (assignment) => {
  router.push({
    name: 'HomeworkDetail',
    params: { id: assignment.id }
  })
}

const viewResult = (assignment) => {
  router.push({
    name: 'HomeworkDetail',
    params: { id: assignment.id }
  })
}

// 生命周期
onMounted(async () => {
  await api.getAssignments()
})
</script>

<style scoped>
.my-homework-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-title h2 {
  margin: 0;
  color: #1f2937;
  font-size: 28px;
  font-weight: 600;
}

.homework-count {
  background: #f3f4f6;
  color: #6b7280;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 14px;
}

.filter-section {
  background: #fff;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
}

.filter-wrapper {
  display: flex;
  gap: 16px;
  align-items: center;
  flex-wrap: wrap;
}

.search-input {
  flex: 1;
  min-width: 300px;
}

.homework-list {
  min-height: 400px;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400px;
}

.homework-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}

.homework-item {
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.homework-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.homework-item.overdue {
  border-left: 4px solid #ef4444;
}

.homework-item.completed {
  border-left: 4px solid #ffdb3b; /* 黄色边框 */
}

.homework-item.self-generated {
  border-left: 4px solid #10b981;
}

.assignment-tag {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.homework-content {
  margin-bottom: 16px;
}

.homework-title {
  margin: 0 0 12px 0;
  color: #1f2937;
  font-size: 18px;
  font-weight: 600;
  line-height: 1.4;
}

.homework-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #6b7280;
  font-size: 14px;
}

.meta-item .el-icon {
  font-size: 16px;
}

.homework-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

@media (max-width: 768px) {
  .homework-grid {
    grid-template-columns: 1fr;
  }
  
  .filter-wrapper {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-input {
    min-width: unset;
  }
}
</style>
