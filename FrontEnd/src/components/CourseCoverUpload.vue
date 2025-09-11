<template>
  <div class="course-cover-upload">
    <el-upload
      class="cover-uploader"
      :show-file-list="false"
      :before-upload="beforeUpload"
      :http-request="customUpload"
      accept="image/*"
    >
      <div class="upload-area" v-if="!coverUrl">
        <el-icon class="upload-icon"><Plus /></el-icon>
        <div class="upload-text">点击上传封面</div>
        <div class="upload-tip">支持 JPG、PNG 格式，建议尺寸 400x300</div>
      </div>
      
      <div class="cover-preview" v-else>
        <el-image
          :src="coverUrl"
          fit="cover"
          class="preview-image"
          :preview-src-list="[coverUrl]"
        />
        <div class="cover-overlay">
          <el-icon class="change-icon"><Edit /></el-icon>
          <span>更换封面</span>
        </div>
      </div>
    </el-upload>
    
    <!-- 封面设置面板 -->
    <div class="cover-settings" v-if="coverUrl">
      <el-button size="small" @click="removeCover" type="danger" plain>
        <el-icon><Delete /></el-icon>
        删除封面
      </el-button>
      <el-button size="small" @click="generateAICover" type="primary" plain>
        <el-icon><Magic /></el-icon>
        AI生成封面
      </el-button>
    </div>
    
    <!-- 预设封面选择 -->
    <div class="preset-covers" v-if="!coverUrl">
      <h4>选择预设封面</h4>
      <div class="preset-grid">
        <div
          v-for="(preset, index) in presetCovers"
          :key="index"
          class="preset-item"
          @click="selectPreset(preset)"
        >
          <el-image
            :src="preset.url"
            fit="cover"
            class="preset-image"
          />
          <div class="preset-label">{{ preset.name }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Edit, Delete, Magic } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  courseTitle: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'cover-change'])

const coverUrl = ref(props.modelValue)

// 预设封面
const presetCovers = ref([
  {
    name: '科技',
    url: 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=400&h=300&fit=crop'
  },
  {
    name: '教育',
    url: 'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=400&h=300&fit=crop'
  },
  {
    name: '编程',
    url: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=400&h=300&fit=crop'
  },
  {
    name: '数学',
    url: 'https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=400&h=300&fit=crop'
  },
  {
    name: '艺术',
    url: 'https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8a?w=400&h=300&fit=crop'
  },
  {
    name: '商务',
    url: 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=300&fit=crop'
  }
])

// 监听外部值变化
watch(() => props.modelValue, (newVal) => {
  coverUrl.value = newVal
})

// 监听内部值变化
watch(coverUrl, (newVal) => {
  emit('update:modelValue', newVal)
  emit('cover-change', newVal)
})

// 上传前验证
const beforeUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB!')
    return false
  }
  return true
}

// 自定义上传
const customUpload = async (options) => {
  try {
    // 这里应该调用后端的上传API
    // 暂时使用本地预览
    const reader = new FileReader()
    reader.onload = (e) => {
      coverUrl.value = e.target.result
      ElMessage.success('封面上传成功')
    }
    reader.readAsDataURL(options.file)
  } catch (error) {
    ElMessage.error('封面上传失败')
  }
}

// 删除封面
const removeCover = () => {
  coverUrl.value = ''
  ElMessage.success('封面已删除')
}

// 选择预设封面
const selectPreset = (preset) => {
  coverUrl.value = preset.url
  ElMessage.success(`已选择${preset.name}封面`)
}

// AI生成封面
const generateAICover = () => {
  if (!props.courseTitle) {
    ElMessage.warning('请先输入课程标题')
    return
  }
  
  // 这里应该调用AI生成封面的API
  ElMessage.info('AI生成封面功能开发中...')
  
  // 模拟AI生成
  setTimeout(() => {
    const colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57']
    const randomColor = colors[Math.floor(Math.random() * colors.length)]
    coverUrl.value = `https://via.placeholder.com/400x300/${randomColor.substring(1)}/ffffff?text=${encodeURIComponent(props.courseTitle)}`
    ElMessage.success('AI封面生成完成')
  }, 2000)
}
</script>

<style scoped>
.course-cover-upload {
  width: 100%;
}

.cover-uploader {
  width: 100%;
}

.upload-area {
  width: 100%;
  height: 200px;
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: border-color 0.3s;
}

.upload-area:hover {
  border-color: #409eff;
}

.upload-icon {
  font-size: 32px;
  color: #c0c4cc;
  margin-bottom: 8px;
}

.upload-text {
  font-size: 16px;
  color: #606266;
  margin-bottom: 4px;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
}

.cover-preview {
  position: relative;
  width: 100%;
  height: 200px;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
}

.preview-image {
  width: 100%;
  height: 100%;
}

.cover-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
  color: white;
}

.cover-preview:hover .cover-overlay {
  opacity: 1;
}

.change-icon {
  font-size: 24px;
  margin-bottom: 4px;
}

.cover-settings {
  margin-top: 12px;
  display: flex;
  gap: 8px;
}

.preset-covers {
  margin-top: 20px;
}

.preset-covers h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #606266;
}

.preset-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.preset-item {
  cursor: pointer;
  border-radius: 6px;
  overflow: hidden;
  transition: transform 0.2s;
}

.preset-item:hover {
  transform: scale(1.05);
}

.preset-image {
  width: 100%;
  height: 80px;
}

.preset-label {
  padding: 4px 8px;
  font-size: 12px;
  text-align: center;
  background: #f5f7fa;
  color: #606266;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .preset-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .cover-settings {
    flex-direction: column;
  }
}
</style> 