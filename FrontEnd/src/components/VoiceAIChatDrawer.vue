<template>
  <el-drawer
    v-model="visible"
    title="AI智能助手 (语音版)"
    direction="rtl"
    size="700px"
    :before-close="handleClose"
    class="voice-ai-chat-drawer"
  >
    <div class="chat-container">
      <!-- 语音控制区域 -->
      <div class="voice-controls">
        <div class="voice-buttons">
          <el-button
            :type="isListening ? 'danger' : 'primary'"
            :icon="isListening ? 'Microphone' : 'Microphone'"
            size="large"
            @click="toggleVoiceInput"
            :loading="isListening"
            :disabled="!isSupported"
            class="voice-btn"
            :title="isListening ? '点击停止语音输入' : '点击开始语音输入'"
          >
            {{ isListening ? '停止' : '语音' }}
          </el-button>
          
          <el-button
            :type="isSpeaking ? 'warning' : 'success'"
            :icon="isSpeaking ? 'VideoPause' : 'VideoPlay'"
            size="large"
            @click="toggleVoiceOutput"
            :disabled="!hasResponse"
            class="voice-btn"
            :title="isSpeaking ? '停止语音播放' : '语音播放回答'"
          >
            {{ isSpeaking ? '停止' : '播放' }}
          </el-button>
          
          <el-button
            type="info"
            :icon="Setting"
            size="large"
            @click="openVoiceSettings"
            class="voice-btn"
            title="语音设置"
          >
            设置
          </el-button>
        </div>
        
        <!-- 语音状态指示器 -->
        <div v-if="isListening" class="listening-indicator">
          <div class="pulse-ring"></div>
          <span>正在听取您的问题...</span>
        </div>
        
        <!-- 语音输入显示 -->
        <div v-if="voiceInput" class="voice-input-display">
          <el-card shadow="never" class="input-card">
            <template #header>
              <div class="input-header">
                <el-icon><Microphone /></el-icon>
                <span>语音输入</span>
              </div>
            </template>
            <p class="input-text">{{ voiceInput }}</p>
            <div class="input-actions">
              <el-button size="small" @click="sendVoiceInput" type="primary">
                发送
              </el-button>
              <el-button size="small" @click="clearVoiceInput">
                清除
              </el-button>
            </div>
          </el-card>
        </div>
      </div>
      
      <!-- 聊天内容区域 -->
      <div class="chat-content">
        <div class="chat-messages" ref="messagesContainer">
          <div
            v-for="(message, index) in chatMessages"
            :key="index"
            :class="['message', message.type]"
          >
            <div class="message-avatar">
              <el-avatar :size="40" :icon="message.type === 'user' ? 'User' : 'Service'" />
            </div>
            <div class="message-content">
              <div class="message-text" v-html="message.content"></div>
              <div class="message-time">{{ message.time }}</div>
              <div v-if="message.type === 'assistant'" class="message-actions">
                <el-button
                  size="small"
                  type="text"
                  @click="speakMessage(message.content)"
                  :disabled="isSpeaking"
                >
                  <el-icon><VideoPlay /></el-icon>
                  朗读
                </el-button>
                <el-button
                  size="small"
                  type="text"
                  @click="copyMessage(message.content)"
                >
                  <el-icon><CopyDocument /></el-icon>
                  复制
                </el-button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 输入区域 -->
        <div class="chat-input">
          <el-input
            v-model="textInput"
            placeholder="输入您的问题，或使用语音输入..."
            type="textarea"
            :rows="3"
            @keyup.enter.ctrl="sendMessage"
          />
          <div class="input-actions">
            <el-button type="primary" @click="sendMessage" :loading="isLoading">
              <el-icon><Promotion /></el-icon>
              发送
            </el-button>
            <el-button @click="clearChat">
              <el-icon><Delete /></el-icon>
              清空
            </el-button>
          </div>
        </div>
      </div>
      
      <!-- 快捷命令 -->
      <div class="quick-commands">
        <h4>💡 快捷命令</h4>
        <div class="command-tags">
          <el-tag
            v-for="command in quickCommands"
            :key="command.text"
            :type="command.type === 'navigation' ? 'success' : 'primary'"
            class="command-tag"
            @click="speakCommand(command)"
          >
            {{ command.text }}
            <el-icon v-if="command.type === 'navigation'" class="command-icon">
              <Location />
            </el-icon>
            <el-icon v-else class="command-icon">
              <ChatDotRound />
            </el-icon>
          </el-tag>
        </div>
      </div>
    </div>
    
    <!-- 语音设置抽屉 -->
    <VoiceSettings v-model="showVoiceSettings" />
  </el-drawer>
