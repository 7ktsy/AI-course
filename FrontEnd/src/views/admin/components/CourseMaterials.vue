<template>
  <div class="course-materials">
    <div class="materials-header">
      <h2>{{ course.title }} - 课程资料</h2>
      <p class="subtitle">共 {{ course.materials?.length || 0 }} 个资料文件</p>
    </div>

    <div class="materials-content">
      <div v-if="course.materials && course.materials.length > 0">
        <div class="materials-actions">
          <el-button 
            type="primary" 
            size="small" 
            @click="batchDownload"
            :disabled="selectedMaterials.length === 0"
          >
            <el-icon><Download /></el-icon>
            批量下载 ({{ selectedMaterials.length }})
          </el-button>
          <el-button 
            type="success" 
            size="small" 
            @click="selectAll"
          >
            <el-icon><Select /></el-icon>
            全选
          </el-button>
          <el-button 
            type="info" 
            size="small" 
            @click="clearSelection"
          >
            <el-icon><Close /></el-icon>
            清空选择
          </el-button>
        </div>
        
        <el-table 
          :data="course.materials" 
          stripe 
          class="materials-table"
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="id" label="ID" width="80" />
          
          <el-table-column label="资料信息" min-width="300">
            <template #default="{ row }">
              <div class="material-info">
                <div class="material-title">{{ row.title }}</div>
                <div class="material-description">{{ row.description }}</div>
                <div class="material-filename">
                  <el-icon><Document /></el-icon>
                  {{ row.filename }}
                </div>
              </div>
            </template>
          </el-table-column>

          <el-table-column prop="status" label="状态" width="120" align="center">
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

          <el-table-column prop="rag_doc_id" label="RAG文档ID" width="150">
            <template #default="{ row }">
              <el-tag v-if="row.rag_doc_id" size="small" type="success">
                {{ row.rag_doc_id }}
              </el-tag>
              <span v-else class="no-doc-id">未设置</span>
            </template>
          </el-table-column>

          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-tooltip content="查看详情" placement="top">
                  <el-button 
                    size="small" 
                    type="primary" 
                    text
                    @click="viewMaterialDetail(row)"
                  >
                    <el-icon><View /></el-icon>
                  </el-button>
                </el-tooltip>
                <el-tooltip content="下载文件" placement="top">
                  <el-button 
                    size="small" 
                    type="success" 
                    text
                    @click="downloadMaterial(row)"
                  >
                    <el-icon><Download /></el-icon>
                  </el-button>
                </el-tooltip>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <div v-else class="empty-state">
        <el-empty description="暂无课程资料" />
      </div>
    </div>

    <!-- 资料详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="资料详情"
      width="600px"
      :close-on-click-modal="false"
    >
      <div v-if="selectedMaterial" class="material-detail">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="资料ID">{{ selectedMaterial.id }}</el-descriptions-item>
          <el-descriptions-item label="标题">{{ selectedMaterial.title }}</el-descriptions-item>
          <el-descriptions-item label="描述">{{ selectedMaterial.description }}</el-descriptions-item>
          <el-descriptions-item label="文件名">{{ selectedMaterial.filename }}</el-descriptions-item>
          <el-descriptions-item label="文件路径">{{ selectedMaterial.file_path }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(selectedMaterial.status)">
              {{ getStatusLabel(selectedMaterial.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="上传时间">{{ formatDate(selectedMaterial.uploadtime) }}</el-descriptions-item>
          <el-descriptions-item label="RAG文档ID">
            {{ selectedMaterial.rag_doc_id || '未设置' }}
          </el-descriptions-item>
          <el-descriptions-item label="错误信息" v-if="selectedMaterial.error_msg">
            <div class="error-message">{{ selectedMaterial.error_msg }}</div>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>

    <!-- 底部操作按钮 -->
    <div class="footer-actions">
      <el-button @click="$emit('close')">关闭</el-button>
      <el-button type="primary" @click="exportMaterials">导出资料列表</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Document, View, Download, Select, Close 
} from '@element-plus/icons-vue'
import { downloadFile, batchDownloadFiles, exportMaterials as exportMaterialsData } from '@/utils/exportUtils'

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
const selectedMaterial = ref(null)
const selectedMaterials = ref([]) // 新增：用于批量选择

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

const viewMaterialDetail = (material) => {
  selectedMaterial.value = material
  detailDialogVisible.value = true
}

const downloadMaterial = async (material) => {
  try {
    // 检查材料是否有有效的ID
    if (!material.id) {
      ElMessage.error('资料ID无效')
      return
    }

    // 尝试不同的API路径
    let downloadUrl = `http://127.0.0.1:8000/material/download/${material.id}`
    
    // 如果第一个路径失败，尝试其他可能的路径
    try {
      await downloadFile(downloadUrl, material.filename || material.title)
      ElMessage.success('文件下载成功')
    } catch (error) {
      // 尝试其他可能的API路径
      const alternativeUrls = [
        `http://127.0.0.1:8000/api/material/download/${material.id}`,
        `http://127.0.0.1:8000/course/material/download/${material.id}`,
        `http://127.0.0.1:8000/material/${material.id}/download`
      ]
      
      let success = false
      for (const url of alternativeUrls) {
        try {
          await downloadFile(url, material.filename || material.title)
          ElMessage.success('文件下载成功')
          success = true
          break
        } catch (altError) {
          console.log(`尝试路径 ${url} 失败:`, altError)
          continue
        }
      }
      
      if (!success) {
        throw new Error('所有下载路径都失败')
      }
    }
  } catch (error) {
    ElMessage.error(`文件下载失败: ${error.message}`)
    console.error('Download error:', error)
  }
}

const batchDownload = async () => {
  if (selectedMaterials.value.length === 0) {
    ElMessage.warning('请选择要下载的资料')
    return
  }

  try {
    const selectedIds = selectedMaterials.value.map(material => material.id)
    
    // 检查是否有有效的ID
    if (selectedIds.some(id => !id)) {
      ElMessage.error('部分资料ID无效，无法下载')
      return
    }
    
    const count = await batchDownloadFiles(selectedIds, '批量下载')
    ElMessage.success(`成功下载 ${count} 个文件`)
    selectedMaterials.value = [] // 清空选择
  } catch (error) {
    ElMessage.error(`批量下载失败: ${error.message}`)
    console.error('Batch download error:', error)
  }
}

const selectAll = () => {
  selectedMaterials.value = [...props.course.materials]
}

const clearSelection = () => {
  selectedMaterials.value = []
}

const handleSelectionChange = (selection) => {
  selectedMaterials.value = selection
}

const exportMaterials = () => {
  try {
    if (!props.course.materials || props.course.materials.length === 0) {
      ElMessage.warning('暂无资料可导出')
      return
    }
    
    const count = exportMaterialsData(props.course.materials, props.course.title)
    ElMessage.success(`成功导出 ${count} 个资料信息`)
  } catch (error) {
    ElMessage.error('导出失败：' + error.message)
  }
}
</script>

<style scoped>
.course-materials {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.materials-header {
  margin-bottom: 20px;
  text-align: center;
}

.materials-header h2 {
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

.materials-content {
  margin-bottom: 20px;
}

.materials-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-bottom: 15px;
  padding: 10px 0;
  border-bottom: 1px solid #e4e7ed;
  background: white;
}

.materials-table {
  margin-bottom: 20px;
}

.materials-table :deep(.el-table__header) {
  background-color: #f8f9fa;
}

.materials-table :deep(.el-table__header th) {
  background-color: #f8f9fa;
  color: #606266;
  font-weight: 600;
  border-bottom: 2px solid #e4e7ed;
}

.material-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.material-title {
  font-weight: 600;
  color: #303133;
  font-size: 14px;
}

.material-description {
  color: #606266;
  font-size: 12px;
  line-height: 1.4;
}

.material-filename {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #909399;
  font-size: 12px;
}

.material-filename .el-icon {
  font-size: 14px;
}

.no-doc-id {
  color: #909399;
  font-style: italic;
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

.material-detail {
  padding: 20px 0;
}

.error-message {
  color: #f56c6c;
  background: #fef0f0;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 12px;
  line-height: 1.4;
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
  .course-materials {
    padding: 10px;
  }
  
  .materials-table {
    font-size: 12px;
  }
  
  .footer-actions {
    flex-direction: column;
    align-items: center;
  }
}
</style> 