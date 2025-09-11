<template>
  <div class="chat-detail-edit">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-button @click="goBack" class="back-btn">
          <el-icon><Back /></el-icon>
          返回列表
        </el-button>
        <h1 class="page-title">
          <el-icon><ChatDotRound /></el-icon>
          {{ assistant?.name || '聊天助手详情' }}
        </h1>
      </div>
      <div class="header-right">
        <el-button @click="resetConfig" :disabled="!hasChanges">
          <el-icon><Refresh /></el-icon>
          重置
        </el-button>
        <el-button type="primary" @click="saveConfig" :loading="saving" :disabled="!hasChanges">
          <el-icon><Check /></el-icon>
          保存配置
        </el-button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>

    <!-- 主要内容 -->
    <div v-else-if="assistant" class="main-content">
      <el-row :gutter="20">
        <!-- 左侧：基本信息 -->
        <el-col :span="8">
          <el-card class="info-card" shadow="never">
            <template #header>
              <div class="card-header">
                <el-icon><ChatDotRound /></el-icon>
                <span>基本信息</span>
              </div>
            </template>
            
            <el-form :model="basicForm" label-width="100px">
              <el-form-item label="助手ID">
                <el-input v-model="assistant.chat_id" disabled />
              </el-form-item>
              
              <el-form-item label="助手名称">
                <el-input v-model="basicForm.name" placeholder="请输入助手名称" />
              </el-form-item>
              
              <el-form-item label="描述">
                <el-input 
                  v-model="basicForm.description" 
                  type="textarea" 
                  :rows="3"
                  placeholder="请输入助手描述" 
                />
              </el-form-item>
              
              <el-form-item label="助手类型">
                <el-tag :type="assistant.is_course_chat ? 'success' : 'info'">
                  {{ assistant.is_course_chat ? '课程助手' : '通用助手' }}
                </el-tag>
              </el-form-item>
              
              <el-form-item v-if="assistant.is_course_chat" label="课程信息">
                <div class="course-info">
                  <div class="course-title">{{ assistant.course_info?.course_title }}</div>
                  <div class="course-meta">
                    <span>教师: {{ assistant.course_info?.teacher_name }}</span>
                    <span>类型: {{ assistant.course_info?.chat_type_name }}</span>
                  </div>
                </div>
              </el-form-item>
            </el-form>
          </el-card>
        </el-col>

        <!-- 右侧：参数配置 -->
        <el-col :span="16">
          <!-- LLM配置 -->
          <el-card class="config-card" shadow="never">
            <template #header>
              <div class="card-header">
                <el-icon><Cpu /></el-icon>
                <span>LLM配置</span>
                <el-tag size="small" type="info" class="config-tag">AI模型参数</el-tag>
              </div>
            </template>
            
            <el-form :model="llmForm" label-width="120px">
              <el-form-item label="模型名称">
                <el-select v-model="llmForm.model_name" placeholder="选择模型">
                  <el-option label="deepseek-chat" value="deepseek-chat" />
                  <el-option label="gpt-3.5-turbo" value="gpt-3.5-turbo" />
                  <el-option label="gpt-4" value="gpt-4" />
                  <el-option label="claude-3" value="claude-3" />
                </el-select>
              </el-form-item>
              
              <el-form-item label="温度 (Temperature)">
                <div class="slider-container">
                  <el-slider
                    v-model="llmForm.temperature"
                    :min="0"
                    :max="2"
                    :step="0.1"
                    show-input
                    :show-input-controls="false"
                    input-size="small"
                    class="parameter-slider"
                  />
                  <div class="parameter-tip">
                    <span v-if="llmForm.temperature <= 0.1">低温度：适合需要精确答案的场景</span>
                    <span v-else-if="llmForm.temperature <= 0.3">中低温度：平衡准确性和创造性</span>
                    <span v-else-if="llmForm.temperature <= 0.7">中高温度：适合需要创造性的场景</span>
                    <span v-else>高温度：适合需要高度创造性的场景</span>
                  </div>
                </div>
              </el-form-item>
              
              <el-form-item label="Top P">
                <div class="slider-container">
                  <el-slider
                    v-model="llmForm.top_p"
                    :min="0"
                    :max="1"
                    :step="0.1"
                    show-input
                    :show-input-controls="false"
                    input-size="small"
                    class="parameter-slider"
                  />
                  <div class="parameter-tip">控制词汇选择的多样性，值越高越多样</div>
                </div>
              </el-form-item>
              
              <el-form-item label="频率惩罚">
                <div class="slider-container">
                  <el-slider
                    v-model="llmForm.frequency_penalty"
                    :min="0"
                    :max="2"
                    :step="0.1"
                    show-input
                    :show-input-controls="false"
                    input-size="small"
                    class="parameter-slider"
                  />
                  <div class="parameter-tip">减少重复词汇的使用</div>
                </div>
              </el-form-item>
              
              <el-form-item label="存在惩罚">
                <div class="slider-container">
                  <el-slider
                    v-model="llmForm.presence_penalty"
                    :min="0"
                    :max="2"
                    :step="0.1"
                    show-input
                    :show-input-controls="false"
                    input-size="small"
                    class="parameter-slider"
                  />
                  <div class="parameter-tip">鼓励模型谈论新话题</div>
                </div>
              </el-form-item>
            </el-form>
          </el-card>

          <!-- Prompt配置 -->
          <el-card class="config-card" shadow="never">
            <template #header>
              <div class="card-header">
                <el-icon><Edit /></el-icon>
                <span>Prompt配置</span>
                <el-tag size="small" type="warning" class="config-tag">提示词参数</el-tag>
              </div>
            </template>
            
            <el-form :model="promptForm" label-width="120px">
              <el-form-item label="开场白">
                <el-input 
                  v-model="promptForm.opener" 
                  type="textarea" 
                  :rows="3"
                  placeholder="请输入开场白" 
                />
              </el-form-item>
              
              <el-form-item label="主要提示词">
                <el-input 
                  v-model="promptForm.prompt" 
                  type="textarea" 
                  :rows="6"
                  placeholder="请输入主要提示词" 
                />
                <div class="parameter-tip">可以使用 {knowledge} 变量引用知识库内容</div>
              </el-form-item>
              
              <el-form-item label="空响应提示">
                <el-input 
                  v-model="promptForm.empty_response" 
                  type="textarea" 
                  :rows="2"
                  placeholder="当知识库中没有相关内容时的提示" 
                />
              </el-form-item>
              
              <el-form-item label="相似度阈值">
                <div class="slider-container">
                  <el-slider
                    v-model="promptForm.similarity_threshold"
                    :min="0"
                    :max="1"
                    :step="0.05"
                    show-input
                    :show-input-controls="false"
                    input-size="small"
                    class="parameter-slider"
                  />
                  <div class="parameter-tip">
                    <span v-if="promptForm.similarity_threshold <= 0.2">低阈值：返回更多相关内容</span>
                    <span v-else-if="promptForm.similarity_threshold <= 0.4">中等阈值：平衡相关性和准确性</span>
                    <span v-else>高阈值：只返回高度相关的内容</span>
                  </div>
                </div>
              </el-form-item>
              
              <el-form-item label="Top N">
                <el-input-number
                  v-model="promptForm.top_n"
                  :min="1"
                  :max="20"
                  :step="1"
                  size="small"
                />
                <div class="parameter-tip">从知识库中检索的相关文档数量</div>
              </el-form-item>
              
              <el-form-item label="关键词权重">
                <div class="slider-container">
                  <el-slider
                    v-model="promptForm.keywords_similarity_weight"
                    :min="0"
                    :max="1"
                    :step="0.1"
                    show-input
                    :show-input-controls="false"
                    input-size="small"
                    class="parameter-slider"
                  />
                  <div class="parameter-tip">关键词匹配在相似度计算中的权重</div>
                </div>
              </el-form-item>
              
              <el-form-item label="显示引用">
                <el-switch v-model="promptForm.show_quote" />
                <div class="parameter-tip">是否在回答中显示知识库的引用</div>
              </el-form-item>
              
              <el-form-item label="多轮优化">
                <el-switch v-model="promptForm.refine_multiturn" />
                <div class="parameter-tip">是否启用多轮对话优化</div>
              </el-form-item>
              
              <el-form-item label="TTS">
                <el-switch v-model="promptForm.tts" />
                <div class="parameter-tip">是否启用文本转语音功能</div>
              </el-form-item>
            </el-form>
          </el-card>

          <!-- 预设模板 -->
          <el-card class="config-card" shadow="never">
            <template #header>
              <div class="card-header">
                <el-icon><Setting /></el-icon>
                <span>预设配置模板</span>
                <el-tag size="small" type="success" class="config-tag">快速应用</el-tag>
              </div>
            </template>
            
            <div class="template-buttons">
              <el-button 
                v-for="template in configTemplates" 
                :key="template.name"
                @click="applyTemplate(template)"
                size="small"
                type="info"
                plain
              >
                {{ template.label }}
              </el-button>
            </div>
            
            <div class="template-description">
              <p>点击上面的按钮可以快速应用课程专用的助手配置模板，然后根据需要进行微调。</p>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 错误状态 -->
    <div v-else class="error-container">
      <el-empty description="助手信息加载失败" />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  ChatDotRound, Cpu, Edit, Setting, Back, Refresh, Check
} from '@element-plus/icons-vue'

