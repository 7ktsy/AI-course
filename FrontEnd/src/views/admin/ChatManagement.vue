<template>
  <div class="chat-management">
    <!-- 页面状态提示 -->
    <el-alert
      title="聊天助手管理页面已就绪"
      description="您可以查看和配置所有聊天助手的参数设置"
      type="success"
      :closable="false"
      show-icon
      style="margin-bottom: 20px;"
    />
    
    <!-- 统计信息 -->
    <el-card class="status-card" shadow="hover">
      <template #header>
        <div class="status-header">
          <el-icon><ChatDotRound /></el-icon>
          <span>聊天助手统计概览</span>
        </div>
      </template>
      <div class="status-content">
        <div class="status-item">
          <el-icon class="status-icon"><ChatDotRound /></el-icon>
          <div class="status-info">
            <div class="status-label">总助手数</div>
            <div class="status-value">{{ chatStats.totalAssistants || 0 }}</div>
          </div>
        </div>
        <div class="status-item">
          <el-icon class="status-icon"><Reading /></el-icon>
          <div class="status-info">
            <div class="status-label">课程助手</div>
            <div class="status-value">{{ chatStats.courseAssistants || 0 }}个</div>
          </div>
        </div>
        <div class="status-item">
          <el-icon class="status-icon"><Setting /></el-icon>
          <div class="status-info">
            <div class="status-label">通用助手</div>
            <div class="status-value">{{ chatStats.generalAssistants || 0 }}个</div>
          </div>
        </div>
        <div class="status-item">
          <el-icon class="status-icon"><CircleCheck /></el-icon>
          <div class="status-info">
            <div class="status-label">活跃助手</div>
            <div class="status-value">{{ chatStats.activeAssistants || 0 }}个</div>
          </div>
        </div>
      </div>
    </el-card>
    
    <!-- 顶部导航栏 -->
    <div class="top-nav">
      <div class="nav-left">
        <h1 class="page-title">
          <el-icon class="title-icon"><ChatDotRound /></el-icon>
          聊天助手管理
        </h1>
        <p class="page-subtitle">管理系统中的所有聊天助手配置</p>
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

    <!-- 筛选和搜索 -->
    <div class="filter-section">
      <el-card shadow="never" class="filter-card">
        <div class="filter-row">
          <el-input
            v-model="searchQuery"
            placeholder="搜索助手名称或描述"
            class="search-input"
            clearable
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          
          <el-select v-model="typeFilter" placeholder="助手类型" clearable @change="handleSearch">
            <el-option label="全部助手" value="" />
            <el-option label="课程助手" value="course" />
            <el-option label="通用助手" value="general" />
          </el-select>
          
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon> 搜索
          </el-button>
        </div>
      </el-card>
    </div>

    <!-- 助手列表 -->
    <div class="assistants-section">
      <el-card shadow="never" class="list-card">
        <template #header>
          <div class="list-header">
            <span>聊天助手列表 ({{ filteredAssistants.length }} 个助手)</span>
            <div class="header-actions">
              <el-button size="small" @click="exportAssistants">
                <el-icon><Download /></el-icon> 导出
              </el-button>
            </div>
          </div>
        </template>

        <el-table
          :data="filteredAssistants"
          v-loading="loading"
          stripe
          class="assistants-table"
        >
          <el-table-column prop="chat_id" label="助手ID" width="280" />
          
          <el-table-column label="助手信息" min-width="300">
            <template #default="{ row }">
              <div class="assistant-info">
                <div class="assistant-name">{{ row.name }}</div>
                <div class="assistant-description">{{ row.description }}</div>
                <div class="assistant-meta">
                  <el-tag size="small" :type="row.is_course_chat ? 'success' : 'info'">
                    {{ row.is_course_chat ? '课程助手' : '通用助手' }}
                  </el-tag>
                  <el-tag v-if="row.is_course_chat && row.course_info?.chat_type_name" size="small" type="warning">
                    {{ row.course_info.chat_type_name }}
                  </el-tag>
                </div>
              </div>
            </template>
          </el-table-column>

          <el-table-column label="课程信息" width="200" v-if="showCourseInfo">
            <template #default="{ row }">
              <div v-if="row.is_course_chat && row.course_info" class="course-info">
                <div class="course-title">{{ row.course_info.course_title }}</div>
                <div class="teacher-name">教师: {{ row.course_info.teacher_name }}</div>
              </div>
              <div v-else class="no-course">通用助手</div>
            </template>
          </el-table-column>

          <el-table-column label="创建时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.create_date) }}
            </template>
          </el-table-column>

          <el-table-column label="更新时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.update_date) }}
            </template>
          </el-table-column>

          <el-table-column label="操作" width="150" fixed="right">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-tooltip content="查看详情" placement="top">
                  <el-button 
                    size="small" 
                    type="primary" 
                    @click="router.push(`/dashboard/chat-detail/${row.chat_id}`)"
                    class="action-btn"
                  >
                    <el-icon><View /></el-icon>
                    详情
                  </el-button>
                </el-tooltip>
                <el-tooltip content="配置参数" placement="top">
                  <el-button 
                    size="small" 
                    type="warning" 
                    @click="configureAssistant(row)"
                    class="action-btn"
                  >
                    <el-icon><Setting /></el-icon>
                    配置
                  </el-button>
                </el-tooltip>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- 助手配置对话框 -->
    <el-dialog
      v-model="configDialogVisible"
      title="聊天助手配置"
      width="70%"
      :close-on-click-modal="false"
    >
      <ChatConfig 
        v-if="selectedAssistant" 
        :assistant="selectedAssistant" 
        @close="configDialogVisible = false"
        @updated="handleConfigUpdated"
      />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  ChatDotRound, Refresh, Back, Search, Download, View, Setting,
  Reading, CircleCheck
} from '@element-plus/icons-vue'
import ChatConfig from './components/ChatConfig.vue'

