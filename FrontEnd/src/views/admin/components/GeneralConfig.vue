<template>
  <div class="general-config">
    <!-- 默认配置 -->
    <el-card class="config-card" shadow="never">
      <template #header>
        <div class="card-header">
          <el-icon><Setting /></el-icon>
          <span>默认配置</span>
          <el-tag size="small" type="info">系统默认参数</el-tag>
        </div>
      </template>
      
      <el-row :gutter="20">
        <!-- 默认LLM配置 -->
        <el-col :span="12">
          <div class="config-section">
            <h4>默认LLM配置</h4>
            <el-descriptions :column="1" border size="small">
              <el-descriptions-item label="模型名称">
                {{ generalConfig.default_llm.model_name }}
              </el-descriptions-item>
              <el-descriptions-item label="温度">
                {{ generalConfig.default_llm.temperature }}
              </el-descriptions-item>
              <el-descriptions-item label="Top P">
                {{ generalConfig.default_llm.top_p }}
              </el-descriptions-item>
              <el-descriptions-item label="频率惩罚">
                {{ generalConfig.default_llm.frequency_penalty }}
              </el-descriptions-item>
              <el-descriptions-item label="存在惩罚">
                {{ generalConfig.default_llm.presence_penalty }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </el-col>
        
        <!-- 默认Prompt配置 -->
        <el-col :span="12">
          <div class="config-section">
            <h4>默认Prompt配置</h4>
            <el-descriptions :column="1" border size="small">
              <el-descriptions-item label="相似度阈值">
                {{ generalConfig.default_prompt.similarity_threshold }}
              </el-descriptions-item>
              <el-descriptions-item label="Top N">
                {{ generalConfig.default_prompt.top_n }}
              </el-descriptions-item>
              <el-descriptions-item label="关键词权重">
                {{ generalConfig.default_prompt.keywords_similarity_weight }}
              </el-descriptions-item>
              <el-descriptions-item label="显示引用">
                {{ generalConfig.default_prompt.show_quote ? '是' : '否' }}
              </el-descriptions-item>
              <el-descriptions-item label="多轮优化">
                {{ generalConfig.default_prompt.refine_multiturn ? '是' : '否' }}
              </el-descriptions-item>
              <el-descriptions-item label="TTS">
                {{ generalConfig.default_prompt.tts ? '是' : '否' }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </el-col>
      </el-row>
      
      <!-- 默认Prompt内容 -->
      <div class="config-section">
        <h4>默认Prompt内容</h4>
        <el-row :gutter="20">
          <el-col :span="8">
            <div class="prompt-item">
              <label>开场白：</label>
              <div class="prompt-content">{{ generalConfig.default_prompt.opener }}</div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="prompt-item">
              <label>主要提示词：</label>
              <div class="prompt-content">{{ generalConfig.default_prompt.prompt }}</div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="prompt-item">
              <label>空响应提示：</label>
              <div class="prompt-content">{{ generalConfig.default_prompt.empty_response }}</div>
            </div>
          </el-col>
        </el-row>
      </div>
    </el-card>

    <!-- 助手类型配置 -->
    <el-card class="config-card" shadow="never">
      <template #header>
        <div class="card-header">
          <el-icon><ChatDotRound /></el-icon>
          <span>助手类型配置</span>
          <el-tag size="small" type="success">预定义助手类型</el-tag>
        </div>
      </template>
      
      <div class="assistant-types">
        <el-row :gutter="20">
          <el-col 
            v-for="assistant in generalConfig.assistant_types" 
            :key="assistant.name"
            :span="12"
            style="margin-bottom: 20px;"
          >
            <el-card class="assistant-card" shadow="hover">
              <template #header>
                <div class="assistant-header">
                  <div class="assistant-title">
                    <el-icon><ChatDotRound /></el-icon>
                    <span>{{ assistant.label }}</span>
                  </div>
                  <el-tag size="small" type="info">{{ assistant.name }}</el-tag>
                </div>
              </template>
              
              <div class="assistant-content">
                <p class="assistant-description">{{ assistant.description }}</p>
                
                <el-collapse>
                  <el-collapse-item title="LLM配置" name="llm">
                    <el-descriptions :column="2" border size="small">
                      <el-descriptions-item label="模型">
                        {{ assistant.config.llm.model_name }}
                      </el-descriptions-item>
                      <el-descriptions-item label="温度">
                        {{ assistant.config.llm.temperature }}
                      </el-descriptions-item>
                      <el-descriptions-item label="Top P">
                        {{ assistant.config.llm.top_p }}
                      </el-descriptions-item>
                      <el-descriptions-item label="频率惩罚">
                        {{ assistant.config.llm.frequency_penalty }}
                      </el-descriptions-item>
                      <el-descriptions-item label="存在惩罚">
                        {{ assistant.config.llm.presence_penalty }}
                      </el-descriptions-item>
                    </el-descriptions>
                  </el-collapse-item>
                  
                  <el-collapse-item title="Prompt配置" name="prompt">
                    <el-descriptions :column="2" border size="small">
                      <el-descriptions-item label="相似度阈值">
                        {{ assistant.config.prompt.similarity_threshold }}
                      </el-descriptions-item>
                      <el-descriptions-item label="Top N">
                        {{ assistant.config.prompt.top_n }}
                      </el-descriptions-item>
                      <el-descriptions-item label="关键词权重">
                        {{ assistant.config.prompt.keywords_similarity_weight }}
                      </el-descriptions-item>
                      <el-descriptions-item label="显示引用">
                        {{ assistant.config.prompt.show_quote ? '是' : '否' }}
                      </el-descriptions-item>
                      <el-descriptions-item label="多轮优化">
                        {{ assistant.config.prompt.refine_multiturn ? '是' : '否' }}
                      </el-descriptions-item>
                      <el-descriptions-item label="TTS">
                        {{ assistant.config.prompt.tts ? '是' : '否' }}
                      </el-descriptions-item>
                    </el-descriptions>
                  </el-collapse-item>
                  
                  <el-collapse-item title="Prompt内容" name="content">
                    <div class="prompt-details">
                      <div class="prompt-detail-item">
                        <label>开场白：</label>
                        <div class="prompt-text">{{ assistant.config.prompt.opener }}</div>
                      </div>
                      <div class="prompt-detail-item">
                        <label>主要提示词：</label>
                        <div class="prompt-text">{{ assistant.config.prompt.prompt }}</div>
                      </div>
                      <div class="prompt-detail-item">
                        <label>空响应提示：</label>
                        <div class="prompt-text">{{ assistant.config.prompt.empty_response }}</div>
                      </div>
                    </div>
                  </el-collapse-item>
                </el-collapse>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </el-card>

    <!-- 操作按钮 -->
    <div class="footer-actions">
      <el-button @click="exportConfig">
        <el-icon><Download /></el-icon> 导出配置
      </el-button>
      <el-button @click="resetConfig">
        <el-icon><Refresh /></el-icon> 重置配置
      </el-button>
      <el-button type="primary" @click="saveConfig">
        <el-icon><Check /></el-icon> 保存配置
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Setting, ChatDotRound, Download, Refresh, Check 
} from '@element-plus/icons-vue'
import { exportToCSV } from '@/utils/exportUtils'

// Props
const props = defineProps({
  generalConfig: {
    type: Object,
    required: true
  }
})

// Emits
const emit = defineEmits(['config-updated'])

// 方法
const exportConfig = () => {
  try {
    // 准备导出数据
    const exportData = [
      {
        配置类型: '默认LLM配置',
        模型名称: props.generalConfig.default_llm.model_name,
        温度: props.generalConfig.default_llm.temperature,
        'Top P': props.generalConfig.default_llm.top_p,
        频率惩罚: props.generalConfig.default_llm.frequency_penalty,
        存在惩罚: props.generalConfig.default_llm.presence_penalty
      },
      {
        配置类型: '默认Prompt配置',
        相似度阈值: props.generalConfig.default_prompt.similarity_threshold,
        'Top N': props.generalConfig.default_prompt.top_n,
        关键词权重: props.generalConfig.default_prompt.keywords_similarity_weight,
        显示引用: props.generalConfig.default_prompt.show_quote ? '是' : '否',
        多轮优化: props.generalConfig.default_prompt.refine_multiturn ? '是' : '否',
        TTS: props.generalConfig.default_prompt.tts ? '是' : '否'
      }
    ]

    // 添加助手类型配置
    props.generalConfig.assistant_types.forEach(assistant => {
      exportData.push({
        配置类型: `${assistant.label}配置`,
        助手名称: assistant.name,
        描述: assistant.description,
        模型名称: assistant.config.llm.model_name,
        温度: assistant.config.llm.temperature,
        'Top P': assistant.config.llm.top_p,
        相似度阈值: assistant.config.prompt.similarity_threshold,
        'Top N': assistant.config.prompt.top_n
      })
    })

    exportToCSV(exportData, '通用助手配置')
    ElMessage.success('配置导出成功')
  } catch (error) {
    ElMessage.error(`导出失败: ${error.message}`)
  }
}

const resetConfig = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要重置所有配置到默认值吗？此操作不可撤销。',
      '确认重置',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 这里可以调用API重置配置
    ElMessage.success('配置已重置')
    emit('config-updated', props.generalConfig)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('重置失败')
    }
  }
}