// 路由
const route = useRoute()
const router = useRouter()

// 响应式数据
const loading = ref(true)
const saving = ref(false)
const assistant = ref(null)

// 表单数据
const basicForm = reactive({
  name: '',
  description: ''
})

const llmForm = reactive({
  model_name: 'deepseek-chat',
  temperature: 0.3,
  top_p: 0.8,
  frequency_penalty: 0.1,
  presence_penalty: 0.1
})

const promptForm = reactive({
  opener: '',
  prompt: '',
  empty_response: '',
  similarity_threshold: 0.2,
  top_n: 6,
  keywords_similarity_weight: 0.3,
  show_quote: true,
  refine_multiturn: true,
  tts: false
})

// 预设配置模板
const configTemplates = [
  {
    name: 'general',
    label: '通用助手',
    config: {
      llm: {
        model_name: "deepseek-chat",
        temperature: 0.3,
        top_p: 0.8,
        frequency_penalty: 0.1,
        presence_penalty: 0.1
      },
      prompt: {
        opener: "你好！我是这门课程的智能助手，可以帮你解答课程相关的问题。请告诉我你想了解什么？",
        prompt: "你是一个专业的课程助手。请基于知识库中的课程内容来回答问题。回答要准确、详细，并考虑聊天历史。如果知识库中没有相关信息，请明确说明。",
        empty_response: "抱歉，知识库中没有找到相关信息。请换个问题试试，或者联系老师获取帮助。",
        similarity_threshold: 0.2,
        top_n: 6,
        keywords_similarity_weight: 0.3,
        show_quote: true,
        refine_multiturn: true,
        tts: false
      }
    }
  },
  {
    name: 'analysis',
    label: '学情分析助手',
    config: {
      llm: {
        model_name: "deepseek-chat",
        temperature: 0.1,
        top_p: 0.3,
        frequency_penalty: 0.7,
        presence_penalty: 0.4
      },
      prompt: {
        opener: "你好！我是学情分析助手，专门负责分析学生的学习情况和提供个性化建议。请提供学生的作业数据或学习表现，我将为你进行详细分析。",
        prompt: "你是一个专业的学情分析专家。请基于提供的数据分析学生的学习情况，包括：1. 知识点掌握程度评估 2. 学习优势和不足 3. 个性化学习建议 4. 改进方向。分析要客观、具体，并提供可操作的建议。",
        empty_response: "抱歉，没有足够的数据进行分析。请提供更多学生的学习数据。",
        similarity_threshold: 0.3,
        top_n: 8,
        keywords_similarity_weight: 0.4,
        show_quote: true,
        refine_multiturn: true,
        tts: false
      }
    }
  },
  {
    name: 'preparation',
    label: '教师备课助手',
    config: {
      llm: {
        model_name: "deepseek-chat",
        temperature: 0.4,
        top_p: 0.9,
        frequency_penalty: 0.2,
        presence_penalty: 0.1
      },
      prompt: {
        opener: "你好！我是教师备课助手，专门帮助教师设计教案和教学活动。请告诉我你要备课的章节或主题，我将为你提供详细的备课建议。",
        prompt: `你是一个教师备课助理，你根据教师上传的课程大纲和课程知识点汇总帮助教师自动生成教学内容，包括本周课堂知识点讲解，教学关键内容，实训练习与指导、时间分布等。
        以下是知识库：
        {knowledge}
        以上是知识库。
生成的教学内容以下几块为核心：一、上周知识点回顾，二、本周知识点讲解，三、教学关键内容（板书/PPT重点）（注意以mermaid形式生成，Mermaid 的序列图语法对中文符号敏感），四、实训练习与指导，五、课堂时间分布，六、相关知识点拓展`,
        empty_response: "抱歉，没有找到相关的课程内容。请检查课程资料是否完整。",
        similarity_threshold: 0.25,
        top_n: 10,
        keywords_similarity_weight: 0.3,
        show_quote: true,
        refine_multiturn: true,
        tts: false
      }
    }
  },
  {
    name: 'qa',
    label: '学生答疑助手',
    config: {
      llm: {
        model_name: "deepseek-chat",
        temperature: 0.2,
        top_p: 0.7,
        frequency_penalty: 0.3,
        presence_penalty: 0.2
      },
      prompt: {
        opener: "你好！我是学生答疑助手，专门回答同学们的课程问题。请直接提出你的问题，我会尽力为你解答！",
        prompt: "你是一个耐心的学习导师。请基于课程内容回答学生的问题，要求：1. 回答要清晰易懂 2. 提供解题思路和方法 3. 适当举例说明 4. 鼓励学生思考 5. 如果问题超出课程范围，引导到相关知识点。",
        empty_response: "这个问题可能超出了当前课程的范围。建议你复习相关知识点，或者向老师请教。",
        similarity_threshold: 0.2,
        top_n: 6,
        keywords_similarity_weight: 0.3,
        show_quote: true,
        refine_multiturn: true,
        tts: false
      }
    }
  },
  {
    name: 'grading',
    label: '作业批改助手',
    config: {
      llm: {
        model_name: "deepseek-chat",
        temperature: 0.05,
        top_p: 0.2,
        frequency_penalty: 0.8,
        presence_penalty: 0.5
      },
      prompt: {
        opener: "你好！我是作业批改助手，专门负责批改作业和提供反馈。请提供作业题目和参考答案，我将为你进行专业批改。",
        prompt: "你是一个严格的作业批改专家。请严格按照参考答案批改作业，要求：1. 客观公正评分 2. 指出具体错误 3. 提供改进建议 4. 鼓励学生进步 5. 保持评分标准一致。对于主观题，要给出详细的评价理由。",
        empty_response: "无法进行批改，请确保提供了完整的作业内容和参考答案。",
        similarity_threshold: 0.4,
        top_n: 8,
        keywords_similarity_weight: 0.4,
        show_quote: true,
        refine_multiturn: true,
        tts: false
      }
    }
  }
]

