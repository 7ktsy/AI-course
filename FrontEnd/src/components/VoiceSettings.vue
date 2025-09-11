<template>
  <el-drawer
    v-model="visible"
    title="语音设置"
    direction="rtl"
    size="400px"
    :before-close="handleClose"
  >
    <div class="voice-settings">
      <el-form :model="settings" label-width="100px">
        <!-- 语音选择 -->
        <el-form-item label="语音选择">
          <el-select v-model="settings.voice" placeholder="选择语音" @change="updateVoice">
            <el-option
              v-for="voice in availableVoices"
              :key="voice.name"
              :label="voice.name"
              :value="voice.name"
            >
              <span>{{ voice.name }}</span>
              <span style="float: right; color: #8492a6; font-size: 13px">
                {{ voice.lang }}
              </span>
            </el-option>
          </el-select>
        </el-form-item>

        <!-- 语速调节 -->
        <el-form-item label="语速">
          <el-slider
            v-model="settings.rate"
            :min="0.5"
            :max="2"
            :step="0.1"
            show-input
            :format-tooltip="formatRate"
            @change="updateVoice"
          />
          <div class="setting-description">
            较慢的语速让语音更清晰，较快的语速提高效率
          </div>
        </el-form-item>

        <!-- 音调调节 -->
        <el-form-item label="音调">
          <el-slider
            v-model="settings.pitch"
            :min="0.5"
            :max="2"
            :step="0.1"
            show-input
            :format-tooltip="formatPitch"
            @change="updateVoice"
          />
          <div class="setting-description">
            较低的音调更沉稳，较高的音调更活泼
          </div>
        </el-form-item>

        <!-- 音量调节 -->
        <el-form-item label="音量">
          <el-slider
            v-model="settings.volume"
            :min="0"
            :max="1"
            :step="0.1"
            show-input
            :format-tooltip="formatVolume"
            @change="updateVoice"
          />
          <div class="setting-description">
            调节语音播放的音量大小
          </div>
        </el-form-item>

        <!-- 语音预览 -->
        <el-form-item label="语音预览">
          <div class="preview-controls">
            <el-button type="primary" @click="previewVoice" :loading="isPreviewing">
              <el-icon><VideoPlay /></el-icon>
              播放预览
            </el-button>
            <el-button @click="stopPreview" :disabled="!isPreviewing">
              <el-icon><VideoPause /></el-icon>
              停止
            </el-button>
          </div>
          <div class="preview-text">
            <el-input
              v-model="previewText"
              type="textarea"
              :rows="3"
              placeholder="输入要预览的文本"
            />
          </div>
        </el-form-item>

        <!-- 预设方案 -->
        <el-form-item label="预设方案">
          <div class="preset-buttons">
            <el-button
              v-for="preset in presets"
              :key="preset.name"
              size="small"
              @click="applyPreset(preset)"
            >
              {{ preset.name }}
            </el-button>
          </div>
        </el-form-item>

        <!-- 保存设置 -->
        <el-form-item>
          <el-button type="primary" @click="saveSettings">
            保存设置
          </el-button>
          <el-button @click="resetSettings">
            重置默认
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </el-drawer>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { VideoPlay, VideoPause } from '@element-plus/icons-vue'
import voiceNavigation from '@/utils/voiceNavigation'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

const visible = ref(false)
const isPreviewing = ref(false)
const availableVoices = ref([])

// 语音设置
const settings = ref({
  voice: '',
  rate: 0.9,      // 语速稍慢，更自然
  pitch: 1.05,    // 音调适中，更自然
  volume: 0.9     // 音量适中
})

// 预览文本
const previewText = ref('你好！我是AI智能助手，很高兴为您服务。')

// 预设方案
const presets = [
  {
    name: '自然模式',
    settings: { rate: 0.9, pitch: 1.05, volume: 0.9 }
  },
  {
    name: '清晰模式',
    settings: { rate: 0.8, pitch: 1.0, volume: 0.9 }
  },
  {
    name: '优化模式',
    settings: { rate: 1.0, pitch: 1.1, volume: 0.85 }
  },
  {
    name: '快速模式',
    settings: { rate: 1.2, pitch: 1.0, volume: 0.8 }
  },
  {
    name: '温柔模式',
    settings: { rate: 0.75, pitch: 0.9, volume: 0.85 }
  },
  {
    name: '活泼模式',
    settings: { rate: 0.9, pitch: 1.2, volume: 0.95 }
  }
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
  stopPreview()
}

