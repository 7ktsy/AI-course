<template>
  <div class="preparation-manage">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>教案管理</h1>
      <p>管理您的教案，支持AI优化和分享功能</p>
    </div>
    
    <!-- 顶部操作栏 -->
    <div class="operation-bar">
      <el-button type="primary" @click="$router.push('/dashboard/preparation')">
        <i class="bi bi-plus-lg"></i>
        新建教案
      </el-button>
      <el-button @click="handleBatchExport" type="success">
        <i class="bi bi-download"></i>
        批量导出
      </el-button>
      <el-tag type="info">共 {{ totalPreparations }} 份教案</el-tag>
    </div>

    <!-- 筛选区域 -->
    <el-card shadow="never" class="filter-card">
      <el-form :model="filterForm" inline>
        <el-form-item label="来源">
          <el-select v-model="filterForm.source" placeholder="全部来源" clearable>
            <el-option label="我创建的" value="own" />
            <el-option label="分享给我的" value="shared" />
            <el-option label="全部" value="all" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="课程">
          <el-select v-model="filterForm.courseId" placeholder="全部课程" clearable>
            <el-option 
              v-for="course in courseList" 
              :key="course.id"
              :label="course.title" 
              :value="course.id" 
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部状态" clearable>
            <el-option label="草稿" value="draft" />
            <el-option label="已完成" value="completed" />
            <el-option label="已使用" value="used" />
          </el-select>
        </el-form-item>

        <el-form-item label="关键词">
          <el-input
            v-model="filterForm.keyword"
            placeholder="搜索教案标题或内容..."
            style="width: 200px"
            clearable
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleFilter">筛选</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 教案列表 -->
    <el-card shadow="never" class="content-card">
      <el-table
        :data="preparationList"
        v-loading="loading"
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        
        <el-table-column prop="title" label="教案标题" min-width="200">
          <template #default="scope">
            <div class="title-cell">
              <span>{{ scope.row.title }}</span>
              <div class="title-tags">
                <el-tag v-if="scope.row.is_owner" size="small" type="success">我的</el-tag>
                <el-tag v-if="scope.row.is_shared" size="small" type="warning">分享</el-tag>
                <el-tag v-if="scope.row.is_public" size="small" type="info">公开</el-tag>
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="course_name" label="课程" width="150" />
        
        <el-table-column prop="teacher_name" label="创建者" width="120" />
        
        <el-table-column label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusColor(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="updated_at" label="更新时间" width="180" />
        
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="viewPreparation(scope.row)">
              查看
            </el-button>
            <el-button 
              v-if="scope.row.can_edit" 
              size="small" 
              type="primary"
              @click="editPreparation(scope.row)"
            >
              编辑
            </el-button>
            <el-button 
              size="small" 
              type="success"
              @click="showAIOptimization(scope.row)"
            >
              AI优化
            </el-button>
            <el-dropdown @command="(command) => handleMoreAction(command, scope.row)">
              <el-button size="small">
                更多<i class="el-icon--right el-icon-arrow-down"></i>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="share">分享教案</el-dropdown-item>
                  <el-dropdown-item command="duplicate">复制教案</el-dropdown-item>
                  <el-dropdown-item command="export">导出</el-dropdown-item>
                  <el-dropdown-item 
                    v-if="scope.row.is_owner" 
                    command="delete" 
                    divided
                  >
                    删除教案
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50]"
          :total="totalPreparations"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 教案详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="教案详情" width="80%" destroy-on-close>
      <div v-if="currentPreparation" class="preparation-detail">
        <div class="detail-header">
          <h3>{{ currentPreparation.title }}</h3>
          <div class="detail-meta">
            <el-tag>{{ currentPreparation.course_name }}</el-tag>
            <el-tag type="info">{{ currentPreparation.teacher_name }}</el-tag>
            <el-tag :type="getStatusColor(currentPreparation.status)">
              {{ getStatusText(currentPreparation.status) }}
            </el-tag>
            <el-tag v-if="currentPreparation.is_public" type="success">公开</el-tag>
          </div>
        </div>
        
        <div class="detail-content" v-html="renderedContent"></div>
      </div>
    </el-dialog>

    <!-- AI优化对话框 -->
    <el-dialog v-model="showAIDialog" title="AI优化建议" width="70%" destroy-on-close>
      <div v-if="currentPreparation" class="ai-optimization">
        <div class="optimization-header">
          <h4>{{ currentPreparation.title }}</h4>
          <el-select v-model="optimizationType" placeholder="选择优化类型">
            <el-option label="语法优化" value="grammar" />
            <el-option label="结构优化" value="structure" />
            <el-option label="内容优化" value="content" />
            <el-option label="教学法优化" value="pedagogy" />
          </el-select>
        </div>
        
        <div class="optimization-content">
          <el-input
            v-model="customPrompt"
            type="textarea"
            :rows="3"
            placeholder="自定义优化提示词（可选）..."
          />
          
          <div class="optimization-actions">
            <el-button 
              type="primary" 
              :loading="aiLoading"
              @click="getAISuggestions"
            >
              获取AI建议
            </el-button>
          </div>
          
          <div v-if="aiSuggestions" class="ai-suggestions">
            <h5>AI优化建议：</h5>
            <div class="suggestion-content" v-html="renderMarkdown(aiSuggestions.ai_response)"></div>
            
            <div class="suggestion-actions">
              <el-button 
                type="success" 
                @click="applyAISuggestions"
                :loading="applyLoading"
              >
                应用AI建议
              </el-button>
              <el-button @click="aiSuggestions = null">
                关闭
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- 分享教案对话框 -->
    <el-dialog v-model="showShareDialog" title="分享教案" width="50%" destroy-on-close>
      <div v-if="currentPreparation" class="share-preparation">
        <el-form :model="shareForm" label-width="80px">
          <el-form-item label="教案标题">
            <span>{{ currentPreparation.title }}</span>
          </el-form-item>
          
          <el-form-item label="分享给">
            <el-select
              v-model="shareForm.to_teacher_ids"
              multiple
              filterable
              placeholder="选择要分享的教师"
              style="width: 100%"
            >
              <el-option
                v-for="teacher in teacherList"
                :key="teacher.id"
                :label="teacher.username"
                :value="teacher.id"
              />
            </el-select>
          </el-form-item>
          
          <el-form-item label="留言">
            <el-input
              v-model="shareForm.message"
              type="textarea"
              :rows="3"
              placeholder="分享留言（可选）..."
            />
          </el-form-item>
        </el-form>
        
        <div class="share-actions">
          <el-button type="primary" @click="sharePreparation" :loading="shareLoading">
            确认分享
          </el-button>
          <el-button @click="showShareDialog = false">
            取消
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'
import { marked } from 'marked'

