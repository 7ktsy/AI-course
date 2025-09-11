<template>
  <div class="photo-search-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2 class="page-title">
        <i class="bi bi-camera"></i>
        拍照搜题
      </h2>
      <p class="page-description">上传题目图片，AI助手将为您提供详细解答</p>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 左侧：图片上传和展示区域 -->
      <div class="image-section">
        <div class="upload-area" v-if="!uploadedImage">
          <div class="upload-content">
            <i class="bi bi-cloud-upload upload-icon"></i>
            <h3>上传题目图片</h3>
            <p>支持 JPG、PNG、GIF 格式，最大 10MB</p>
            <el-button 
              type="primary" 
              size="large" 
              @click="triggerFileInput"
              class="upload-btn"
            >
              <i class="bi bi-camera"></i>
              选择图片
            </el-button>
            <p class="upload-tip">或直接拖拽图片到此处</p>
          </div>
          <input
            ref="fileInput"
            type="file"
            accept="image/*"
            @change="handleFileUpload"
            style="display: none"
          />
        </div>

        <!-- 图片预览区域 -->
        <div class="image-preview" v-if="uploadedImage">
          <div class="image-header">
            <h3>题目图片</h3>
            <div class="image-actions">
              <el-button 
                type="primary" 
                size="small" 
                @click="analyzeImage"
                :loading="analyzing"
              >
                <i class="bi bi-search"></i>
                开始分析
              </el-button>
              <el-button 
                type="default" 
                size="small" 
                @click="resetImage"
              >
                <i class="bi bi-arrow-clockwise"></i>
                重新上传
              </el-button>
            </div>
          </div>
          <div class="image-container">
            <img :src="uploadedImage" alt="题目图片" class="preview-image" />
          </div>
        </div>
      </div>

      <!-- 右侧：AI答疑区域 -->
      <div class="ai-answer-section">
        <div class="answer-header">
          <h3>
            <i class="bi bi-robot"></i>
            AI 智能解答
          </h3>
          <div class="voice-controls" v-if="aiAnswer">
            <el-button 
              type="success" 
              size="small" 
              @click="playVoiceAnswer"
              :loading="speaking"
            >
              <i class="bi bi-volume-up"></i>
              语音播放
            </el-button>
            <el-button 
              type="warning" 
              size="small" 
              @click="stopVoiceAnswer"
              v-if="speaking"
            >
              <i class="bi bi-stop-circle"></i>
              停止播放
            </el-button>
          </div>
        </div>

        <div class="answer-content">
          <div v-if="!aiAnswer" class="empty-state">
            <i class="bi bi-lightbulb empty-icon"></i>
            <h4>等待分析</h4>
            <p>请先上传题目图片，然后点击"开始分析"按钮</p>
          </div>

          <div v-else class="answer-text">
            <div class="answer-section">
              <h4 class="section-title">
                <i class="bi bi-lightbulb"></i>
                题目分析
              </h4>
              <p>{{ aiAnswer.analysis }}</p>
            </div>

            <div class="answer-section">
              <h4 class="section-title">
                <i class="bi bi-pencil-square"></i>
                解题步骤
              </h4>
              <ol class="solution-steps">
                <li v-for="(step, index) in aiAnswer.steps" :key="index">
                  {{ step }}
                </li>
              </ol>
            </div>

            <div class="answer-section">
              <h4 class="section-title">
                <i class="bi bi-check-circle"></i>
                最终答案
              </h4>
              <div class="final-answer">
                <span class="answer-label">答案：</span>
                <span class="answer-value">{{ aiAnswer.answer }}</span>
              </div>
            </div>

            <div class="answer-section">
              <h4 class="section-title">
                <i class="bi bi-book"></i>
                知识点总结
              </h4>
              <div class="knowledge-points">
                <el-tag 
                  v-for="point in aiAnswer.knowledgePoints" 
                  :key="point"
                  type="info"
                  class="knowledge-tag"
                >
                  {{ point }}
                </el-tag>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'

// 响应式数据
const fileInput = ref(null)
const uploadedImage = ref('')
const analyzing = ref(false)
const speaking = ref(false)
const aiAnswer = ref(null)