// 获取可用语音
const getAvailableVoices = () => {
  const voices = window.speechSynthesis.getVoices()
  availableVoices.value = voices.filter(voice => 
    voice.lang.startsWith('zh') || 
    voice.name.includes('Chinese') ||
    voice.name.includes('Microsoft') ||
    voice.name.includes('Google')
  )
  
  // 如果没有设置语音，选择第一个
  if (!settings.value.voice && availableVoices.value.length > 0) {
    settings.value.voice = availableVoices.value[0].name
  }
}

// 更新语音设置
const updateVoice = () => {
  // 这里可以实时更新语音导航的设置
  console.log('语音设置已更新:', settings.value)
}

// 预览语音
const previewVoice = () => {
  if (!previewText.value.trim()) {
    ElMessage.warning('请输入要预览的文本')
    return
  }
  
  isPreviewing.value = true
  
  // 创建临时语音合成
  const utterance = new SpeechSynthesisUtterance(previewText.value)
  utterance.lang = 'zh-CN'
  utterance.rate = settings.value.rate
  utterance.pitch = settings.value.pitch
  utterance.volume = settings.value.volume
  
  // 设置语音
  const voices = window.speechSynthesis.getVoices()
  const selectedVoice = voices.find(v => v.name === settings.value.voice)
  if (selectedVoice) {
    utterance.voice = selectedVoice
  }
  
  // 监听播放结束
  utterance.onend = () => {
    isPreviewing.value = false
  }
  
  utterance.onerror = () => {
    isPreviewing.value = false
    ElMessage.error('语音播放失败')
  }
  
  window.speechSynthesis.speak(utterance)
}

// 停止预览
const stopPreview = () => {
  window.speechSynthesis.cancel()
  isPreviewing.value = false
}

// 应用预设
const applyPreset = (preset) => {
  settings.value = { ...settings.value, ...preset.settings }
  ElMessage.success(`已应用${preset.name}`)
}

// 保存设置
const saveSettings = () => {
  // 保存到本地存储
  localStorage.setItem('voiceSettings', JSON.stringify(settings.value))
  
  // 更新语音导航设置
  voiceNavigation.updateVoiceSettings(settings.value)
  
  ElMessage.success('语音设置已保存')
}

// 重置设置
const resetSettings = () => {
  settings.value = {
    voice: '',
    rate: 1.0,
    pitch: 1.1,
    volume: 0.85
  }
  
  // 清除本地存储
  localStorage.removeItem('voiceSettings')
  
  ElMessage.success('已重置为默认设置')
}

// 格式化工具提示
const formatRate = (val) => {
  if (val < 0.8) return '较慢'
  if (val < 1.0) return '正常'
  if (val < 1.3) return '较快'
  return '很快'
}

const formatPitch = (val) => {
  if (val < 0.8) return '低沉'
  if (val < 1.0) return '正常'
  if (val < 1.3) return '明亮'
  return '高亢'
}

const formatVolume = (val) => {
  if (val < 0.3) return '很小'
  if (val < 0.6) return '较小'
  if (val < 0.9) return '正常'
  return '很大'
}

// 加载保存的设置
const loadSettings = () => {
  const saved = localStorage.getItem('voiceSettings')
  if (saved) {
    try {
      const savedSettings = JSON.parse(saved)
      settings.value = { ...settings.value, ...savedSettings }
    } catch (error) {
      console.error('加载语音设置失败:', error)
    }
  }
}

onMounted(() => {
  // 等待语音列表加载
  if (window.speechSynthesis.getVoices().length > 0) {
    getAvailableVoices()
  } else {
    window.speechSynthesis.onvoiceschanged = getAvailableVoices
  }
  
  loadSettings()
})
</script>

<style scoped>
.voice-settings {
  padding: 20px;
}

.setting-description {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
  line-height: 1.4;
}

.preview-controls {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.preview-text {
  margin-top: 10px;
}

.preset-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.preset-buttons .el-button {
  margin: 0;
}

:deep(.el-slider__input) {
  width: 80px;
}

:deep(.el-form-item__label) {
  font-weight: 600;
  color: #303133;
}
</style> 