// 计算属性
const hasChanges = computed(() => {
  if (!assistant.value) return false
  
  // 检查基本信息是否有变化
  const basicChanged = basicForm.name !== assistant.value.name || 
                      basicForm.description !== assistant.value.description
  
  // 检查LLM配置是否有变化
  const llmChanged = JSON.stringify(llmForm) !== JSON.stringify(assistant.value.llm || {})
  
  // 检查Prompt配置是否有变化
  const promptChanged = JSON.stringify(promptForm) !== JSON.stringify(assistant.value.prompt || {})
  
  return basicChanged || llmChanged || promptChanged
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
const loadAssistantDetail = async () => {
  const chatId = route.params.chatId
  if (!chatId) {
    ElMessage.error('助手ID不能为空')
    return
  }
  
  loading.value = true
  try {
    const response = await apiCall(`/chat/assistants/${chatId}`)
    assistant.value = response.data
    
    // 初始化表单数据
    initFormData()
  } catch (error) {
    ElMessage.error('加载助手详情失败')
    console.error('Load assistant detail error:', error)
  } finally {
    loading.value = false
  }
}

const initFormData = () => {
  if (!assistant.value) return
  
  // 基本信息
  basicForm.name = assistant.value.name || ''
  basicForm.description = assistant.value.description || ''
  
  // LLM配置
  if (assistant.value.llm) {
    Object.assign(llmForm, assistant.value.llm)
  }
  
  // Prompt配置
  if (assistant.value.prompt) {
    Object.assign(promptForm, assistant.value.prompt)
  }
}

const applyTemplate = (template) => {
  ElMessageBox.confirm(
    `确定要应用"${template.label}"模板吗？这将覆盖当前的配置。`,
    '应用模板',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    // 应用模板配置
    Object.assign(llmForm, template.config.llm)
    Object.assign(promptForm, template.config.prompt)
    
    ElMessage.success(`已应用${template.label}模板`)
  }).catch(() => {
    // 用户取消
  })
}

const resetConfig = () => {
  ElMessageBox.confirm(
    '确定要重置为原始配置吗？',
    '重置配置',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    initFormData()
    ElMessage.success('配置已重置')
  }).catch(() => {
    // 用户取消
  })
}

