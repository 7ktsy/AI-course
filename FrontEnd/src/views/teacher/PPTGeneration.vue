<template>
  <div class="ppt-generation">
    <div class="page-header">
      <h2>AI PPT生成</h2>
      <p>通过AI助手生成PPT大纲，并自动创建精美的演示文稿</p>
    </div>

    <!-- 步骤指示器 -->
    <el-steps :active="currentStep" finish-status="success" class="steps">
      <el-step title="选择课程" description="选择要生成PPT的课程"></el-step>
      <el-step title="生成大纲" description="AI生成PPT大纲"></el-step>
      <el-step title="编辑大纲" description="调整和完善大纲内容"></el-step>
      <el-step title="生成PPT" description="生成并下载PPT文件"></el-step>
    </el-steps>

    <!-- 步骤1：选择课程 -->
    <div v-if="currentStep === 0" class="step-content">
      <el-card class="step-card">
        <template #header>
          <div class="card-header">
            <span>选择课程</span>
          </div>
        </template>
        
        <el-form :model="form" label-width="120px">
          <el-form-item label="选择课程">
            <el-select 
              v-model="form.courseId" 
              placeholder="请选择课程"
              style="width: 100%"
              @change="handleCourseChange"
            >
              <el-option
                v-for="course in courses"
                :key="course.id"
                :label="course.title"
                :value="course.id"
              />
            </el-select>
          </el-form-item>
          
          <!-- 教案选择 -->
          <el-form-item label="参考教案" v-if="form.courseId">
            <div class="preparation-selection">
              <el-select 
                v-model="form.preparationId" 
                placeholder="选择参考教案（可选）"
                style="width: 100%"
                clearable
                @change="handlePreparationChange"
                filterable
              >
                <el-option
                  v-for="prep in availablePreparations"
                  :key="prep.id"
                  :label="prep.title"
                  :value="prep.id"
                >
                  <div class="preparation-option-item">
                    <div class="prep-title">{{ prep.title }}</div>
                    <div class="prep-meta">
                      <span class="prep-author">{{ prep.teacher_name }}</span>
                      <span class="prep-date">{{ formatDate(prep.updated_at) }}</span>
                    </div>
                  </div>
                </el-option>
              </el-select>
              
              <!-- 选中的教案详情 -->
              <div v-if="selectedPreparation" class="selected-preparation-detail">
                <el-card class="preparation-card" shadow="hover">
                  <template #header>
                    <div class="card-header">
                      <span class="card-title">📚 已选择教案</span>
                      <el-button 
                        type="text" 
                        @click="clearPreparation"
                        size="small"
                      >
                        清除选择
                      </el-button>
                    </div>
                  </template>
                  
                  <div class="preparation-content">
                    <div class="prep-info-row">
                      <span class="label">标题：</span>
                      <span class="value">{{ selectedPreparation.title }}</span>
                    </div>
                    <div class="prep-info-row">
                      <span class="label">作者：</span>
                      <span class="value">{{ selectedPreparation.teacher_name }}</span>
                    </div>
                    <div class="prep-info-row">
                      <span class="label">更新时间：</span>
                      <span class="value">{{ formatDate(selectedPreparation.updated_at) }}</span>
                    </div>
                    <div class="prep-info-row">
                      <span class="label">内容预览：</span>
                      <div class="prep-content-preview">
                        {{ selectedPreparation.content }}
                      </div>
                    </div>
                  </div>
                </el-card>
              </div>
              
              <!-- 无教案提示 -->
              <div v-if="availablePreparations.length === 0" class="no-preparations">
                <el-alert
                  title="暂无可用教案"
                  description="该课程还没有已完成的教案，您可以先创建教案，或者直接生成PPT大纲"
                  type="warning"
                  show-icon
                  :closable="false"
                />
              </div>
            </div>
          </el-form-item>
          
          <el-form-item label="PPT主题">
            <el-input 
              v-model="form.topic" 
              placeholder="请输入PPT主题，如：Python基础语法、计算机网络协议等"
              type="textarea"
              :rows="3"
            />
          </el-form-item>
          
          <el-form-item>
            <el-button 
              type="primary" 
              @click="nextStep"
              :disabled="!form.courseId || !form.topic"
            >
              下一步：生成大纲
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>

    <!-- 步骤2：生成大纲 -->
    <div v-if="currentStep === 1" class="step-content">
      <el-card class="step-card">
        <template #header>
          <div class="card-header">
            <span>生成PPT大纲</span>
          </div>
        </template>
        
        <div class="outline-generation">
          <div class="generation-info">
            <p><strong>课程：</strong>{{ selectedCourse?.title }}</p>
            <p><strong>主题：</strong>{{ form.topic }}</p>
            <p v-if="selectedPreparation"><strong>参考教案：</strong>{{ selectedPreparation.title }}（{{ selectedPreparation.teacher_name }}）</p>
            <p v-else><strong>参考教案：</strong>无</p>
          </div>
          
          <el-button 
            type="primary" 
            @click="generateOutline"
            :loading="generating"
            :disabled="generating"
          >
            {{ generating ? '正在生成大纲...' : '开始生成大纲' }}
          </el-button>
          
          <div v-if="generating" class="generation-tips">
            <el-alert
              title="正在生成大纲"
              description="AI正在分析课程内容和参考教案，生成PPT大纲，请稍候..."
              type="info"
              :closable="false"
              show-icon
            />
          </div>
        </div>
      </el-card>
    </div>

    <!-- 步骤3：编辑大纲 -->
    <div v-if="currentStep === 2" class="step-content">
      <el-card class="step-card">
        <template #header>
          <div class="card-header">
            <span>编辑PPT大纲</span>
            <el-button type="primary" size="small" @click="addChapter">添加章节</el-button>
          </div>
        </template>
        
        <div class="outline-editor">
          <el-form :model="outlineData" label-width="120px">
            <el-form-item label="PPT标题">
              <el-input v-model="outlineData.title" placeholder="请输入PPT标题" />
            </el-form-item>
            
            <el-form-item label="章节内容">
              <div class="chapters-container">
                <div 
                  v-for="(points, chapter, index) in outlineData.content_dict" 
                  :key="index"
                  class="chapter-item"
                >
                  <div class="chapter-header">
                    <el-input 
                      v-model="chapterTitles[index]" 
                      placeholder="章节标题"
                      @input="updateChapterTitle(index, $event)"
                    />
                    <el-button 
                      type="danger" 
                      size="small" 
                      @click="removeChapter(index)"
                      :disabled="Object.keys(outlineData.content_dict).length <= 1"
                    >
                      删除
                    </el-button>
                  </div>
                  
                  <div class="points-container">
                    <div 
                      v-for="(point, pointIndex) in points" 
                      :key="pointIndex"
                      class="point-item"
                    >
                      <el-input 
                        v-model="outlineData.content_dict[chapter][pointIndex]" 
                        placeholder="要点内容"
                      />
                      <el-button 
                        type="danger" 
                        size="small" 
                        @click="removePoint(chapter, pointIndex)"
                        :disabled="points.length <= 1"
                      >
                        删除
                      </el-button>
                    </div>
                    <el-button 
                      type="success" 
                      size="small" 
                      @click="addPoint(chapter)"
                    >
                      添加要点
                    </el-button>
                  </div>
                </div>
              </div>
            </el-form-item>
            
            <el-form-item>
              <el-button @click="prevStep">上一步</el-button>
              <el-button type="primary" @click="nextStep">下一步：生成PPT</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-card>
    </div>

    <!-- 步骤4：生成PPT -->
    <div v-if="currentStep === 3" class="step-content">
      <el-card class="step-card">
        <template #header>
          <div class="card-header">
            <span>生成PPT文件</span>
          </div>
        </template>
        
        <div class="ppt-generation">
          <div class="generation-info">
            <p><strong>PPT标题：</strong>{{ outlineData.title }}</p>
            <p><strong>章节数量：</strong>{{ Object.keys(outlineData.content_dict).length }}</p>
            <p><strong>总要点数：</strong>{{ getTotalPoints() }}</p>
          </div>
          
          <!-- 样式选择区域 -->
          <div class="style-selection">
            <h3>选择PPT样式</h3>
            
            <!-- 主题选择 -->
            <div class="style-section">
              <h4>颜色主题</h4>
              <div class="theme-grid">
                <div 
                  v-for="theme in availableThemes" 
                  :key="theme"
                  class="theme-item"
                  :class="{ active: selectedTheme === theme }"
                  @click="selectedTheme = theme"
                >
                  <div class="theme-preview" :class="`theme-${theme}`">
                    <div class="theme-primary"></div>
                    <div class="theme-secondary"></div>
                    <div class="theme-accent"></div>
                  </div>
                  <div class="theme-info">
                    <div class="theme-name">{{ getThemeDisplayName(theme) }}</div>
                    <div class="theme-description">{{ themeDescriptions[theme] }}</div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 字体选择 -->
            <div class="style-section">
              <h4>字体配置</h4>
              <div class="font-grid">
                <div 
                  v-for="font in availableFonts" 
                  :key="font"
                  class="font-item"
                  :class="{ active: selectedFont === font }"
                  @click="selectedFont = font"
                >
                  <div class="font-preview" :class="`font-${font}`">
                    <div class="font-title">标题文字</div>
                    <div class="font-body">正文内容</div>
                  </div>
                  <div class="font-info">
                    <div class="font-name">{{ getFontDisplayName(font) }}</div>
                    <div class="font-description">{{ fontDescriptions[font] }}</div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 其他选项 -->
            <div class="style-section">
              <h4>其他选项</h4>
              <el-checkbox v-model="includeAnimations">包含动画效果</el-checkbox>
            </div>
          </div>
          
          <el-button 
            type="primary" 
            @click="generatePPT"
            :loading="generatingPPT"
            :disabled="generatingPPT"
            size="large"
          >
            {{ generatingPPT ? '正在生成PPT...' : '生成PPT文件' }}
          </el-button>
          
          <div v-if="generatingPPT" class="generation-tips">
            <el-alert
              title="正在生成PPT"
              description="正在创建精美的PPT文件，请稍候..."
              type="info"
              :closable="false"
              show-icon
            />
          </div>
          
          <div v-if="downloadInfo" class="download-section">
            <el-alert
              title="PPT生成成功！"
              :description="`文件已生成：${downloadInfo.file_name} (${downloadInfo.slide_count} 页)`"
              type="success"
              show-icon
            />
            <div class="download-actions">
              <el-button 
                type="primary" 
                @click="downloadPPT"
                icon="Download"
                size="large"
              >
                下载PPT文件
              </el-button>
              <el-button @click="resetForm" size="large">重新开始</el-button>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Download } from '@element-plus/icons-vue'
