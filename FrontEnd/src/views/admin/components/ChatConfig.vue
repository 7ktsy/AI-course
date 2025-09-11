<template>
  <div class="chat-config">
    <el-form 
      ref="configFormRef" 
      :model="configForm" 
      :rules="configRules" 
      label-width="120px"
      class="config-form"
    >
      <!-- 基本信息 -->
      <el-card class="config-card" shadow="never">
        <template #header>
          <div class="card-header">
            <el-icon><ChatDotRound /></el-icon>
            <span>基本信息</span>
          </div>
        </template>
        
        <el-form-item label="助手名称" prop="name">
          <el-input v-model="configForm.name" placeholder="请输入助手名称" />
        </el-form-item>
        
        <el-form-item label="描述" prop="description">
          <el-input 
            v-model="configForm.description" 
            type="textarea" 
            :rows="3"
            placeholder="请输入助手描述" 
          />
        </el-form-item>
      </el-card>

      <!-- LLM配置 -->
      <el-card class="config-card" shadow="never">
        <template #header>
          <div class="card-header">
            <el-icon><Cpu /></el-icon>
            <span>LLM配置</span>
          </div>
        </template>
        
        <el-form-item label="模型名称" prop="llm.model_name">
          <el-select v-model="configForm.llm.model_name" placeholder="选择模型">
            <el-option label="deepseek-chat" value="deepseek-chat" />
            <el-option label="gpt-3.5-turbo" value="gpt-3.5-turbo" />
            <el-option label="gpt-4" value="gpt-4" />
            <el-option label="claude-3" value="claude-3" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="温度" prop="llm.temperature">
          <el-slider
            v-model="configForm.llm.temperature"
            :min="0"
            :max="2"
            :step="0.1"
            show-input
            :show-input-controls="false"
            input-size="small"
          />
          <div class="param-tip">
            <span v-if="configForm.llm.temperature <= 0.1">低温度：适合需要精确答案的场景</span>
            <span v-else-if="configForm.llm.temperature <= 0.3">中低温度：平衡准确性和创造性</span>
            <span v-else-if="configForm.llm.temperature <= 0.7">中高温度：适合需要创造性的场景</span>
            <span v-else>高温度：适合需要高度创造性的场景</span>
          </div>
        </el-form-item>
        
        <el-form-item label="Top P" prop="llm.top_p">
          <el-slider
            v-model="configForm.llm.top_p"
            :min="0"
            :max="1"
            :step="0.1"
            show-input
            :show-input-controls="false"
            input-size="small"
          />
          <div class="param-tip">控制词汇选择的多样性，值越高越多样</div>
        </el-form-item>
        
        <el-form-item label="频率惩罚" prop="llm.frequency_penalty">
          <el-slider
            v-model="configForm.llm.frequency_penalty"
            :min="0"
            :max="2"
            :step="0.1"
            show-input
            :show-input-controls="false"
            input-size="small"
          />
          <div class="param-tip">减少重复词汇的使用</div>
        </el-form-item>
        
        <el-form-item label="存在惩罚" prop="llm.presence_penalty">
          <el-slider
            v-model="configForm.llm.presence_penalty"
            :min="0"
            :max="2"
            :step="0.1"
            show-input
            :show-input-controls="false"
            input-size="small"
          />
          <div class="param-tip">鼓励模型谈论新话题</div>
        </el-form-item>
      </el-card>

      <!-- Prompt配置 -->
      <el-card class="config-card" shadow="never">
        <template #header>
          <div class="card-header">
            <el-icon><Edit /></el-icon>
            <span>Prompt配置</span>
          </div>
        </template>
        
        <el-form-item label="开场白" prop="prompt.opener">
          <el-input 
            v-model="configForm.prompt.opener" 
            type="textarea" 
            :rows="3"
            placeholder="请输入开场白" 
          />
        </el-form-item>
        
        <el-form-item label="主要提示词" prop="prompt.prompt">
          <el-input 
            v-model="configForm.prompt.prompt" 
            type="textarea" 
            :rows="6"
            placeholder="请输入主要提示词" 
          />
          <div class="param-tip">可以使用 {knowledge} 变量引用知识库内容</div>
        </el-form-item>
        
        <el-form-item label="空响应提示" prop="prompt.empty_response">
          <el-input 
            v-model="configForm.prompt.empty_response" 
            type="textarea" 
            :rows="2"
            placeholder="当知识库中没有相关内容时的提示" 
          />
        </el-form-item>
        
        <el-form-item label="相似度阈值" prop="prompt.similarity_threshold">
          <el-slider
            v-model="configForm.prompt.similarity_threshold"
            :min="0"
            :max="1"
            :step="0.05"
            show-input
            :show-input-controls="false"
            input-size="small"
          />
          <div class="param-tip">
            <span v-if="configForm.prompt.similarity_threshold <= 0.2">低阈值：返回更多相关内容</span>
            <span v-else-if="configForm.prompt.similarity_threshold <= 0.4">中等阈值：平衡相关性和准确性</span>
            <span v-else>高阈值：只返回高度相关的内容</span>
          </div>
        </el-form-item>
        
        <el-form-item label="Top N" prop="prompt.top_n">
          <el-input-number
            v-model="configForm.prompt.top_n"
            :min="1"
            :max="20"
            :step="1"
            size="small"
          />
          <div class="param-tip">从知识库中检索的相关文档数量</div>
        </el-form-item>
        
        <el-form-item label="关键词权重" prop="prompt.keywords_similarity_weight">
          <el-slider
            v-model="configForm.prompt.keywords_similarity_weight"
            :min="0"
            :max="1"
            :step="0.1"
            show-input
            :show-input-controls="false"
            input-size="small"
          />
          <div class="param-tip">关键词匹配在相似度计算中的权重</div>
        </el-form-item>
        
        <el-form-item label="显示引用" prop="prompt.show_quote">
          <el-switch v-model="configForm.prompt.show_quote" />
          <div class="param-tip">是否在回答中显示知识库的引用</div>
        </el-form-item>
        
        <el-form-item label="多轮优化" prop="prompt.refine_multiturn">
          <el-switch v-model="configForm.prompt.refine_multiturn" />
          <div class="param-tip">是否启用多轮对话优化</div>
        </el-form-item>
        
        <el-form-item label="TTS" prop="prompt.tts">
          <el-switch v-model="configForm.prompt.tts" />
          <div class="param-tip">是否启用文本转语音功能</div>
        </el-form-item>
      </el-card>

      <!-- 预设配置模板 -->
      <el-card class="config-card" shadow="never">
        <template #header>
          <div class="card-header">
            <el-icon><Setting /></el-icon>
            <span>预设配置模板</span>
          </div>
        </template>
        
        <div class="template-buttons">
          <el-button 
            v-for="template in configTemplates" 
            :key="template.name"
            @click="applyTemplate(template)"
            size="small"
          >
            {{ template.label }}
          </el-button>
        </div>
        
        <div class="template-description">
          <p>点击上面的按钮可以快速应用课程专用的助手配置模板，然后根据需要进行微调。</p>
          <p><strong>助手类型说明：</strong></p>
          <ul>
            <li><strong>通用助手：</strong>适用于一般课程问答和知识查询</li>
            <li><strong>学情分析助手：</strong>专门用于分析学生学习情况和提供个性化建议</li>
            <li><strong>教师备课助手：</strong>帮助教师设计教案和教学活动</li>
            <li><strong>学生答疑助手：</strong>专门回答学生的课程问题</li>
            <li><strong>作业批改助手：</strong>负责批改作业和提供反馈</li>
          </ul>
        </div>
      </el-card>
    </el-form>

    <!-- 底部操作按钮 -->
    <div class="footer-actions">
      <el-button @click="$emit('close')">取消</el-button>
      <el-button @click="resetConfig">重置</el-button>
      <el-button type="primary" @click="saveConfig" :loading="saving">保存配置</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  ChatDotRound, Cpu, Edit, Setting 
} from '@element-plus/icons-vue'