</template>

<script setup>
import { ref, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Microphone,
  VideoPlay,
  VideoPause,
  User,
  Service,
  Promotion,
  Delete,
  CopyDocument,
  Setting,
  Location,
  ChatDotRound
} from '@element-plus/icons-vue'
import voiceNavigation from '@/utils/voiceNavigation'
import VoiceSettings from './VoiceSettings.vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

const visible = ref(false)
const isListening = ref(false)
const isSpeaking = ref(false)
const isSupported = ref(true)
const isLoading = ref(false)
const hasResponse = ref(false)
const showVoiceSettings = ref(false)

const textInput = ref('')
const voiceInput = ref('')
const chatMessages = ref([])
const messagesContainer = ref(null)

// 语音状态
const voiceStatus = ref({
  type: 'info',
  text: '准备就绪'
})

// 快捷命令
const quickCommands = [
  { text: '你好', type: 'ai' },
  { text: '介绍一下系统功能', type: 'ai' },
  { text: '如何使用语音导航', type: 'ai' },
  { text: '导航到首页', type: 'navigation' },
  { text: '导航到仪表板', type: 'navigation' },
  { text: '导航到课程', type: 'navigation' },
  { text: '返回', type: 'navigation' }
]

// 监听modelValue变化
watch(() => props.modelValue, (newVal) => {
  visible.value = newVal
})

// 监听visible变化
watch(visible, (newVal) => {
  emit('update:modelValue', newVal)
})

// 处理关闭
const handleClose = () => {
  visible.value = false
  stopVoiceInput()
  stopVoiceOutput()
}

// 切换语音输入
const toggleVoiceInput = () => {
  if (isListening.value) {
    stopVoiceInput()
  } else {
    startVoiceInput()
  }
}

// 开始语音输入
const startVoiceInput = () => {
  if (!isSupported.value) {
    ElMessage.warning('您的浏览器不支持语音识别')
    return
  }
  
  isListening.value = true
  voiceInput.value = ''
  voiceStatus.value = { type: 'warning', text: '正在听取...' }
  
  // 使用语音导航的语音识别功能
  voiceNavigation.startListening()
  
  // 监听语音识别结果
  const handleVoiceResult = (event) => {
    if (event.detail && event.detail.transcript) {
      voiceInput.value = event.detail.transcript
      stopVoiceInput()
    }
  }
  
  window.addEventListener('voiceNavigation:voiceResult', handleVoiceResult)
  
  // 5秒后自动停止
  setTimeout(() => {
    if (isListening.value) {
      stopVoiceInput()
    }
  }, 5000)
}

// 停止语音输入
const stopVoiceInput = () => {
  isListening.value = false
  voiceNavigation.stopListening()
  voiceStatus.value = { type: 'success', text: '语音输入完成' }
}

// 发送语音输入
const sendVoiceInput = () => {
  if (voiceInput.value.trim()) {
    // 检查是否是导航命令
    if (isNavigationCommand(voiceInput.value)) {
      executeNavigationCommand(voiceInput.value)
      voiceInput.value = ''
      return
    }
    
    // 如果不是导航命令，发送给AI
    textInput.value = voiceInput.value
    sendMessage()
    voiceInput.value = ''
  }
}

