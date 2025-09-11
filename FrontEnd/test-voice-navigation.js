// 语音导航功能测试脚本
// 在浏览器控制台中运行此脚本来测试语音导航功能

console.log('🎤 语音导航功能测试开始...')

// 测试语音导航实例
function testVoiceNavigation() {
  // 检查语音导航是否可用
  if (typeof voiceNavigation !== 'undefined') {
    console.log('✅ 语音导航实例已加载')
    
    // 测试状态获取
    const status = voiceNavigation.getStatus()
    console.log('📊 当前状态:', status)
    
    // 测试语音合成
    console.log('🗣️ 测试语音合成...')
    voiceNavigation.speak('语音导航功能测试正常')
    
    // 测试命令处理
    console.log('🧭 测试命令处理...')
    voiceNavigation.processVoiceCommand('帮助')
    
    return true
  } else {
    console.error('❌ 语音导航实例未找到')
    return false
  }
}

// 测试浏览器支持
function testBrowserSupport() {
  console.log('🌐 检查浏览器支持...')
  
  const hasSpeechRecognition = 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window
  const hasSpeechSynthesis = 'speechSynthesis' in window
  
  console.log('语音识别支持:', hasSpeechRecognition ? '✅' : '❌')
  console.log('语音合成支持:', hasSpeechSynthesis ? '✅' : '❌')
  
  return hasSpeechRecognition && hasSpeechSynthesis
}

// 测试网络连接
function testNetworkConnection() {
  console.log('🌍 检查网络连接...')
  
  const isOnline = navigator.onLine
  console.log('网络状态:', isOnline ? '✅ 在线' : '❌ 离线')
  
  return isOnline
}

// 测试麦克风权限
async function testMicrophonePermission() {
  console.log('🎤 检查麦克风权限...')
  
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    console.log('✅ 麦克风权限已获取')
    stream.getTracks().forEach(track => track.stop())
    return true
  } catch (error) {
    console.error('❌ 麦克风权限被拒绝:', error.message)
    return false
  }
}

// 运行所有测试
async function runAllTests() {
  console.log('🚀 开始运行语音导航功能测试...\n')
  
  const tests = [
    { name: '浏览器支持', test: testBrowserSupport },
    { name: '网络连接', test: testNetworkConnection },
    { name: '麦克风权限', test: testMicrophonePermission },
    { name: '语音导航实例', test: testVoiceNavigation }
  ]
  
  const results = []
  
  for (const test of tests) {
    console.log(`\n📋 测试: ${test.name}`)
    try {
      const result = await test.test()
      results.push({ name: test.name, passed: result })
      console.log(`${result ? '✅' : '❌'} ${test.name}: ${result ? '通过' : '失败'}`)
    } catch (error) {
      console.error(`❌ ${test.name}: 错误 -`, error)
      results.push({ name: test.name, passed: false, error: error.message })
    }
  }
  
  // 显示测试结果摘要
  console.log('\n📊 测试结果摘要:')
  const passedTests = results.filter(r => r.passed).length
  const totalTests = results.length
  
  console.log(`通过: ${passedTests}/${totalTests}`)
  
  if (passedTests === totalTests) {
    console.log('🎉 所有测试通过！语音导航功能应该可以正常工作。')
  } else {
    console.log('⚠️ 部分测试失败，请检查相关配置。')
    results.filter(r => !r.passed).forEach(r => {
      console.log(`  - ${r.name}: ${r.error || '失败'}`)
    })
  }
  
  return results
}

// 自动运行测试
if (typeof window !== 'undefined') {
  // 等待页面加载完成
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', runAllTests)
  } else {
    runAllTests()
  }
}

// 导出测试函数供手动调用
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    testVoiceNavigation,
    testBrowserSupport,
    testNetworkConnection,
    testMicrophonePermission,
    runAllTests
  }
} 