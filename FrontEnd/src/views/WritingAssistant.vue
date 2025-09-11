<template>
    <div class="writing-assistant">
      <div class="container">
        <h1 class="page-title">AI写作助手</h1>
        
        <!-- 功能选择区域 -->
        <div class="feature-tabs">
          <button 
            :class="['tab-btn', { active: activeTab === 'image' }]"
            @click="activeTab = 'image'"
          >
            写作场景模拟
          </button>
          <button 
            :class="['tab-btn', { active: activeTab === 'writing' }]"
            @click="activeTab = 'writing'"
          >
            写作ai优化
          </button>
        </div>
  
        <!-- 图片生成功能 -->
        <div v-if="activeTab === 'image'" class="image-generation">
          <div class="input-section">
            <h3>根据写作内容生成图片</h3>
            <div class="form-group">
              <label for="promptText">作文内容：</label>
              <textarea
                id="promptText"
                v-model="imageForm.promptText"
                placeholder="请输入你的作文内容,将会进行ai绘画创造出丰富的场景帮助写作"
                rows="15"
                class="form-control"
              ></textarea>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label for="ratio">图片比例：</label>
                <select v-model="imageForm.ratio" class="form-control">
                  <option value="1920:1080">横屏 (16:9)</option>
                  <option value="1024:1024">正方形 (1:1)</option>
                  <option value="1080:1920">竖屏 (9:16)</option>
                </select>
              </div>
              
              <div class="form-group">
                <label for="seed">随机种子（可选）：</label>
                <input
                  id="seed"
                  v-model.number="imageForm.seed"
                  type="number"
                  placeholder="留空为随机"
                  class="form-control"
                />
              </div>
            </div>
            
            <button 
              @click="generateImage" 
              :disabled="isGenerating"
              class="btn btn-primary"
            >
              {{ isGenerating ? '生成中...' : '生成图片' }}
            </button>
          </div>
  
          <!-- 生成结果展示 -->
          <div v-if="generatedImage" class="result-section">
            <h3>生成结果</h3>
            <div class="image-container">
              <img 
                :src="generatedImage.image_url" 
                :alt="imageForm.promptText"
                class="generated-image"
              />
              <div class="image-actions">
                <button @click="downloadImage" class="btn btn-secondary">
                  下载图片
                </button>
                <button @click="regenerateImage" class="btn btn-outline">
                  重新生成
                </button>
              </div>
            </div>
            
            <!-- 图片转视频功能 -->
            <div class="video-generation">
              <h3>将图片转换为动态视频</h3>
              <div class="form-group">
                <label for="videoPrompt">视频描述：</label>
                <textarea
                  id="videoPrompt"
                  v-model="videoForm.promptText"
                  placeholder="请描述您希望生成的视频效果，例如：让画面动起来，添加一些动态元素等"
                  rows="4"
                  class="form-control"
                ></textarea>
              </div>
              
              <div class="form-row">
                <div class="form-group">
                  <label for="videoRatio">视频比例：</label>
                  <select v-model="videoForm.ratio" class="form-control">
                    <option value="1280:720">横屏 (16:9)</option>
                    <option value="1024:1024">正方形 (1:1)</option>
                    <option value="720:1280">竖屏 (9:16)</option>
                  </select>
                </div>
                
                <div class="form-group">
                  <label for="videoDuration">视频时长（秒）：</label>
                  <input
                    id="videoDuration"
                    v-model.number="videoForm.duration"
                    type="number"
                    min="1"
                    max="10"
                    class="form-control"
                  />
                </div>
              </div>
              
              <button 
                @click="generateVideo" 
                :disabled="isGeneratingVideo"
                class="btn btn-primary"
              >
                {{ isGeneratingVideo ? '生成视频中...' : '生成视频' }}
              </button>
            </div>
            
            <!-- 视频生成结果展示 -->
            <div v-if="generatedVideo" class="video-result-section">
              <h3>视频生成结果</h3>
              <div class="video-container">
                <video 
                  :src="generatedVideo.video_url" 
                  controls
                  class="generated-video"
                  preload="metadata"
                >
                  您的浏览器不支持视频播放
                </video>
                <div class="video-actions">
                  <button @click="downloadVideo" class="btn btn-secondary">
                    下载视频
                  </button>
                  <button @click="regenerateVideo" class="btn btn-outline">
                    重新生成
                  </button>
                </div>
              </div>
            </div>
          </div>
  
          <!-- 错误提示 -->
          <div v-if="errorMessage" class="error-message">
            <p>{{ errorMessage }}</p>
          </div>
        </div>
  
        <!-- 写作区域功能 -->
        <div v-if="activeTab === 'writing'" class="writing-area">
          <div class="writing-container">
            <div class="writing-section">
              <h3>写作区域</h3>
              <div class="form-group">
                <label for="writingContent">请输入您的作文内容：</label>
                <textarea
                  id="writingContent"
                  v-model="writingForm.content"
                  placeholder="请在这里输入您的作文内容..."
                  rows="12"
                  class="form-control writing-textarea"
                ></textarea>
              </div>
              
              <div class="writing-actions">
                <button 
                  @click="optimizeWriting" 
                  :disabled="isOptimizing || !writingForm.content.trim()"
                  class="btn btn-primary"
                >
                  {{ isOptimizing ? 'AI优化中...' : 'AI优化' }}
                </button>
                <button @click="clearWriting" class="btn btn-outline">
                  清空内容
                </button>
              </div>
            </div>
  
            <!-- AI优化结果展示 -->
            <div v-if="optimizedContent" class="optimization-section">
              <h3>AI优化建议</h3>
              <div class="optimization-content">
                <div class="original-text">
                  <h4>原文：</h4>
                  <div class="text-content">{{ writingForm.content }}</div>
                </div>
                <div class="optimized-text">
                  <h4>优化后：</h4>
                  <div class="text-content optimized">{{ optimizedContent }}</div>
                </div>
              </div>
              <div class="optimization-actions">
                <button @click="applyOptimization" class="btn btn-success">
                  应用优化
                </button>
                <button @click="regenerateOptimization" class="btn btn-outline">
                  重新优化
                </button>
              </div>
            </div>
  
            <!-- 错误提示 -->
            <div v-if="errorMessage" class="error-message">
              <p>{{ errorMessage }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { ref, reactive } from 'vue'
  import axios from 'axios'
  
  export default {
    name: 'WritingAssistant',
    setup() {
      const activeTab = ref('image')
      const isGenerating = ref(false)
      const isOptimizing = ref(false)
      const isGeneratingVideo = ref(false)
      const generatedImage = ref(null)
      const generatedVideo = ref(null)
      const optimizedContent = ref('')
      const errorMessage = ref('')

      const imageForm = reactive({
        promptText: '',
        ratio: '1920:1080',
        seed: null
      })

      const videoForm = reactive({
        promptText: '',
        ratio: '1280:720',
        duration: 5
      })

      const writingForm = reactive({
        content: ''
      })
  
      const generateImage = async () => {
        if (!imageForm.promptText.trim()) {
          errorMessage.value = '请输入图片描述'
          return
        }
  
        isGenerating.value = true
        errorMessage.value = ''
  
        // 重试机制
        const maxRetries = 3
        let lastError = null
  
        for (let attempt = 1; attempt <= maxRetries; attempt++) {
          try {
            console.log(`🔄 尝试第 ${attempt} 次生成图片...`)
            
            const response = await axios.post('http://127.0.0.1:8000/image-generator/generate-image', {
              promptText: imageForm.promptText,
              ratio: imageForm.ratio,
              model: 'gen4_image',
              seed: imageForm.seed || undefined
            }, {
              timeout: 300000 // 5分钟超时
            })
  
            console.log('📥 收到响应:', response.data)
  
            if (response.data.success) {
              generatedImage.value = response.data
              console.log('✅ 图片生成成功！', response.data)
              isGenerating.value = false
              return
            } else {
              errorMessage.value = response.data.error_message || '图片生成失败'
              console.log('❌ 图片生成失败:', response.data.error_message)
              isGenerating.value = false
              return
            }
          } catch (error) {
            lastError = error
            console.error(`❌ 第 ${attempt} 次尝试失败:`, error)
            
            let errorMsg = ''
            if (error.code === 'ECONNABORTED') {
              errorMsg = '请求超时，请检查网络连接'
            } else if (error.code === 'ERR_NETWORK') {
              errorMsg = '网络连接错误，请检查网络设置'
            } else if (error.response?.status === 500) {
              errorMsg = '服务器内部错误，请稍后重试'
            } else if (error.response?.data?.error_message) {
              errorMsg = error.response.data.error_message
            } else {
              errorMsg = error.message || '未知错误'
            }
            
            if (attempt < maxRetries) {
              errorMessage.value = `${errorMsg} (第 ${attempt} 次尝试失败，正在重试...)`
              console.log(`⏳ 等待2秒后重试...`)
              // 等待2秒后重试
              await new Promise(resolve => setTimeout(resolve, 2000))
            } else {
              errorMessage.value = `${errorMsg} (已重试 ${maxRetries} 次)`
              console.log('💥 所有重试都失败了')
              isGenerating.value = false
            }
          }
        }
      }
  
      const optimizeWriting = async () => {
        if (!writingForm.content.trim()) {
          errorMessage.value = '请输入作文内容'
          return
        }

        isOptimizing.value = true
        errorMessage.value = ''

        try {
          console.log('🤖 开始AI优化写作...')
          
          // 获取认证token
          const token = localStorage.getItem('token')
          if (!token) {
            errorMessage.value = '请先登录'
            isOptimizing.value = false
            return
          }
          
          // 调用AI对话接口进行写作优化
          const response = await axios.post('http://127.0.0.1:8000/chat/simple', null, {
            params: {
              question: `请帮我优化以下作文，使其更加生动、流畅、有逻辑性，同时保持原文的主要内容和风格：\n\n${writingForm.content}`,
              chat_name: "写作助手"
            },
            headers: {
              'Authorization': `Bearer ${token}`
            },
            timeout: 120000 // 2分钟超时
          })

          console.log('📥 收到AI优化响应:', response.data)

          if (response.data.code === 0) {
            optimizedContent.value = response.data.data.answer
            console.log('✅ AI优化成功！')
          } else {
            errorMessage.value = response.data.message || 'AI优化失败'
            console.log('❌ AI优化失败:', response.data.message)
          }
        } catch (error) {
          console.error('❌ AI优化时出错:', error)
          
          let errorMsg = ''
          if (error.code === 'ECONNABORTED') {
            errorMsg = '请求超时，请检查网络连接'
          } else if (error.code === 'ERR_NETWORK') {
            errorMsg = '网络连接错误，请检查网络设置'
          } else if (error.response?.status === 401) {
            errorMsg = '认证失败，请重新登录'
          } else if (error.response?.status === 403) {
            errorMsg = '权限不足，请检查用户权限'
          } else if (error.response?.status === 500) {
            errorMsg = '服务器内部错误，请稍后重试'
          } else if (error.response?.data?.message) {
            errorMsg = error.response.data.message
          } else {
            errorMsg = error.message || '未知错误'
          }
          
          errorMessage.value = errorMsg
        } finally {
          isOptimizing.value = false
        }
      }
  
      const applyOptimization = () => {
        if (optimizedContent.value) {
          writingForm.content = optimizedContent.value
          optimizedContent.value = ''
          console.log('✅ 已应用AI优化')
        }
      }
  
      const regenerateOptimization = () => {
        optimizeWriting()
      }
  
      const clearWriting = () => {
        writingForm.content = ''
        optimizedContent.value = ''
        errorMessage.value = ''
      }
  
      const downloadImage = async () => {
        if (!generatedImage.value?.image_url) return
  
        try {
          const response = await axios.get(generatedImage.value.image_url, {
            responseType: 'blob'
          })
          
          const url = window.URL.createObjectURL(new Blob([response.data]))
          const link = document.createElement('a')
          link.href = url
          link.setAttribute('download', `generated-image-${Date.now()}.jpg`)
          document.body.appendChild(link)
          link.click()
          link.remove()
          window.URL.revokeObjectURL(url)
        } catch (error) {
          console.error('下载图片时出错:', error)
          errorMessage.value = '下载图片失败'
        }
      }
  
      const regenerateImage = () => {
        generateImage()
      }

      const generateVideo = async () => {
        if (!generatedImage.value?.image_url) {
          errorMessage.value = '请先生成图片'
          return
        }

        if (!videoForm.promptText.trim()) {
          errorMessage.value = '请输入视频描述'
          return
        }

        isGeneratingVideo.value = true
        errorMessage.value = ''

        // 重试机制
        const maxRetries = 3
        let lastError = null

        for (let attempt = 1; attempt <= maxRetries; attempt++) {
          try {
            console.log(`🎬 尝试第 ${attempt} 次生成视频...`)
            
            const response = await axios.post('http://127.0.0.1:8000/writing-assistant/image-url-to-video', {
              prompt_text: videoForm.promptText,
              image_url: generatedImage.value.image_url,
              ratio: videoForm.ratio,
              model: 'gen4_turbo',
              duration: videoForm.duration
            }, {
              timeout: 600000 // 10分钟超时
            })

            console.log('📥 收到视频生成响应:', response.data)

            if (response.data.success) {
              generatedVideo.value = response.data
              console.log('✅ 视频生成成功！', response.data)
              isGeneratingVideo.value = false
              return
            } else {
              errorMessage.value = response.data.error_message || '视频生成失败'
              console.log('❌ 视频生成失败:', response.data.error_message)
              isGeneratingVideo.value = false
              return
            }
          } catch (error) {
            lastError = error
            console.error(`❌ 第 ${attempt} 次视频生成尝试失败:`, error)
            
            let errorMsg = ''
            if (error.code === 'ECONNABORTED') {
              errorMsg = '请求超时，请检查网络连接'
            } else if (error.code === 'ERR_NETWORK') {
              errorMsg = '网络连接错误，请检查网络设置'
            } else if (error.response?.status === 500) {
              errorMsg = '服务器内部错误，请稍后重试'
            } else if (error.response?.data?.error_message) {
              errorMsg = error.response.data.error_message
            } else {
              errorMsg = error.message || '未知错误'
            }
            
            if (attempt < maxRetries) {
              errorMessage.value = `${errorMsg} (第 ${attempt} 次尝试失败，正在重试...)`
              console.log(`⏳ 等待3秒后重试...`)
              // 等待3秒后重试
              await new Promise(resolve => setTimeout(resolve, 3000))
            } else {
              errorMessage.value = `${errorMsg} (已重试 ${maxRetries} 次)`
              console.log('💥 所有视频生成重试都失败了')
              isGeneratingVideo.value = false
            }
          }
        }
      }

      const downloadVideo = async () => {
        if (!generatedVideo.value?.video_url) return

        try {
          const response = await axios.get(generatedVideo.value.video_url, {
            responseType: 'blob'
          })
          
          const url = window.URL.createObjectURL(new Blob([response.data]))
          const link = document.createElement('a')
          link.href = url
          link.setAttribute('download', `generated-video-${Date.now()}.mp4`)
          document.body.appendChild(link)
          link.click()
          link.remove()
          window.URL.revokeObjectURL(url)
        } catch (error) {
          console.error('下载视频时出错:', error)
          errorMessage.value = '下载视频失败'
        }
      }

      const regenerateVideo = () => {
        generateVideo()
      }
  
      return {
        activeTab,
        imageForm,
        writingForm,
        isGenerating,
        isOptimizing,
        generatedImage,
        optimizedContent,
        errorMessage,
        generateImage,
        optimizeWriting,
        applyOptimization,
        regenerateOptimization,
        clearWriting,
        downloadImage,
        regenerateImage,
        videoForm,
        isGeneratingVideo,
        generatedVideo,
        generateVideo,
        downloadVideo,
        regenerateVideo
      }
    }
  }
  </script>
  
  <style scoped>
  .writing-assistant {
    min-height: 100vh;
    background-color: #f5f5f5;
    padding: 20px;
  }
  
  .container {
    max-width: 1200px;
    margin: 0 auto;
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    overflow: hidden;
  }
  
  .page-title {
    text-align: center;
    color: #2c3e50;
    margin: 30px 0;
    font-size: 2.5rem;
    font-weight: 700;
  }
  
  .feature-tabs {
    display: flex;
    justify-content: center;
    margin-bottom: 30px;
    border-bottom: 2px solid #e9ecef;
  }
  
  .tab-btn {
    padding: 15px 30px;
    border: none;
    background: none;
    font-size: 1.1rem;
    font-weight: 600;
    color: #6c757d;
    cursor: pointer;
    transition: all 0.3s ease;
    border-bottom: 3px solid transparent;
  }
  
  .tab-btn.active {
    color: #1976d2;
    border-bottom-color: #1976d2;
  }
  
  .tab-btn:hover {
    color: #1976d2;
  }
  
  .image-generation {
    padding: 30px;
  }
  
  .writing-area {
    padding: 30px;
  }
  
  .writing-container {
    max-width: 1000px;
    margin: 0 auto;
  }
  
  .writing-section {
    margin-bottom: 30px;
  }
  
  .writing-section h3 {
    color: #2c3e50;
    margin-bottom: 20px;
    font-size: 1.5rem;
  }
  
  .input-section {
    max-width: 800px;
    margin: 0 auto;
  }
  
  .input-section h3 {
    color: #2c3e50;
    margin-bottom: 20px;
    font-size: 1.5rem;
  }
  
  .form-group {
    margin-bottom: 20px;
  }
  
  .form-group label {
    display: block;
    margin-bottom: 8px;
    font-weight: 600;
    color: #495057;
  }
  
  .form-control {
    width: 100%;
    padding: 12px 15px;
    border: 2px solid #e9ecef;
    border-radius: 8px;
    font-size: 1rem;
    transition: border-color 0.3s ease;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', sans-serif;
  }
  
  .form-control:focus {
    outline: none;
    border-color: #1976d2;
  }
  
  .writing-textarea {
    resize: vertical;
    min-height: 300px;
    line-height: 1.6;
  }
  
  .form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
  }
  
  .btn {
    padding: 12px 25px;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    text-decoration: none;
    display: inline-block;
  }
  
  .btn-primary {
    background: #1976d2;
    color: white;
  }
  
  .btn-primary:hover:not(:disabled) {
    background: #1565c0;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(25, 118, 210, 0.3);
  }
  
  .btn-primary:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  .btn-secondary {
    background: #28a745;
    color: white;
  }
  
  .btn-secondary:hover {
    background: #218838;
  }
  
  .btn-success {
    background: #28a745;
    color: white;
  }
  
  .btn-success:hover {
    background: #218838;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
  }
  
  .btn-outline {
    background: transparent;
    color: #1976d2;
    border: 2px solid #1976d2;
  }
  
  .btn-outline:hover {
    background: #1976d2;
    color: white;
  }
  
  .writing-actions {
    display: flex;
    gap: 15px;
    margin-top: 20px;
  }
  
  .result-section {
    margin-top: 40px;
    padding-top: 30px;
    border-top: 2px solid #e9ecef;
  }
  
  .result-section h3 {
    color: #2c3e50;
    margin-bottom: 20px;
    font-size: 1.5rem;
  }
  
  .image-container {
    text-align: center;
  }
  
  .generated-image {
    max-width: 100%;
    max-height: 500px;
    border-radius: 10px;
    box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
    margin-bottom: 20px;
  }
  
  .image-actions {
    display: flex;
    gap: 15px;
    justify-content: center;
    flex-wrap: wrap;
  }

  .video-generation {
    margin-top: 40px;
    padding: 30px;
    background: #f8f9fa;
    border-radius: 12px;
    border: 1px solid #e9ecef;
  }

  .video-generation h3 {
    color: #2c3e50;
    margin-bottom: 20px;
    font-size: 1.5rem;
  }

  .video-result-section {
    margin-top: 30px;
    padding-top: 30px;
    border-top: 2px solid #e9ecef;
  }

  .video-result-section h3 {
    color: #2c3e50;
    margin-bottom: 20px;
    font-size: 1.5rem;
  }

  .video-container {
    text-align: center;
  }

  .generated-video {
    max-width: 100%;
    max-height: 500px;
    border-radius: 10px;
    box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
    margin-bottom: 20px;
  }

  .video-actions {
    display: flex;
    gap: 15px;
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .optimization-section {
    margin-top: 40px;
    padding: 30px;
    background: #f8f9fa;
    border-radius: 12px;
    border: 1px solid #e9ecef;
  }
  
  .optimization-section h3 {
    color: #2c3e50;
    margin-bottom: 20px;
    font-size: 1.5rem;
  }
  
  .optimization-content {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 30px;
    margin-bottom: 20px;
  }
  
  .original-text,
  .optimized-text {
    background: white;
    padding: 20px;
    border-radius: 8px;
    border: 1px solid #e9ecef;
  }
  
  .original-text h4,
  .optimized-text h4 {
    color: #2c3e50;
    margin-bottom: 15px;
    font-size: 1.1rem;
    font-weight: 600;
  }
  
  .text-content {
    line-height: 1.8;
    color: #495057;
    white-space: pre-wrap;
    word-wrap: break-word;
  }
  
  .text-content.optimized {
    color: #1976d2;
    font-weight: 500;
  }
  
  .optimization-actions {
    display: flex;
    gap: 15px;
    justify-content: center;
  }
  
  .error-message {
    margin-top: 20px;
    padding: 15px;
    background: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
    border-radius: 8px;
  }
  
  @media (max-width: 768px) {
    .form-row,
    .optimization-content {
      grid-template-columns: 1fr;
    }
    
    .page-title {
      font-size: 2rem;
    }
    
    .image-actions,
    .writing-actions,
    .optimization-actions {
      flex-direction: column;
      align-items: center;
    }
    
    .btn {
      width: 100%;
      max-width: 200px;
    }
  }
  </style>