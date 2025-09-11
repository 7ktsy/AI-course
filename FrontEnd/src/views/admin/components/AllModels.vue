<template>
  <div class="all-models">
    <!-- 模型统计 -->
    <el-card class="stats-card" shadow="never">
      <template #header>
        <div class="card-header">
          <el-icon><DataAnalysis /></el-icon>
          <span>模型统计</span>
        </div>
      </template>
      
      <div class="stats-grid">
        <div class="stat-item">
          <div class="stat-value">{{ models.length }}</div>
          <div class="stat-label">总模型数</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ activeModelsCount }}</div>
          <div class="stat-label">活跃模型</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ providersCount }}</div>
          <div class="stat-label">提供商</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ averagePrice }}</div>
          <div class="stat-label">平均价格</div>
        </div>
      </div>
    </el-card>

    <!-- 模型列表 -->
    <el-card class="models-card" shadow="never">
      <template #header>
        <div class="list-header">
          <div class="header-left">
            <el-icon><Cpu /></el-icon>
            <span>模型列表</span>
          </div>
          <div class="header-actions">
            <el-input
              v-model="searchQuery"
              placeholder="搜索模型名称或提供商"
              class="search-input"
              clearable
              @input="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            
            <el-select v-model="statusFilter" placeholder="状态筛选" clearable @change="handleSearch">
              <el-option label="全部状态" value="" />
              <el-option label="活跃" value="active" />
              <el-option label="维护中" value="maintenance" />
              <el-option label="停用" value="inactive" />
            </el-select>
            
            <el-button @click="exportModels">
              <el-icon><Download /></el-icon> 导出
            </el-button>
          </div>
        </div>
      </template>

      <el-table
        :data="filteredModels"
        v-loading="loading"
        stripe
        class="models-table"
      >
        <el-table-column prop="id" label="模型ID" width="150" />
        
        <el-table-column label="模型信息" min-width="250">
          <template #default="{ row }">
            <div class="model-info">
              <div class="model-name">{{ row.name }}</div>
              <div class="model-description">{{ row.description }}</div>
              <div class="model-meta">
                <el-tag size="small" type="info">{{ row.provider }}</el-tag>
                <el-tag size="small" type="warning">{{ row.type }}</el-tag>
                <el-tag 
                  :type="getStatusType(row.status)" 
                  size="small"
                >
                  {{ getStatusLabel(row.status) }}
                </el-tag>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="技术规格" width="200">
          <template #default="{ row }">
            <div class="model-specs">
              <div class="spec-item">
                <span class="spec-label">最大Token:</span>
                <span class="spec-value">{{ formatNumber(row.max_tokens) }}</span>
              </div>
              <div class="spec-item">
                <span class="spec-label">功能:</span>
                <div class="features-list">
                  <el-tag 
                    v-for="feature in row.supported_features.slice(0, 3)" 
                    :key="feature"
                    size="small" 
                    type="success"
                    style="margin-right: 4px; margin-bottom: 4px;"
                  >
                    {{ feature }}
                  </el-tag>
                  <el-tag 
                    v-if="row.supported_features.length > 3"
                    size="small" 
                    type="info"
                  >
                    +{{ row.supported_features.length - 3 }}
                  </el-tag>
                </div>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="价格信息" width="180">
          <template #default="{ row }">
            <div class="pricing-info">
              <div class="price-item">
                <span class="price-label">输入:</span>
                <span class="price-value">${{ row.pricing.input }}</span>
              </div>
              <div class="price-item">
                <span class="price-label">输出:</span>
                <span class="price-value">${{ row.pricing.output }}</span>
              </div>
              <div class="price-unit">{{ row.pricing.unit }}</div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-tooltip content="查看详情" placement="top">
                <el-button 
                  size="small" 
                  type="primary" 
                  @click="viewModelDetails(row)"
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
                  @click="configureModel(row)"
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

    <!-- 模型详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      :title="`${selectedModel?.name} - 详细信息`"
      width="60%"
      :close-on-click-modal="false"
    >
      <div v-if="selectedModel" class="model-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="模型ID">{{ selectedModel.id }}</el-descriptions-item>
          <el-descriptions-item label="模型名称">{{ selectedModel.name }}</el-descriptions-item>
          <el-descriptions-item label="提供商">{{ selectedModel.provider }}</el-descriptions-item>
          <el-descriptions-item label="类型">{{ selectedModel.type }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(selectedModel.status)">
              {{ getStatusLabel(selectedModel.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="最大Token">{{ formatNumber(selectedModel.max_tokens) }}</el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">{{ selectedModel.description }}</el-descriptions-item>
        </el-descriptions>
        
        <div class="detail-section">
          <h4>支持功能</h4>
          <div class="features-grid">
            <el-tag 
              v-for="feature in selectedModel.supported_features" 
              :key="feature"
              size="medium"
              type="success"
              style="margin: 4px;"
            >
              {{ feature }}
            </el-tag>
          </div>
        </div>
        
        <div class="detail-section">
          <h4>价格信息</h4>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="输入价格">${{ selectedModel.pricing.input }}</el-descriptions-item>
            <el-descriptions-item label="输出价格">${{ selectedModel.pricing.output }}</el-descriptions-item>
            <el-descriptions-item label="计费单位" :span="2">{{ selectedModel.pricing.unit }}</el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Cpu, DataAnalysis, Search, Download, View, Setting 
} from '@element-plus/icons-vue'
import { exportToCSV } from '@/utils/exportUtils'

// Props
const props = defineProps({
  models: {
    type: Array,
    required: true
  }
})

// Emits
const emit = defineEmits(['model-updated'])

// 响应式数据
const loading = ref(false)
const searchQuery = ref('')
const statusFilter = ref('')
const detailDialogVisible = ref(false)
const selectedModel = ref(null)

// 计算属性
const activeModelsCount = computed(() => {
  return props.models.filter(model => model.status === 'active').length
})

const providersCount = computed(() => {
  const providers = new Set(props.models.map(model => model.provider))
  return providers.size
})

const averagePrice = computed(() => {
  const prices = props.models.map(model => 
    parseFloat(model.pricing.input) + parseFloat(model.pricing.output)
  )
  const avg = prices.reduce((sum, price) => sum + price, 0) / prices.length
  return avg.toFixed(4)
})

const filteredModels = computed(() => {
  let filtered = props.models

  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(model => 
      model.name.toLowerCase().includes(query) ||
      model.provider.toLowerCase().includes(query) ||
      model.description.toLowerCase().includes(query)
    )
  }

  // 状态过滤
  if (statusFilter.value) {
    filtered = filtered.filter(model => model.status === statusFilter.value)
  }

  return filtered
})

// 方法
const getStatusType = (status) => {
  const types = {
    'active': 'success',
    'maintenance': 'warning',
    'inactive': 'danger'
  }
  return types[status] || 'info'
}

const getStatusLabel = (status) => {
  const labels = {
    'active': '活跃',
    'maintenance': '维护中',
    'inactive': '停用'
  }
  return labels[status] || status
}

const formatNumber = (num) => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}

const handleSearch = () => {
  // 搜索逻辑已在计算属性中处理
  console.log('搜索条件:', { searchQuery: searchQuery.value, statusFilter: statusFilter.value })
}

const viewModelDetails = (model) => {
  selectedModel.value = model
  detailDialogVisible.value = true
}

const configureModel = (model) => {
  ElMessage.info(`配置模型: ${model.name}`)
  emit('model-updated', model)
}

const exportModels = () => {
  try {
    const exportData = props.models.map(model => ({
      模型ID: model.id,
      模型名称: model.name,
      提供商: model.provider,
      类型: model.type,
      状态: getStatusLabel(model.status),
      描述: model.description,
      最大Token: formatNumber(model.max_tokens),
      支持功能: model.supported_features.join(', '),
      输入价格: `$${model.pricing.input}`,
      输出价格: `$${model.pricing.output}`,
      计费单位: model.pricing.unit
    }))

    exportToCSV(exportData, 'AI模型列表')
    ElMessage.success('模型信息导出成功')
  } catch (error) {
    ElMessage.error(`导出失败: ${error.message}`)
  }
}
</script>

<style scoped>
.all-models {
  padding: 20px 0;
}

.stats-card {
  margin-bottom: 20px;
  border: none;
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

.models-card {
  border: none;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #303133;
}

.header-left .el-icon {
  color: #409eff;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.search-input {
  width: 250px;
}

.model-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.model-name {
  font-weight: 600;
  color: #303133;
  font-size: 14px;
}

.model-description {
  color: #606266;
  font-size: 13px;
  line-height: 1.4;
}

.model-meta {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.model-specs {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.spec-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.spec-label {
  font-size: 12px;
  color: #909399;
  min-width: 60px;
}

.spec-value {
  font-size: 13px;
  color: #303133;
  font-weight: 500;
}

.features-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.pricing-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.price-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.price-label {
  font-size: 12px;
  color: #909399;
}

.price-value {
  font-size: 13px;
  color: #303133;
  font-weight: 500;
}

.price-unit {
  font-size: 11px;
  color: #c0c4cc;
  text-align: right;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.action-btn {
  flex: 1;
}

.model-detail {
  padding: 20px 0;
}

.detail-section {
  margin-top: 24px;
}

.detail-section h4 {
  margin: 0 0 16px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.features-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .all-models {
    padding: 10px 0;
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
  
  .list-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .header-actions {
    width: 100%;
    flex-wrap: wrap;
  }
  
  .search-input {
    width: 100%;
  }
}
</style> 