// 检查是否是导航命令
const isNavigationCommand = (input) => {
  const navigationKeywords = [
    '导航到', '去', '打开', '跳转到', '前往', '进入', '访问',
    '首页', '登录', '演示', '仪表板', '课程', '管理', '备课', '资料',
    '返回', '前进', '刷新', '停止', '帮助'
  ]
  
  const lowerInput = input.toLowerCase()
  return navigationKeywords.some(keyword => lowerInput.includes(keyword))
}

// 执行导航命令
const executeNavigationCommand = (command) => {
  const lowerCommand = command.toLowerCase()
  
  // 获取路由器实例
  const router = useRouter()
  
  // 导航命令映射
  const navigationMap = {
    '首页': () => router.push('/'),
    '登录': () => router.push('/login'),
    '演示': () => router.push('/voice-demo'),
    '语音演示': () => router.push('/voice-demo'),
    '语音AI演示': () => router.push('/voice-ai-demo'),
    'AI助手演示': () => router.push('/voice-ai-demo'),
    '仪表板': () => router.push('/dashboard'),
    '我的课程': () => router.push('/dashboard/courses'),
    '全部课程': () => router.push('/dashboard/all-courses'),
    '个人资料': () => router.push('/dashboard/profile'),
    '班级管理': () => router.push('/dashboard/class-management'),
    '智能备课': () => router.push('/dashboard/preparation'),
    '教案管理': () => router.push('/dashboard/preparation-manage'),
    'PPT生成': () => router.push('/dashboard/ppt-generation'),
    'AI出题': () => router.push('/dashboard/ai-question-generator'),
    '返回': () => router.go(-1),
    '前进': () => router.go(1),
    '刷新': () => window.location.reload(),
    '停止': () => stopVoiceInput(),
    '帮助': () => showNavigationHelp()
  }
  
  // 处理"导航到..."格式的命令
  if (lowerCommand.includes('导航到') || lowerCommand.includes('去') || lowerCommand.includes('打开') || lowerCommand.includes('跳转到') || lowerCommand.includes('前往') || lowerCommand.includes('进入') || lowerCommand.includes('访问')) {
    for (const [key, handler] of Object.entries(navigationMap)) {
      if (lowerCommand.includes(key.toLowerCase())) {
        ElMessage.success(`正在导航到${key}`)
        handler()
        return
      }
    }
    
    // 如果没有找到匹配的页面，提示用户
    ElMessage.warning('抱歉，没有找到对应的页面，请尝试其他导航命令')
    return
  }
  
  // 直接匹配命令
  for (const [key, handler] of Object.entries(navigationMap)) {
    if (lowerCommand.includes(key.toLowerCase())) {
      ElMessage.success(`正在执行：${key}`)
      handler()
      return
    }
  }
  
  // 如果没有找到匹配的命令，提示用户
  ElMessage.warning('抱歉，没有理解您的导航命令，请重试')
}

// 显示导航帮助
const showNavigationHelp = () => {
  const helpText = `
    可用的导航命令包括：
    页面导航：首页、登录、演示、仪表板、我的课程、全部课程、个人资料、
    班级管理、智能备课、教案管理、PPT生成、AI出题
    浏览器控制：返回、前进、刷新、停止、帮助
    您可以说"导航到首页"、"去仪表板"、"打开课程"等
  `
  ElMessage.info(helpText)
}

// 清除语音输入
const clearVoiceInput = () => {
  voiceInput.value = ''
}

// 切换语音输出
const toggleVoiceOutput = () => {
  if (isSpeaking.value) {
    stopVoiceOutput()
  } else {
    const lastAssistantMessage = chatMessages.value
      .filter(msg => msg.type === 'assistant')
      .pop()
    
    if (lastAssistantMessage) {
      speakMessage(lastAssistantMessage.content)
    }
  }
}