// 预设的AI回答数据
const presetAnswer = {
  analysis: "TCP三次握手过程详解：TCP三次握手是TCP协议中建立可靠连接的核心机制，通过客户端和服务端之间的三次交互，确保通信双方的收发能力正常，并同步初始序列号，防止历史重复连接导致的数据混乱。",
  steps: [
    "板块一：TCP三次握手的核心机制 - 目的与作用：TCP三次握手的主要目的是建立可靠的连接，确保通信双方（客户端和服务端）的收发能力正常，并同步初始序列号（Sequence Number），防止历史重复连接导致的数据混乱。通过三次交互，双方确认彼此的接收和发送能力，避免因网络延迟或丢包导致的错误连接。",
    "关键字段解析：SYN（Synchronize）表示请求建立连接，仅在第一次和第二次握手中置为1；ACK（Acknowledgment）表示确认对方的报文，在第二次和第三次握手中置为1；seq（Sequence Number）是初始序列号，用于后续数据包的顺序控制；ack（Acknowledgment Number）是确认号，值为对方seq+1，表示期望收到的下一个字节序号。",
    "状态转换流程：客户端状态变化为CLOSED → SYN-SENT → ESTABLISHED；服务端状态变化为LISTEN → SYN-RECEIVED → ESTABLISHED。",
    "板块二：为什么需要三次握手？两次或四次行不行？ - 防止历史重复连接问题：如果只有两次握手，网络延迟可能导致旧的SYN包到达服务端，服务端误认为新连接已建立，造成资源浪费和数据错乱。三次握手能确保客户端确认服务端的响应，避免此类问题。",
    "确保双向通信可靠：两次握手只能保证客户端→服务端的通信正常，但无法确认服务端→客户端的通信是否畅通。第三次握手让服务端确认客户端能正确接收数据。",
    "四次握手的冗余性：理论上可以四次握手（如客户端再发一次ACK），但TCP设计追求高效，三次已经足够保证可靠性，增加次数只会降低效率而无额外收益。",
    "总结：TCP三次握手是可靠传输的基础机制，通过SYN、ACK、seq/ack字段的交互确保连接正确建立。少于三次可能导致历史连接问题，多于三次则无必要，因此三次是最优解。"
  ],
  answer: "TCP三次握手是建立可靠连接的最优机制，通过SYN、ACK、seq/ack字段的三次交互确保双向通信可靠，防止历史重复连接问题。",
  knowledgePoints: ["TCP协议", "三次握手", "网络通信", "可靠传输", "序列号同步", "连接建立"]
}

// 触发文件选择
const triggerFileInput = () => {
  fileInput.value.click()
}

// 处理文件上传
const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (!file) return

  // 验证文件类型
  if (!file.type.startsWith('image/')) {
    ElMessage.error('请选择图片文件')
    return
  }

  // 验证文件大小（10MB）
  if (file.size > 10 * 1024 * 1024) {
    ElMessage.error('图片大小不能超过10MB')
    return
  }

  // 创建预览URL
  const reader = new FileReader()
  reader.onload = (e) => {
    uploadedImage.value = e.target.result
    // 重置AI回答
    aiAnswer.value = null
  }
  reader.readAsDataURL(file)
}

// 分析图片
const analyzeImage = async () => {
  if (!uploadedImage.value) {
    ElMessage.warning('请先上传图片')
    return
  }

  analyzing.value = true
  
  // 模拟分析过程
  setTimeout(() => {
    aiAnswer.value = presetAnswer
    analyzing.value = false
    ElMessage.success('分析完成！')
  }, 2000)
}

// 重置图片
const resetImage = () => {
  uploadedImage.value = ''
  aiAnswer.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

// 语音播放
const playVoiceAnswer = () => {
  if (!aiAnswer.value) return
  
  speaking.value = true
  
  // 创建语音合成
  const speech = new SpeechSynthesisUtterance()
  
  // 优化语音内容，添加自然停顿和语调
  const voiceText = `
    题目分析：${aiAnswer.value.analysis}
    
    解题步骤：
    ${aiAnswer.value.steps.map((step, index) => `第${index + 1}步，${step}`).join('。')}
    
    最终答案：${aiAnswer.value.answer}
    
    知识点总结：${aiAnswer.value.knowledgePoints.join('、')}
  `.trim()
  
  speech.text = voiceText
  speech.lang = 'zh-CN'
  
  // 优化语音参数，让声音更自然
  speech.rate = 1.0        // 语速稍慢，更自然
  speech.pitch = 1.1       // 音调稍高，更有活力
  speech.volume = 0.85     // 音量适中
  
  // 尝试选择更好的语音
  const voices = window.speechSynthesis.getVoices()
  const chineseVoice = voices.find(voice => 
    voice.lang.includes('zh') && 
    (voice.name.includes('Xiaoxiao') || voice.name.includes('Yunxi') || voice.name.includes('Xiaoyi'))
  )
  
  if (chineseVoice) {
    speech.voice = chineseVoice
  }
  
  speech.onend = () => {
    speaking.value = false
  }
  
  speech.onerror = () => {
    speaking.value = false
    ElMessage.error('语音播放失败')
  }
  
  // 确保语音列表加载完成
  if (voices.length === 0) {
    window.speechSynthesis.onvoiceschanged = () => {
      const updatedVoices = window.speechSynthesis.getVoices()
      const chineseVoice = updatedVoices.find(voice => 
        voice.lang.includes('zh') && 
        (voice.name.includes('Xiaoxiao') || voice.name.includes('Yunxi') || voice.name.includes('Xiaoyi'))
      )
      if (chineseVoice) {
        speech.voice = chineseVoice
      }
      window.speechSynthesis.speak(speech)
    }
  } else {
    window.speechSynthesis.speak(speech)
  }
}

// 停止语音播放
const stopVoiceAnswer = () => {
  window.speechSynthesis.cancel()
  speaking.value = false
}

// 拖拽上传功能
const handleDragOver = (e) => {
  e.preventDefault()
  e.currentTarget.classList.add('drag-over')
}

const handleDragLeave = (e) => {
  e.preventDefault()
  e.currentTarget.classList.remove('drag-over')
}

const handleDrop = (e) => {
  e.preventDefault()
  e.currentTarget.classList.remove('drag-over')
  
  const files = e.dataTransfer.files
  if (files.length > 0) {
    const file = files[0]
    if (file.type.startsWith('image/')) {
      const reader = new FileReader()
      reader.onload = (e) => {
        uploadedImage.value = e.target.result
        aiAnswer.value = null
      }
      reader.readAsDataURL(file)
    } else {
      ElMessage.error('请选择图片文件')
    }
  }
}

// 组件挂载时添加拖拽事件监听
onMounted(() => {
  const uploadArea = document.querySelector('.upload-area')
  if (uploadArea) {
    uploadArea.addEventListener('dragover', handleDragOver)
    uploadArea.addEventListener('dragleave', handleDragLeave)
    uploadArea.addEventListener('drop', handleDrop)
  }
})

// 组件卸载时移除事件监听
onUnmounted(() => {
  const uploadArea = document.querySelector('.upload-area')
  if (uploadArea) {
    uploadArea.removeEventListener('dragover', handleDragOver)
    uploadArea.removeEventListener('dragleave', handleDragLeave)
    uploadArea.removeEventListener('drop', handleDrop)
  }
  
  // 停止语音播放
  window.speechSynthesis.cancel()
})
</script>

<style scoped>
.photo-search-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: calc(100vh - 200px);
}

