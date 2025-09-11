<template>
  <div class="question-bank">
    <!-- 顶部操作栏 -->
    <el-card shadow="never" class="header-card">
      <div class="header-content">
        <div class="header-left">
          <h2>题库管理</h2>
          <el-tag type="info">共 {{ totalQuestions }} 道题目</el-tag>
        </div>
        <div class="header-right">
          <el-button-group>
            <el-button type="primary" @click="showAddDialog = true">
              <el-icon><Plus /></el-icon>
              添加题目
            </el-button>
            <el-button @click="handleBatchImport">
              <el-icon><Upload /></el-icon>
              批量导入
            </el-button>
            <el-button @click="handleBatchExport">
              <el-icon><Download /></el-icon>
              批量导出
            </el-button>
          </el-button-group>
        </div>
      </div>
    </el-card>

    <!-- 筛选区域 -->
    <el-card shadow="never" class="filter-card">
      <el-form :model="filterForm" inline>
        <el-form-item label="题目类型">
          <el-select v-model="filterForm.type" placeholder="全部类型" clearable>
            <el-option label="选择题" value="选择" />
            <el-option label="填空题" value="填空" />
            <el-option label="简答题" value="简答" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="难度等级">
          <el-select v-model="filterForm.difficulty" placeholder="全部难度" clearable>
            <el-option label="简单" value="easy" />
            <el-option label="中等" value="medium" />
            <el-option label="困难" value="hard" />
          </el-select>
        </el-form-item>

        <el-form-item label="关键词">
          <el-input
            v-model="filterForm.keyword"
            placeholder="搜索题目内容..."
            style="width: 200px"
            clearable
          />
        </el-form-item>

        <el-form-item>
          <el-button-group>
            <el-button type="primary" @click="handleFilter">
              <el-icon><Search /></el-icon>
              筛选
            </el-button>
            <el-button @click="resetFilter">
              <el-icon><Refresh /></el-icon>
              重置
            </el-button>
          </el-button-group>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 题目列表 -->
    <el-card shadow="never" class="content-card">
      <div class="batch-actions" v-if="selectedQuestions.length > 0">
        <div class="batch-info">
          <el-tag type="info" size="large">
            <el-icon><Select /></el-icon>
            已选择 {{ selectedQuestions.length }} 道题目
          </el-tag>
          <div class="batch-buttons">
            <el-button size="small" type="danger" @click="handleBatchDelete">
              <el-icon><Delete /></el-icon>
              批量删除
            </el-button>
            <el-button size="small" type="success" @click="handleBatchAddToAssignment">
              <el-icon><Plus /></el-icon>
              添加到作业
            </el-button>
          </div>
        </div>
      </div>

      <el-table
        :data="questionList"
        v-loading="loading"
        @selection-change="handleSelectionChange"
        style="width: 100%"
      >
        <el-table-column type="selection" width="55" />
        
        <el-table-column prop="id" label="ID" width="80" />
        
        <el-table-column label="题目内容" min-width="300">
          <template #default="scope">
            <div class="question-content">
              <div class="question-text" v-html="scope.row.content"></div>
              <div class="question-tags">
                <el-tag :type="getTypeColor(scope.row.type)" size="small">
                  {{ scope.row.type }}
                </el-tag>
                <el-tag :type="getDifficultyColor(scope.row.difficulty)" size="small">
                  {{ getDifficultyText(scope.row.difficulty) }}
                </el-tag>
                <el-tag v-if="scope.row.key_knowledge" type="info" size="small" effect="plain">
                  知识点: {{ scope.row.key_knowledge }}
                </el-tag>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="points" label="分值" width="80" />
        
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="scope">
            <el-dropdown @command="handleCommand" trigger="click">
              <el-button size="small" class="operation-btn">
                操作<el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item :command="{ action: 'view', row: scope.row }">
                    <el-icon><View /></el-icon>
                    查看详情
                  </el-dropdown-item>
                  <el-dropdown-item :command="{ action: 'edit', row: scope.row }">
                    <el-icon><Edit /></el-icon>
                    编辑题目
                  </el-dropdown-item>
                  <el-dropdown-item :command="{ action: 'addToAssignment', row: scope.row }" divided>
                    <el-icon><Plus /></el-icon>
                    添加到作业
                  </el-dropdown-item>
                  <el-dropdown-item :command="{ action: 'delete', row: scope.row }" divided>
                    <el-icon><Delete /></el-icon>
                    删除题目
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
          :page-sizes="[10, 20, 50, 100]"
          :total="totalQuestions"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 添加/编辑题目对话框 -->
    <el-dialog
      v-model="showAddDialog"
      :title="editingQuestion ? '编辑题目' : '添加题目'"
      width="60%"
      destroy-on-close
    >
      <el-form :model="questionForm" :rules="questionRules" ref="questionFormRef" label-width="100px">
        <el-form-item label="题目类型" prop="type">
          <el-select v-model="questionForm.type" placeholder="请选择题目类型">
            <el-option label="选择题" value="选择" />
            <el-option label="填空题" value="填空" />
            <el-option label="简答题" value="简答" />
          </el-select>
        </el-form-item>

        <el-form-item label="难度等级" prop="difficulty">
          <el-radio-group v-model="questionForm.difficulty">
            <el-radio label="easy">简单</el-radio>
            <el-radio label="medium">中等</el-radio>
            <el-radio label="hard">困难</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="分值" prop="points">
          <el-input-number v-model="questionForm.points" :min="1" :max="100" />
        </el-form-item>

        <el-form-item label="题目内容" prop="content">
          <el-input
            v-model="questionForm.content"
            type="textarea"
            :rows="4"
            placeholder="请输入题目内容"
          />
        </el-form-item>

        <!-- 选择题选项 -->
        <template v-if="questionForm.type === '选择'">
          <el-form-item 
            v-for="(option, index) in ['A', 'B', 'C', 'D']" 
            :key="option"
            :label="`选项${option}`"
            :prop="`options.${index}`"
          >
            <el-input v-model="questionForm.options[index]" :placeholder="`请输入选项${option}`" />
          </el-form-item>
        </template>

        <el-form-item label="标准答案" prop="answer">
          <el-input
            v-model="questionForm.answer"
            type="textarea"
            :rows="3"
            placeholder="请输入标准答案"
          />
        </el-form-item>

        <el-form-item label="知识点" prop="key_knowledge">
          <el-input
            v-model="questionForm.key_knowledge"
            placeholder="请输入相关知识点"
          />
          <div class="form-item-tip" style="font-size: 12px; color: #909399; margin-top: 4px;">
            例如：物理层、数据链路层、网络层等
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showAddDialog = false">
            <el-icon><Close /></el-icon>
            取消
          </el-button>
          <el-button type="primary" @click="saveQuestion" :loading="saving">
            <el-icon><Check /></el-icon>
            {{ editingQuestion ? '保存修改' : '添加题目' }}
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 题目详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="题目详情" width="50%">
      <div v-if="currentQuestion" class="question-detail">
        <div class="detail-item">
          <label>题目类型：</label>
          <el-tag :type="getTypeColor(currentQuestion.type)">
            {{ currentQuestion.type }}
          </el-tag>
        </div>
        <div class="detail-item">
          <label>难度等级：</label>
          <el-tag :type="getDifficultyColor(currentQuestion.difficulty)">
            {{ getDifficultyText(currentQuestion.difficulty) }}
          </el-tag>
        </div>
        <div class="detail-item">
          <label>分值：</label>
          <span>{{ currentQuestion.points }} 分</span>
        </div>
        <div class="detail-item">
          <label>题目内容：</label>
          <div v-html="currentQuestion.content"></div>
        </div>
        <div v-if="currentQuestion.type === '选择'" class="detail-item">
          <label>选项：</label>
          <div class="options">
            <div v-for="(option, index) in currentQuestion.options" :key="index">
              {{ ['A', 'B', 'C', 'D'][index] }}. {{ option }}
            </div>
          </div>
        </div>
        <div class="detail-item">
          <label>标准答案：</label>
          <div v-html="currentQuestion.answer"></div>
        </div>
        <div class="detail-item">
          <label>知识点：</label>
          <div>{{ currentQuestion.key_knowledge }}</div>
        </div>
      </div>
    </el-dialog>

    <!-- 添加到作业对话框 -->
    <el-dialog v-model="showAddToAssignmentDialog" title="添加到作业" width="50%">
      <div class="add-to-assignment">
        <el-form label-width="100px">
          <el-form-item label="选择作业">
            <el-select 
              v-model="selectedAssignment" 
              placeholder="请选择要添加到的作业"
              style="width: 100%"
            >
              <el-option
                v-for="assignment in assignmentList"
                :key="assignment.id"
                :label="assignment.title"
                :value="assignment.id"
              >
                <div class="assignment-option">
                  <div class="assignment-title">{{ assignment.title }}</div>
                  <div class="assignment-meta">
                    <span>课程: {{ getCourseName(assignment.course_id) }}</span>
                    <span>截止时间: {{ formatDate(assignment.deadline) }}</span>
                    <span v-if="assignment.questionCount">题目数: {{ assignment.questionCount }}</span>
                  </div>
                </div>
              </el-option>
            </el-select>
          </el-form-item>
          
          <el-form-item label="选中题目">
            <div class="selected-questions">
              <el-tag 
                v-for="question in selectedQuestions" 
                :key="question.id"
                type="info"
                style="margin: 2px"
              >
                {{ question.content.substring(0, 30) }}...
              </el-tag>
            </div>
            <div class="question-count">
              共 {{ selectedQuestions.length }} 道题目
            </div>
          </el-form-item>
        </el-form>
        
        <div class="dialog-actions">
          <el-button @click="showAddToAssignmentDialog = false">
            <el-icon><Close /></el-icon>
            取消
          </el-button>
          <el-button 
            type="primary" 
            @click="confirmAddToAssignment"
            :loading="addToAssignmentLoading"
            :disabled="!selectedAssignment"
          >
            <el-icon><Check /></el-icon>
            确认添加
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowDown, View, Edit, Plus, Delete, Upload, Download, Select, Search, Refresh, Close, Check } from '@element-plus/icons-vue'
import axios from 'axios'

