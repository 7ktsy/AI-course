<template>
  <div class="chat-detail">
    <div class="detail-container">
      <!-- 基本信息 -->
      <el-card class="info-card" shadow="never">
        <template #header>
          <div class="card-header">
            <el-icon><ChatDotRound /></el-icon>
            <span>基本信息</span>
          </div>
        </template>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="助手ID">{{ assistant.chat_id }}</el-descriptions-item>
          <el-descriptions-item label="助手名称">{{ assistant.name }}</el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">{{ assistant.description }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(assistant.create_date) }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ formatDate(assistant.update_date) }}</el-descriptions-item>
          <el-descriptions-item label="助手类型">
            <el-tag :type="assistant.is_course_chat ? 'success' : 'info'">
              {{ assistant.is_course_chat ? '课程助手' : '通用助手' }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 课程信息 -->
      <el-card class="info-card" shadow="never" v-if="assistant.is_course_chat && assistant.course_info">
        <template #header>
          <div class="card-header">
            <el-icon><Reading /></el-icon>
            <span>课程信息</span>
          </div>
        </template>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="课程ID">{{ assistant.course_info.course_id }}</el-descriptions-item>
          <el-descriptions-item label="课程名称">{{ assistant.course_info.course_title }}</el-descriptions-item>
          <el-descriptions-item label="教师ID">{{ assistant.course_info.teacher_id }}</el-descriptions-item>
          <el-descriptions-item label="教师姓名">{{ assistant.course_info.teacher_name }}</el-descriptions-item>
          <el-descriptions-item label="助手类型">{{ assistant.course_info.chat_type_name }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ assistant.course_info.created_at }}</el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- LLM配置 -->
      <el-card class="info-card" shadow="never">
        <template #header>
          <div class="card-header">
            <el-icon><Cpu /></el-icon>
            <span>LLM配置</span>
          </div>
        </template>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="模型名称">{{ assistant.llm?.model_name || '未设置' }}</el-descriptions-item>
          <el-descriptions-item label="温度">{{ assistant.llm?.temperature || '未设置' }}</el-descriptions-item>
          <el-descriptions-item label="Top P">{{ assistant.llm?.top_p || '未设置' }}</el-descriptions-item>
          <el-descriptions-item label="频率惩罚">{{ assistant.llm?.frequency_penalty || '未设置' }}</el-descriptions-item>
          <el-descriptions-item label="存在惩罚">{{ assistant.llm?.presence_penalty || '未设置' }}</el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- Prompt配置 -->
      <el-card class="info-card" shadow="never">
        <template #header>
          <div class="card-header">
            <el-icon><Edit /></el-icon>
            <span>Prompt配置</span>
          </div>
        </template>
        <div class="prompt-config">
          <div class="config-section">
            <h4>开场白</h4>
            <div class="config-content">{{ assistant.prompt?.opener || '未设置' }}</div>
          </div>
          
          <div class="config-section">
            <h4>主要提示词</h4>
            <div class="config-content">{{ assistant.prompt?.prompt || '未设置' }}</div>
          </div>
          
          <div class="config-section">
            <h4>空响应提示</h4>
            <div class="config-content">{{ assistant.prompt?.empty_response || '未设置' }}</div>
          </div>
          
          <el-descriptions :column="3" border style="margin-top: 20px;">
            <el-descriptions-item label="相似度阈值">{{ assistant.prompt?.similarity_threshold || '未设置' }}</el-descriptions-item>
            <el-descriptions-item label="Top N">{{ assistant.prompt?.top_n || '未设置' }}</el-descriptions-item>
            <el-descriptions-item label="关键词权重">{{ assistant.prompt?.keywords_similarity_weight || '未设置' }}</el-descriptions-item>
            <el-descriptions-item label="显示引用">
              <el-tag :type="assistant.prompt?.show_quote ? 'success' : 'info'">
                {{ assistant.prompt?.show_quote ? '是' : '否' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="多轮优化">
              <el-tag :type="assistant.prompt?.refine_multiturn ? 'success' : 'info'">
                {{ assistant.prompt?.refine_multiturn ? '是' : '否' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="TTS">
              <el-tag :type="assistant.prompt?.tts ? 'success' : 'info'">
                {{ assistant.prompt?.tts ? '是' : '否' }}
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </el-card>

      <!-- 数据集信息 -->
      <el-card class="info-card" shadow="never">
        <template #header>
          <div class="card-header">
            <el-icon><Document /></el-icon>
            <span>数据集信息</span>
          </div>
        </template>
        <div v-if="assistant.dataset_ids && assistant.dataset_ids.length > 0">
          <el-tag 
            v-for="dataset_id in assistant.dataset_ids" 
            :key="dataset_id"
            size="small"
            type="success"
            style="margin-right: 8px; margin-bottom: 8px;"
          >
            {{ dataset_id }}
          </el-tag>
        </div>
        <div v-else class="empty-state">
          <el-empty description="未配置数据集" />
        </div>
      </el-card>

      <!-- 配置建议 -->
      <el-card class="info-card" shadow="never">
        <template #header>
          <div class="card-header">
            <el-icon><Star /></el-icon>
            <span>配置建议</span>
          </div>
        </template>
        <div class="suggestions">
          <div class="suggestion-item">
            <el-icon class="suggestion-icon"><InfoFilled /></el-icon>
            <div class="suggestion-content">
              <strong>温度设置：</strong>
              <span v-if="assistant.llm?.temperature <= 0.1">当前设置为低温度，适合需要精确答案的场景</span>
              <span v-else-if="assistant.llm?.temperature <= 0.3">当前设置为中低温度，适合需要平衡准确性和创造性的场景</span>
              <span v-else-if="assistant.llm?.temperature <= 0.7">当前设置为中高温度，适合需要创造性的场景</span>
              <span v-else>当前设置为高温度，适合需要高度创造性的场景</span>
            </div>
          </div>
          
          <div class="suggestion-item">
            <el-icon class="suggestion-icon"><InfoFilled /></el-icon>
            <div class="suggestion-content">
              <strong>相似度阈值：</strong>
              <span v-if="assistant.prompt?.similarity_threshold <= 0.2">当前设置为低阈值，会返回更多相关内容</span>
              <span v-else-if="assistant.prompt?.similarity_threshold <= 0.4">当前设置为中等阈值，平衡相关性和准确性</span>
              <span v-else>当前设置为高阈值，只返回高度相关的内容</span>
            </div>
          </div>
          
          <div class="suggestion-item">
            <el-icon class="suggestion-icon"><InfoFilled /></el-icon>
            <div class="suggestion-content">
              <strong>Top N设置：</strong>
              <span v-if="assistant.prompt?.top_n <= 3">当前设置为低数量，响应速度较快但可能信息有限</span>
              <span v-else-if="assistant.prompt?.top_n <= 8">当前设置为中等数量，平衡响应速度和信息丰富度</span>
              <span v-else>当前设置为高数量，信息丰富但响应可能较慢</span>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 底部操作按钮 -->
    <div class="footer-actions">
      <el-button @click="$emit('close')">关闭</el-button>
      <el-button type="primary" @click="exportConfig">导出配置</el-button>
    </div>
  </div>
</template>

<script setup>
import { ElMessage } from 'element-plus'
import { 
  ChatDotRound, Reading, Cpu, Edit, Document, Star, InfoFilled 
} from '@element-plus/icons-vue'

// Props
const props = defineProps({
  assistant: {
    type: Object,
    required: true
  }
})

// Emits
const emit = defineEmits(['close'])

// 方法
const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString('zh-CN')
}

const exportConfig = () => {
  const config = {
    chat_id: props.assistant.chat_id,
    name: props.assistant.name,
    description: props.assistant.description,
    llm: props.assistant.llm,
    prompt: props.assistant.prompt,
    dataset_ids: props.assistant.dataset_ids,
    course_info: props.assistant.course_info
  }
  
  const blob = new Blob([JSON.stringify(config, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${props.assistant.name}_config.json`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
  
  ElMessage.success('配置导出成功')
}
</script>

<style scoped>
.chat-detail {
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

.prompt-config {
  padding: 20px 0;
}

.config-section {
  margin-bottom: 20px;
}

.config-section h4 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 14px;
  font-weight: 600;
}

.config-content {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 4px;
  font-size: 12px;
  line-height: 1.5;
  color: #606266;
  white-space: pre-wrap;
  max-height: 100px;
  overflow-y: auto;
}

.suggestions {
  padding: 20px 0;
}

.suggestion-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 16px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #409eff;
}

.suggestion-icon {
  color: #409eff;
  font-size: 16px;
  margin-top: 2px;
}

.suggestion-content {
  flex: 1;
  font-size: 14px;
  line-height: 1.5;
  color: #606266;
}

.suggestion-content strong {
  color: #303133;
  font-weight: 600;
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
  .chat-detail {
    padding: 10px;
  }
  
  .suggestion-item {
    flex-direction: column;
    gap: 8px;
  }
  
  .footer-actions {
    flex-direction: column;
    align-items: center;
  }
}
</style> 