<template>
  <div class="homework-management">
    <!-- 顶部操作栏 -->
    <el-card shadow="never" class="header-card">
      <div class="header-content">
        <div class="header-left">
          <h2>作业管理</h2>
          <el-tag type="info">共 {{ totalAssignments }} 份作业</el-tag>
        </div>
        <div class="header-right">
          <el-button type="primary" @click="showCreateDialog = true">
            <i class="bi bi-plus-lg"></i>
            创建作业
          </el-button>
          <el-button @click="handleBatchAction">
            <i class="bi bi-gear"></i>
            批量操作
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 筛选区域 -->
    <el-card shadow="never" class="filter-card">
      <el-form :model="filterForm" inline>
        <el-form-item label="作业状态">
          <el-select v-model="filterForm.status" placeholder="全部状态" clearable>
            <el-option label="草稿" value="draft" />
            <el-option label="已发布" value="published" />
            <el-option label="进行中" value="ongoing" />
            <el-option label="已截止" value="expired" />
            <el-option label="已结束" value="finished" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="课程">
          <el-select v-model="filterForm.courseId" placeholder="全部课程" clearable>
            <el-option 
              v-for="course in courseList" 
              :key="course.id"
              :label="course.name" 
              :value="course.id" 
            />
          </el-select>
        </el-form-item>

        <el-form-item label="班级">
          <el-select v-model="filterForm.classId" placeholder="全部班级" clearable>
            <el-option 
              v-for="classItem in classList" 
              :key="classItem.id"
              :label="classItem.name" 
              :value="classItem.id" 
            />
          </el-select>
        </el-form-item>

        <el-form-item label="关键词">
          <el-input
            v-model="filterForm.keyword"
            placeholder="搜索作业标题..."
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

    <!-- 作业列表 -->
    <el-card shadow="never" class="content-card">
      <el-table
        :data="assignmentList"
        v-loading="loading"
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        
        <el-table-column prop="title" label="作业标题" min-width="200">
          <template #default="scope">
            <el-link type="primary" @click="viewAssignment(scope.row)">
              {{ scope.row.title }}
            </el-link>
          </template>
        </el-table-column>
        
        <el-table-column label="题目数量" width="100" align="center">
          <template #default="scope">
            <el-button link type="primary" @click="viewAssignment(scope.row)">
              {{ scope.row.questionCount || 0 }} 题
            </el-button>
          </template>
        </el-table-column>

        <el-table-column label="截止时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.deadline) }}
          </template>
        </el-table-column>
        
        <el-table-column label="创建时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="250" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="viewAssignment(scope.row)">
              查看
            </el-button>
            <el-button 
              size="small" 
              type="primary"
              @click="editAssignment(scope.row)"
            >
              编辑
            </el-button>
            <el-button 
              size="small" 
              type="success"
              @click="viewAnalysis(scope.row)"
            >
              学情分析
            </el-button>
            <el-dropdown @command="(command) => handleMoreAction(command, scope.row)">
              <el-button size="small">
                更多<i class="el-icon--right el-icon-arrow-down"></i>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="questions">管理题目</el-dropdown-item>
                  <el-dropdown-item command="delete" divided>删除作业</el-dropdown-item>
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
          :total="totalAssignments"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 创建/编辑作业对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingAssignment ? '编辑作业' : '创建作业'"
      width="60%"
      destroy-on-close
    >
      <el-form :model="assignmentForm" :rules="assignmentRules" ref="assignmentFormRef" label-width="120px">
        <el-form-item label="作业标题" prop="title">
          <el-input v-model="assignmentForm.title" placeholder="请输入作业标题" />
        </el-form-item>

        <el-form-item label="作业描述" prop="description">
          <el-input
            v-model="assignmentForm.description"
            type="textarea"
            :rows="4"
            placeholder="请输入作业描述和要求"
          />
        </el-form-item>

        <el-form-item label="选择课程" prop="courseId">
          <el-select v-model="assignmentForm.courseId" placeholder="请选择课程">
            <el-option 
              v-for="course in courseList" 
              :key="course.id"
              :label="course.name" 
              :value="course.id" 
            />
          </el-select>
        </el-form-item>

        <el-form-item label="选择班级" prop="classId">
          <el-select v-model="assignmentForm.classId" placeholder="请选择班级">
            <el-option 
              v-for="classItem in classList" 
              :key="classItem.id"
              :label="classItem.name" 
              :value="classItem.id" 
            />
          </el-select>
        </el-form-item>

        <el-form-item label="截止时间" prop="deadline">
          <el-date-picker
            v-model="assignmentForm.deadline"
            type="datetime"
            placeholder="选择截止时间"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="作业设置">
          <el-checkbox v-model="assignmentForm.allowLateSubmission">允许逾期提交</el-checkbox>
          <el-checkbox v-model="assignmentForm.showAnswerAfterDeadline">截止后显示答案</el-checkbox>
          <el-checkbox v-model="assignmentForm.randomQuestionOrder">随机题目顺序</el-checkbox>
        </el-form-item>

        <el-form-item label="总分" prop="totalScore">
          <el-input-number 
            v-model="assignmentForm.totalScore" 
            :min="0" 
            :max="1000"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button @click="saveAsDraft" :loading="saving">保存草稿</el-button>
        <el-button type="primary" @click="saveAndPublish" :loading="saving">
          {{ editingAssignment ? '保存修改' : '保存并发布' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 管理题目对话框 -->
    <el-dialog
      v-model="showQuestionsDialog"
      title="管理作业题目"
      width="80%"
      destroy-on-close
    >
      <div class="questions-management">
        <div class="questions-header">
          <el-button type="primary" @click="showAddQuestionDialog = true">
            添加题目
          </el-button>
          <el-button @click="removeSelectedQuestions" :disabled="selectedQuestionIds.length === 0">
            移除选中
          </el-button>
        </div>

        <el-table
          :data="assignmentQuestions"
          @selection-change="handleQuestionSelectionChange"
          row-key="id"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="order" label="顺序" width="80" />
          <el-table-column prop="content" label="题目内容" min-width="300" />
          <el-table-column prop="type" label="类型" width="100" />
          <el-table-column prop="score" label="分值" width="80" />
          <el-table-column label="操作" width="150">
            <template #default="scope">
              <el-button size="small" @click="moveQuestionUp(scope.row)" :disabled="scope.$index === 0">
                上移
              </el-button>
              <el-button size="small" @click="moveQuestionDown(scope.row)" :disabled="scope.$index === assignmentQuestions.length - 1">
                下移
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>

    <!-- 添加题目到作业对话框 -->
    <el-dialog
      v-model="showAddQuestionDialog"
      title="添加题目到作业"
      width="70%"
    >
      <!-- 这里可以复用题库管理的题目选择功能 -->
      <div class="add-question-content">
        <el-table
          :data="availableQuestions"
          @selection-change="handleAvailableQuestionSelection"
          max-height="400"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="content" label="题目内容" min-width="300" />
          <el-table-column prop="type" label="类型" width="100" />
          <!-- <el-table-column prop="difficulty" label="难度" width="100" /> -->
        </el-table>
      </div>
      
      <template #footer>
        <el-button @click="showAddQuestionDialog = false">取消</el-button>
        <el-button type="primary" @click="addQuestionsToAssignment">
          添加选中题目
        </el-button>
      </template>
    </el-dialog>

    <!-- 查看作业题目对话框 -->
    <el-dialog
      v-model="showViewDialog"
      :title="currentViewAssignment ? `查看作业：${currentViewAssignment.title}` : '查看作业'"
      width="80%"
      destroy-on-close
    >
      <div class="assignment-view">
        <!-- 作业基本信息 -->
        <el-descriptions v-if="currentViewAssignment" :column="2" border>
          <el-descriptions-item label="作业标题">{{ currentViewAssignment.title }}</el-descriptions-item>
          <el-descriptions-item label="截止时间">{{ currentViewAssignment.deadline }}</el-descriptions-item>
          <el-descriptions-item label="课程">{{ currentViewAssignment.courseName }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ currentViewAssignment.created_at }}</el-descriptions-item>
        </el-descriptions>

        <!-- 题目列表 -->
        <div class="questions-list">
          <h3>题目列表</h3>
          <el-card v-for="question in currentQuestions" :key="question.id" class="question-card">
            <template #header>
              <div class="question-header">
                <span>第 {{ question.order }} 题 ({{ question.type }})</span>
                <div class="question-info">
                  <el-tag size="small" type="success">{{ question.points }}分</el-tag>
                  <el-tag size="small" type="warning" v-if="question.difficulty">{{ question.difficulty }}</el-tag>
                  <el-tag size="small" type="info" v-if="question.key_knowledge">{{ question.key_knowledge }}</el-tag>
                </div>
              </div>
            </template>
            
            <!-- 题目内容 -->
            <div class="question-content">
              <p class="question-text">{{ question.content }}</p>
              
              <!-- 选择题选项 -->
              <el-radio-group v-if="question.type === '选择' && question.options" v-model="question.selectedAnswer" disabled>
                <el-radio v-for="(option, index) in question.options" :key="index" :label="option">
                  {{ option }}
                </el-radio>
              </el-radio-group>

              <!-- 答案区域 -->
              <div class="answer-section" v-if="question.answer">
                <el-divider content-position="left">参考答案</el-divider>
                <p class="answer-text">{{ question.answer }}</p>
              </div>
            </div>
          </el-card>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import { useRouter } from 'vue-router'

// 路由
const router = useRouter()

// 响应式数据
const loading = ref(false)
const saving = ref(false)
const showCreateDialog = ref(false)
const showQuestionsDialog = ref(false)
const showAddQuestionDialog = ref(false)
const editingAssignment = ref(null)
const currentAssignment = ref(null)
const assignmentFormRef = ref()

const currentPage = ref(1)
const pageSize = ref(20)
const totalAssignments = ref(0)
const assignmentList = ref([])
const courseList = ref([])
const classList = ref([])
const assignmentQuestions = ref([])
const availableQuestions = ref([])
const selectedQuestionIds = ref([])
const selectedAvailableQuestions = ref([])

// 在 setup 中添加新的响应式变量
const showViewDialog = ref(false)
const currentQuestions = ref([])
const currentViewAssignment = ref(null)

// 筛选表单
const filterForm = reactive({
  status: '',
  courseId: '',
  classId: '',
  keyword: ''
})

// 作业表单
const assignmentForm = reactive({
  title: '',
  description: '',
  courseId: '',
  classId: '',
  deadline: '',
  allowLateSubmission: false,
  showAnswerAfterDeadline: true,
  randomQuestionOrder: false,
  totalScore: 100
})

// 表单验证规则
const assignmentRules = {
  title: [{ required: true, message: '请输入作业标题', trigger: 'blur' }],
  description: [{ required: true, message: '请输入作业描述', trigger: 'blur' }],
  courseId: [{ required: true, message: '请选择课程', trigger: 'change' }],
  deadline: [{ required: true, message: '请选择截止时间', trigger: 'change' }]
}

// 初始化
onMounted(() => {
  fetchAssignments()
  fetchCourses()
  fetchClasses()
})

// 获取作业列表
const fetchAssignments = async () => {
  loading.value = true
  try {
    const response = await axios.get('/assignment/all', {
      params: {
        page: currentPage.value,
        page_size: pageSize.value,
        ...filterForm
      },
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    // 获取每个作业的题目数量
    const assignments = response.data.data || []
    for (const assignment of assignments) {
      try {
        const questionsResponse = await axios.get(`/assignment/${assignment.id}/questions`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        })
        assignment.questionCount = questionsResponse.data.questions?.length || 0
      } catch (error) {
        assignment.questionCount = 0
      }
    }
    assignmentList.value = assignments
    totalAssignments.value = response.data.pagination.total || 0
    
    // 更新分页信息
    currentPage.value = response.data.pagination.page
    pageSize.value = response.data.pagination.page_size
  } catch (error) {
    if (error.response?.status === 403) {
      ElMessage.error('没有权限访问作业列表')
    } else {
      ElMessage.error('获取作业列表失败')
    }
  } finally {
    loading.value = false
  }
}

// 获取课程列表
const fetchCourses = async () => {
  try {
    const response = await axios.get('/course/my', {  // 修改为正确的API路径
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}` // 添加token
      }
    })
    // 后端返回格式是 { "courses": [...] }，需要提取courses数组
    courseList.value = response.data.courses || []
  } catch (error) {
    if (error.response?.status === 404) {
      ElMessage.error('课程列表接口不存在')
    } else {
      console.error('获取课程列表失败:', error)
      ElMessage.error('获取课程列表失败')
    }
  }
}

// 获取班级列表 - 由于后端没有班级概念，这里暂时返回空数组
const fetchClasses = async () => {
  try {
    // 后端没有班级API，暂时返回空数组
    classList.value = []
    // 如果将来需要班级功能，可以在这里添加API调用
    // const response = await axios.get('/api/teacher/classes', {
    //   headers: {
    //     'Authorization': `Bearer ${localStorage.getItem('token')}`
    //   }
    // })
    // classList.value = response.data || []
  } catch (error) {
    console.error('获取班级列表失败:', error)
    ElMessage.error('获取班级列表失败')
  }
}

// 获取作业题目
const fetchAssignmentQuestions = async (assignmentId) => {
  try {
    const response = await axios.get(`/assignment/${assignmentId}/questions`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    assignmentQuestions.value = response.data.questions || []
  } catch (error) {
    ElMessage.error('获取作业题目失败')
  }
}

// 获取可用题目
const fetchAvailableQuestions = async () => {
  try {
    const response = await axios.get('/assignment/questions/all', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    // 后端返回格式是 { "data": [...], "pagination": {...} }，需要提取data数组
    availableQuestions.value = response.data.data || []
  } catch (error) {
    ElMessage.error('获取题目列表失败')
  }
}

// 辅助函数
const getStatusColor = (status) => {
  const colors = {
    draft: 'info',
    published: 'success',
    ongoing: 'warning',
    expired: 'danger',
    finished: ''
  }
  return colors[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    draft: '草稿',
    published: '已发布',
    ongoing: '进行中',
    expired: '已截止',
    finished: '已结束'
  }
  return texts[status] || '未知'
}

// 添加日期格式化函数
const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
}

// 修改提交率计算函数
const getSubmissionRate = (assignment) => {
  const totalStudents = assignment.total_students || 0;
  const submittedCount = assignment.submitted_count || 0;
  if (totalStudents === 0) return 0;
  return Math.round((submittedCount / totalStudents) * 100);
}

// 事件处理函数
const handleFilter = () => {
  currentPage.value = 1
  fetchAssignments()
}

const resetFilter = () => {
  Object.keys(filterForm).forEach(key => {
    filterForm[key] = ''
  })
  handleFilter()
}

const handleSizeChange = (size) => {
  pageSize.value = size
  fetchAssignments()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  fetchAssignments()
}

// 修改查看作业函数
const viewAssignment = async (assignment) => {
  currentViewAssignment.value = assignment
  try {
    const response = await axios.get(`/assignment/${assignment.id}/questions`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    currentQuestions.value = response.data.questions || []
    showViewDialog.value = true
  } catch (error) {
    ElMessage.error('获取作业题目失败')
  }
}

const editAssignment = (assignment) => {
  editingAssignment.value = assignment
  Object.keys(assignmentForm).forEach(key => {
    assignmentForm[key] = assignment[key] || ''
  })
  showCreateDialog.value = true
}

const viewQuestions = (assignment) => {
  currentAssignment.value = assignment
  fetchAssignmentQuestions(assignment.id)
  showQuestionsDialog.value = true
}

const viewAnalysis = (assignment) => {
  router.push({
    name: 'LearningAnalysis',
    params: { id: assignment.id }
  })
}

const handleMoreAction = async (command, assignment) => {
  switch (command) {
    case 'questions':
      viewQuestions(assignment)
      break
    case 'submissions':
      ElMessage.info('查看提交功能开发中...')
      break
    case 'statistics':
      ElMessage.info('统计分析功能开发中...')
      break
    case 'duplicate':
      ElMessage.info('复制作业功能开发中...')
      break
    case 'delete':
      await deleteAssignment(assignment)
      break
  }
}

// 删除作业
const deleteAssignment = async (assignment) => {
  try {
    await ElMessageBox.confirm('确定要删除这份作业吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await axios.delete(`/assignment/${assignment.id}`, {  // 修正删除作业的API路径
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    ElMessage.success('作业删除成功')
    fetchAssignments()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const saveAsDraft = async () => {
  try {
    await assignmentFormRef.value.validate()
    saving.value = true
    
    // 只发送后端API需要的字段
    const data = {
      title: assignmentForm.title,
      description: assignmentForm.description,
      course_id: assignmentForm.courseId, // 注意字段名转换
      deadline: assignmentForm.deadline,
      question_ids: [] // 暂时为空数组，后续可以通过题目管理功能添加
    }
    
    if (editingAssignment.value) {
      // 后端没有更新作业的API，暂时显示提示
      ElMessage.warning('编辑功能暂未实现，请重新创建作业')
      showCreateDialog.value = false
      resetAssignmentForm()
      return
    } else {
      await axios.post('/assignment/create', data, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      ElMessage.success('作业创建成功')
    }
    
    showCreateDialog.value = false
    resetAssignmentForm()
    fetchAssignments()
  } catch (error) {
    ElMessage.error('操作失败')
  } finally {
    saving.value = false
  }
}

// 保存作业（创建新作业）
const saveAndPublish = async () => {
  try {
    await assignmentFormRef.value.validate()
    saving.value = true
    
    // 只发送后端API需要的字段
    const data = {
      title: assignmentForm.title,
      description: assignmentForm.description,
      course_id: assignmentForm.courseId, // 注意字段名转换
      deadline: assignmentForm.deadline,
      question_ids: [] // 暂时为空数组，后续可以通过题目管理功能添加
    }
    
    if (editingAssignment.value) {
      // 后端没有更新作业的API，暂时显示提示
      ElMessage.warning('编辑功能暂未实现，请重新创建作业')
      showCreateDialog.value = false
      resetAssignmentForm()
      return
    } else {
      await axios.post('/assignment/create', data, {  // 修正创建作业的API路径
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      ElMessage.success('作业创建并发布成功')
    }
    
    showCreateDialog.value = false
    resetAssignmentForm()
    fetchAssignments()
  } catch (error) {
    ElMessage.error('操作失败')
  } finally {
    saving.value = false
  }
}

const handleQuestionSelectionChange = (selection) => {
  selectedQuestionIds.value = selection.map(q => q.id)
}

const handleAvailableQuestionSelection = (selection) => {
  selectedAvailableQuestions.value = selection
}

// 添加题目到作业
const addQuestionsToAssignment = async () => {
  if (selectedAvailableQuestions.value.length === 0) {
    ElMessage.warning('请选择要添加的题目')
    return
  }
  
  try {
    const promises = selectedAvailableQuestions.value.map(question =>
      axios.post(`/assignment/${currentAssignment.value.id}/questions`, {
        question_id: question.id,
        points: question.points || 1.0 // 默认分值为1.0
      }, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
    )
    
    await Promise.all(promises)
    ElMessage.success('题目添加成功')
    showAddQuestionDialog.value = false
    fetchAssignmentQuestions(currentAssignment.value.id)
  } catch (error) {
    ElMessage.error('添加题目失败')
  }
}

// 从作业中移除题目
const removeSelectedQuestions = async () => {
  if (selectedQuestionIds.value.length === 0) {
    ElMessage.warning('请选择要移除的题目')
    return
  }
  
  try {
    await ElMessageBox.confirm('确定要移除选中的题目吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const promises = selectedQuestionIds.value.map(questionId =>
      axios.delete(`/assignment/${currentAssignment.value.id}/questions/${questionId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
    )
    
    await Promise.all(promises)
    ElMessage.success('题目移除成功')
    fetchAssignmentQuestions(currentAssignment.value.id)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('移除题目失败')
    }
  }
}

// 调整题目顺序
const moveQuestionUp = async (question) => {
  try {
    await axios.put(`/assignment/${currentAssignment.value.id}/questions/${question.id}/order`, null, {
      params: {
        new_order: question.order - 1
      },
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    await fetchAssignmentQuestions(currentAssignment.value.id)
  } catch (error) {
    ElMessage.error('调整顺序失败')
  }
}

const moveQuestionDown = async (question) => {
  try {
    await axios.put(`/assignment/${currentAssignment.value.id}/questions/${question.id}/order`, null, {
      params: {
        new_order: question.order + 1
      },
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    await fetchAssignmentQuestions(currentAssignment.value.id)
  } catch (error) {
    ElMessage.error('调整顺序失败')
  }
}

const resetAssignmentForm = () => {
  Object.keys(assignmentForm).forEach(key => {
    if (typeof assignmentForm[key] === 'boolean') {
      assignmentForm[key] = false
    } else if (typeof assignmentForm[key] === 'number') {
      assignmentForm[key] = 100
    } else {
      assignmentForm[key] = ''
    }
  })
  editingAssignment.value = null
}

const handleBatchAction = () => {
  ElMessage.info('批量操作功能开发中...')
}

// 在对话框打开时获取可用题目
const handleAddQuestionDialogOpen = () => {
  fetchAvailableQuestions()
}

// 添加获取课程和班级名称的函数
const getCourseNameById = (courseId) => {
  const course = courseList.value.find(c => c.id === courseId);
  return course ? course.name : '未知课程';
}

const getClassNameById = (classId) => {
  const classItem = classList.value.find(c => c.id === classId);
  return classItem ? classItem.name : '未知班级';
}
</script>

<style scoped>
.homework-management {
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

.submission-info {
  text-align: center;
}

.submission-info div {
  margin-bottom: 5px;
  font-size: 12px;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}

.questions-management {
  padding: 10px 0;
}

.questions-header {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
}

.add-question-content {
  margin: 20px 0;
}

.assignment-view {
  padding: 20px 0;
}

.questions-list {
  margin-top: 20px;
}

.question-card {
  margin-bottom: 20px;
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.question-info {
  display: flex;
  gap: 10px;
}

.question-content {
  padding: 10px 0;
}

.question-text {
  font-size: 16px;
  margin-bottom: 15px;
}

.answer-section {
  margin-top: 15px;
}

.answer-text {
  color: #67c23a;
  font-weight: 500;
}

:deep(.el-radio-group) {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

:deep(.el-descriptions) {
  margin-bottom: 20px;
}
</style>