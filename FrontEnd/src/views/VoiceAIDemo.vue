<template>
  <div class="voice-ai-demo">
    <el-card class="demo-card">
      <template #header>
        <div class="card-header">
          <h2>🎤 语音AI助手演示</h2>
          <el-tag type="success">支持语音交互的AI助手</el-tag>
        </div>
      </template>
      
      <div class="demo-content">
        <el-alert
          title="语音AI助手已启用"
          type="info"
          :closable="false"
          show-icon
        >
          <template #default>
            点击顶部导航栏的"语音助手"开关，或使用语音命令"打开语音助手"来体验语音AI助手功能。
          </template>
        </el-alert>

        <el-divider />

        <div class="feature-section">
          <h3>🚀 主要功能</h3>
          <el-row :gutter="20">
            <el-col :span="8">
              <el-card shadow="hover" class="feature-card">
                <h4>🎤 语音输入</h4>
                <p>支持中文语音识别，实时转换语音为文字</p>
                <el-button type="primary" @click="testVoiceInput">
                  测试语音输入
                </el-button>
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card shadow="hover" class="feature-card">
                <h4>🗣️ 语音输出</h4>
                <p>AI回答自动语音朗读，支持播放控制</p>
                <el-button type="success" @click="testVoiceOutput">
                  测试语音输出
                </el-button>
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card shadow="hover" class="feature-card">
                <h4>💬 智能对话</h4>
                <p>支持多轮对话，智能理解上下文</p>
                <el-button type="warning" @click="openVoiceAI">
                  打开语音助手
                </el-button>
              </el-card>
            </el-col>
          </el-row>
        </div>

        <el-divider />

        <div class="usage-section">
          <h3>📖 使用方法</h3>
          <el-steps :active="1" direction="vertical">
            <el-step title="启动语音AI助手" description="点击顶部导航栏的语音助手开关">
              <template #icon>
                <el-icon><Microphone /></el-icon>
              </template>
            </el-step>
            <el-step title="语音输入问题" description="点击麦克风按钮，说出您的问题">
              <template #icon>
                <el-icon><ChatDotRound /></el-icon>
              </template>
            </el-step>
            <el-step title="AI智能回答" description="AI会分析您的问题并给出回答">
              <template #icon>
                <el-icon><Service /></el-icon>
              </template>
            </el-step>
            <el-step title="语音朗读回答" description="AI回答会自动语音朗读，也可以手动控制">
              <template #icon>
                <el-icon><VideoPlay /></el-icon>
              </template>
            </el-step>
          </el-steps>
        </div>

        <el-divider />

        <div class="commands-section">
          <h3>💡 快捷语音命令</h3>
          <el-row :gutter="20">
            <el-col :span="12">
              <h4>启动命令</h4>
              <div class="command-list">
                <el-tag
                  v-for="command in startCommands"
                  :key="command"
                  class="command-tag"
                  @click="speakCommand(command)"
                >
                  {{ command }}
                </el-tag>
              </div>
            </el-col>
            <el-col :span="12">
              <h4>常用问题</h4>
              <div class="command-list">
                <el-tag
                  v-for="command in questionCommands"
                  :key="command"
                  class="command-tag"
                  @click="speakCommand(command)"
                >
                  {{ command }}
                </el-tag>
              </div>
            </el-col>
          </el-row>
        </div>

        <el-divider />

        <div class="tips-section">
          <h3>🎯 使用技巧</h3>
          <el-alert
            v-for="(tip, index) in tips"
            :key="index"
            :title="tip.title"
            :type="tip.type"
            :description="tip.description"
            show-icon
            :closable="false"
            class="tip-alert"
          />
        </div>

        <el-divider />

        <div class="demo-actions">
          <h3>🎮 快速体验</h3>
          <div class="action-buttons">
            <el-button type="primary" size="large" @click="openVoiceAI">
              <el-icon><Microphone /></el-icon>
              打开语音AI助手
            </el-button>
            <el-button type="success" size="large" @click="testVoiceInput">
              <el-icon><ChatDotRound /></el-icon>
              测试语音输入
            </el-button>
            <el-button type="warning" size="large" @click="testVoiceOutput">
              <el-icon><VideoPlay /></el-icon>
              测试语音输出
            </el-button>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Microphone,
  ChatDotRound,
  Service,
  VideoPlay
} from '@element-plus/icons-vue'
import voiceNavigation from '@/utils/voiceNavigation'

