<template>
  <div class="voice-demo">
    <el-card class="demo-card">
      <template #header>
        <div class="card-header">
          <h2>🎤 语音导航功能演示</h2>
          <el-tag type="success">已集成到应用中</el-tag>
        </div>
      </template>
      
      <div class="demo-content">
        <el-alert
          title="语音导航已启用"
          type="info"
          :closable="false"
          show-icon
        >
          <template #default>
            在页面右下角可以看到语音控制按钮，点击开始体验语音导航功能。
            <br>
            <strong>提示：</strong>语音识别需要网络连接和麦克风权限。
          </template>
        </el-alert>

        <el-divider />

        <div class="feature-section">
          <h3>🚀 主要功能</h3>
          <el-row :gutter="20">
            <el-col :span="8">
              <el-card shadow="hover" class="feature-card">
                <h4>🎤 语音识别</h4>
                <p>支持中文语音识别，实时转换语音为文字</p>
                <el-button type="primary" @click="testRecognition">
                  测试识别
                </el-button>
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card shadow="hover" class="feature-card">
                <h4>🗣️ 语音合成</h4>
                <p>中文语音反馈，自然流畅的语音输出</p>
                <el-button type="success" @click="testSynthesis">
                  测试语音
                </el-button>
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card shadow="hover" class="feature-card">
                <h4>🧭 智能导航</h4>
                <p>基于用户角色的智能页面导航</p>
                <el-button type="warning" @click="testNavigation">
                  测试导航
                </el-button>
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card shadow="hover" class="feature-card">
                <h4>🎵 语音设置</h4>
                <p>优化的语音参数，更自然的语音体验</p>
                <el-button type="primary" @click="testVoiceSettings">
                  测试设置
                </el-button>
              </el-card>
            </el-col>
          </el-row>
        </div>

        <el-divider />

        <div class="commands-section">
          <h3>📋 可用命令</h3>
          <el-tabs v-model="activeTab">
            <el-tab-pane label="页面导航" name="navigation">
              <div class="command-grid">
                <el-tag
                  v-for="command in navigationCommands"
                  :key="command"
                  class="command-tag"
                  @click="speakCommand(command)"
                >
                  {{ command }}
                </el-tag>
              </div>
            </el-tab-pane>
            <el-tab-pane label="智能命令" name="smart">
              <div class="command-grid">
                <el-tag
                  v-for="command in smartCommands"
                  :key="command"
                  class="command-tag"
                  @click="speakCommand(command)"
                >
                  {{ command }}
                </el-tag>
              </div>
            </el-tab-pane>
            <el-tab-pane label="系统控制" name="system">
              <div class="command-grid">
                <el-tag
                  v-for="command in systemCommands"
                  :key="command"
                  class="command-tag"
                  @click="speakCommand(command)"
                >
                  {{ command }}
                </el-tag>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>

        <el-divider />

        <div class="shortcuts-section">
          <h3>⌨️ 键盘快捷键</h3>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="切换语音导航">
              <kbd>Ctrl + Shift + V</kbd>
            </el-descriptions-item>
            <el-descriptions-item label="显示帮助">
              <kbd>Ctrl + Shift + H</kbd>
            </el-descriptions-item>
            <el-descriptions-item label="测试语音">
              <kbd>Ctrl + Shift + T</kbd>
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <el-divider />

        <div class="usage-section">
          <h3>📖 使用说明</h3>
          <el-steps :active="1" direction="vertical">
            <el-step title="启动语音导航" description="点击右下角麦克风按钮或按 Ctrl+Shift+V">
              <template #icon>
                <el-icon><Microphone /></el-icon>
              </template>
            </el-step>
            <el-step title="说出命令" description="清晰地说出您想要执行的命令">
              <template #icon>
                <el-icon><ChatDotRound /></el-icon>
              </template>
            </el-step>
            <el-step title="等待执行" description="系统会语音确认并执行相应操作">
              <template #icon>
                <el-icon><Check /></el-icon>
              </template>
            </el-step>
            <el-step title="停止导航" description="说停止或再次点击按钮结束">
              <template #icon>
                <el-icon><VideoPause /></el-icon>
              </template>
            </el-step>
          </el-steps>
        </div>

        <el-divider />

        <div class="tips-section">
          <h3>💡 使用技巧</h3>
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
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import voiceNavigation from '@/utils/voiceNavigation'
import { Microphone, ChatDotRound, Check, VideoPause } from '@element-plus/icons-vue'

export default {
  name: 'VoiceNavigationDemo',
  components: {
    Microphone,
    ChatDotRound,
    Check,
    VideoPause
  },
  setup() {
    const router = useRouter()
    const activeTab = ref('navigation')

    const navigationCommands = [
      '首页', '登录', '演示', '仪表板', '我的课程', '全部课程', 
      '个人资料', '班级管理', '智能备课', '教案管理', 
      'PPT生成', 'AI出题'
    ]

    const smartCommands = [
      '课程', '管理', '备课', '资料'
    ]

    const systemCommands = [
      '返回', '前进', '刷新', '停止', '帮助'
    ]

    const tips = [
      {
        title: '清晰发音',
        type: 'info',
        description: '在安静的环境下清晰地说出命令，提高识别准确率'
      },
      {
        title: '模糊匹配',
        type: 'success',
        description: '支持模糊匹配，如说"课程"可匹配"我的课程"'
      },
      {
        title: '数字导航',
        type: 'warning',
        description: '可以使用数字导航，如"去第1页"、"去第2页"'
      },
      {
        title: '权限控制',
        type: 'error',
        description: '某些功能需要相应权限，系统会智能判断用户角色'
      }
    ]

    const testRecognition = () => {
      voiceNavigation.speak('语音识别功能正常，请尝试说出"首页"来测试导航')
    }

    const testSynthesis = () => {
      voiceNavigation.speak('语音合成功能正常，您可以听到这段语音反馈')
    }

    const testNavigation = () => {
      voiceNavigation.speak('正在测试智能导航功能')
      setTimeout(() => {
        router.push('/dashboard')
      }, 2000)
    }

    const testVoiceSettings = () => {
      voiceNavigation.testVoiceSettings()
    }

    const speakCommand = (command) => {
      voiceNavigation.speak(`您可以尝试说：${command}`)
    }

    return {
      activeTab,
      navigationCommands,
      smartCommands,
      systemCommands,
      tips,
      testRecognition,
      testSynthesis,
      testNavigation,
      testVoiceSettings,
      speakCommand
    }
  }
}
</script>

<style scoped>
.voice-demo {
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

.commands-section {
  margin: 30px 0;
}

.command-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 15px;
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

.shortcuts-section {
  margin: 30px 0;
}

.shortcuts-section kbd {
  background: #f5f7fa;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 4px 8px;
  font-size: 12px;
  font-family: monospace;
  color: #606266;
}

.usage-section {
  margin: 30px 0;
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

/* 响应式设计 */
@media (max-width: 768px) {
  .voice-demo {
    padding: 10px;
  }
  
  .feature-card {
    height: auto;
    margin-bottom: 20px;
  }
  
  .command-grid {
    justify-content: center;
  }
  
  .card-header {
    flex-direction: column;
    gap: 10px;
    text-align: center;
  }
}
</style> 