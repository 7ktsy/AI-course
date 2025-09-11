<template>
  <div class="generator-container">
    <!-- 顶部选择区域 -->
    <div class="header-section">
      <div class="header-top">
        <h2>试卷生成助手</h2>
        <el-select 
          v-model="selectedCourse" 
          placeholder="请选择课程"
          class="course-select"
          @change="handleCourseChange"
        >
          <el-option
            v-for="course in courses"
            :key="course.id"
            :label="course.title"
            :value="course.id"
          />
        </el-select>
      </div>

      <!-- 试卷配置区域 -->
      <div class="config-section" v-if="selectedCourse">
        <div class="config-grid">
          <div class="config-item">
            <span class="label">选择题：</span>
            <div class="config-inputs">
              <el-input-number v-model="config.choice" :min="0" :max="10" size="small" class="number-input" />
              <span class="label-small">题</span>
              <el-input-number v-model="config.choicePoints" :min="1" :max="10" size="small" class="number-input" />
              <span class="label-small">分/题</span>
            </div>
          </div>

          <div class="config-item">
            <span class="label">填空题：</span>
            <div class="config-inputs">
              <el-input-number v-model="config.blank" :min="0" :max="10" size="small" class="number-input" />
              <span class="label-small">题</span>
              <el-input-number v-model="config.blankPoints" :min="1" :max="10" size="small" class="number-input" />
              <span class="label-small">分/题</span>
            </div>
          </div>

          <div class="config-item">
            <span class="label">简答题：</span>
            <div class="config-inputs">
              <el-input-number v-model="config.short" :min="0" :max="5" size="small" class="number-input" />
              <span class="label-small">题</span>
              <el-input-number v-model="config.shortPoints" :min="1" :max="20" size="small" class="number-input" />
              <span class="label-small">分/题</span>
            </div>
          </div>

          <div class="config-item full-width">
            <span class="label">难度分布：</span>
            <el-slider
              v-model="config.difficulty"
              range
              :marks="{
                0: '简单',
                50: '中等',
                100: '困难'
              }"
            />
          </div>
        </div>

        <div class="config-footer">
          <div class="requirements-input">
            <el-input
              v-model="config.requirements"
              type="textarea"
              :rows="2"
              placeholder="请输入其他具体要求，如考察重点、知识点范围等..."
            />
          </div>

          <div class="config-actions">
            <el-button-group>
              <el-button type="primary" :loading="generating" @click="generatePaper">
                生成试卷
              </el-button>
              <el-button @click="applyTemplate">
                应用模板
              </el-button>
              <el-button @click="resetConfig">
                重置
              </el-button>
            </el-button-group>
          </div>
        </div>
      </div>

      <!-- 未选择课程时的提示 -->
      <div v-else class="no-course-tip">
        请先选择一门课程以配置试卷
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="content-section">
      <!-- 生成结果展示区域 -->
      <div v-if="paperContent" class="result-section">
        <div class="paper-header">
          <div class="paper-info">
            <h3>生成的试卷内容</h3>
            <div class="meta-info">
              <span>生成时间：{{ generateTime }}</span>
              <span>总分：{{ totalPoints }} 分</span>
              <span>课程：{{ selectedCourseTitle }}</span>
            </div>
          </div>
          <div class="paper-actions">
            <el-button-group>
              <el-button 
                type="primary"
                :class="{ active: showAnswers }"
                @click="showAnswers = !showAnswers"
              >
                {{ showAnswers ? '隐藏答案' : '显示答案' }}
              </el-button>
              <el-button 
                type="success"
                @click="exportPaper('paper')"
              >
                导出试卷
              </el-button>
              <el-button 
                type="warning"
                @click="exportPaper('answer')"
              >
                导出答案
              </el-button>
              <el-button 
                type="info"
                @click="handleUploadToBank"
              >
                上传题库
              </el-button>
            </el-button-group>
          </div>
        </div>

        <div class="paper-content">
          <div class="rendered-content" v-html="renderedContent"></div>
        </div>
      </div>

      <!-- 无内容时的提示 -->
      <div v-else-if="!generating" class="no-content">
        <el-empty description="请配置试卷要求并点击生成" />
      </div>
    </div>

    <!-- 在 template 中添加试卷预览对话框 -->
    <el-dialog
      v-model="showPreview"
      title="试卷预览"
      fullscreen
      :show-close="true"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
    >
      <template #header="{ close, titleId, titleClass }">
        <div class="preview-header">
          <h3 :id="titleId" :class="titleClass">{{ selectedCourseTitle }} - 试卷预览</h3>
          <div class="preview-actions">
            <el-button-group>
              <el-button 
                type="primary"
                :class="{ active: showAnswers }"
                @click="showAnswers = !showAnswers"
              >
                {{ showAnswers ? '隐藏答案' : '显示答案' }}
              </el-button>
              <el-button 
                type="success"
                @click="exportPaper('paper')"
              >
                导出试卷
              </el-button>
              <el-button 
                type="warning"
                @click="exportPaper('answer')"
              >
                导出答案
              </el-button>
              <el-button 
                type="info"
                @click="handleUploadToBank"
              >
                上传题库
              </el-button>
            </el-button-group>
            <el-button type="danger" @click="close">关闭</el-button>
          </div>
        </div>
      </template>

      <div class="preview-content">
        <div class="paper-info">
          <span>生成时间：{{ generateTime }}</span>
          <span>总分：{{ totalPoints }} 分</span>
        </div>
        <div class="paper-content">
          <div class="rendered-content" v-html="renderedContent"></div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import { saveAs } from 'file-saver'