const saveConfig = () => {
  // 这里可以调用API保存配置
  ElMessage.success('配置保存成功')
  emit('config-updated', props.generalConfig)
}
</script>

<style scoped>
.general-config {
  padding: 20px 0;
}

.config-card {
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

.config-section {
  margin-bottom: 20px;
}

.config-section h4 {
  margin: 0 0 12px 0;
  color: #606266;
  font-size: 16px;
  font-weight: 600;
}

.prompt-item {
  margin-bottom: 16px;
}

.prompt-item label {
  display: block;
  margin-bottom: 8px;
  color: #606266;
  font-weight: 500;
  font-size: 14px;
}

.prompt-content {
  padding: 12px;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  font-size: 13px;
  line-height: 1.5;
  color: #606266;
  max-height: 80px;
  overflow-y: auto;
}

.assistant-types {
  margin-top: 20px;
}

.assistant-card {
  height: 100%;
  border: 1px solid #e4e7ed;
}

.assistant-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.assistant-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #303133;
}

.assistant-title .el-icon {
  color: #409eff;
}

.assistant-content {
  padding: 0;
}

.assistant-description {
  margin: 0 0 16px 0;
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
}

.prompt-details {
  padding: 16px 0;
}

.prompt-detail-item {
  margin-bottom: 16px;
}

.prompt-detail-item label {
  display: block;
  margin-bottom: 8px;
  color: #606266;
  font-weight: 500;
  font-size: 14px;
}

.prompt-text {
  padding: 12px;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  font-size: 13px;
  line-height: 1.5;
  color: #606266;
  max-height: 120px;
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
  .general-config {
    padding: 10px 0;
  }
  
  .assistant-types .el-col {
    width: 100% !important;
  }
  
  .footer-actions {
    flex-direction: column;
    align-items: center;
  }
}
</style> 