// 语音播放消息
const speakMessage = (content) => {
  if (!content) return
  
  // 移除HTML标签
  const textContent = content.replace(/<[^>]*>/g, '')
  
  isSpeaking.value = true
  voiceStatus.value = { type: 'warning', text: '正在朗读...' }
  
  voiceNavigation.speak(textContent)
  
  // 监听语音合成结束
  const handleSpeechEnd = () => {
    isSpeaking.value = false
    voiceStatus.value = { type: 'success', text: '朗读完成' }
  }
  
  window.addEventListener('voiceNavigation:voiceEnd', handleSpeechEnd, { once: true })
}

// 停止语音输出
const stopVoiceOutput = () => {
  isSpeaking.value = false
  voiceNavigation.stopSpeaking()
  voiceStatus.value = { type: 'info', text: '准备就绪' }
}

// 发送消息
const sendMessage = async () => {
  const message = textInput.value.trim()
  if (!message) return
  
  // 添加用户消息
  addMessage('user', message)
  textInput.value = ''
  
  // 模拟AI回复
  isLoading.value = true
  await simulateAIResponse(message)
  isLoading.value = false
}

// 添加消息
const addMessage = (type, content) => {
  const message = {
    type,
    content,
    time: new Date().toLocaleTimeString()
  }
  
  chatMessages.value.push(message)
  
  // 滚动到底部
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
  
  if (type === 'assistant') {
    hasResponse.value = true
  }
}

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

// 调用AI对话API
const callAIChatAPI = async (question) => {
  try {
    // 直接使用已存在的聊天助手"介绍AI"
    const response = await apiCall(`/chat/simple?question=${encodeURIComponent(question)}&chat_name=介绍AI`, {
      method: 'POST'
    })
    
    if (response.code === 0 && response.data) {
      return response.data.answer || '抱歉，我没有理解您的问题，请换个方式提问。'
    } else {
      throw new Error(response.message || 'AI回复失败')
    }
  } catch (error) {
    console.error('AI对话API调用失败:', error)
    // 如果API调用失败，返回友好的错误信息
    return '抱歉，AI服务暂时不可用，请稍后再试。如果问题持续存在，请联系管理员。'
  }
}

// 模拟AI回复
const simulateAIResponse = async (userMessage) => {
  try {
    // 调用真实的AI对话API
    const response = await callAIChatAPI(userMessage)
    
    // 添加AI回复
    addMessage('assistant', response.replace(/\n/g, '<br>'))
    
    // 自动语音播放回复
    setTimeout(() => {
      speakMessage(response)
    }, 500)
    
  } catch (error) {
    console.error('AI回复失败:', error)
    // 如果API调用失败，使用备用回复
    const fallbackResponse = '抱歉，AI服务暂时不可用。让我为您提供一些常见问题的解答：\n\n' +
      '• 系统功能包括课程管理、学生管理、作业系统、学情分析等\n' +
      '• 语音导航可通过右下角麦克风按钮或Ctrl+Shift+V快捷键启动\n' +
      '• 如需帮助，请联系系统管理员'
    
    addMessage('assistant', fallbackResponse.replace(/\n/g, '<br>'))
    
    // 自动语音播放备用回复
    setTimeout(() => {
      speakMessage(fallbackResponse)
    }, 500)
  }
}

// 清空聊天
const clearChat = () => {
  chatMessages.value = []
  hasResponse.value = false
  voiceInput.value = ''
}