// Props
const props = defineProps({
  assistant: {
    type: Object,
    required: true
  }
})

// Emits
const emit = defineEmits(['close', 'updated'])

// 响应式数据
const configFormRef = ref()
const saving = ref(false)

// 配置表单
const configForm = reactive({
  name: '',
  description: '',
  llm: {
    model_name: 'deepseek-chat',
    temperature: 0.3,
    top_p: 0.8,
    frequency_penalty: 0.1,
    presence_penalty: 0.1
  },
  prompt: {
    opener: '',
    prompt: '',
    empty_response: '',
    similarity_threshold: 0.2,
    top_n: 6,
    keywords_similarity_weight: 0.3,
    show_quote: true,
    refine_multiturn: true,
    tts: false
  }
})

// 表单验证规则
const configRules = {
  name: [
    { required: true, message: '请输入助手名称', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入助手描述', trigger: 'blur' }
  ],
  'llm.model_name': [
    { required: true, message: '请选择模型', trigger: 'change' }
  ],
  'prompt.opener': [
    { required: true, message: '请输入开场白', trigger: 'blur' }
  ],
  'prompt.prompt': [
    { required: true, message: '请输入主要提示词', trigger: 'blur' }
  ]
}

// 预设配置模板 - 使用后端定义的课程助手类型
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
const initConfig = () => {
  // 初始化表单数据
  configForm.name = props.assistant.name || ''
  configForm.description = props.assistant.description || ''
  
  // LLM配置
  if (props.assistant.llm) {
    configForm.llm = { ...props.assistant.llm }
  }
  
  // Prompt配置
  if (props.assistant.prompt) {
    configForm.prompt = { ...props.assistant.prompt }
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
    Object.assign(configForm.llm, template.config.llm)
    Object.assign(configForm.prompt, template.config.prompt)
    
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
    initConfig()
    ElMessage.success('配置已重置')
  }).catch(() => {
    // 用户取消
  })
}

const saveConfig = async () => {
  try {
    await configFormRef.value.validate()
    
    saving.value = true
    
    const updateData = {
      description: configForm.description,
      llm: configForm.llm,
      prompt: configForm.prompt
    }
    
    await apiCall(`/chat/assistants/${props.assistant.chat_id}`, {
      method: 'PUT',
      body: JSON.stringify(updateData)
    })
    
    ElMessage.success('配置保存成功')
    emit('updated')
    emit('close')
    
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

// 生命周期
onMounted(() => {
  initConfig()
})
</script>

<style scoped>
.chat-config {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.config-form {
  margin-bottom: 20px;
}

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

.param-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  line-height: 1.4;
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
  margin: 0 0 12px 0;
}

.template-description ul {
  margin: 0;
  padding-left: 20px;
}

.template-description li {
  margin-bottom: 8px;
  line-height: 1.6;
}

.template-description strong {
  color: #303133;
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
  .chat-config {
    padding: 10px;
  }
  
  .template-buttons {
    flex-direction: column;
  }
  
  .footer-actions {
    flex-direction: column;
    align-items: center;
  }
}
</style> 