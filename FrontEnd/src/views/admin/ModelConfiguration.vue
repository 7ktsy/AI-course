<template>
  <div class="model-configuration">
    <!-- 页面状态提示 -->
    <el-alert
      title="模型配置页面已就绪"
      description="您可以配置通用助手参数和查看所有模型信息"
      type="success"
      :closable="false"
      show-icon
      style="margin-bottom: 20px;"
    />
    
    <!-- 顶部导航栏 -->
    <div class="top-nav">
      <div class="nav-left">
        <h1 class="page-title">
          <el-icon class="title-icon"><Setting /></el-icon>
          模型配置
        </h1>
        <p class="page-subtitle">配置通用助手参数和管理模型设置</p>
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

    <!-- 标签页导航 -->
    <div class="tab-section">
      <el-card shadow="never" class="tab-card">
        <el-tabs v-model="activeTab" @tab-click="handleTabClick">
          <el-tab-pane label="通用配置" name="general">
            <template #label>
              <el-icon><Setting /></el-icon>
              <span>通用配置</span>
            </template>
            <GeneralConfig 
              v-if="activeTab === 'general'"
              :general-config="generalConfig"
              @config-updated="handleConfigUpdated"
            />
          </el-tab-pane>
          
          <el-tab-pane label="全部模型" name="models">
            <template #label>
              <el-icon><Cpu /></el-icon>
              <span>全部模型</span>
            </template>
            <AllModels 
              v-if="activeTab === 'models'"
              :models="models"
              @model-updated="handleModelUpdated"
            />
          </el-tab-pane>
        </el-tabs>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  Setting, Cpu, Refresh, Back 
} from '@element-plus/icons-vue'
import GeneralConfig from './components/GeneralConfig.vue'
import AllModels from './components/AllModels.vue'

// 获取router实例
const router = useRouter()

// 响应式数据
const activeTab = ref('general')
const loading = ref(false)

