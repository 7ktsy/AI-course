<template>
  <div class="voice-navigation">
    <!-- 语音导航按钮 -->
    <div class="voice-controls">
      <el-button
        :type="isListening ? 'danger' : 'primary'"
        :icon="isListening ? 'Microphone' : 'Microphone'"
        circle
        size="large"
        @click="toggleVoiceNavigation"
        :loading="isListening"
        :disabled="!isSupported"
        class="voice-btn"
        :title="isListening ? '点击停止语音导航 (Ctrl+Shift+V)' : '点击开始语音导航 (Ctrl+Shift+V)'"
      >
        {{ isListening ? '停止' : '语音' }}
      </el-button>
      
      <!-- 状态指示器 -->
      <div v-if="isListening" class="listening-indicator">
        <div class="pulse-ring"></div>
        <span>正在监听...</span>
      </div>
    </div>

    <!-- 语音命令提示 -->
    <el-drawer
      v-model="showCommands"
      title="语音导航命令"
      direction="rtl"
      size="350px"
    >
      <div class="commands-list">
        <h4>可用的语音命令：</h4>
        <el-divider />
        
        <div class="command-category">
          <h5>页面导航</h5>
          <el-tag
            v-for="command in navigationCommands"
            :key="command"
            class="command-tag"
            @click="speakCommand(command)"
          >
            {{ command }}
          </el-tag>
        </div>

        <el-divider />

        <div class="command-category">
          <h5>AI助手</h5>
          <el-tag
            v-for="command in aiCommands"
            :key="command"
            class="command-tag"
            @click="speakCommand(command)"
          >
            {{ command }}
          </el-tag>
        </div>

        <el-divider />

        <div class="command-category">
          <h5>浏览器控制</h5>
          <el-tag
            v-for="command in browserCommands"
            :key="command"
            class="command-tag"
            @click="speakCommand(command)"
          >
            {{ command }}
          </el-tag>
        </div>

        <el-divider />

        <div class="command-category">
          <h5>智能命令</h5>
          <el-tag
            v-for="command in smartCommands"
            :key="command"
            class="command-tag"
            @click="speakCommand(command)"
          >
            {{ command }}
          </el-tag>
        </div>

        <el-divider />

        <div class="command-category">
          <h5>系统控制</h5>
          <el-tag
            v-for="command in systemCommands"
            :key="command"
            class="command-tag"
            @click="speakCommand(command)"
          >
            {{ command }}
          </el-tag>
        </div>

        <el-divider />

        <div class="keyboard-shortcuts">
          <h5>键盘快捷键</h5>
          <div class="shortcut-item">
            <kbd>Ctrl + Shift + V</kbd>
            <span>切换语音导航</span>
          </div>
          <div class="shortcut-item">
            <kbd>Ctrl + Shift + H</kbd>
            <span>显示帮助</span>
          </div>
          <div class="shortcut-item">
            <kbd>Ctrl + Shift + T</kbd>
            <span>测试语音</span>
          </div>
        </div>

        <el-divider />

        <div class="usage-tips">
          <h5>使用提示：</h5>
          <ul>
            <li>点击麦克风按钮或按 <kbd>Ctrl+Shift+V</kbd> 开始语音导航</li>
            <li>说出页面名称或功能名称</li>
            <li>支持模糊匹配，如"课程"可匹配"我的课程"</li>
            <li>支持数字导航，如"去第1页"</li>
            <li>支持方向导航，如"返回"、"前进"</li>
            <li>说"停止"或再次点击按钮停止监听</li>
            <li>说"帮助"获取命令列表</li>
          </ul>
        </div>
      </div>
    </el-drawer>

    <!-- 快捷按钮 -->
    <div class="quick-actions">
      <el-button
        type="info"
        size="small"
        @click="showCommands = true"
        icon="QuestionFilled"
        title="查看命令列表 (Ctrl+Shift+H)"
      >
        命令列表
      </el-button>
      
      <el-button
        type="success"
        size="small"
        @click="testVoice"
        icon="VideoPlay"
        title="测试语音功能 (Ctrl+Shift+T)"
      >
        测试语音
      </el-button>
      
      <el-button
        type="primary"
        size="small"
        @click="testVoiceSettings"
        icon="Microphone"
        title="测试语音设置 (Ctrl+Shift+S)"
      >
        测试设置
      </el-button>
      
      <el-button
        type="warning"
        size="small"
        @click="openVoiceSettings"
        icon="Setting"
        title="语音设置"
      >
        语音设置
      </el-button>
    </div>

    <!-- 语音反馈提示 -->
    <el-message
      v-if="showFeedback"
      :type="feedbackType"
      :message="feedbackMessage"
      show-close
      @close="showFeedback = false"
      class="voice-feedback"
    />

    <!-- 语音状态提示 -->
    <div v-if="isListening" class="voice-status-overlay">
      <div class="voice-status-content">
        <div class="voice-animation">
          <div class="voice-wave"></div>
          <div class="voice-wave"></div>
          <div class="voice-wave"></div>
        </div>
        <p>正在听取您的指令...</p>
        <small>说"停止"或按 Ctrl+Shift+V 结束</small>
      </div>
    </div>
    
    <!-- 语音设置抽屉 -->
    <VoiceSettings v-model="showVoiceSettings" />
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import voiceNavigation from '@/utils/voiceNavigation'
import VoiceSettings from './VoiceSettings.vue'

