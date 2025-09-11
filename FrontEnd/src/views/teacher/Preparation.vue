<template>
  <div class="preparation-container">
    <!-- 顶部选择区域 -->
    <div class="header-section">
      <h2>{{ isEditMode ? '编辑教案' : '创建教案' }}</h2>
      <div class="header-actions">
        <el-select 
          v-model="selectedCourse" 
          placeholder="请选择课程"
          class="course-select"
          @change="handleCourseChange"
          :disabled="isEditMode"
        >
          <el-option
            v-for="course in courses"
            :key="course.id"
            :label="course.title"
            :value="course.id"
          />
        </el-select>
        
        <el-input
          v-model="preparationTitle"
          placeholder="请输入教案标题"
          class="title-input"
          :disabled="isEditMode"
        />
        
        <el-select 
          v-model="preparationStatus" 
          placeholder="选择状态"
          class="status-select"
        >
          <el-option label="草稿" value="draft" />
          <el-option label="已完成" value="completed" />
          <el-option label="已使用" value="used" />
        </el-select>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="content-section" v-if="selectedCourse || isEditMode">
      <!-- 输入区域 -->
      <div class="input-section">
        <el-input
          v-model="userInput"
          type="textarea"
          :rows="3"
          placeholder="请输入您的备课需求..."
          @keyup.enter.ctrl="generateContent"
        />
        <div class="button-group">
          <el-button 
            type="primary" 
            :loading="loading"
            @click="generateContent"
          >
            生成备课内容
          </el-button>
          <el-button 
            type="info" 
            @click="showEditor = true"
            :disabled="!rawContent"
            icon="Edit"
          >
            编辑内容
          </el-button>
          <el-button 
            type="success" 
            @click="savePreparation"
            :loading="saveLoading"
            :disabled="!rawContent || !preparationTitle"
            icon="Check"
          >
            {{ isEditMode ? '更新教案' : '保存教案' }}
          </el-button>
          <el-button 
            type="warning" 
            @click="exportContent"
            :disabled="!rawContent"
            icon="Download"
          >
            导出MD
          </el-button>
          <el-button 
            type="warning" 
            @click="clearContent"
            :disabled="!rawContent"
            icon="Delete"
          >
            清空内容
          </el-button>
        </div>
      </div>

      <!-- 渲染内容区域 -->
      <div class="render-section" v-if="renderedContent">
        <div class="content-header">
          <h3>{{ preparationTitle || '生成的备课内容' }}</h3>
          <div class="content-meta">
            <span>生成时间：{{ generateTime }}</span>
            <span v-if="selectedCourseTitle">课程：{{ selectedCourseTitle }}</span>
            <el-button 
              size="small" 
              type="primary" 
              @click="showEditor = true"
              icon="Edit"
            >
              编辑
            </el-button>
          </div>
        </div>
        <div class="rendered-content" v-html="renderedContent"></div>
      </div>

      <!-- 无内容时的提示 -->
      <div v-else class="no-content">
        <el-empty description="请输入备课需求并点击生成" />
      </div>
    </div>

    <!-- 未选择课程时的提示 -->
    <div v-else class="no-course-selected">
      <el-empty description="请先选择一门课程" />
    </div>

    <!-- 内容编辑抽屉 -->
    <el-drawer
      v-model="showEditor"
      title="编辑备课内容"
      :size="'60%'"
      direction="rtl"
      :before-close="handleEditorClose"
    >
      <div class="editor-container">
        <div class="editor-toolbar">
          <el-button-group>
            <el-button 
              :type="editorMode === 'edit' ? 'primary' : ''"
              @click="editorMode = 'edit'"
              icon="Edit"
            >
              编辑模式
            </el-button>
            <el-button 
              :type="editorMode === 'preview' ? 'primary' : ''"
              @click="editorMode = 'preview'"
              icon="View"
            >
              预览模式
            </el-button>
            <el-button 
              :type="editorMode === 'split' ? 'primary' : ''"
              @click="editorMode = 'split'"
              icon="Grid"
            >
              分屏模式
            </el-button>
          </el-button-group>
          
          <div class="editor-actions">
            <el-button 
              type="success" 
              @click="saveAndApplyChanges"
              icon="Check"
            >
              应用更改
            </el-button>
            <el-button 
              type="info" 
              @click="resetContent"
              icon="RefreshLeft"
            >
              重置内容
            </el-button>
          </div>
        </div>

        <!-- 编辑器内容区域 -->
        <div class="editor-content" :class="`mode-${editorMode}`">
          <!-- 编辑区域 -->
          <div class="edit-pane" v-show="editorMode === 'edit' || editorMode === 'split'">
            <div class="pane-header">
              <h4>Markdown 源码</h4>
              <span class="word-count">{{ editableContent.length }} 字符</span>
            </div>
            <el-input
              v-model="editableContent"
              type="textarea"
              :rows="25"
              placeholder="在此编辑 Markdown 内容..."
              class="markdown-editor"
              @input="onContentChange"
            />
          </div>

          <!-- 预览区域 -->
          <div class="preview-pane" v-show="editorMode === 'preview' || editorMode === 'split'">
            <div class="pane-header">
              <h4>实时预览</h4>
            </div>
            <div class="preview-content" v-html="previewContent"></div>
          </div>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import request from '@/utils/request'
