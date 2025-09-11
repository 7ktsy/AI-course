import { useRouter } from 'vue-router'

class VoiceNavigation {
  constructor() {
    this.recognition = null
    this.synthesis = window.speechSynthesis
    this.isListening = false
    this.router = null
    this.commands = new Map()
    this.keyboardShortcuts = new Map()
    this.retryCount = 0
    this.maxRetries = 3
    this.isOnline = navigator.onLine
    this.offlineMode = false

    // 语音设置
    this.voiceSettings = {
      voice: '',
      rate: 0.9,      // 语速稍慢，更自然
      pitch: 1.05,    // 音调适中，更自然
      volume: 0.9     // 音量适中
    }

    this.initSpeechRecognition()
    this.initCommands()
    this.initKeyboardShortcuts()
    this.initNetworkListeners()
    this.loadVoiceSettings()
  }

  // 初始化网络监听器
  initNetworkListeners() {
    window.addEventListener('online', () => {
      this.isOnline = true
      this.offlineMode = false
      console.log('网络连接已恢复')
      this.dispatchEvent('networkOnline')
    })

    window.addEventListener('offline', () => {
      this.isOnline = false
      console.log('网络连接已断开')
      this.dispatchEvent('networkOffline')
    })
  }

  // 初始化语音识别
  initSpeechRecognition() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
      this.recognition = new SpeechRecognition()
      this.recognition.continuous = false
      this.recognition.interimResults = false
      this.recognition.lang = 'zh-CN' // 中文识别
      this.recognition.maxAlternatives = 1

      this.recognition.onstart = () => {
        console.log('语音识别开始')
        this.isListening = true
        this.dispatchEvent('voiceStart')
      }

      this.recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript
        console.log('识别到语音:', transcript)
        this.retryCount = 0 // 重置重试计数
        this.processVoiceCommand(transcript)