const saveConfig = async () => {
  try {
    saving.value = true
    
    const updateData = {
      description: basicForm.description,
      llm: llmForm,
      prompt: promptForm
    }
    
    await apiCall(`/chat/assistants/${assistant.value.chat_id}`, {
      method: 'PUT',
      body: JSON.stringify(updateData)
    })
    
    // 更新本地数据
    assistant.value.description = basicForm.description
    assistant.value.llm = { ...llmForm }
    assistant.value.prompt = { ...promptForm }
    
    ElMessage.success('配置保存成功')
  } catch (error) {
    if (error.message) {
      ElMessage.error(error.message)
    } else {
      ElMessage.error('保存配置失败')
    }
    console.error('Save config error:', error)
  } finally {
    saving.value = false
  }
}

const goBack = () => {
  router.push('/dashboard/chat-management')
}

// 生命周期
onMounted(() => {
  loadAssistantDetail()
})
</script>

<style scoped>
.chat-detail-edit {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-title {
  display: flex;
  align-items: center;
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.page-title .el-icon {
  margin-right: 8px;
  color: #409eff;
}

.header-right {
  display: flex;
  gap: 12px;
}

.loading-container {
  padding: 40px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.main-content {
  margin-bottom: 20px;
}

.info-card,
.config-card {
  margin-bottom: 20px;
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

.config-tag {
  margin-left: auto;
}

.course-info {
  padding: 12px;
  background: #f8f9fa;
  border-radius: 4px;
}

.course-title {
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.course-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #909399;
}

.slider-container {
  width: 100%;
}

.parameter-slider {
  margin-bottom: 8px;
}

.parameter-tip {
  font-size: 12px;
  color: #909399;
  line-height: 1.4;
  margin-top: 4px;
}

.template-buttons {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.template-description {
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
}

.template-description p {
  margin: 0;
}

.error-container {
  padding: 40px;
  text-align: center;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-detail-edit {
    padding: 10px;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .header-left {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .template-buttons {
    flex-direction: column;
  }
}
</style> 