import { saveAs } from 'file-saver'
import { marked } from 'marked'
import mermaid from 'mermaid' // 添加 mermaid 导入

const route = useRoute()
const router = useRouter()

// 数据定义
const courses = ref([])
const selectedCourse = ref(null)
const preparationTitle = ref('')
const preparationStatus = ref('draft')
const userInput = ref('')
const loading = ref(false)
const saveLoading = ref(false)
const rawContent = ref('')
const renderedContent = ref('')
const generateTime = ref('')

// 编辑器相关状态
const showEditor = ref(false)
const editorMode = ref('split') // 'edit', 'preview', 'split'
const editableContent = ref('')
const previewContent = ref('')
const hasUnsavedChanges = ref(false)

// 编辑模式相关
const isEditMode = ref(false)
const currentPreparationId = ref(null)

// 计算属性
const selectedCourseTitle = computed(() => {
  return courses.value.find(c => c.id === selectedCourse.value)?.title || '未知课程'
})

// 初始化
onMounted(async () => {
  initMermaid()
  await loadCourses()
  
  // 检查是否是编辑模式
  const preparationId = route.query.id
  if (preparationId) {
    isEditMode.value = true
    currentPreparationId.value = preparationId
    await loadPreparation(preparationId)
  }
})

// 获取教师的课程列表
const loadCourses = async () => {
  try {
    console.log('开始获取课程列表...')
    const response = await request.get('/course/my')
    console.log('课程API响应:', response)
    
    if (response?.data?.code === 0) {
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

// 加载教案详情
const loadPreparation = async (preparationId) => {
  try {
    const response = await request.get(`/preparation/${preparationId}`)
    if (response?.data?.code === 0) {
      const preparation = response.data.data
      preparationTitle.value = preparation.title
      preparationStatus.value = preparation.status
      selectedCourse.value = preparation.course_id
      rawContent.value = preparation.content
      renderedContent.value = renderMarkdown(preparation.content)
      generateTime.value = new Date().toLocaleString()
    }
  } catch (error) {
    console.error('获取教案详情失败:', error)
    ElMessage.error('获取教案详情失败')
  }
}

// 处理课程选择变化
const handleCourseChange = () => {
  if (!isEditMode.value) {
    clearContent()
  }
}

// 预处理Markdown内容
const preprocessMarkdown = (markdown) => {
  // 处理特殊信息框标记
  markdown = markdown.replace(/^!!! info/gm, ':::info')
  markdown = markdown.replace(/^!!! warning/gm, ':::warning')
  markdown = markdown.replace(/^!!! task/gm, ':::task')
  
  return markdown
}

// 后处理HTML
const postprocessHTML = (html) => {
  // 为不同级别的标题添加CSS类
  html = html.replace(/<h1([^>]*)>/g, '<h1$1 class="main-title">')
  html = html.replace(/<h2([^>]*)>/g, '<h2$1 class="section-header-h2">')
  html = html.replace(/<h3([^>]*)>/g, '<h3$1 class="section-header">')
  html = html.replace(/<h4([^>]*)>/g, '<h4$1 class="subsection-header">')
  html = html.replace(/<h5([^>]*)>/g, '<h5$1 class="subsection-header">')
  
  // 包装表格
  html = html.replace(/<table>/g, '<div class="table-container"><table>')
  html = html.replace(/<\/table>/g, '</table></div>')
  
  // 处理特殊标记的信息框
  html = html.replace(/<p>:::info\s*(.*?)<\/p>/g, '<div class="info-box"><strong>ℹ️ 信息</strong><br>$1</div>')
  html = html.replace(/<p>:::warning\s*(.*?)<\/p>/g, '<div class="warning-box"><strong>⚠️ 注意</strong><br>$1</div>')
  html = html.replace(/<p>:::task\s*(.*?)<\/p>/g, '<div class="task-item"><strong>📝 任务</strong><br>$1</div>')
  
  // 处理重要概念的引用块
  html = html.replace(/<blockquote><p><strong>(重要概念|注意|提示|案例)<\/strong>/g, 
    '<div class="highlight-box"><strong>💡 $1</strong>')
  html = html.replace(/<\/p><\/blockquote>/g, '</div>')
  
  // 处理Mermaid图表
  html = html.replace(/<pre><code class="language-mermaid">([\s\S]*?)<\/code><\/pre>/g, 
    '<div class="mermaid-container"><div class="mermaid">$1</div></div>')
  
  return html
}

// 初始化 Mermaid
const initMermaid = () => {
  mermaid.initialize({
    startOnLoad: false,
    theme: 'default',
    securityLevel: 'loose',
    themeVariables: {
      primaryColor: '#ff0000'
    }
  })
}

// 渲染 Mermaid 图表
const renderMermaidCharts = async () => {
  await nextTick()
  
  // 渲染主内容区域的 mermaid 图表
  const mainMermaidElements = document.querySelectorAll('.rendered-content .mermaid')
  for (let i = 0; i < mainMermaidElements.length; i++) {
    const element = mainMermaidElements[i]
    if (element.getAttribute('data-processed') !== 'true') {
      try {
        const graphDefinition = element.textContent
        const { svg } = await mermaid.render(`mermaid-main-${i}`, graphDefinition)
        element.innerHTML = svg
        element.setAttribute('data-processed', 'true')
      } catch (error) {
        console.error('Mermaid rendering error:', error)
        element.innerHTML = '<p style="color: red;">图表渲染失败</p>'
      }
    }
  }
  
  // 渲染预览区域的 mermaid 图表
  const previewMermaidElements = document.querySelectorAll('.preview-content .mermaid')
  for (let i = 0; i < previewMermaidElements.length; i++) {
    const element = previewMermaidElements[i]
    if (element.getAttribute('data-processed') !== 'true') {
      try {
        const graphDefinition = element.textContent
        const { svg } = await mermaid.render(`mermaid-preview-${i}`, graphDefinition)
        element.innerHTML = svg
        element.setAttribute('data-processed', 'true')
      } catch (error) {
        console.error('Mermaid rendering error:', error)
        element.innerHTML = '<p style="color: red;">图表渲染失败</p>'
      }
    }
  }
}

// 渲染Markdown内容
const renderMarkdown = (content) => {
  if (!content.trim()) {
    return ''
  }
  
  // 配置marked选项
  marked.setOptions({
    breaks: true,
    gfm: true,
    highlight: function(code, lang) {
      return code
    }
  })
  
  // 预处理
  const processedMarkdown = preprocessMarkdown(content)
  
  // 转换为HTML
  const html = marked.parse(processedMarkdown)
  
  // 后处理
  const processedHTML = postprocessHTML(html)
  
  // 延迟渲染 Mermaid 图表
  setTimeout(() => {
    renderMermaidCharts()
  }, 100)
  
  return processedHTML
}

// 防抖的内容更新函数
let debounceTimer = null
const debouncedUpdatePreview = () => {
  if (debounceTimer) {
    clearTimeout(debounceTimer)
  }
  debounceTimer = setTimeout(() => {
    previewContent.value = renderMarkdown(editableContent.value)
  }, 300)
}

// 内容变化处理
const onContentChange = () => {
  hasUnsavedChanges.value = editableContent.value !== rawContent.value
  debouncedUpdatePreview()
}

// 应用更改
const saveAndApplyChanges = () => {
  if (!editableContent.value.trim()) {
    ElMessage.warning('内容不能为空')
    return
  }
  
  // 更新原始内容
  rawContent.value = editableContent.value
  
  // 重新渲染
  renderedContent.value = renderMarkdown(rawContent.value)
  
  // 更新生成时间
  generateTime.value = new Date().toLocaleString()
  
  // 标记为已保存
  hasUnsavedChanges.value = false
  
  // 关闭编辑器
  showEditor.value = false
  
  ElMessage.success('内容已更新')
}

// 重置内容
const resetContent = () => {
  editableContent.value = rawContent.value
  previewContent.value = renderMarkdown(rawContent.value)
  hasUnsavedChanges.value = false
  ElMessage.info('内容已重置')
}

// 编辑器关闭前处理
const handleEditorClose = async (done) => {
  if (hasUnsavedChanges.value) {
    try {
      await ElMessageBox.confirm(
        '您有未保存的更改，确定要关闭编辑器吗？',
        '提示',
        {
          confirmButtonText: '保存并关闭',
          cancelButtonText: '不保存',
          distinguishCancelAndClose: true,
          type: 'warning',
        }
      )
      // 用户选择保存并关闭
      saveAndApplyChanges()
      done()
    } catch (action) {
      if (action === 'cancel') {
        // 用户选择不保存
        resetContent()
        done()
      }
      // action === 'close' 时不关闭抽屉
    }
  } else {
    done()
  }
}

// 监听编辑器显示状态
watch(showEditor, (newVal) => {
  if (newVal && rawContent.value) {
    editableContent.value = rawContent.value
    previewContent.value = renderMarkdown(rawContent.value)
    hasUnsavedChanges.value = false
  }
})

// 生成备课内容
const generateContent = async () => {
  if (!userInput.value.trim()) {
    ElMessage.warning('请输入备课需求')
    return
  }

  if (!selectedCourse.value && !isEditMode.value) {
    ElMessage.warning('请先选择课程')
    return
  }

  const userMessage = userInput.value.trim()
  loading.value = true

  try {
    const response = await request.post(
      `/chat/simple?question=${encodeURIComponent(userMessage)}&chat_name=${encodeURIComponent('教师备课与设计')}`,
      null,
      {
        timeout: 120000
      }
    )

    if (response?.data?.code === 0 && response?.data?.data?.answer) {
      // 保存原始内容
      rawContent.value = response.data.data.answer
      
      // 渲染Markdown内容
      renderedContent.value = renderMarkdown(rawContent.value)
      
      // 记录生成时间
      generateTime.value = new Date().toLocaleString()
      
      // 清空输入框
      userInput.value = ''
      
      ElMessage.success('备课内容生成成功')
    } else {
      console.error('API响应错误:', response.data)
      let errorMsg = '生成备课内容失败'
      if (response?.data?.message) {
        errorMsg += `: ${response.data.message}`
      }
      if (response?.data?.code === 100) {
        errorMsg = '服务器正忙，请稍后再试'
      }
      ElMessage.error(errorMsg)
    }
  } catch (error) {
    console.error('生成备课内容失败:', error)
    if (error.code === 'ECONNABORTED') {
      ElMessage.error('响应时间过长，请稍后重试')
    } else {
      ElMessage.error(error.response?.data?.message || '生成备课内容失败')
    }
  } finally {
    loading.value = false
  }
}

// 导出备课内容
const exportContent = () => {
  if (!rawContent.value) {
    ElMessage.warning('没有可导出的内容')
    return
  }

  const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
  const filename = `教案_${preparationTitle.value || selectedCourseTitle.value}_${timestamp}.md`

  let content = `# ${preparationTitle.value || selectedCourseTitle.value} - 教案\n\n`
  content += `## 基本信息\n\n`
  content += `- **课程**: ${selectedCourseTitle.value}\n`
  content += `- **状态**: ${getStatusText(preparationStatus.value)}\n`
  content += `- **创建时间**: ${generateTime.value}\n`
  content += `- **更新时间**: ${new Date().toLocaleString()}\n\n`
  content += `---\n\n`
  content += `## 教案内容\n\n`
  content += rawContent.value

  const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' })
  saveAs(blob, filename)
  ElMessage.success('教案导出成功')
}

// 获取状态文本
const getStatusText = (status) => {
  const statusMap = {
    draft: '草稿',
    completed: '已完成',
    used: '已使用'
  }
  return statusMap[status] || '未知'
}

// 清空内容
const clearContent = () => {
  userInput.value = ''
  rawContent.value = ''
  renderedContent.value = ''
  generateTime.value = ''
  editableContent.value = ''
  previewContent.value = ''
  hasUnsavedChanges.value = false
  
  if (!isEditMode.value) {
    preparationTitle.value = ''
    preparationStatus.value = 'draft'
  }
}

// 保存教案
const savePreparation = async () => {
  if (!preparationTitle.value.trim()) {
    ElMessage.warning('请输入教案标题')
    return
  }
  
  if (!rawContent.value.trim()) {
    ElMessage.warning('请先生成或编辑教案内容')
    return
  }
  
  if (!selectedCourse.value && !isEditMode.value) {
    ElMessage.warning('请选择课程')
    return
  }
  
  saveLoading.value = true
  try {
    if (isEditMode.value) {
      // 更新教案
      const response = await request.put(`/preparation/${currentPreparationId.value}`, {
        title: preparationTitle.value,
        content: rawContent.value,
        status: preparationStatus.value
      })
      
      if (response?.data?.code === 0) {
        ElMessage.success('教案更新成功')
        router.push('/dashboard/preparation-manage')
      }
    } else {
      // 创建教案
      const response = await request.post('/preparation/create', {
        title: preparationTitle.value,
        content: rawContent.value,
        course_id: selectedCourse.value,
        status: preparationStatus.value
      })
      
      if (response?.data?.code === 0) {
        ElMessage.success('教案创建成功')
        router.push('/dashboard/preparation-manage')
      }
    }
  } catch (error) {
    console.error('保存教案失败:', error)
    ElMessage.error('保存教案失败')
  } finally {
    saveLoading.value = false
  }
}
</script>

<style scoped>
.preparation-container {
  padding: 20px;
  height: calc(100vh - 120px);
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.header-section {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 20px;
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.header-section h2 {
  margin: 0;
  color: #2c3e50;
  font-size: 24px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

.course-select {
  width: 300px;
}

.title-input {
  width: 250px;
}

.status-select {
  width: 150px;
}

.content-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.input-section {
  background: white;
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.button-group {
  margin-top: 15px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.button-group .el-button {
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.button-group .el-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.render-section {
  flex: 1;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.content-header {
  padding: 20px;
  border-bottom: 1px solid #ebeef5;
  background: #fafafa;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.content-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 18px;
  font-weight: 600;
}

.content-meta {
  display: flex;
  align-items: center;
  gap: 20px;
  font-size: 14px;
  color: #666;
}

.rendered-content {
  flex: 1;
  padding: 30px;
  overflow-y: auto;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', sans-serif;
  line-height: 1.6;
}

.no-content,
.no-course-selected {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

/* 从smart-markdown-renderer.html复制的样式 */
.rendered-content :deep(.main-title) {
  text-align: center;
  color: #2c3e50;
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
  padding: 20px;
  border-radius: 10px;
  margin-bottom: 30px;
  font-size: 2.2em;
  box-shadow: 0 4px 15px rgba(79, 172, 254, 0.3);
}

.rendered-content :deep(.section-header-h2) {
  background: linear-gradient(135deg, #c9d9eb 0%, #f8fafa 100%);
  color: #2c3e50;
  padding: 15px 20px;
  border-radius: 8px;
  margin: 25px 0 15px 0;
  position: relative;
  box-shadow: 0 3px 10px rgba(79, 172, 254, 0.3);
  border-left: 5px solid #0066cc;
}

.rendered-content :deep(.section-header-h2::before) {
  content: '📚';
  position: absolute;
  left: -15px;
  top: 50%;
  transform: translateY(-50%);
  background: white;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.rendered-content :deep(.section-header) {
  background: linear-gradient(135deg, #ffeaa7 0%, #f7d3ca 100%);
  color: #2c3e50;
  padding: 12px 18px;
  border-radius: 6px;
  margin: 20px 0 12px 0;
  position: relative;
  border-left: 4px solid #e17055;
  box-shadow: 0 2px 6px rgba(250, 177, 160, 0.3);
}

.rendered-content :deep(.section-header::before) {
  content: '📝';
  margin-right: 8px;
}

.rendered-content :deep(.subsection-header) {
  color: #2c3e50;
  background: #f8f9fa;
  padding: 8px 12px;
  margin: 12px 0 8px 0;
  border-radius: 3px;
  border-left: 3px solid #3498db;
  font-weight: 500;
}

.rendered-content :deep(.table-container) {
  overflow-x: auto;
  margin: 15px 0;
}

.rendered-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 15px 0;
  background: white;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.rendered-content :deep(th),
.rendered-content :deep(td) {
  border: 1px solid #ddd;
  padding: 12px;
  text-align: left;
}

.rendered-content :deep(th) {
  background: linear-gradient(135deg, #b7bedb 0%);
  color: rgb(0, 0, 0);
  font-weight: bold;
}

.rendered-content :deep(tr:nth-child(even)) {
  background-color: #f8f9fa;
}

.rendered-content :deep(tr:hover) {
  background-color: #e3f2fd;
}

.rendered-content :deep(.info-box) {
  background: #e3f2fd;
  border-left: 4px solid #2196f3;
  padding: 15px;
  margin: 15px 0;
  border-radius: 0 5px 5px 0;
}

.rendered-content :deep(.warning-box) {
  background: #fff3e0;
  border-left: 4px solid #ff9800;
  padding: 15px;
  margin: 15px 0;
  border-radius: 0 5px 5px 0;
}

.rendered-content :deep(.task-item) {
  background: #e8f5e8;
  border-left: 4px solid #27ae60;
  padding: 15px;
  margin: 10px 0;
  border-radius: 0 5px 5px 0;
}

.rendered-content :deep(.highlight-box) {
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 5px;
  padding: 15px;
  margin: 15px 0;
}

.rendered-content :deep(pre) {
  background: #f4f4f4;
  padding: 15px;
  border-radius: 5px;
  overflow-x: auto;
  border-left: 4px solid #3498db;
}

.rendered-content :deep(code) {
  background: #f4f4f4;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Consolas', 'Monaco', monospace;
  color: #e74c3c;
}

.rendered-content :deep(ul),
.rendered-content :deep(ol) {
  padding-left: 25px;
}

.rendered-content :deep(li) {
  margin: 8px 0;
}

.rendered-content :deep(hr) {
  border: none;
  height: 2px;
  background: linear-gradient(90deg, transparent, #3498db, transparent);
  margin: 30px 0;
}

.rendered-content :deep(.mermaid-container) {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 5px;
  padding: 20px;
  margin: 15px 0;
  text-align: center;
}

.rendered-content :deep(blockquote) {
  border-left: 4px solid #f39c12;
  background: #fef9e7;
  padding: 15px;
  margin: 15px 0;
  font-style: italic;
}

.editor-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.editor-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 0;
  border-bottom: 1px solid #ebeef5;
  margin-bottom: 20px;
}

.editor-actions {
  display: flex;
  gap: 10px;
}

.editor-content {
  flex: 1;
  display: flex;
  gap: 20px;
  height: calc(100% - 80px);
}

.edit-pane,
.preview-pane {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fafafa;
  border-radius: 8px;
  overflow: hidden;
}

.pane-header {
  padding: 12px 15px;
  background: #f0f0f0;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pane-header h4 {
  margin: 0;
  color: #2c3e50;
  font-size: 14px;
  font-weight: 600;
}

.word-count {
  font-size: 12px;
  color: #909399;
}

.markdown-editor {
  flex: 1;
  border: none;
  background: white;
}

.preview-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background: white;
  line-height: 1.6;
}

.mode-edit .preview-pane,
.mode-preview .edit-pane {
  display: none;
}

.mode-split .edit-pane,
.mode-split .preview-pane {
  flex: 1;
}

@media (max-width: 768px) {
  .preparation-container {
    padding: 10px;
  }
  
  .header-section {
    flex-direction: column;
    align-items: stretch;
    gap: 15px;
  }
  
  .header-actions {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }

  .course-select,
  .title-input,
  .status-select {
    width: 100%;
  }
  
  .rendered-content {
    padding: 15px;
  }
  
  .button-group {
    flex-direction: column;
  }
}
</style>