import request from '@/utils/request'

// 响应式数据
const currentStep = ref(0)
const courses = ref([])
const selectedCourse = ref(null)
const generating = ref(false)
const generatingPPT = ref(false)
const downloadInfo = ref(null)

// 表单数据
const form = reactive({
  courseId: null,
  topic: '',
  preparationId: null // 新增教案ID
})

// 大纲数据
const outlineData = reactive({
  title: '',
  content_dict: {}
})

// 章节标题（用于编辑）
const chapterTitles = ref([])

// 样式选择
const availableThemes = ref([])
const selectedTheme = ref('professional')
const themeDescriptions = ref({})

const availableFonts = ref([])
const selectedFont = ref('default')
const fontDescriptions = ref({})

const includeAnimations = ref(false)

// 教案数据
const availablePreparations = ref([])
const selectedPreparation = ref(null)

// 获取课程列表
const fetchCourses = async () => {
  try {
    const response = await request.get('/course/my')
    if (response?.data?.code === 0) {
      courses.value = response.data.data.courses || []
    } else {
      ElMessage.error('获取课程列表失败')
    }
  } catch (error) {
    console.error('获取课程列表失败:', error)
    ElMessage.error('获取课程列表失败')
  }
}

// 获取教案列表
const fetchPreparations = async () => {
  if (!form.courseId) {
    availablePreparations.value = []
    selectedPreparation.value = null
    return
  }
  try {
    const response = await request.get(`/ppt/preparations/${form.courseId}`)
    if (response?.data?.code === 0) {
      availablePreparations.value = response.data.data.preparations || []
      selectedPreparation.value = null // 重置选中的教案
    } else {
      ElMessage.error('获取教案列表失败')
    }
  } catch (error) {
    console.error('获取教案列表失败:', error)
    ElMessage.error('获取教案列表失败')
  }
}