export default {
  name: 'VoiceNavigation',
  setup() {
    const router = useRouter()
    const isListening = ref(false)
    const isSupported = ref(true)
    const showCommands = ref(false)
    const showFeedback = ref(false)
    const feedbackType = ref('info')
    const feedbackMessage = ref('')
    const showVoiceSettings = ref(false)

    // 命令分类
    const navigationCommands = [
      '首页', '登录', '演示', '仪表板', '我的课程', '全部课程', 
      '个人资料', '班级管理', '智能备课', '教案管理', 
      'PPT生成', 'AI出题'
    ]

    const aiCommands = [
      'AI助手', '语音助手', '智能助手', '语音AI'
    ]

    const browserCommands = [
      '返回', '前进', '刷新'
    ]

    const smartCommands = [
      '课程', '管理', '备课', '资料'
    ]

    const systemCommands = [
      '停止', '帮助'
    ]

    // 切换语音导航
    const toggleVoiceNavigation = () => {
      voiceNavigation.toggleVoiceNavigation()
    }

    // 测试语音
    const testVoice = () => {
      voiceNavigation.testVoice()
      showFeedbackMessage('语音测试完成', 'success')
    }

    // 测试语音设置
    const testVoiceSettings = () => {
      voiceNavigation.testVoiceSettings()
      showFeedbackMessage('语音设置测试完成', 'success')
    }

    // 朗读命令
    const speakCommand = (command) => {
      voiceNavigation.speak(`您可以尝试说：${command}`)
    }

    // 打开语音设置
    const openVoiceSettings = () => {
      showVoiceSettings.value = true
    }

    // 显示反馈消息
    const showFeedbackMessage = (message, type = 'info') => {
      feedbackMessage.value = message
      feedbackType.value = type
      showFeedback.value = true
      
      setTimeout(() => {
        showFeedback.value = false
      }, 3000)
    }

    // 更新状态
    const updateStatus = () => {
      const status = voiceNavigation.getStatus()
      isListening.value = status.isListening
      isSupported.value = status.isSupported
    }

    // 监听状态变化
    const statusInterval = setInterval(updateStatus, 100)

    // 监听语音导航事件
    const handleVoiceEvent = (event) => {
      const { type, detail } = event
      
      switch (type) {
        case 'voiceNavigation:voiceStart':
          showFeedbackMessage('语音导航已启动', 'success')
          break
        case 'voiceNavigation:voiceEnd':
          showFeedbackMessage('语音导航已停止', 'info')
          break
        case 'voiceNavigation:voiceError':
          const errorMessage = detail?.message || '语音识别出错，请重试'
          showFeedbackMessage(errorMessage, 'error')
          break
        case 'voiceNavigation:voiceNotSupported':
          showFeedbackMessage('您的浏览器不支持语音识别功能', 'warning')
          break
        case 'voiceNavigation:networkOnline':
          showFeedbackMessage('网络连接已恢复', 'success')
          break
        case 'voiceNavigation:networkOffline':
          showFeedbackMessage('网络连接已断开，语音功能可能不可用', 'warning')
          break
      }
    }

    onMounted(() => {
      // 设置路由器实例
      voiceNavigation.setRouter(router)
      
      // 检查浏览器支持
      if (!voiceNavigation.getStatus().isSupported) {
        isSupported.value = false
        showFeedbackMessage('您的浏览器不支持语音识别功能', 'warning')
      }

      // 监听语音导航事件
      window.addEventListener('voiceNavigation:voiceStart', handleVoiceEvent)
      window.addEventListener('voiceNavigation:voiceEnd', handleVoiceEvent)
      window.addEventListener('voiceNavigation:voiceError', handleVoiceEvent)
      window.addEventListener('voiceNavigation:voiceNotSupported', handleVoiceEvent)
      window.addEventListener('voiceNavigation:networkOnline', handleVoiceEvent)
      window.addEventListener('voiceNavigation:networkOffline', handleVoiceEvent)
    })

    onUnmounted(() => {
      clearInterval(statusInterval)
      
      // 移除事件监听
      window.removeEventListener('voiceNavigation:voiceStart', handleVoiceEvent)
      window.removeEventListener('voiceNavigation:voiceEnd', handleVoiceEvent)
      window.removeEventListener('voiceNavigation:voiceError', handleVoiceEvent)
      window.removeEventListener('voiceNavigation:voiceNotSupported', handleVoiceEvent)
      window.removeEventListener('voiceNavigation:networkOnline', handleVoiceEvent)
      window.removeEventListener('voiceNavigation:networkOffline', handleVoiceEvent)
    })

    return {
      isListening,
      isSupported,
      showCommands,
      showFeedback,
      feedbackType,
      feedbackMessage,
      navigationCommands,
      aiCommands,
      browserCommands,
      smartCommands,
      systemCommands,
      toggleVoiceNavigation,
      testVoice,
      testVoiceSettings,
      speakCommand,
      openVoiceSettings,
      showVoiceSettings
    }
  }
}
</script>