import { marked } from 'marked'

// 数据定义
const courses = ref([])
const selectedCourse = ref(null)
const generating = ref(false)
const paperContent = ref('')
const showAnswers = ref(false)
const generateTime = ref('')

// 试卷配置
const config = ref({
  choice: 3,
  choicePoints: 2,
  blank: 4,
  blankPoints: 2,
  short: 2,
  shortPoints: 10,
  difficulty: [20, 60], // 难度分布范围
  requirements: ''
})

// 计算属性
const selectedCourseTitle = computed(() => {
  return courses.value.find(c => c.id === selectedCourse.value)?.title || '未知课程'
})

const totalPoints = computed(() => {
  const { choice, choicePoints, blank, blankPoints, short, shortPoints } = config.value
  return choice * choicePoints + blank * blankPoints + short * shortPoints
})

const renderedContent = computed(() => {
  if (!paperContent.value) return ''
  return renderMarkdown(paperContent.value)
})

// 添加预览对话框控制变量
const showPreview = ref(false)

// 获取教师的课程列表
const loadCourses = async () => {
  try {
    const response = await request.get('/course/my')
    if (response?.data?.code === 0 && response?.data?.data?.courses) {
      courses.value = response.data.data.courses
      console.log('成功获取课程列表:', courses.value)
    } else {
      console.error('课程API响应格式错误:', response?.data)
      ElMessage.error('获取课程列表失败: 响应格式错误')
    }
  } catch (error) {
    console.error('获取课程列表失败:', error)
    console.error('错误详情:', {
      message: error.message,
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      config: error.config
    })
    
    if (error.response?.status === 404) {
      ElMessage.error('课程API接口不存在，请检查后端服务')
    } else if (error.response?.status === 401) {
      ElMessage.error('请先登录')
    } else if (error.response?.status === 403) {
      ElMessage.error('没有权限访问课程')
    } else {
      ElMessage.error('获取课程列表失败')
    }
  }
}

// 处理课程选择变化
const handleCourseChange = () => {
  paperContent.value = ''
  generateTime.value = ''
}

// 应用模板配置
const applyTemplate = () => {
  config.value = {
    choice: 5,
    choicePoints: 2,
    blank: 5,
    blankPoints: 2,
    short: 2,
    shortPoints: 10,
    difficulty: [30, 70],
    requirements: '请覆盖本课程主要知识点，难度适中'
  }
  ElMessage.success('已应用默认模板')
}

// 重置配置
const resetConfig = () => {
  config.value = {
    choice: 3,
    choicePoints: 2,
    blank: 4,
    blankPoints: 2,
    short: 2,
    shortPoints: 10,
    difficulty: [20, 60],
    requirements: ''
  }
}