const router = useRouter()
const loading = ref(false)
const showDetailDialog = ref(false)
const showAIDialog = ref(false)
const showShareDialog = ref(false)
const currentPreparation = ref(null)
const aiSuggestions = ref(null)
const aiLoading = ref(false)
const applyLoading = ref(false)
const shareLoading = ref(false)

const currentPage = ref(1)
const pageSize = ref(20)
const totalPreparations = ref(0)
const preparationList = ref([])
const courseList = ref([])
const teacherList = ref([])

// 筛选表单
const filterForm = reactive({
  source: 'all',
  courseId: '',
  status: '',
  keyword: ''
})

// AI优化相关
const optimizationType = ref('content')
const customPrompt = ref('')

// 分享表单
const shareForm = reactive({
  to_teacher_ids: [],
  message: ''
})

// 计算属性
const renderedContent = computed(() => {
  if (!currentPreparation.value?.content) return ''
  return marked.parse(currentPreparation.value.content)
})

// 初始化
onMounted(() => {
  fetchPreparations()
  fetchCourses()
  fetchTeachers()
})

// 获取教案列表
const fetchPreparations = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      source: filterForm.source,
      ...(filterForm.courseId && { course_id: filterForm.courseId }),
      ...(filterForm.status && { status: filterForm.status }),
      ...(filterForm.keyword && { keyword: filterForm.keyword })
    }
    
    console.log('请求参数:', params)
    console.log('请求URL:', '/preparation/my')
    console.log('请求头:', { Authorization: `Bearer ${localStorage.getItem('token')}` })
    
    const response = await request.get('/preparation/my', { params })
    console.log('API响应:', response)
    
    if (response?.data?.code === 0) {
      preparationList.value = response.data.data.preparations
      totalPreparations.value = response.data.data.total
      console.log('教案列表:', preparationList.value)
      console.log('总数:', totalPreparations.value)
    } else {
      console.error('API响应错误:', response?.data)
      ElMessage.error(response?.data?.message || '获取教案列表失败')
    }
  } catch (error) {
    console.error('获取教案列表失败:', error)
    console.error('错误详情:', {
      message: error.message,
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      config: error.config
    })
    
    if (error.response?.status === 404) {
      ElMessage.error('教案API接口不存在，请检查后端服务')
    } else if (error.response?.status === 401) {
      ElMessage.error('请先登录')
    } else if (error.response?.status === 403) {
      ElMessage.error('没有权限访问教案')
    } else {
      ElMessage.error('获取教案列表失败')
    }
  } finally {
    loading.value = false
  }
}