// 响应式数据
const loading = ref(false)
const saving = ref(false)
const showAddDialog = ref(false)
const showDetailDialog = ref(false)
const showAddToAssignmentDialog = ref(false)
const editingQuestion = ref(null)
const currentQuestion = ref(null)
const selectedQuestions = ref([])
const questionFormRef = ref()

const currentPage = ref(1)
const pageSize = ref(10)
const totalQuestions = ref(0)
const questionList = ref([])
const assignmentList = ref([])
const courseList = ref([])
const selectedAssignment = ref(null)
const addToAssignmentLoading = ref(false)

// 筛选表单
const filterForm = reactive({
  type: '',
  difficulty: '',
  keyword: ''
})

// 题目表单
const questionForm = reactive({
  type: '',
  difficulty: 'medium',
  content: '',
  options: ['', '', '', ''],
  answer: '',
  points: 1,
  key_knowledge: ''
})

// 表单验证规则
const questionRules = {
  type: [{ required: true, message: '请选择题目类型', trigger: 'change' }],
  difficulty: [{ required: true, message: '请选择难度等级', trigger: 'change' }],
  content: [{ required: true, message: '请输入题目内容', trigger: 'blur' }],
  answer: [{ required: true, message: '请输入标准答案', trigger: 'blur' }],
  points: [{ required: true, message: '请输入分值', trigger: 'blur' }],
  key_knowledge: [{ required: true, message: '请输入知识点', trigger: 'blur' }]
}