// 生成试卷
const generatePaper = async () => {
  if (!selectedCourse.value) {
    ElMessage.warning('请先选择课程')
    return
  }

  const totalQuestions = config.value.choice + config.value.blank + config.value.short
  if (totalQuestions === 0) {
    ElMessage.warning('请至少配置一种题型的数量')
    return
  }

  generating.value = true
  const prompt = generatePrompt()

  try {
    const response = await request.post(
      `/chat/simple?question=${encodeURIComponent(prompt)}&chat_name=${encodeURIComponent('考题模拟助手')}`,
      null,
      {
        timeout: 120000
      }
    )

    if (response?.data?.code === 0 && response?.data?.data?.answer) {
      paperContent.value = response.data.data.answer
      generateTime.value = new Date().toLocaleString()
      showPreview.value = true // 生成成功后直接显示预览
      ElMessage.success('试卷生成成功')
    } else {
      let errorMsg = '生成试卷失败'
      if (response?.data?.message) {
        errorMsg += `: ${response.data.message}`
      }
      ElMessage.error(errorMsg)
    }
  } catch (error) {
    console.error('生成试卷失败:', error)
    if (error.code === 'ECONNABORTED') {
      ElMessage.error('响应时间过长，请稍后重试')
    } else {
      ElMessage.error(error.response?.data?.message || '生成试卷失败')
    }
  } finally {
    generating.value = false
  }
}

// 生成提示语
const generatePrompt = () => {
  const { choice, choicePoints, blank, blankPoints, short, shortPoints, difficulty, requirements } = config.value
  
  let prompt = `请帮我生成一份${selectedCourseTitle.value}的试卷，要求如下：\n\n`
  prompt += `1. 题型和分值：\n`
  if (choice > 0) prompt += `- ${choice}道选择题，每题${choicePoints}分\n`
  if (blank > 0) prompt += `- ${blank}道填空题，每题${blankPoints}分\n`
  if (short > 0) prompt += `- ${short}道简答题，每题${shortPoints}分\n`
  
  prompt += `\n2. 难度要求：\n`
  prompt += `- 简单题占比：${difficulty[0]}%\n`
  prompt += `- 中等题占比：${difficulty[1] - difficulty[0]}%\n`
  prompt += `- 困难题占比：${100 - difficulty[1]}%\n`
  
  if (requirements) {
    prompt += `\n3. 重点考察要求：\n${requirements}\n`
  }
  
  prompt += `\n请按照以下格式生成试卷：
1. 使用Markdown格式
2. 清晰标注每道题的分值
3. 每道题的答案必须另起一行，以"【答案】"开头
4. 试卷标题格式：# 课程名称 + 试卷
5. 每种题型用二级标题标注，如：## 一、选择题`

  return prompt
}

// 渲染Markdown内容
const renderMarkdown = (content) => {
  if (!content) return ''
  
  // 配置marked选项
  marked.setOptions({
    breaks: true,
    gfm: true
  })

  let processedContent = content
  
  // 如果不显示答案，移除答案部分
  if (!showAnswers.value) {
    processedContent = content.replace(/【答案】.*?(?=\n(?:\n|$))/gs, '【答案】已隐藏')
  }

  // 转换为HTML并添加样式
  const html = marked.parse(processedContent)
  
  return html
}

// 导出试卷或答案
const exportPaper = (type) => {
  if (!paperContent.value) {
    ElMessage.warning('没有可导出的内容')
    return
  }

  const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
  const filename = `${selectedCourseTitle.value}_${type === 'paper' ? '试卷' : '答案'}_${timestamp}.md`

  let content = paperContent.value
  if (type === 'paper') {
    // 导出试卷时移除答案
    content = content.replace(/答案：.+?(?=\n\n|$)/gs, '')
  }

  const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' })
  saveAs(blob, filename)
  ElMessage.success('导出成功')
}

// 上传至题库
const handleUploadToBank = () => {
  ElMessage.info('题库上传功能开发中...')
}

// 生命周期钩子
onMounted(async () => {
  await loadCourses()
})
</script>