// 处理课程选择
const handleCourseChange = () => {
  selectedCourse.value = courses.value.find(c => c.id === form.courseId)
  fetchPreparations() // 课程变化时重新获取教案
}

// 处理教案选择
const handlePreparationChange = () => {
  selectedPreparation.value = availablePreparations.value.find(p => p.id === form.preparationId)
}

// 清除选中的教案
const clearPreparation = () => {
  form.preparationId = null
  selectedPreparation.value = null
}

// 格式化日期
const formatDate = (timestamp) => {
  if (!timestamp) return 'N/A'
  const date = new Date(timestamp)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}`
}

// 生成大纲
const generateOutline = async () => {
  if (!form.courseId || !form.topic) {
    ElMessage.warning('请选择课程并输入主题')
    return
  }
  
  generating.value = true
  
  try {
    const response = await request.post('/ppt/generate-outline', {
      course_id: form.courseId,
      topic: form.topic,
      preparation_id: form.preparationId || null // 传递教案ID
    })
    
    if (response?.data?.code === 0) {
      // 更新大纲数据
      Object.assign(outlineData, response.data.data)
      
      // 初始化章节标题
      chapterTitles.value = Object.keys(outlineData.content_dict)
      
      ElMessage.success('大纲生成成功！')
      nextStep()
    } else {
      ElMessage.error(response?.data?.message || '生成大纲失败')
    }
  } catch (error) {
    console.error('生成大纲失败:', error)
    ElMessage.error('生成大纲失败，请重试')
  } finally {
    generating.value = false
  }
}

// 获取主题列表
const fetchThemes = async () => {
  try {
    const response = await request.get('/ppt/themes')
    if (response?.data?.code === 0) {
      availableThemes.value = response.data.data.themes
      themeDescriptions.value = response.data.data.theme_descriptions
    }
  } catch (error) {
    console.error('获取主题列表失败:', error)
  }
}

// 获取字体配置列表
const fetchFonts = async () => {
  try {
    const response = await request.get('/ppt/fonts')
    if (response?.data?.code === 0) {
      availableFonts.value = response.data.data.fonts
      fontDescriptions.value = response.data.data.font_descriptions
    }
  } catch (error) {
    console.error('获取字体配置列表失败:', error)
  }
}

// 生成PPT
const generatePPT = async () => {
  generatingPPT.value = true
  
  try {
    const response = await request.post('/ppt/generate', {
      title: outlineData.title,
      content_dict: outlineData.content_dict,
      course_id: form.courseId,
      theme: selectedTheme.value,
      font_config: selectedFont.value,
      include_animations: includeAnimations.value
    })
    
    if (response?.data?.code === 0) {
      downloadInfo.value = response.data.data
      ElMessage.success('PPT生成成功！')
    } else {
      ElMessage.error(response?.data?.message || '生成PPT失败')
    }
  } catch (error) {
    console.error('生成PPT失败:', error)
    ElMessage.error('生成PPT失败，请重试')
  } finally {
    generatingPPT.value = false
  }
}

// 下载PPT
const downloadPPT = () => {
  if (downloadInfo.value) {
    const link = document.createElement('a')
    link.href = downloadInfo.value.download_url
    link.download = downloadInfo.value.file_name
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }
}

// 编辑大纲相关方法
const addChapter = () => {
  const newChapterKey = `新章节${Object.keys(outlineData.content_dict).length + 1}`
  outlineData.content_dict[newChapterKey] = ['新要点']
  chapterTitles.value.push(newChapterKey)
}

const removeChapter = (index) => {
  const chapters = Object.keys(outlineData.content_dict)
  const chapterKey = chapters[index]
  delete outlineData.content_dict[chapterKey]
  chapterTitles.value.splice(index, 1)
}

const updateChapterTitle = (index, newTitle) => {
  const chapters = Object.keys(outlineData.content_dict)
  const oldKey = chapters[index]
  const points = outlineData.content_dict[oldKey]
  
  delete outlineData.content_dict[oldKey]
  outlineData.content_dict[newTitle] = points
  chapterTitles.value[index] = newTitle
}

const addPoint = (chapter) => {
  outlineData.content_dict[chapter].push('新要点')
}

const removePoint = (chapter, pointIndex) => {
  outlineData.content_dict[chapter].splice(pointIndex, 1)
}

// 计算总要点数
const getTotalPoints = () => {
  return Object.values(outlineData.content_dict).reduce((total, points) => total + points.length, 0)
}

// 获取主题显示名称
const getThemeDisplayName = (theme) => {
  const displayNames = {
    'professional': '专业商务',
    'modern': '现代简约',
    'elegant': '优雅精致',
    'tech': '科技感'
  }
  return displayNames[theme] || theme
}

// 获取字体显示名称
const getFontDisplayName = (font) => {
  const displayNames = {
    'default': '微软雅黑',
    'modern': '思源黑体',
    'elegant': '华文细黑'
  }
  return displayNames[font] || font
}

// 步骤控制
const nextStep = () => {
  if (currentStep.value < 3) {
    currentStep.value++
  }
}

const prevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

// 重置表单
const resetForm = () => {
  currentStep.value = 0
  form.courseId = null
  form.topic = ''
  form.preparationId = null // 重置教案ID
  selectedPreparation.value = null // 重置选中的教案
  availablePreparations.value = [] // 清空教案列表
  Object.assign(outlineData, { title: '', content_dict: {} })
  chapterTitles.value = []
  downloadInfo.value = null
  selectedTheme.value = 'professional'
  selectedFont.value = 'default'
  includeAnimations.value = false
}

// 组件挂载时获取数据
onMounted(() => {
  fetchCourses()
  fetchThemes()
  fetchFonts()
})
</script>

<style scoped>
.ppt-generation {
  padding: 20px;
}

.page-header {
  margin-bottom: 30px;
  text-align: center;
}

.page-header h2 {
  color: #303133;
  margin-bottom: 10px;
}

.page-header p {
  color: #606266;
  font-size: 14px;
}

.steps {
  margin-bottom: 40px;
}

.step-content {
  max-width: 800px;
  margin: 0 auto;
}

.step-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.outline-generation {
  text-align: center;
}

.generation-info {
  margin-bottom: 20px;
  text-align: left;
  background: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
}

.generation-info p {
  margin: 5px 0;
  color: #606266;
}

.generation-tips {
  margin-top: 20px;
}

.outline-editor {
  margin-top: 20px;
}

.chapters-container {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 15px;
}

.chapter-item {
  margin-bottom: 20px;
  padding: 15px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  background: #fafafa;
}

.chapter-header {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-bottom: 15px;
}

.chapter-header .el-input {
  flex: 1;
}

.points-container {
  margin-left: 20px;
}

.point-item {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-bottom: 10px;
}

.point-item .el-input {
  flex: 1;
}

.ppt-generation {
  text-align: center;
}

.style-selection {
  margin-top: 30px;
  margin-bottom: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 4px;
}

.style-selection h3 {
  margin-bottom: 20px;
  color: #303133;
}

.style-section {
  margin-bottom: 25px;
}

.style-section h4 {
  margin-bottom: 15px;
  color: #606266;
}

.theme-grid, .font-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 15px;
}

.theme-item, .font-item {
  cursor: pointer;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 15px;
  background: #fff;
  display: flex;
  flex-direction: column;
  align-items: center;
  transition: all 0.3s ease;
}

.theme-item:hover, .font-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.theme-item.active, .font-item.active {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.theme-preview, .font-preview {
  width: 100px;
  height: 70px;
  border-radius: 4px;
  margin-bottom: 10px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
  padding: 5px 0;
}

/* 主题预览样式 */
.theme-preview .theme-primary {
  width: 100%;
  height: 20px;
  border-radius: 4px;
  margin-bottom: 5px;
}

.theme-preview .theme-secondary {
  width: 100%;
  height: 20px;
  border-radius: 4px;
  margin-bottom: 5px;
}

.theme-preview .theme-accent {
  width: 100%;
  height: 20px;
  border-radius: 4px;
}

/* 具体主题颜色 */
.theme-professional .theme-primary { background-color: #004c99; }
.theme-professional .theme-secondary { background-color: #337ab7; }
.theme-professional .theme-accent { background-color: #5cb85c; }

.theme-modern .theme-primary { background-color: #34495e; }
.theme-modern .theme-secondary { background-color: #2c3e50; }
.theme-modern .theme-accent { background-color: #e74c3c; }

.theme-elegant .theme-primary { background-color: #ce7af0; }
.theme-elegant .theme-secondary { background-color: #c673e5; }
.theme-elegant .theme-accent { background-color: #f1c40f; }

.theme-tech .theme-primary { background-color: #2980b9; }
.theme-tech .theme-secondary { background-color: #3498db; }
.theme-tech .theme-accent { background-color: #e67e22; }

/* 字体预览样式 */
.font-preview {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  padding: 10px;
}

.font-preview .font-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 8px;
  color: #333;
}

.font-preview .font-body {
  font-size: 12px;
  color: #666;
  line-height: 1.4;
}

/* 字体样式 */
.font-default .font-title { font-family: "微软雅黑", sans-serif; }
.font-default .font-body { font-family: "微软雅黑", sans-serif; }

.font-modern .font-title { font-family: "思源黑体", "Source Han Sans", sans-serif; }
.font-modern .font-body { font-family: "思源黑体", "Source Han Sans", sans-serif; }

.font-elegant .font-title { font-family: "华文细黑", "STXihei", serif; }
.font-elegant .font-body { font-family: "华文细黑", "STXihei", serif; }

.theme-info, .font-info {
  text-align: center;
  font-size: 12px;
  color: #909399;
}

.theme-name, .font-name {
  font-weight: bold;
  color: #303133;
  margin-bottom: 4px;
}

.theme-description, .font-description {
  font-size: 11px;
  line-height: 1.3;
  color: #909399;
}

.preparation-selection {
  margin-top: 15px;
  margin-bottom: 20px;
}

.preparation-option-item {
  padding: 8px 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.prep-title {
  font-weight: 600;
  font-size: 14px;
  color: #303133;
  line-height: 1.4;
}

.prep-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #909399;
}

.prep-author {
  color: #409eff;
}

.prep-date {
  color: #67c23a;
}

.selected-preparation-detail {
  margin-top: 20px;
}

.preparation-card {
  margin-top: 15px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
}

.preparation-card .card-header {
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: #f8f9fa;
  border-bottom: 1px solid #e4e7ed;
}

.preparation-card .card-title {
  font-size: 16px;
  color: #303133;
  font-weight: bold;
}

.preparation-content {
  padding: 16px 20px;
}

.prep-info-row {
  display: flex;
  margin-bottom: 12px;
  align-items: flex-start;
}

.prep-info-row:last-child {
  margin-bottom: 0;
}

.prep-info-row .label {
  min-width: 80px;
  font-weight: 600;
  color: #606266;
  font-size: 14px;
}

.prep-info-row .value {
  flex: 1;
  color: #303133;
  font-size: 14px;
  line-height: 1.5;
}

.prep-content-preview {
  flex: 1;
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
  background: #f8f9fa;
  padding: 12px;
  border-radius: 4px;
  border-left: 3px solid #409eff;
  max-height: 120px;
  overflow-y: auto;
}

.no-preparations {
  margin-top: 15px;
  margin-bottom: 20px;
}

.download-section {
  margin-top: 30px;
}

.download-actions {
  margin-top: 20px;
  display: flex;
  gap: 15px;
  justify-content: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .step-content {
    max-width: 100%;
    padding: 0 10px;
  }
  
  .chapter-header,
  .point-item {
    flex-direction: column;
    align-items: stretch;
  }
  
  .download-actions {
    flex-direction: column;
  }
}
</style> 