// 通用配置数据
const generalConfig = ref({
  default_llm: {
    model_name: 'deepseek-chat',
    temperature: 0.3,
    top_p: 0.8,
    frequency_penalty: 0.1,
    presence_penalty: 0.1
  },
  default_prompt: {
    opener: '你好！我是你的智能助手，有什么可以帮你的吗？',
    prompt: '你是一个智能助手。请总结知识库的内容以回答问题。请列出知识库中的数据并详细回答。当所有知识库内容与问题无关时，你的回答必须包含句子"抱歉，知识库中没有找到你想要的信息，换个问题试试呢?" 回答需要考虑聊天历史。',
    empty_response: '抱歉，知识库中没有找到你想要的信息，换个问题试试呢?',
    similarity_threshold: 0.2,
    top_n: 6,
    keywords_similarity_weight: 0.3,
    show_quote: true,
    refine_multiturn: true,
    tts: false
  },
  assistant_types: [
    {
      name: 'general',
      label: '通用助手',
      description: '适用于一般问答和知识查询',
      config: {
        llm: {
          model_name: 'deepseek-chat',
          temperature: 0.3,
          top_p: 0.8,
          frequency_penalty: 0.1,
          presence_penalty: 0.1
        },
        prompt: {
          opener: '你好！我是这门课程的智能助手，可以帮你解答课程相关的问题。请告诉我你想了解什么？',
          prompt: '你是一个专业的课程助手。请基于知识库中的课程内容来回答问题。回答要准确、详细，并考虑聊天历史。如果知识库中没有相关信息，请明确说明。',
          empty_response: '抱歉，知识库中没有找到相关信息。请换个问题试试，或者联系老师获取帮助。',
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
      description: '专门用于分析学生学习情况和提供个性化建议',
      config: {
        llm: {
          model_name: 'deepseek-chat',
          temperature: 0.1,
          top_p: 0.3,
          frequency_penalty: 0.7,
          presence_penalty: 0.4
        },
        prompt: {
          opener: '你好！我是学情分析助手，专门负责分析学生的学习情况和提供个性化建议。请提供学生的作业数据或学习表现，我将为你进行详细分析。',
          prompt: '你是一个专业的学情分析专家。请基于提供的数据分析学生的学习情况，包括：1. 知识点掌握程度评估 2. 学习优势和不足 3. 个性化学习建议 4. 改进方向。分析要客观、具体，并提供可操作的建议。',
          empty_response: '抱歉，没有足够的数据进行分析。请提供更多学生的学习数据。',
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
      description: '帮助教师设计教案和教学活动',
      config: {
        llm: {
          model_name: 'deepseek-chat',
          temperature: 0.4,
          top_p: 0.9,
          frequency_penalty: 0.2,
          presence_penalty: 0.1
        },
        prompt: {
          opener: '你好！我是教师备课助手，专门帮助教师设计教案和教学活动。请告诉我你要备课的章节或主题，我将为你提供详细的备课建议。',
          prompt: `你是一个教师备课助理，你根据教师上传的课程大纲和课程知识点汇总帮助教师自动生成教学内容，包括本周课堂知识点讲解，教学关键内容，实训练习与指导、时间分布等。
以下是知识库：
{knowledge}
以上是知识库。
生成的教学内容以下几块为核心：一、上周知识点回顾，二、本周知识点讲解，三、教学关键内容（板书/PPT重点）（注意以mermaid形式生成，Mermaid 的序列图语法对中文符号敏感），四、实训练习与指导，五、课堂时间分布，六、相关知识点拓展`,
          empty_response: '抱歉，没有找到相关的课程内容。请检查课程资料是否完整。',
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
      description: '专门回答学生的课程问题',
      config: {
        llm: {
          model_name: 'deepseek-chat',
          temperature: 0.2,
          top_p: 0.7,
          frequency_penalty: 0.3,
          presence_penalty: 0.2
        },
        prompt: {
          opener: '你好！我是学生答疑助手，专门回答同学们的课程问题。请直接提出你的问题，我会尽力为你解答！',
          prompt: '你是一个耐心的学习导师。请基于课程内容回答学生的问题，要求：1. 回答要清晰易懂 2. 提供解题思路和方法 3. 适当举例说明 4. 鼓励学生思考 5. 如果问题超出课程范围，引导到相关知识点。',
          empty_response: '这个问题可能超出了当前课程的范围。建议你复习相关知识点，或者向老师请教。',
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
      description: '负责批改作业和提供反馈',
      config: {
        llm: {
          model_name: 'deepseek-chat',
          temperature: 0.05,
          top_p: 0.2,
          frequency_penalty: 0.8,
          presence_penalty: 0.5
        },
        prompt: {
          opener: '你好！我是作业批改助手，专门负责批改作业和提供反馈。请提供作业题目和参考答案，我将为你进行专业批改。',
          prompt: '你是一个严格的作业批改专家。请严格按照参考答案批改作业，要求：1. 客观公正评分 2. 指出具体错误 3. 提供改进建议 4. 鼓励学生进步 5. 保持评分标准一致。对于主观题，要给出详细的评价理由。',
          empty_response: '无法进行批改，请确保提供了完整的作业内容和参考答案。',
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
})

// 模型数据
const models = ref([
  {
    id: 'deepseek-chat',
    name: 'DeepSeek Chat',
    provider: 'DeepSeek',
    type: 'Chat',
    description: 'DeepSeek公司开发的大语言模型，支持中文对话',
    status: 'active',
    max_tokens: 4096,
    supported_features: ['对话', '代码生成', '文本分析'],
    pricing: {
      input: '0.0001',
      output: '0.0002',
      unit: 'per 1K tokens'
    }
  },
  {
    id: 'gpt-3.5-turbo',
    name: 'GPT-3.5 Turbo',
    provider: 'OpenAI',
    type: 'Chat',
    description: 'OpenAI开发的GPT-3.5系列模型，性能优秀且成本较低',
    status: 'active',
    max_tokens: 4096,
    supported_features: ['对话', '代码生成', '文本分析', '多模态'],
    pricing: {
      input: '0.0015',
      output: '0.002',
      unit: 'per 1K tokens'
    }
  },
  {
    id: 'gpt-4',
    name: 'GPT-4',
    provider: 'OpenAI',
    type: 'Chat',
    description: 'OpenAI最新的大语言模型，具有更强的推理和创造能力',
    status: 'active',
    max_tokens: 8192,
    supported_features: ['对话', '代码生成', '文本分析', '多模态', '复杂推理'],
    pricing: {
      input: '0.03',
      output: '0.06',
      unit: 'per 1K tokens'
    }
  },
  {
    id: 'claude-3',
    name: 'Claude 3',
    provider: 'Anthropic',
    type: 'Chat',
    description: 'Anthropic开发的Claude系列最新模型，安全性高',
    status: 'active',
    max_tokens: 200000,
    supported_features: ['对话', '代码生成', '文本分析', '文档处理'],
    pricing: {
      input: '0.015',
      output: '0.075',
      unit: 'per 1K tokens'
    }
  }
])

// 方法
const handleTabClick = (tab) => {
  console.log('切换到标签页:', tab.props.name)
}

const handleConfigUpdated = (config) => {
  ElMessage.success('通用配置更新成功')
  // 这里可以调用API保存配置
  console.log('配置已更新:', config)
}

const handleModelUpdated = (model) => {
  ElMessage.success('模型配置更新成功')
  // 这里可以调用API保存模型配置
  console.log('模型已更新:', model)
}

const refreshData = () => {
  loading.value = true
  // 模拟加载数据
  setTimeout(() => {
    loading.value = false
    ElMessage.success('数据刷新成功')
  }, 1000)
}

// 生命周期
onMounted(() => {
  // 初始化数据
  console.log('模型配置页面已加载')
})
</script>

<style scoped>
.model-configuration {
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

.tab-section {
  margin-bottom: 20px;
}

.tab-card {
  border: none;
}

.tab-card :deep(.el-tabs__header) {
  margin-bottom: 20px;
}

.tab-card :deep(.el-tabs__item) {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 500;
}

.tab-card :deep(.el-tabs__item .el-icon) {
  font-size: 18px;
}

.tab-card :deep(.el-tabs__content) {
  padding: 20px 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .model-configuration {
    padding: 10px;
  }
  
  .top-nav {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .tab-card :deep(.el-tabs__item) {
    font-size: 14px;
  }
}
</style> 