// 获取router实例
const router = useRouter()

// 响应式数据
const loading = ref(false)
const assistants = ref([])
const selectedAssistant = ref(null)
const configDialogVisible = ref(false)

// 搜索和筛选
const searchQuery = ref('')
const typeFilter = ref('')

// 统计信息
const chatStats = ref({
  totalAssistants: 0,
  courseAssistants: 0,
  generalAssistants: 0,
  activeAssistants: 0
})

// 计算属性
const filteredAssistants = computed(() => {
  let filtered = assistants.value

  // 类型筛选
  if (typeFilter.value) {
    if (typeFilter.value === 'course') {
      filtered = filtered.filter(a => a.is_course_chat)
    } else if (typeFilter.value === 'general') {
      filtered = filtered.filter(a => !a.is_course_chat)
    }
  }

  // 搜索筛选
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(a => 
      a.name.toLowerCase().includes(query) ||
      a.description.toLowerCase().includes(query)
    )
  }

  return filtered
})

const showCourseInfo = computed(() => {
  return assistants.value.some(a => a.is_course_chat)
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
const loadAssistants = async () => {
  loading.value = true
  try {
    const response = await apiCall('/chat/assistants')
    assistants.value = response.data || []
    updateChatStats()
  } catch (error) {
    ElMessage.error('加载聊天助手列表失败')
    console.error('Load assistants error:', error)
  } finally {
    loading.value = false
  }
}

const updateChatStats = () => {
  const total = assistants.value.length
  const courseAssistants = assistants.value.filter(a => a.is_course_chat).length
  const generalAssistants = total - courseAssistants
  
  chatStats.value = {
    totalAssistants: total,
    courseAssistants: courseAssistants,
    generalAssistants: generalAssistants,
    activeAssistants: total // 假设所有助手都是活跃的
  }
}

const refreshData = () => {
  loadAssistants()
}

const handleSearch = () => {
  // 搜索是响应式的，不需要额外处理
}

const configureAssistant = (assistant) => {
  selectedAssistant.value = assistant
  configDialogVisible.value = true
}

const handleConfigUpdated = () => {
  ElMessage.success('配置更新成功')
  loadAssistants() // 重新加载数据
}

const exportAssistants = () => {
  ElMessage.info('导出功能开发中...')
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString('zh-CN')
}

// 生命周期
onMounted(() => {
  loadAssistants()
})
</script>

<style scoped>
.chat-management {
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

.filter-section {
  margin-bottom: 20px;
}

.filter-card {
  border: none;
}

.filter-row {
  display: flex;
  gap: 16px;
  align-items: center;
}

.search-input {
  flex: 1;
  max-width: 300px;
}

.assistants-section {
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

.assistants-table {
  margin-bottom: 20px;
}

.assistants-table :deep(.el-table__header) {
  background-color: #f8f9fa;
}

.assistants-table :deep(.el-table__header th) {
  background-color: #f8f9fa;
  color: #606266;
  font-weight: 600;
  border-bottom: 2px solid #e4e7ed;
}

.assistants-table :deep(.el-table__row:hover) {
  background-color: #f5f7fa;
}

.assistant-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.assistant-name {
  font-weight: 600;
  color: #303133;
  font-size: 16px;
}

.assistant-description {
  color: #606266;
  font-size: 14px;
  line-height: 1.4;
}

.assistant-meta {
  display: flex;
  gap: 8px;
}

.course-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.course-title {
  font-weight: 600;
  color: #303133;
  font-size: 14px;
}

.teacher-name {
  font-size: 12px;
  color: #909399;
}

.no-course {
  color: #909399;
  font-style: italic;
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
  .chat-management {
    padding: 10px;
  }
  
  .top-nav {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .filter-row {
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