<style scoped>
.generator-container {
  padding: 20px;
  height: calc(100vh - 120px);
  display: flex;
  flex-direction: column;
  background-color: #f5f5f5;
  gap: 20px;
}

.header-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.header-top {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
}

.header-top h2 {
  margin: 0;
  color: #2c3e50;
  white-space: nowrap;
}

.course-select {
  width: 300px;
}

.config-section {
  border-top: 1px solid #ebeef5;
  padding-top: 20px;
}

.config-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.config-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.config-item.full-width {
  grid-column: 1 / -1;
}

.config-inputs {
  display: flex;
  align-items: center;
  gap: 8px;
}

.label {
  color: #606266;
  font-size: 14px;
}

.label-small {
  color: #909399;
  font-size: 13px;
  margin: 0 4px;
}

.number-input {
  width: 90px;
}

.config-footer {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.requirements-input {
  flex: 1;
}

.config-actions {
  display: flex;
  gap: 10px;
}

.no-course-tip {
  color: #909399;
  text-align: center;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 4px;
}

.content-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.result-section {
  flex: 1;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.paper-header {
  padding: 20px;
  border-bottom: 1px solid #ebeef5;
  background: #f8f9fa;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.paper-info h3 {
  margin: 0 0 10px 0;
  color: #2c3e50;
}

.meta-info {
  display: flex;
  gap: 20px;
  color: #606266;
  font-size: 14px;
}

.paper-actions {
  display: flex;
  gap: 10px;
}

.paper-content {
  flex: 1;
  overflow-y: auto;
  padding: 30px;
}

.rendered-content {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', sans-serif;
  line-height: 1.6;
}

.rendered-content :deep(h1) {
  text-align: center;
  margin-bottom: 30px;
  color: #2c3e50;
}

.rendered-content :deep(h2) {
  color: #2c3e50;
  border-bottom: 2px solid #3498db;
  padding-bottom: 10px;
  margin: 30px 0 20px;
}

.rendered-content :deep(p) {
  margin: 15px 0;
}

.no-content,
.no-course-selected {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.active {
  background-color: #409eff !important;
  color: white !important;
}

@media (max-width: 1200px) {
  .config-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .generator-container {
    padding: 10px;
  }
  
  .header-top {
    flex-direction: column;
    align-items: stretch;
  }
  
  .course-select {
    width: 100%;
  }
  
  .config-grid {
    grid-template-columns: 1fr;
  }
  
  .config-footer {
    flex-direction: column;
  }
  
  .config-actions {
    width: 100%;
    justify-content: center;
  }
  
  .paper-header {
    flex-direction: column;
    gap: 15px;
  }
  
  .paper-actions {
    width: 100%;
  }
  
  .paper-actions .el-button-group {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
  }
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #dcdfe6;
}

.preview-header h3 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.preview-actions {
  display: flex;
  gap: 16px;
}

.preview-content {
  height: calc(100vh - 120px);
  padding: 20px;
  overflow-y: auto;
}

.paper-info {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  color: #606266;
  font-size: 14px;
}

.paper-content {
  background: white;
  padding: 40px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.rendered-content {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', sans-serif;
  line-height: 1.8;
  font-size: 16px;
}

.rendered-content :deep(h1) {
  text-align: center;
  margin-bottom: 40px;
  color: #2c3e50;
  font-size: 24px;
}

.rendered-content :deep(h2) {
  color: #2c3e50;
  border-bottom: 2px solid #3498db;
  padding-bottom: 10px;
  margin: 30px 0 20px;
  font-size: 20px;
}

.rendered-content :deep(p) {
  margin: 15px 0;
}

/* 题目样式 */
.rendered-content :deep(ol) {
  padding-left: 20px;
}

.rendered-content :deep(li) {
  margin-bottom: 20px;
}

/* 答案样式 */
.rendered-content :deep(p:contains("【答案】")) {
  color: #67c23a;
  margin-top: 8px;
  padding-left: 20px;
  border-left: 3px solid #67c23a;
}

@media print {
  .preview-header {
    display: none;
  }

  .preview-content {
    height: auto;
    padding: 0;
  }

  .paper-content {
    box-shadow: none;
    padding: 0;
  }
}
</style>