// 获取课程列表
const fetchCourses = async () => {
  try {
    const response = await request.get('/course/my')
    if (response?.data?.code === 0) {
      courseList.value = response.data.data.courses
    }
  } catch (error) {
    console.error('获取课程列表失败:', error)
  }
}

// 获取教师列表
const fetchTeachers = async () => {
  try {
    const response = await request.get('/user/teachers')
    if (response?.data?.code === 0) {
      teacherList.value = response.data.data.teachers
    }
  } catch (error) {
    console.error('获取教师列表失败:', error)
  }
}

// 辅助函数
const getStatusColor = (status) => {
  const colors = {
    draft: 'info',
    completed: 'success',
    used: 'warning'
  }
  return colors[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    draft: '草稿',
    completed: '已完成',
    used: '已使用'
  }
  return texts[status] || '未知'
}

// 事件处理
const handleFilter = () => {
  currentPage.value = 1
  fetchPreparations()
}

const resetFilter = () => {
  Object.keys(filterForm).forEach(key => {
    filterForm[key] = key === 'source' ? 'all' : ''
  })
  handleFilter()
}

const handleSizeChange = (size) => {
  pageSize.value = size
  fetchPreparations()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  fetchPreparations()
}

// 查看教案详情
const viewPreparation = async (preparation) => {
  try {
    const response = await request.get(`/preparation/${preparation.id}`)
    if (response?.data?.code === 0) {
      currentPreparation.value = response.data.data
      showDetailDialog.value = true
    }
  } catch (error) {
    console.error('获取教案详情失败:', error)
    ElMessage.error('获取教案详情失败')
  }
}

// 编辑教案
const editPreparation = (preparation) => {
  router.push(`/dashboard/preparation?id=${preparation.id}`)
}

// 显示AI优化对话框
const showAIOptimization = async (preparation) => {
  try {
    const response = await request.get(`/preparation/${preparation.id}`)
    if (response?.data?.code === 0) {
      currentPreparation.value = response.data.data
      showAIDialog.value = true
      aiSuggestions.value = null
      optimizationType.value = 'content'
      customPrompt.value = ''
    }
  } catch (error) {
    console.error('获取教案详情失败:', error)
    ElMessage.error('获取教案详情失败')
  }
}

// 获取AI建议
const getAISuggestions = async () => {
  if (!currentPreparation.value) return
  
  aiLoading.value = true
  try {
    const data = {
      optimization_type: optimizationType.value,
      ...(customPrompt.value && { custom_prompt: customPrompt.value })
    }
    
    const response = await request.post(
      `/preparation/${currentPreparation.value.id}/ai-optimize`,
      data
    )
    
    if (response?.data?.code === 0) {
      aiSuggestions.value = response.data.data.suggestions
      ElMessage.success('AI建议生成成功')
    }
  } catch (error) {
    console.error('获取AI建议失败:', error)
    ElMessage.error('获取AI建议失败')
  } finally {
    aiLoading.value = false
  }
}