// 初始化
onMounted(() => {
  fetchQuestions()
  fetchAssignments()
  fetchCourses()
})

// 获取题目列表
const fetchQuestions = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('token') // 从localStorage获取token
    const response = await axios.get('/assignment/questions/all', {
      params: {
        page: currentPage.value,
        page_size: pageSize.value,
        question_type: filterForm.type || null
      },
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (response.data.data) {
      questionList.value = response.data.data
      totalQuestions.value = response.data.pagination.total
    }
  } catch (error) {
    if (error.response?.status === 403) {
      ElMessage.error('没有访问权限，请重新登录')
    } else {
      ElMessage.error('获取题目列表失败')
    }
  } finally {
    loading.value = false
  }
}

// 获取作业列表
const fetchAssignments = async () => {
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get('/assignment/all', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    const assignments = response.data.data || []
    
    // 获取每个作业的题目数量
    for (const assignment of assignments) {
      try {
        const questionsResponse = await axios.get(`/assignment/${assignment.id}/questions`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        assignment.questionCount = questionsResponse.data.questions?.length || 0
      } catch (error) {
        assignment.questionCount = 0
      }
    }
    
    assignmentList.value = assignments
  } catch (error) {
    if (error.response?.status === 403) {
      ElMessage.error('没有访问权限，请重新登录')
    } else {
      ElMessage.error('获取作业列表失败')
    }
  }
}

// 获取课程列表
const fetchCourses = async () => {
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get('/course/my', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    courseList.value = response.data.data?.courses || []
  } catch (error) {
    if (error.response?.status === 403) {
      ElMessage.error('没有访问权限，请重新登录')
    } else {
      ElMessage.error('获取课程列表失败')
    }
  }
}

// 辅助函数
const getTypeColor = (type) => {
  const colors = {
    '选择': 'primary',
    '填空': 'success',
    '简答': 'warning'
  }
  return colors[type] || 'info'
}

const getDifficultyColor = (difficulty) => {
  const colors = {
    easy: 'success',
    medium: 'warning',
    hard: 'danger'
  }
  return colors[difficulty] || 'info'
}

const getDifficultyText = (difficulty) => {
  const texts = {
    easy: '简单',
    medium: '中等',
    hard: '困难'
  }
  return texts[difficulty] || '未知'
}

// 获取课程名称
const getCourseName = (courseId) => {
  const course = courseList.value.find(c => c.id === courseId)
  return course ? course.title : '未知课程'
}

// 事件处理函数
const handleFilter = () => {
  currentPage.value = 1
  fetchQuestions()
}

const resetFilter = () => {
  Object.keys(filterForm).forEach(key => {
    filterForm[key] = ''
  })
  handleFilter()
}

const handleSelectionChange = (selection) => {
  selectedQuestions.value = selection
}

const handleSizeChange = (size) => {
  pageSize.value = size
  fetchQuestions()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  fetchQuestions()
}

const viewQuestion = (question) => {
  currentQuestion.value = question
  showDetailDialog.value = true
}

const addQuestionToAssignment = (question) => {
  selectedQuestions.value = [question]
  showAddToAssignmentDialog.value = true
  selectedAssignment.value = null
}

const editQuestion = (question) => {
  editingQuestion.value = question
  Object.assign(questionForm, {
    type: question.type,
    difficulty: question.difficulty || getRandomDifficulty(),
    content: question.content,
    options: question.options || ['', '', '', ''],
    answer: question.answer,
    points: question.points,
    key_knowledge: question.key_knowledge
  })
  showAddDialog.value = true
}

const getRandomDifficulty = () => {
  const difficulties = ['easy', 'medium', 'hard']
  return difficulties[Math.floor(Math.random() * difficulties.length)]
}

// 保存题目
const saveQuestion = async () => {
  try {
    await questionFormRef.value.validate()
    saving.value = true
    
    const token = localStorage.getItem('token')
    const questionData = {
      ...questionForm,
      options: questionForm.type === '选择' ? questionForm.options : null
    }
    
    if (editingQuestion.value) {
      await axios.put(`/assignment/questions/${editingQuestion.value.id}`, questionData, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      ElMessage.success('题目编辑成功')
    } else {
      await axios.post('/assignment/questions', questionData, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      ElMessage.success('题目添加成功')
    }
    
    showAddDialog.value = false
    resetQuestionForm()
    fetchQuestions()
  } catch (error) {
    if (error.response?.status === 403) {
      ElMessage.error('没有访问权限，请重新登录')
    } else {
      ElMessage.error('操作失败')
    }
  } finally {
    saving.value = false
  }
}

// 删除题目
const deleteQuestion = async (question) => {
  try {
    await ElMessageBox.confirm('确定要删除这道题目吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const token = localStorage.getItem('token')
    await axios.delete(`/assignment/questions/${question.id}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    ElMessage.success('题目删除成功')
    fetchQuestions()
  } catch (error) {
    if (error !== 'cancel') {
      if (error.response?.status === 403) {
        ElMessage.error('没有访问权限，请重新登录')
      } else {
        ElMessage.error('删除失败')
      }
    }
  }
}

// 批量删除
const handleBatchDelete = async () => {
  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${selectedQuestions.value.length} 道题目吗？`, '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const token = localStorage.getItem('token')
    const deletePromises = selectedQuestions.value.map(q => 
      axios.delete(`/assignment/questions/${q.id}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
    )
    await Promise.all(deletePromises)
    
    ElMessage.success('批量删除成功')
    fetchQuestions()
  } catch (error) {
    if (error !== 'cancel') {
      if (error.response?.status === 403) {
        ElMessage.error('没有访问权限，请重新登录')
      } else {
        ElMessage.error('批量删除失败')
      }
    }
  }
}

const handleBatchAddToAssignment = () => {
  if (selectedQuestions.value.length === 0) {
    ElMessage.warning('请先选择要添加的题目')
    return
  }
  showAddToAssignmentDialog.value = true
  selectedAssignment.value = null
}

const handleBatchImport = () => {
  ElMessage.info('批量导入功能开发中...')
}

const handleBatchExport = () => {
  ElMessage.info('批量导出功能开发中...')
}

// 确认添加到作业
const confirmAddToAssignment = async () => {
  if (!selectedAssignment.value) {
    ElMessage.warning('请选择要添加到的作业')
    return
  }
  
  if (selectedQuestions.value.length === 0) {
    ElMessage.warning('没有选中的题目')
    return
  }
  
  addToAssignmentLoading.value = true
  try {
    const token = localStorage.getItem('token')
    const promises = selectedQuestions.value.map(question =>
      axios.post(`/assignment/${selectedAssignment.value}/questions`, null, {
        params: {
          question_id: question.id,
          points: question.points || 1.0
        },
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
    )
    
    await Promise.all(promises)
    ElMessage.success(`成功添加 ${selectedQuestions.value.length} 道题目到作业`)
    showAddToAssignmentDialog.value = false
    selectedQuestions.value = []
    selectedAssignment.value = null
  } catch (error) {
    if (error.response?.status === 403) {
      ElMessage.error('没有访问权限，请重新登录')
    } else {
      ElMessage.error('添加题目到作业失败')
    }
  } finally {
    addToAssignmentLoading.value = false
  }
}

// 处理表格操作命令
const handleCommand = async (command) => {
  const question = command.row
  if (command.action === 'view') {
    viewQuestion(question)
  } else if (command.action === 'edit') {
    editQuestion(question)
  } else if (command.action === 'addToAssignment') {
    selectedQuestions.value = [question]
    showAddToAssignmentDialog.value = true
    selectedAssignment.value = null
  } else if (command.action === 'delete') {
    await deleteQuestion(question)
  }
}

// 日期格式化函数
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const resetQuestionForm = () => {
  Object.assign(questionForm, {
    type: '',
    difficulty: 'medium',
    content: '',
    options: ['', '', '', ''],
    answer: '',
    points: 1,
    key_knowledge: ''
  })
  editingQuestion.value = null
}
</script>

<style scoped>
.question-bank {
  padding: 20px 0;
}

.header-card,
.filter-card,
.content-card {
  margin-bottom: 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.header-left h2 {
  margin: 0;
}

.header-right {
  display: flex;
  gap: 10px;
}

.header-right .el-button-group {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-radius: 6px;
  overflow: hidden;
}

.header-right .el-button-group .el-button {
  border: none;
  transition: all 0.3s ease;
}

.header-right .el-button-group .el-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.batch-actions {
  margin-bottom: 20px;
}

.batch-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 15px;
}

.batch-info .el-tag {
  display: flex;
  align-items: center;
  gap: 5px;
}

.batch-buttons {
  display: flex;
  gap: 10px;
}

.question-content {
  padding: 10px 0;
}

.question-text {
  margin-bottom: 10px;
  line-height: 1.6;
  white-space: pre-wrap;  /* 保留换行和空格 */
}

.question-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 8px;
}

.question-tags .el-tag {
  margin-right: 0;
}

/* 知识点标签样式 */
.el-tag.el-tag--info.el-tag--plain {
  border-style: dashed;
  padding: 0 8px;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
  padding: 15px 0;
  background: #fafafa;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

.question-detail .detail-item {
  margin-bottom: 15px;
}

.question-detail .detail-item label {
  font-weight: bold;
  color: #303133;
  margin-right: 10px;
}

.question-detail .options div {
  margin: 5px 0;
  padding: 5px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.form-item-tip {
  line-height: 1.4;
  padding: 4px 0;
}

.add-to-assignment {
  padding: 20px 0;
}

.assignment-option {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.assignment-title {
  font-weight: 500;
  color: #303133;
}

.assignment-meta {
  font-size: 12px;
  color: #909399;
  display: flex;
  gap: 15px;
}

.selected-questions {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 10px;
  background-color: #fafafa;
}

.question-count {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
  text-align: center;
}

.dialog-actions {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.dialog-footer {
  display: flex;
  justify-content: center;
  gap: 15px;
}

/* 表格操作按钮样式 */
.el-table .el-dropdown {
  width: 100%;
}

.el-table .el-dropdown .el-button {
  width: 100%;
  justify-content: center;
}

/* 操作按钮优雅蓝绿色样式 */
.operation-btn {
  background: linear-gradient(135deg, #64b5f6 0%, #42a5f5 100%) !important;
  border-color: #42a5f5 !important;
  color: white !important;
  font-weight: 500;
  transition: all 0.3s ease;
}

.operation-btn:hover {
  background: linear-gradient(135deg, #5ba3e8 0%, #3b8fd8 100%) !important;
  border-color: #3b8fd8 !important;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(66, 165, 245, 0.3);
}

.operation-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 6px rgba(66, 165, 245, 0.2);
}

.operation-btn:focus {
  background: linear-gradient(135deg, #64b5f6 0%, #42a5f5 100%) !important;
  border-color: #42a5f5 !important;
  color: white !important;
}

.el-dropdown-menu .el-dropdown-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
}

.el-dropdown-menu .el-dropdown-item .el-icon {
  font-size: 14px;
}

/* 筛选按钮组样式 */
.el-form-item .el-button-group {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.el-form-item .el-button-group .el-button {
  border: none;
  transition: all 0.3s ease;
}

.el-form-item .el-button-group .el-button:hover {
  transform: translateY(-1px);
}
</style>