<style scoped>
.voice-navigation {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 10px;
}

.voice-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.voice-btn {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
}

.voice-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

.listening-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.9);
  padding: 8px 12px;
  border-radius: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

.pulse-ring {
  width: 12px;
  height: 12px;
  background: #f56c6c;
  border-radius: 50%;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.2);
    opacity: 0.7;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

.quick-actions {
  display: flex;
  gap: 8px;
}

.commands-list {
  padding: 20px;
}

.command-category h5 {
  margin: 0 0 10px 0;
  color: #409eff;
  font-weight: 600;
}

.command-tag {
  margin: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.command-tag:hover {
  transform: scale(1.05);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.keyboard-shortcuts {
  margin-top: 20px;
}

.keyboard-shortcuts h5 {
  color: #e6a23c;
  margin-bottom: 10px;
}

.shortcut-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.shortcut-item kbd {
  background: #f5f7fa;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 2px 6px;
  font-size: 12px;
  font-family: monospace;
  color: #606266;
}

.usage-tips {
  margin-top: 20px;
}

.usage-tips h5 {
  color: #67c23a;
  margin-bottom: 10px;
}

.usage-tips ul {
  padding-left: 20px;
  margin: 0;
}

.usage-tips li {
  margin-bottom: 8px;
  color: #606266;
  line-height: 1.5;
}

.usage-tips kbd {
  background: #f5f7fa;
  border: 1px solid #dcdfe6;
  border-radius: 3px;
  padding: 1px 4px;
  font-size: 11px;
  font-family: monospace;
  color: #606266;
}

.voice-feedback {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1001;
}

.voice-status-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.voice-status-content {
  background: white;
  padding: 40px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.voice-animation {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  margin-bottom: 20px;
}

.voice-wave {
  width: 4px;
  height: 20px;
  background: #409eff;
  border-radius: 2px;
  animation: voiceWave 1.2s infinite ease-in-out;
}

.voice-wave:nth-child(2) {
  animation-delay: 0.2s;
}

.voice-wave:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes voiceWave {
  0%, 40%, 100% {
    transform: scaleY(1);
  }
  20% {
    transform: scaleY(2);
  }
}

.voice-status-content p {
  margin: 0 0 10px 0;
  font-size: 18px;
  color: #303133;
}

.voice-status-content small {
  color: #909399;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .voice-navigation {
    bottom: 10px;
    right: 10px;
  }
  
  .voice-btn {
    width: 50px;
    height: 50px;
  }
  
  .listening-indicator {
    padding: 6px 10px;
    font-size: 12px;
  }
  
  .quick-actions {
    flex-direction: column;
  }

  .voice-status-content {
    margin: 20px;
    padding: 30px 20px;
  }
}
</style> 