// 应用AI建议
const applyAISuggestions = async () => {
  if (!aiSuggestions.value) return
  
  applyLoading.value = true
  try {
    // 后端接口期望的是 optimized_content 参数
    const response = await request.post(
      `/preparation/${currentPreparation.value.id}/apply-ai-suggestions`,
      { optimized_content: aiSuggestions.value.optimized_content || '' }
    )
    
    if (response?.data?.code === 0) {
      ElMessage.success('AI建议应用成功')
      showAIDialog.value = false
      fetchPreparations() // 刷新列表
    }
  } catch (error) {
    console.error('应用AI建议失败:', error)
    ElMessage.error('应用AI建议失败')
  } finally {
    applyLoading.value = false
  }
}

// 分享教案
const sharePreparation = async () => {
  if (!shareForm.to_teacher_ids.length) {
    ElMessage.warning('请选择要分享的教师')
    return
  }
  
  shareLoading.value = true
  try {
    const response = await request.post(
      `/preparation/${currentPreparation.value.id}/share`,
      shareForm
    )
    
    if (response?.data?.code === 0) {
      ElMessage.success(response.data.data.msg)
      showShareDialog.value = false
      // 重置表单
      shareForm.to_teacher_ids = []
      shareForm.message = ''
    }
  } catch (error) {
    console.error('分享教案失败:', error)
    ElMessage.error('分享教案失败')
  } finally {
    shareLoading.value = false
  }
}