.page-header {
  margin-bottom: 30px;
  text-align: center;
}

.page-title {
  font-size: 28px;
  color: #303133;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.page-title i {
  color: #409EFF;
}

.page-description {
  color: #909399;
  font-size: 16px;
  margin: 0;
}

.main-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  max-width: 1400px;
  margin: 0 auto;
}

.image-section, .ai-answer-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.upload-area {
  padding: 60px 40px;
  text-align: center;
  border: 2px dashed #dcdfe6;
  border-radius: 12px;
  margin: 20px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.upload-area:hover, .upload-area.drag-over {
  border-color: #409EFF;
  background-color: #f0f9ff;
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.upload-icon {
  font-size: 48px;
  color: #c0c4cc;
  margin-bottom: 10px;
}

.upload-content h3 {
  margin: 0;
  color: #303133;
  font-size: 20px;
}

.upload-content p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.upload-btn {
  margin: 10px 0;
  padding: 12px 24px;
  font-size: 16px;
}

.upload-tip {
  font-size: 12px;
  color: #c0c4cc;
}

.image-preview {
  padding: 20px;
}

.image-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #ebeef5;
}

.image-header h3 {
  margin: 0;
  color: #303133;
  font-size: 18px;
}

.image-actions {
  display: flex;
  gap: 10px;
}

.image-container {
  text-align: center;
  background: #fafafa;
  border-radius: 8px;
  padding: 20px;
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-image {
  max-width: 100%;
  max-height: 400px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.answer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 20px 0;
  border-bottom: 1px solid #ebeef5;
  margin-bottom: 20px;
}

.answer-header h3 {
  margin: 0;
  color: #303133;
  font-size: 18px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.answer-header i {
  color: #409EFF;
}

.voice-controls {
  display: flex;
  gap: 10px;
}

.answer-content {
  padding: 0 20px 20px;
  min-height: 400px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #909399;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 20px;
  color: #c0c4cc;
}

.empty-state h4 {
  margin: 0 0 10px 0;
  color: #606266;
}

.empty-state p {
  margin: 0;
  font-size: 14px;
}

.answer-text {
  line-height: 1.6;
}

.answer-section {
  margin-bottom: 25px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.answer-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 15px 0;
  color: #303133;
  font-size: 16px;
}

.section-title i {
  color: #409EFF;
}

.solution-steps {
  margin: 0;
  padding-left: 20px;
}

.solution-steps li {
  margin-bottom: 8px;
  color: #606266;
}

.final-answer {
  background: #f0f9ff;
  padding: 15px;
  border-radius: 8px;
  border-left: 4px solid #409EFF;
}

.answer-label {
  font-weight: bold;
  color: #303133;
}

.answer-value {
  color: #409EFF;
  font-weight: bold;
  font-size: 16px;
}

.knowledge-points {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.knowledge-tag {
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .main-content {
    grid-template-columns: 1fr;
    gap: 20px;
  }
}

@media (max-width: 768px) {
  .photo-search-container {
    padding: 15px;
  }
  
  .page-title {
    font-size: 24px;
  }
  
  .upload-area {
    padding: 40px 20px;
  }
  
  .image-actions {
    flex-direction: column;
  }
  
  .voice-controls {
    flex-direction: column;
  }
}
</style> 