        // 分发语音识别结果事件
        this.dispatchEvent('voiceResult', { transcript })
      }

      this.recognition.onerror = (event) => {
        console.error('语音识别错误:', event.error)
        this.isListening = false

        let errorMessage = '语音识别出错'
        let shouldRetry = false

        switch (event.error) {
          case 'network':
            errorMessage = '网络连接错误，请检查网络连接'
            shouldRetry = true
            break
          case 'not-allowed':
            errorMessage = '麦克风权限被拒绝，请允许麦克风访问'
            break
          case 'no-speech':
            errorMessage = '没有检测到语音，请重试'
            shouldRetry = true
            break
          case 'audio-capture':
            errorMessage = '音频捕获错误，请检查麦克风设备'
            break
          case 'service-not-allowed':
            errorMessage = '语音服务不可用，请稍后重试'
            shouldRetry = true
            break
          default:
            errorMessage = `语音识别错误: ${event.error}`
            shouldRetry = true
        }

        this.dispatchEvent('voiceError', { error: event.error, message: errorMessage })

        // 重试逻辑
        if (shouldRetry && this.retryCount < this.maxRetries) {
          this.retryCount++
          console.log(`重试语音识别 (${this.retryCount}/${this.maxRetries})`)
          setTimeout(() => {
            this.startListening()
          }, 1000)
        } else {
          this.retryCount = 0
          // 如果重试失败，提供离线模式选项
          if (this.retryCount >= this.maxRetries) {
            this.speak('语音识别暂时不可用，您可以继续使用键盘快捷键进行导航')
          }
        }
      }

      this.recognition.onend = () => {
        console.log('语音识别结束')
        this.isListening = false
        this.dispatchEvent('voiceEnd')
      }
    } else {
      console.error('浏览器不支持语音识别')
      this.dispatchEvent('voiceNotSupported')
    }
  }

  // 初始化语音命令映射
  initCommands() {
    // 页面导航命令
    this.commands.set('首页', () => this.navigateTo('/'))
    this.commands.set('登录', () => this.navigateTo('/login'))
    this.commands.set('演示', () => this.navigateTo('/voice-demo'))
    this.commands.set('语音演示', () => this.navigateTo('/voice-demo'))
    this.commands.set('语音AI演示', () => this.navigateTo('/voice-ai-demo'))
    this.commands.set('AI助手演示', () => this.navigateTo('/voice-ai-demo'))
    this.commands.set('仪表板', () => this.navigateTo('/dashboard'))
    this.commands.set('我的课程', () => this.navigateTo('/dashboard/courses'))
    this.commands.set('全部课程', () => this.navigateTo('/dashboard/all-courses'))
    this.commands.set('个人资料', () => this.navigateTo('/dashboard/profile'))
    this.commands.set('班级管理', () => this.navigateTo('/dashboard/class-management'))
    this.commands.set('智能备课', () => this.navigateTo('/dashboard/preparation'))
    this.commands.set('教案管理', () => this.navigateTo('/dashboard/preparation-manage'))
    this.commands.set('PPT生成', () => this.navigateTo('/dashboard/ppt-generation'))
    this.commands.set('AI出题', () => this.navigateTo('/dashboard/ai-question-generator'))

    // AI助手命令
    this.commands.set('AI助手', () => this.openAIChat())
    this.commands.set('语音助手', () => this.openVoiceAIChat())
    this.commands.set('打开AI助手', () => this.openAIChat())
    this.commands.set('打开语音助手', () => this.openVoiceAIChat())
    this.commands.set('智能助手', () => this.openAIChat())
    this.commands.set('语音AI', () => this.openVoiceAIChat())

    // 浏览器控制命令
    this.commands.set('返回', () => this.goBack())
    this.commands.set('前进', () => this.goForward())
    this.commands.set('刷新', () => this.refresh())
    this.commands.set('停止', () => this.stopListening())
    this.commands.set('帮助', () => this.showHelp())

    // 智能命令
    this.commands.set('课程', () => this.smartNavigate('course'))
    this.commands.set('管理', () => this.smartNavigate('management'))
    this.commands.set('备课', () => this.smartNavigate('preparation'))
    this.commands.set('资料', () => this.smartNavigate('profile'))
  }

  // 初始化键盘快捷键
  initKeyboardShortcuts() {
    this.keyboardShortcuts.set('Ctrl+Shift+V', () => this.toggleVoiceNavigation())
    this.keyboardShortcuts.set('Ctrl+Shift+H', () => this.showHelp())
    this.keyboardShortcuts.set('Ctrl+Shift+T', () => this.testVoice())
    this.keyboardShortcuts.set('Ctrl+Shift+S', () => this.testVoiceSettings()) // 测试语音设置

    // 绑定键盘事件
    document.addEventListener('keydown', (event) => {
      this.handleKeyboardShortcut(event)
    })
  }

  // 处理键盘快捷键
  handleKeyboardShortcut(event) {
    const key = this.getKeyCombination(event)
    const handler = this.keyboardShortcuts.get(key)

    if (handler) {
      event.preventDefault()
      handler()
    }
  }

  // 获取按键组合
  getKeyCombination(event) {
    const keys = []

    if (event.ctrlKey) keys.push('Ctrl')
    if (event.shiftKey) keys.push('Shift')
    if (event.altKey) keys.push('Alt')
    if (event.metaKey) keys.push('Meta')

    if (event.key !== 'Control' && event.key !== 'Shift' && event.key !== 'Alt' && event.key !== 'Meta') {
      keys.push(event.key.toUpperCase())
    }

    return keys.join('+')
  }

  // 设置路由器实例
  setRouter(router) {
    this.router = router
  }

  // 开始监听语音
  startListening() {
    if (!navigator.onLine) {
      this.speak('网络连接不可用，请检查网络连接')
      this.dispatchEvent('voiceError', { error: 'network', message: '网络连接不可用' })
      return
    }

    if (this.recognition && !this.isListening) {
      try {
        this.recognition.start()
        this.speak('语音识别启动')
      } catch (error) {
        console.error('启动语音识别失败:', error)
        this.speak('启动语音识别失败，请重试')
        this.dispatchEvent('voiceError', { error: 'start-failed', message: '启动语音识别失败' })
      }
    }
  }

  // 停止监听语音
  stopListening() {
    if (this.recognition && this.isListening) {
      this.recognition.stop()
      this.speak('语音导航已停止')
    }
  }

  // 切换语音导航状态
  toggleVoiceNavigation() {
    if (this.isListening) {
      this.stopListening()
    } else {
      this.startListening()
    }
  }

  // 处理语音命令
  processVoiceCommand(transcript) {
    const command = transcript.trim()

    // 检查是否有匹配的命令
    for (const [key, handler] of this.commands) {
      if (command.includes(key)) {
        this.speak(`正在执行：${key}`)
        handler()
        return
      }
    }

    // 模糊匹配
    const matchedCommand = this.fuzzyMatch(command)
    if (matchedCommand) {
      this.speak(`正在执行：${matchedCommand}`)
      this.commands.get(matchedCommand)()
      return
    }

    // 智能命令处理
    const smartResult = this.processSmartCommand(command)
    if (smartResult) {
      this.speak(smartResult.message)
      if (smartResult.action) {
        smartResult.action()
      }
      return
    }

    // 没有找到匹配的命令
    this.speak('抱歉，我没有理解您的指令，请重试')
  }

  // 智能命令处理
  processSmartCommand(command) {
    const lowerCommand = command.toLowerCase()

    // 数字导航
    const numberMatch = command.match(/(\d+)/)
    if (numberMatch) {
      const number = parseInt(numberMatch[1])
      return this.handleNumberNavigation(number)
    }

    // 方向导航
    if (lowerCommand.includes('上') || lowerCommand.includes('前')) {
      return { message: '正在返回上一页', action: () => this.goBack() }
    }

    if (lowerCommand.includes('下') || lowerCommand.includes('后')) {
      return { message: '正在前进到下一页', action: () => this.goForward() }
    }

    return null
  }

  // 数字导航处理
  handleNumberNavigation(number) {
    const routes = [
      { path: '/', name: '首页' },
      { path: '/login', name: '登录' },
      { path: '/voice-demo', name: '语音演示' },
      { path: '/dashboard', name: '仪表板' },
      { path: '/dashboard/courses', name: '我的课程' },
      { path: '/dashboard/all-courses', name: '全部课程' },
      { path: '/dashboard/profile', name: '个人资料' }
    ]

    if (number >= 1 && number <= routes.length) {
      const route = routes[number - 1]
      return {
        message: `正在导航到${route.name}`,
        action: () => this.navigateTo(route.path)
      }
    }

    return null
  }

  // 智能导航
  smartNavigate(type) {
    const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')

    switch (type) {
      case 'course':
        if (userInfo.role === 'student') {
          this.navigateTo('/dashboard/courses')
        } else {
          this.navigateTo('/dashboard/all-courses')
        }
        break
      case 'management':
        if (userInfo.role === 'teacher') {
          this.navigateTo('/dashboard/class-management')
        } else {
          this.speak('您没有管理权限')
        }
        break
      case 'preparation':
        if (userInfo.role === 'teacher') {
          this.navigateTo('/dashboard/preparation')
        } else {
          this.speak('备课功能仅对教师开放')
        }
        break
      case 'profile':
        this.navigateTo('/dashboard/profile')
        break
    }
  }

  // 模糊匹配命令
  fuzzyMatch(input) {
    const inputLower = input.toLowerCase()

    for (const [key] of this.commands) {
      const keyLower = key.toLowerCase()
      if (inputLower.includes(keyLower) || keyLower.includes(inputLower)) {
        return key
      }
    }

    return null
  }

  // 打开AI助手
  openAIChat() {
    // 触发打开AI助手的事件
    this.dispatchEvent('openAIChat')
    this.speak('正在打开AI助手')
  }

  // 打开语音AI助手
  openVoiceAIChat() {
    // 触发打开语音AI助手的事件
    this.dispatchEvent('openVoiceAIChat')
    this.speak('正在打开语音AI助手')
  }

  // 路由导航
  navigateTo(path) {
    if (this.router) {
      this.router.push(path)
    }
  }

  // 返回上一页
  goBack() {
    if (this.router) {
      this.router.go(-1)
    }
  }

  // 前进
  goForward() {
    if (this.router) {
      this.router.go(1)
    }
  }

  // 刷新页面
  refresh() {
    window.location.reload()
  }

  // 显示帮助信息
  showHelp() {
    const helpText = `
      可用的语音命令包括：
      页面导航：首页、登录、演示、仪表板、我的课程、全部课程、个人资料、
      班级管理、智能备课、教案管理、PPT生成、AI出题
      浏览器控制：返回、前进、刷新、停止、帮助
      智能命令：课程、管理、备课、资料
      数字导航：去第1页到第7页
      键盘快捷键：Ctrl+Shift+V 切换语音导航，Ctrl+Shift+H 显示帮助，Ctrl+Shift+T 测试语音，Ctrl+Shift+S 测试语音设置
    `
    this.speak(helpText)
  }

  // 测试语音
  testVoice() {
    this.speak('语音导航功能正常，您可以开始使用了')
  }

  // 测试不同语音设置
  testVoiceSettings() {
    const testTexts = [
      '您好，我是语音导航助手，很高兴为您服务。',
      '正在为您导航到首页，请稍候。',
      '抱歉，我没有理解您的指令，请重试。',
      '语音识别启动，请说出您的指令。'
    ]
    
    let currentIndex = 0
    
    const playNext = () => {
      if (currentIndex < testTexts.length) {
        this.speak(testTexts[currentIndex])
        currentIndex++
        setTimeout(playNext, 3000) // 3秒后播放下一句
      }
    }
    
    playNext()
  }

  // 停止语音播放
  stopSpeaking() {
    if (this.synthesis) {
      this.synthesis.cancel()
    }
  }

  // 语音合成 - 优化版本，参考拍照搜题的实现
  speak(text) {
    if (this.synthesis) {
      // 停止当前播放
      this.synthesis.cancel()
      
      const utterance = new SpeechSynthesisUtterance()
      utterance.lang = 'zh-CN'
      
      // 优化语音内容，添加自然停顿和语调
      // 根据不同类型的文本进行格式化
      let formattedText = text
      
      // 如果是帮助信息，添加更好的停顿
      if (text.includes('可用的语音命令包括')) {
        formattedText = text.replace(/\n/g, '。').replace(/：/g, '，')
      }
      
      // 如果是导航命令，添加更自然的表达
      if (text.includes('正在执行：') || text.includes('正在导航到')) {
        formattedText = text.replace('正在执行：', '好的，正在为您执行')
        formattedText = formattedText.replace('正在导航到', '正在为您导航到')
      }
      
      // 如果是错误信息，使用更友好的语调
      if (text.includes('抱歉') || text.includes('没有理解')) {
        formattedText = text.replace('抱歉，', '不好意思，')
      }
      
      utterance.text = formattedText
      
      // 优化语音参数，让声音更自然 - 参考拍照搜题的设置
      utterance.rate = 0.9        // 语速稍慢，更自然（比拍照搜题稍慢）
      utterance.pitch = 1.05      // 音调适中，更自然（比拍照搜题稍低）
      utterance.volume = 0.9      // 音量适中（比拍照搜题稍高）
      
      // 尝试选择更好的语音 - 使用和拍照搜题相同的逻辑
      const voices = this.synthesis.getVoices()
      
      // 优先选择用户设置的语音
      if (this.voiceSettings.voice) {
        const selectedVoice = voices.find(v => v.name === this.voiceSettings.voice)
        if (selectedVoice) {
          utterance.voice = selectedVoice
        }
      }
      
      // 如果没有设置语音，使用优化的语音选择
      if (!utterance.voice) {
        // 优先选择高质量的中文语音
        const chineseVoice = voices.find(voice => 
          voice.lang.includes('zh') && 
          (voice.name.includes('Xiaoxiao') || 
           voice.name.includes('Yunxi') || 
           voice.name.includes('Xiaoyi') ||
           voice.name.includes('Microsoft') ||
           voice.name.includes('Google'))
        )
        
        if (chineseVoice) {
          utterance.voice = chineseVoice
        } else {
          // 如果没有找到首选语音，选择第一个中文语音
          const anyChineseVoice = voices.find(v => v.lang.startsWith('zh'))
          if (anyChineseVoice) {
            utterance.voice = anyChineseVoice
          }
        }
      }
      
      // 添加语音播放事件监听
      utterance.onend = () => {
        console.log('语音播放完成')
        this.dispatchEvent('speechEnd')
      }
      
      utterance.onerror = (event) => {
        console.error('语音播放错误:', event.error)
        this.dispatchEvent('speechError', { error: event.error })
      }
      
      // 确保语音列表加载完成
      if (voices.length === 0) {
        window.speechSynthesis.onvoiceschanged = () => {
          const updatedVoices = this.synthesis.getVoices()
          
          // 重新选择语音
          if (!utterance.voice) {
            const chineseVoice = updatedVoices.find(voice => 
              voice.lang.includes('zh') && 
              (voice.name.includes('Xiaoxiao') || 
               voice.name.includes('Yunxi') || 
               voice.name.includes('Xiaoyi') ||
               voice.name.includes('Microsoft') ||
               voice.name.includes('Google'))
            )
            if (chineseVoice) {
              utterance.voice = chineseVoice
            }
          }
          
          this.synthesis.speak(utterance)
        }
      } else {
        this.synthesis.speak(utterance)
      }
    }
  }

  // 获取当前状态
  getStatus() {
    return {
      isListening: this.isListening,
      isSupported: !!this.recognition,
      isOnline: this.isOnline,
      retryCount: this.retryCount
    }
  }

  // 添加自定义命令
  addCommand(keyword, handler) {
    this.commands.set(keyword, handler)
  }

  // 移除命令
  removeCommand(keyword) {
    this.commands.delete(keyword)
  }

  // 添加键盘快捷键
  addKeyboardShortcut(keyCombination, handler) {
    this.keyboardShortcuts.set(keyCombination, handler)
  }

  // 移除键盘快捷键
  removeKeyboardShortcut(keyCombination) {
    this.keyboardShortcuts.delete(keyCombination)
  }

  // 分发自定义事件
  dispatchEvent(eventName, data = {}) {
    const event = new CustomEvent(`voiceNavigation:${eventName}`, {
      detail: data
    })
    window.dispatchEvent(event)
  }

  // 加载语音设置
  loadVoiceSettings() {
    const savedSettings = localStorage.getItem('voiceSettings')
    if (savedSettings) {
      try {
        this.voiceSettings = JSON.parse(savedSettings)
        console.log('加载语音设置成功:', this.voiceSettings)
      } catch (e) {
        console.error('加载语音设置失败:', e)
      }
    }
  }

  // 保存语音设置
  saveVoiceSettings() {
    localStorage.setItem('voiceSettings', JSON.stringify(this.voiceSettings))
    console.log('保存语音设置成功:', this.voiceSettings)
  }

  // 更新语音设置
  updateVoiceSettings(settings) {
    this.voiceSettings = { ...this.voiceSettings, ...settings }
    this.saveVoiceSettings()
    this.speak('语音设置已更新')
  }

  // 获取语音设置
  getVoiceSettings() {
    return this.voiceSettings
  }
}

// 创建单例实例
const voiceNavigation = new VoiceNavigation()

export default voiceNavigation 