// 更多操作
const handleMoreAction = async (command, preparation) => {
  switch (command) {
    case 'share':
      currentPreparation.value = preparation
      showShareDialog.value = true
      shareForm.to_teacher_ids = []
      shareForm.message = ''
      break
      
    case 'duplicate':
      try {
        const response = await request.post(`/preparation/${preparation.id}/duplicate`)
        if (response?.data?.code === 0) {
          ElMessage.success('教案复制成功')
          fetchPreparations()
        }
      } catch (error) {
        console.error('复制教案失败:', error)
        ElMessage.error('复制教案失败')
      }
      break
      
    case 'export':
      // 导出功能
      try {
        const response = await request.get(`/preparation/${preparation.id}`)
        if (response?.data?.code === 0) {
          const prepData = response.data.data
          const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
          const filename = `教案_${prepData.title}_${timestamp}.md`
          
          let content = `# ${prepData.title} - 教案\n\n`
          content += `## 基本信息\n\n`
          content += `- **课程**: ${prepData.course_name}\n`
          content += `- **创建者**: ${prepData.teacher_name}\n`
          content += `- **状态**: ${getStatusText(prepData.status)}\n`
          content += `- **创建时间**: ${prepData.created_at}\n`
          content += `- **更新时间**: ${prepData.updated_at}\n`
          if (prepData.is_public) {
            content += `- **公开状态**: 公开\n`
          }
          content += `\n---\n\n`
          content += `## 教案内容\n\n`
          content += prepData.content
          
          const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' })
          const url = URL.createObjectURL(blob)
          const link = document.createElement('a')
          link.href = url
          link.download = filename
          document.body.appendChild(link)
          link.click()
          document.body.removeChild(link)
          URL.revokeObjectURL(url)
          
          ElMessage.success('教案导出成功')
        }
      } catch (error) {
        console.error('导出教案失败:', error)
        ElMessage.error('导出教案失败')
      }
      break
      
    case 'delete':
      try {
        await ElMessageBox.confirm('确定要删除这份教案吗？', '警告', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        const response = await request.delete(`/preparation/${preparation.id}`)
        if (response?.data?.code === 0) {
          ElMessage.success('教案删除成功')
          fetchPreparations()
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('删除教案失败:', error)
          ElMessage.error('删除教案失败')
        }
      }
      break
  }
}

const handleBatchExport = async () => {
  // 获取当前筛选条件下的所有教案
  try {
    ElMessage.info('正在准备批量导出...')
    
    // 获取所有教案（不分页）
    const response = await request.get('/preparation/my', { 
      params: {
        page: 1,
        page_size: 1000, // 获取大量数据
        source: filterForm.source,
        ...(filterForm.courseId && { course_id: filterForm.courseId }),
        ...(filterForm.status && { status: filterForm.status }),
        ...(filterForm.keyword && { keyword: filterForm.keyword })
      }
    })
    
    if (response?.data?.code === 0) {
      const preparations = response.data.data.preparations
      
      if (preparations.length === 0) {
        ElMessage.warning('没有可导出的教案')
        return
      }
      
      // 创建ZIP文件
      const JSZip = await import('jszip')
      const zip = new JSZip.default()
      
      // 为每个教案创建文件
      for (const prep of preparations) {
        let content = `# ${prep.title} - 教案\n\n`
        content += `## 基本信息\n\n`
        content += `- **课程**: ${prep.course_name}\n`
        content += `- **创建者**: ${prep.teacher_name}\n`
        content += `- **状态**: ${getStatusText(prep.status)}\n`
        content += `- **创建时间**: ${prep.created_at}\n`
        content += `- **更新时间**: ${prep.updated_at}\n`
        if (prep.is_public) {
          content += `- **公开状态**: 公开\n`
        }
        content += `\n---\n\n`
        content += `## 教案内容\n\n`
        content += prep.content || '内容为空'
        
        const filename = `${prep.title.replace(/[<>:"/\\|?*]/g, '_')}.md`
        zip.file(filename, content)
      }
      
      // 生成并下载ZIP文件
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
      const zipFilename = `教案批量导出_${timestamp}.zip`
      
      const zipBlob = await zip.generateAsync({ type: 'blob' })
      const url = URL.createObjectURL(zipBlob)
      const link = document.createElement('a')
      link.href = url
      link.download = zipFilename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
      
      ElMessage.success(`成功导出 ${preparations.length} 份教案`)
    }
  } catch (error) {
    console.error('批量导出失败:', error)
    ElMessage.error('批量导出失败')
  }
}

// 辅助函数：渲染Markdown
const renderMarkdown = (markdown) => {
  if (!markdown) return ''
  return marked.parse(markdown)
}
</script>

<style scoped>
.preparation-manage {
  padding: 20px;
  min-height: calc(100vh);
  background: white;
}

.page-header {
  margin-bottom: 30px;
  margin-top: -10px;
  text-align: center;
}

.page-header h1 {
  color: #303133;
  margin-bottom: 8px;
  margin-top: 0;
  font-size: 28px;
  font-weight: 600;
}

.page-header p {
  color: #909399;
  font-size: 16px;
  margin-top: 0;
}

.operation-bar {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 20px;
  width: 100%;
  gap: 15px;
}

.header-card,
.filter-card,
.content-card {
  margin-bottom: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: none;
  overflow: hidden;
}

.filter-card {
  background: white;
}

.filter-card .el-form {
  padding: 20px;
}

.filter-card .el-form-item {
  margin-bottom: 15px;
}

.filter-card .el-button {
  border-radius: 6px;
  font-weight: 500;
}

.content-card {
  background: white;
}

.content-card .el-table {
  border-radius: 8px;
  overflow: hidden;
}

.title-cell {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.title-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.title-tags .el-tag {
  border-radius: 12px;
  font-size: 11px;
  padding: 2px 8px;
  border: none;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
  padding: 20px;
  background: #fafafa;
  border-radius: 0 0 12px 12px;
}

.preparation-detail {
  padding: 20px 0;
}

.detail-header {
  margin-bottom: 25px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f0f0f0;
}

.detail-header h3 {
  margin: 0 0 15px 0;
  color: #2c3e50;
  font-size: 20px;
  font-weight: 600;
}

.detail-meta {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.detail-meta .el-tag {
  border-radius: 16px;
  padding: 6px 12px;
  font-weight: 500;
}

.detail-content {
  line-height: 1.8;
  padding: 20px 0;
  color: #2c3e50;
}

.ai-optimization {
  padding: 20px 0;
}

.optimization-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 2px solid #f0f0f0;
}

.optimization-header h4 {
  margin: 0;
  color: #2c3e50;
  font-size: 18px;
  font-weight: 600;
}

.optimization-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.optimization-actions {
  display: flex;
  justify-content: center;
  margin: 20px 0;
}

.optimization-actions .el-button {
  border-radius: 8px;
  font-weight: 500;
  padding: 12px 24px;
}

.ai-suggestions {
  border: 2px solid #e4e7ed;
  border-radius: 12px;
  padding: 25px;
  background: #fafafa;
  margin-top: 25px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.ai-suggestions h5 {
  margin: 0 0 20px 0;
  color: #1890ff;
  font-size: 18px;
  font-weight: 600;
  text-align: center;
  padding-bottom: 10px;
  border-bottom: 2px solid #1890ff;
}

.suggestion-content {
  line-height: 1.8;
  margin-bottom: 25px;
  background: white;
  padding: 20px;
  border-radius: 10px;
  border-left: 5px solid #1890ff;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.suggestion-content :deep(h2) {
  color: #1890ff;
  border-bottom: 2px solid #1890ff;
  padding-bottom: 10px;
  margin-bottom: 20px;
  font-size: 20px;
  font-weight: 600;
}

.suggestion-content :deep(h3) {
  color: #606266;
  margin: 20px 0 12px 0;
  font-size: 16px;
  font-weight: 600;
}

.suggestion-content :deep(ul) {
  padding-left: 25px;
}

.suggestion-content :deep(li) {
  margin: 10px 0;
  line-height: 1.6;
}

.suggestion-content :deep(strong) {
  color: #1890ff;
  font-weight: 600;
}

.suggestion-content :deep(blockquote) {
  border-left: 4px solid #52c41a;
  background: #f6ffed;
  padding: 15px 20px;
  margin: 15px 0;
  border-radius: 0 8px 8px 0;
  font-style: italic;
}

.suggestion-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
}

.suggestion-actions .el-button {
  border-radius: 8px;
  font-weight: 500;
  padding: 10px 20px;
  min-width: 100px;
}

.share-preparation {
  padding: 20px 0;
}

.share-actions {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 25px;
}

.share-actions .el-button {
  border-radius: 8px;
  font-weight: 500;
  padding: 10px 20px;
  min-width: 100px;
}

:deep(.el-tabs__content) {
  padding: 20px 0;
}

:deep(.el-tab-pane) {
  line-height: 1.6;
}

:deep(.el-table) {
  border-radius: 8px;
  overflow: hidden;
}

:deep(.el-table th) {
  background: #fafafa;
  color: #2c3e50;
  font-weight: 600;
  border-bottom: 2px solid #dee2e6;
}

:deep(.el-table td) {
  border-bottom: 1px solid #f0f0f0;
}

:deep(.el-table tr:hover) {
  background: #f0f9ff;
}

:deep(.el-button) {
  border-radius: 6px;
  font-weight: 500;
  transition: all 0.3s ease;
}

:deep(.el-button:hover) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

:deep(.el-select) {
  border-radius: 6px;
}

:deep(.el-input) {
  border-radius: 6px;
}

:deep(.el-pagination) {
  justify-content: center;
  margin-top: 20px;
}

:deep(.el-pagination .el-pager li) {
  border-radius: 6px;
  margin: 0 2px;
}

@media (max-width: 768px) {
  .preparation-manage {
    padding: 10px 0;
  }
  
  .page-header h1 {
    font-size: 24px;
  }
  
  .operation-bar {
    flex-direction: column;
    gap: 15px;
    align-items: center;
  }
  
  .title-cell {
    flex-direction: column;
    gap: 5px;
  }
  
  .title-tags {
    flex-wrap: wrap;
  }
  
  .detail-meta {
    flex-wrap: wrap;
    gap: 5px;
  }
  
  .optimization-header {
    flex-direction: column;
    gap: 15px;
  }
  
  .suggestion-actions,
  .share-actions {
    flex-direction: column;
  }
  
  .ai-suggestions {
    padding: 15px;
  }
  
  .suggestion-content {
    padding: 15px;
  }
}
</style>