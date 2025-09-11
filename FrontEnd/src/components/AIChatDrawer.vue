<template>
  <el-drawer
    v-model="visible"
    title="AI智能助手"
    direction="rtl"
    size="500px"
    :before-close="handleClose"
    class="ai-chat-drawer"
  >
    <div class="chat-container">
      <div class="chat-header">
        <h3>AI智能助手</h3>
        <p>我可以帮助您解答问题，告诉你具体的模块功能</p>
      </div>
      
      <div class="chat-content">
        <iframe
          v-if="visible"
          :src="chatUrl"
          class="chat-iframe"
          frameborder="0"
          allow="microphone; camera"
        ></iframe>
      </div>
      
      <div class="chat-footer">
        <el-button type="primary" @click="refreshChat">
          <el-icon><Refresh /></el-icon>
          刷新对话
        </el-button>
        <el-button @click="handleClose">
          <el-icon><Close /></el-icon>
          关闭
        </el-button>
      </div>
    </div>
  </el-drawer>
</template>

<script setup>
import { ref, watch } from 'vue'
import { Refresh, Close } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

const visible = ref(false)
const chatUrl = ref('http://localhost:8080/chat/share?shared_id=ce6e1698671a11f09dbed225975ede12&from=chat&auth=FlNDlkM2MwM2UxMTExZjA5NGUxMGU0NW')

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
}

// 刷新聊天
const refreshChat = () => {
  // 重新加载iframe
  const iframe = document.querySelector('.chat-iframe')
  if (iframe) {
    iframe.src = iframe.src
  }
}
</script>

<style scoped>
.ai-chat-drawer {
  --el-drawer-bg-color: #f5f5f5;
}

.chat-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chat-header {
  padding: 15px;
  background: linear-gradient(135deg, #43a6fd 0%, #abdffd 100%);
  color: white;
  border-radius: 8px;
  margin-bottom: 20px;
}

.chat-header h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
}

.chat-header p {
  margin: 0;
  font-size: 14px;
  opacity: 0.9;
}

.chat-content {
  flex: 1;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chat-iframe {
  width: 100%;
  height: 100%;
  min-height: 400px;
  border: none;
}

.chat-footer {
  padding: 20px 0;
  display: flex;
  gap: 12px;
  justify-content: center;
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
</style> 