// 复制消息
const copyMessage = async (content) => {
  try {
    const textContent = content.replace(/<[^>]*>/g, '')
    await navigator.clipboard.writeText(textContent)
    ElMessage.success('已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

// 朗读快捷命令
const speakCommand = (command) => {
  if (command.type === 'navigation') {
    // 如果是导航命令，直接执行
    executeNavigationCommand(command.text)
  } else {
    // 如果是AI命令，设置为语音输入
    voiceInput.value = command.text
    ElMessage.info(`已设置语音输入: ${command.text}`)
  }
}

// 打开语音设置
const openVoiceSettings = () => {
  showVoiceSettings.value = true
}

// 检查浏览器支持
onMounted(() => {
  const status = voiceNavigation.getStatus()
  isSupported.value = status.isSupported
  
  if (!isSupported.value) {
    voiceStatus.value = { type: 'error', text: '浏览器不支持语音功能' }
  }
})

// 清理资源
onUnmounted(() => {
  stopVoiceInput()
  stopVoiceOutput()
})
</script>

<style scoped>
.voice-ai-chat-drawer {
  --el-drawer-bg-color: #f8f9fa;
}

.chat-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.voice-controls {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.voice-buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
}

.voice-btn {
  min-width: 80px;
  height: 50px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.voice-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

.voice-btn:active {
  transform: scale(0.98);
}

.listening-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.9);
  padding: 12px 20px;
  border-radius: 25px;
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

.voice-input-display {
  margin-top: 10px;
}

.input-card {
  border: 2px solid #e1f5fe;
  background: #f8f9fa;
}

.input-header {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #1976d2;
  font-weight: 600;
}

.input-text {
  margin: 10px 0;
  padding: 10px;
  background: white;
  border-radius: 8px;
  border-left: 4px solid #1976d2;
  font-size: 14px;
  line-height: 1.5;
}

.input-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.chat-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  min-height: 400px;
}

.chat-messages {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  max-height: 500px;
}

.message {
  display: flex;
  gap: 15px;
  margin-bottom: 25px;
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  flex-shrink: 0;
}

.message-content {
  flex: 1;
  max-width: 80%;
}

.message.user .message-content {
  text-align: right;
}

.message-text {
  padding: 16px 20px;
  border-radius: 16px;
  background: #f0f2f5;
  font-size: 16px;
  line-height: 1.6;
  word-wrap: break-word;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.message.user .message-text {
  background: #1976d2;
  color: white;
}

.message.assistant .message-text {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  font-size: 15px;
  line-height: 1.7;
}

.message-time {
  font-size: 12px;
  color: #999;
  margin-top: 6px;
}

.message.user .message-time {
  text-align: right;
}

.message-actions {
  margin-top: 10px;
  display: flex;
  gap: 10px;
}

.chat-input {
  padding: 20px;
  border-top: 1px solid #e9ecef;
  background: #f8f9fa;
}

.chat-input .input-actions {
  margin-top: 12px;
  justify-content: flex-end;
}

.quick-commands {
  padding: 15px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.quick-commands h4 {
  margin: 0 0 12px 0;
  color: #333;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.command-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.command-tag {
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 13px;
}

.command-tag:hover {
  transform: scale(1.05);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.command-tag.el-tag--success {
  background: linear-gradient(135deg, #67c23a, #85ce61);
  border-color: #67c23a;
  color: white;
}

.command-tag.el-tag--primary {
  background: linear-gradient(135deg, #409eff, #66b1ff);
  border-color: #409eff;
  color: white;
}

.command-icon {
  font-size: 14px;
  margin-left: 2px;
}

:deep(.el-drawer__header) {
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
  margin-bottom: 0;
  padding: 16px 20px;
}

:deep(.el-drawer__body) {
  padding: 20px;
  height: calc(100% - 60px);
}

:deep(.el-drawer__title) {
  font-weight: 600;
  color: #333;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .voice-buttons {
    gap: 15px;
  }
  
  .voice-btn {
    min-width: 70px;
    height: 45px;
    font-size: 13px;
  }
  
  .message-content {
    max-width: 85%;
  }
  
  .chat-messages {
    padding: 15px;
  }
  
  .message-text {
    font-size: 14px;
    padding: 12px 16px;
  }
}
</style> 