export default {
  name: 'VoiceAIDemo',
  components: {
    Microphone,
    ChatDotRound,
    Service,
    VideoPlay
  },
  setup() {
    const startCommands = [
      '打开语音助手',
      'AI助手',
      '语音AI',
      '智能助手'
    ]

    const questionCommands = [
      '你好',
      '介绍一下系统功能',
      '如何使用语音导航',
      '如何创建课程',
      '如何管理学生',
      '如何生成作业'
    ]

    const tips = [
      {
        title: '清晰发音',
        type: 'info',
        description: '在安静环境下清晰地说出问题，提高识别准确率'
      },
      {
        title: '问题明确',
        type: 'success',
        description: '提出具体明确的问题，AI能更好地理解您的需求'
      },
      {
        title: '利用快捷命令',
        type: 'warning',
        description: '使用预设的快捷命令，快速获取常用信息'
      },
      {
        title: '语音控制',
        type: 'error',
        description: '可以随时停止语音播放，控制对话节奏'
      }
    ]

    const testVoiceInput = () => {
      voiceNavigation.speak('正在测试语音输入功能，请点击语音助手开始体验')
      ElMessage.info('请打开语音AI助手测试语音输入功能')
    }

    const testVoiceOutput = () => {
      voiceNavigation.speak('这是语音输出测试，您可以听到这段语音反馈')
      ElMessage.success('语音输出测试完成')
    }

    const openVoiceAI = () => {
      // 触发打开语音AI助手的事件
      window.dispatchEvent(new CustomEvent('voiceNavigation:openVoiceAIChat'))
      voiceNavigation.speak('正在打开语音AI助手')
    }

    const speakCommand = (command) => {
      voiceNavigation.speak(`您可以尝试说：${command}`)
      ElMessage.info(`已设置语音命令: ${command}`)
    }

    return {
      startCommands,
      questionCommands,
      tips,
      testVoiceInput,
      testVoiceOutput,
      openVoiceAI,
      speakCommand
    }
  }
}
</script>

<style scoped>
.voice-ai-demo {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.demo-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  color: #303133;
}

.demo-content {
  padding: 20px 0;
}

.feature-section {
  margin: 30px 0;
}

.feature-card {
  text-align: center;
  height: 200px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.feature-card h4 {
  color: #409eff;
  margin-bottom: 10px;
}

.feature-card p {
  color: #606266;
  margin-bottom: 20px;
}

.usage-section {
  margin: 30px 0;
}

.commands-section {
  margin: 30px 0;
}

.commands-section h4 {
  color: #409eff;
  margin-bottom: 15px;
}

.command-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.command-tag {
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 14px;
  padding: 8px 12px;
}

.command-tag:hover {
  transform: scale(1.05);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.tips-section {
  margin: 30px 0;
}

.tip-alert {
  margin-bottom: 15px;
}

.tip-alert:last-child {
  margin-bottom: 0;
}

.demo-actions {
  margin: 30px 0;
  text-align: center;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .voice-ai-demo {
    padding: 10px;
  }
  
  .feature-card {
    height: auto;
    margin-bottom: 20px;
  }
  
  .command-list {
    justify-content: center;
  }
  
  .card-header {
    flex-direction: column;
    gap: 10px;
    text-align: center;
  }
  
  .action-buttons {
    flex-direction: column;
    align-items: center;
  }
}
</style> 