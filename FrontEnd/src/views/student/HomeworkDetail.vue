<template>
  <div class="homework-detail-container">
    <!-- 返回按钮 -->
    <div class="back-header">
      <el-button @click="goBack" size="large">
        <el-icon><ArrowLeft /></el-icon>
        返回作业列表
      </el-button>
    </div>

    <!-- 作业信息 -->
    <div class="assignment-info" v-if="assignmentInfo" v-loading="loading">
      <div class="info-header">
        <h1 class="assignment-title">{{ assignmentInfo.title }}</h1>
        <div class="assignment-meta">
          <el-tag 
            :type="isSelfGenerated ? 'success' : 'primary'" 
            size="large"
          >
            {{ isSelfGenerated ? '实时测评' : '教师布置' }}
          </el-tag>
          <el-tag 
            v-if="isSubmitted" 
            type="success" 
            size="large"
          >
            已提交
          </el-tag>
          <el-tag 
            v-else-if="isOverdue" 
            type="danger" 
            size="large"
          >
            已过期
          </el-tag>
        </div>
      </div>
      
      <div class="info-details">
        <div class="detail-item">
          <el-icon><School /></el-icon>
          <span>课程：{{ assignmentInfo.course_title }}</span>
        </div>
        <div class="detail-item" v-if="assignmentInfo.deadline">
          <el-icon><Clock /></el-icon>
          <span>截止时间：{{ formatDate(assignmentInfo.deadline) }}</span>
        </div>
        <div class="detail-item">
          <el-icon><Document /></el-icon>
          <span>题目数量：{{ questions.length }} 题</span>
        </div>
        <div class="detail-item" v-if="totalScore">
          <el-icon><Trophy /></el-icon>
          <span>总分：{{ totalScore }} 分</span>
        </div>
        <div class="detail-item" v-if="isSubmitted && submissionInfo">
          <el-icon><DocumentChecked /></el-icon>
          <span>获得分数：{{ submissionInfo.score }} 分</span>
        </div>
        <div class="detail-item" v-if="isSubmitted && submissionInfo">
          <el-icon><Clock /></el-icon>
          <span>提交时间：{{ submissionInfo.submit_time }}</span>
        </div>
      </div>
    </div>

    <!-- 题目列表 -->
    <div class="questions-container" v-if="questions.length > 0" v-loading="questionsLoading">
      <div class="questions-header">
        <h2>题目列表</h2>
        <div class="progress-info">
          <span>已完成：{{ answeredCount }}/{{ questions.length }}</span>
          <el-progress 
            :percentage="progressPercentage" 
            :stroke-width="8"
            style="width: 200px"
          />
        </div>
      </div>

      <div class="question-list">
        <div 
          v-for="(question, index) in questions" 
          :key="question.id" 
          class="question-item"
          :class="{ 
            'answered': !isSubmitted && answers[question.id],
            'submitted': isSubmitted
          }"
        >
          <div class="question-header">
            <span class="question-number">第 {{ index + 1 }} 题</span>
            <el-tag 
              :type="getQuestionTypeColor(question.type)" 
              size="small"
            >
              {{ question.type }}
            </el-tag>
            <span class="question-points">{{ question.points }} 分</span>
          </div>

          <div class="question-content">
            <div class="question-text" v-html="question.content"></div>
            
            <!-- 选择题 -->
            <div v-if="question.type === '选择'" class="question-options">
              <el-radio-group 
                v-model="answers[question.id]" 
                class="options-group"
                :disabled="isSubmitted"
              >
                <el-radio 
                  v-for="(option, optionIndex) in question.options" 
                  :key="optionIndex" 
                  :label="option"
                  class="option-item"
                >
                  {{ option }}
                </el-radio>
              </el-radio-group>
            </div>

            <!-- 填空题 -->
            <div v-else-if="question.type === '填空'" class="question-input">
              <el-input
                v-model="answers[question.id]"
                placeholder="请输入答案"
                size="large"
                clearable
                :disabled="isSubmitted"
              />
            </div>

            <!-- 主观题 -->
            <div v-else class="question-textarea">
              <el-input
                v-model="answers[question.id]"
                type="textarea"
                :rows="6"
                placeholder="请输入详细答案..."
                maxlength="2000"
                show-word-limit
                :disabled="isSubmitted"
              />
            </div>
          </div>

          <!-- 知识点提示 -->
          <div v-if="question.key_knowledge" class="knowledge-hint">
            <el-icon><InfoFilled /></el-icon>
            <span>知识点：{{ question.key_knowledge }}</span>
          </div>

          <!-- 已提交后的答案对比 -->
          <div v-if="isSubmitted && question.answer" class="answer-comparison">
            <div class="comparison-header">
              <el-icon><DocumentChecked /></el-icon>
              <span>答案对比</span>
            </div>
            <div class="comparison-content">
              <div class="answer-section">
                <div class="answer-label my-answer">我的答案：</div>
                <div class="answer-value">{{ getMyAnswer(question.id) || '未作答' }}</div>
              </div>
              <div class="answer-section">
                <div class="answer-label correct-answer">标准答案：</div>
                <div class="answer-value">{{ question.answer }}</div>
              </div>
              <div v-if="getQuestionScore(question.id)" class="score-section">
                <div class="score-display">
                  得分：{{ getQuestionScore(question.id) }} / {{ question.points }} 分
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 提交区域 -->
    <div class="submit-section" v-if="questions.length > 0">
      <div class="submit-info">
        <!-- 已提交状态 -->
        <div v-if="isSubmitted" class="completion-status">
          <el-icon class="completed">
            <CircleCheck />
          </el-icon>
          <span>作业已提交完成</span>
        </div>
        
        <!-- 未提交状态 -->
        <div v-else class="completion-status">
          <el-icon :class="{ 'completed': isAllAnswered }">
            <CircleCheck v-if="isAllAnswered" />
            <Warning v-else />
          </el-icon>
          <span>
            {{ isAllAnswered ? '所有题目已完成' : `还有 ${questions.length - answeredCount} 题未完成` }}
          </span>
        </div>
        
        <div class="submit-warning" v-if="!isSubmitted && isOverdue">
          <el-alert
            title="注意：该作业已过截止时间，提交后可能不会被正常评分"
            type="warning"
            show-icon
            :closable="false"
          />
        </div>
      </div>

      <div class="submit-actions">
        <!-- 已提交：显示查看结果按钮 -->
        <template v-if="isSubmitted">
          <el-button size="large" @click="goBack">
            <el-icon><ArrowLeft /></el-icon>
            返回作业列表
          </el-button>
          <el-button 
            type="success" 
            size="large" 
            @click="viewSubmissionDetails"
          >
            <el-icon><DocumentChecked /></el-icon>
            查看总分
          </el-button>
        </template>
        
        <!-- 未提交：显示保存和提交按钮 -->
        <template v-else>
          <el-button size="large" @click="saveDraft">
            <el-icon><DocumentCopy /></el-icon>
            保存草稿
          </el-button>
          <el-button 
            type="primary" 
            size="large" 
            @click="submitAssignment"
            :loading="submitting"
            :disabled="!isAllAnswered"
          >
            <el-icon><Promotion /></el-icon>
            提交作业
          </el-button>
        </template>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="!loading && !questionsLoading && questions.length === 0" class="empty-state">
      <el-empty description="该作业暂无题目" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  ArrowLeft, 
  School, 
  Clock, 
  Document, 
  Trophy, 
  InfoFilled, 
  CircleCheck, 
  Warning,
  DocumentCopy,
  Promotion,
  DocumentChecked
} from '@element-plus/icons-vue'
import request from '@/utils/request'

const router = useRouter()
const route = useRoute()

// 数据定义
const assignmentInfo = ref(null)
const questions = ref([])
const answers = ref({})
const submissionInfo = ref(null) // 添加提交信息
const loading = ref(false)
const questionsLoading = ref(false)
const submitting = ref(false)

// 当前用户信息
const currentUser = JSON.parse(localStorage.getItem('userInfo') || '{}')

// 计算属性
const isSelfGenerated = computed(() => {
  return assignmentInfo.value?.creator_id === String(currentUser.id)
})

const isOverdue = computed(() => {
  if (!assignmentInfo.value?.deadline) return false
  return new Date(assignmentInfo.value.deadline) < new Date()
})

const totalScore = computed(() => {
  return questions.value.reduce((sum, q) => sum + (q.points || 0), 0)
})

const answeredCount = computed(() => {
  return Object.values(answers.value).filter(answer => answer && answer.toString().trim()).length
})

const progressPercentage = computed(() => {
  if (questions.value.length === 0) return 0
  return Math.round((answeredCount.value / questions.value.length) * 100)
})

const isAllAnswered = computed(() => {
  return answeredCount.value === questions.value.length
})

// 添加作业是否已提交的计算属性
const isSubmitted = computed(() => {
  return submissionInfo.value !== null
})

// API 调用
const api = {
  // 获取作业信息
  async getAssignmentInfo(assignmentId) {
    try {
      loading.value = true
      // 这里需要一个获取作业基本信息的API
      // 暂时从作业列表API中模拟获取
      const response = await request.get('/student/assignment/list')
      if (response && response.data) {
        const assignment = response.data.find(a => a.id === parseInt(assignmentId))
        if (assignment) {
          assignmentInfo.value = assignment
        } else {
          throw new Error('作业不存在')
        }
      }
    } catch (error) {
      console.error('获取作业信息失败:', error)
      ElMessage.error('获取作业信息失败')
      goBack()
    } finally {
      loading.value = false
    }
  },

  // 获取作业题目
  async getAssignmentQuestions(assignmentId) {
    try {
      questionsLoading.value = true
      const response = await request.get(`/assignment/${assignmentId}/questions`)
      console.log('题目列表响应:', response)
      if (response && response.data && response.data.questions) {
        questions.value = response.data.questions
        // 初始化答案对象
        questions.value.forEach(q => {
          if (!answers.value[q.id]) {
            answers.value[q.id] = ''
          }
        })
      }
    } catch (error) {
      console.error('获取题目失败:', error)
      ElMessage.error('获取题目失败')
    } finally {
      questionsLoading.value = false
    }
  },

  // 提交作业
  async submitAssignment(assignmentId, answersData) {
    try {
      submitting.value = true
      const submitData = {
        answers: Object.entries(answersData).map(([questionId, answer]) => ({
          question_id: parseInt(questionId),
          answer: answer.toString().trim()
        }))
      }
      
      console.log('提交数据:', submitData)
      const response = await request.post(`/student/assignment/${assignmentId}/submit`, submitData)
      console.log('提交响应:', response)
      
      if (response && response.data) {
        ElMessage.success('作业提交成功！')
        // 跳转到结果页面或返回列表
        router.push({
          name: 'MyHomework'
        })
        return response.data
      }
    } catch (error) {
      console.error('提交作业失败:', error)
      if (error.response?.data?.detail) {
        ElMessage.error(error.response.data.detail)
      } else {
        ElMessage.error('提交作业失败')
      }
      throw error
    } finally {
      submitting.value = false
    }
  },

  // 检查作业提交状态
  async checkSubmissionStatus(assignmentId) {
    try {
      const response = await request({
        method: 'get',
        url: `/student/assignment/${assignmentId}/my_result`,
        silentNotFound: true  // 静默处理404错误
      })
      if (response && response.data) {
        submissionInfo.value = response.data
        console.log('作业已提交，提交信息:', response.data)
        return true
      }
    } catch (error) {
      // 如果返回404，说明该作业未提交，这是正常情况
      if (error.response?.status === 404) {
        submissionInfo.value = null
        return false
      }
      // 其他错误才记录日志
      console.warn('检查提交状态失败:', error.message)
      return false
    }
  }
}

// 工具函数
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

const getQuestionTypeColor = (type) => {
  const typeColors = {
    '选择': 'primary',
    '填空': 'success',
    '主观': 'warning',
    '编码': 'danger'
  }
  return typeColors[type] || 'info'
}

const getQuestionFeedback = (questionId) => {
  if (!submissionInfo.value || !submissionInfo.value.feedback) {
    return null
  }
  
  try {
    const feedback = JSON.parse(submissionInfo.value.feedback)
    
    // 方法1: 直接匹配Question ID（新数据格式）
    let result = feedback.find(f => f.question_id === questionId || f.question_id === parseInt(questionId))
    
    if (!result) {
      // 方法2: 通过题目顺序匹配（兼容旧数据格式）
      const questionIndex = questions.value.findIndex(q => q.id === questionId)
      if (questionIndex >= 0 && feedback[questionIndex]) {
        result = feedback[questionIndex]
      }
    }
    
    if (!result) {
      // 方法3: 如果还是没找到，尝试通过order字段匹配
      const question = questions.value.find(q => q.id === questionId)
      if (question && question.order) {
        result = feedback.find(f => f.question_id === question.order || f.order === question.order)
      }
    }

    return result
  } catch (e) {
    console.error('解析反馈信息失败:', e)
    return null
  }
}

const getMyAnswer = (questionId) => {
  return answers.value[questionId] || ''
}

const getQuestionScore = (questionId) => {
  const feedback = getQuestionFeedback(questionId)
  return feedback ? feedback.score : null
   
}

// 事件处理
const goBack = () => {
  router.push({ name: 'MyHomework' })
}

const saveDraft = () => {
  // 保存到本地存储
  const draftKey = `homework_draft_${route.params.id}`
  localStorage.setItem(draftKey, JSON.stringify(answers.value))
  ElMessage.success('草稿已保存')
}

const submitAssignment = async () => {
  try {
    // 检查是否所有题目都已回答
    if (!isAllAnswered.value) {
      await ElMessageBox.confirm(
        '还有题目未完成，确定要提交吗？未完成的题目将得0分。',
        '确认提交',
        {
          type: 'warning',
          confirmButtonText: '确定提交',
          cancelButtonText: '继续答题'
        }
      )
    } else {
      await ElMessageBox.confirm(
        '确定要提交作业吗？提交后将无法修改。',
        '确认提交',
        {
          type: 'info',
          confirmButtonText: '确定提交',
          cancelButtonText: '再检查一下'
        }
      )
    }

    await api.submitAssignment(route.params.id, answers.value)
    
    // 清除草稿
    const draftKey = `homework_draft_${route.params.id}`
    localStorage.removeItem(draftKey)
    
  } catch (error) {
    if (error !== 'cancel') {
      console.error('提交失败:', error)
    }
  }
}

const viewSubmissionDetails = () => {
  // 跳转到作业列表或显示简单的提示
  ElMessage.success(`总分：${submissionInfo.value.score} 分`)
  goBack()
}

// 生命周期
onMounted(async () => {
  const assignmentId = route.params.id
  if (!assignmentId) {
    ElMessage.error('作业ID不存在')
    goBack()
    return
  }

  // 加载作业信息、题目和提交状态
  await Promise.all([
    api.getAssignmentInfo(assignmentId),
    api.getAssignmentQuestions(assignmentId),
    api.checkSubmissionStatus(assignmentId)
  ])

  console.log('作业提交状态:', isSubmitted.value)
  console.log('题目数据:', questions.value)
  console.log('提交信息:', submissionInfo.value)

  // 如果作业已提交，加载提交的答案
  if (isSubmitted.value && submissionInfo.value) {
    try {
      const submittedAnswers = JSON.parse(submissionInfo.value.answer)
      answers.value = { ...answers.value, ...submittedAnswers }
      console.log('已加载提交的答案:', submittedAnswers)
    } catch (e) {
      console.error('解析提交答案失败:', e)
    }
  } else {
    // 如果未提交，尝试加载草稿
    const draftKey = `homework_draft_${assignmentId}`
    const savedDraft = localStorage.getItem(draftKey)
    if (savedDraft) {
      try {
        const draftAnswers = JSON.parse(savedDraft)
        answers.value = { ...answers.value, ...draftAnswers }
        ElMessage.info('已加载上次保存的草稿')
      } catch (e) {
        console.error('加载草稿失败:', e)
      }
    }
  }
})
</script>

<style scoped>
.homework-detail-container {
  padding: 20px;
  max-width: 900px;
  margin: 0 auto;
}

.back-header {
  margin-bottom: 20px;
}

.assignment-info {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
}

.info-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.assignment-title {
  margin: 0;
  color: #1f2937;
  font-size: 24px;
  font-weight: 600;
  flex: 1;
  margin-right: 16px;
}

.assignment-meta {
  display: flex;
  gap: 8px;
}

.info-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #6b7280;
  font-size: 14px;
}

.detail-item .el-icon {
  font-size: 16px;
  color: #9ca3af;
}

.questions-container {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
}

.questions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e5e7eb;
}

.questions-header h2 {
  margin: 0;
  color: #1f2937;
  font-size: 20px;
  font-weight: 600;
}

.progress-info {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #6b7280;
  font-size: 14px;
}

.question-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.question-item {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 20px;
  transition: all 0.3s ease;
}

.question-item.answered {
  border-color: #10b981;
  background: #f0fdf4;
}

.question-item.submitted {
  border-color: #f59e0b; /* Orange for submitted */
  background: #fffbeb;
}

.question-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.question-number {
  font-weight: 600;
  color: #1f2937;
}

.question-points {
  color: #6b7280;
  font-size: 14px;
  margin-left: auto;
}

.question-content {
  margin-bottom: 12px;
}

.question-text {
  margin-bottom: 16px;
  line-height: 1.6;
  color: #374151;
  font-size: 16px;
}

.question-options {
  margin-top: 12px;
}

.options-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.option-item {
  margin: 0;
  height: auto;
  line-height: 1.6;
}

.question-input,
.question-textarea {
  margin-top: 12px;
}

.knowledge-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #6b7280;
  font-size: 14px;
  background: #f9fafb;
  padding: 8px 12px;
  border-radius: 6px;
  margin-top: 12px;
}

.knowledge-hint .el-icon {
  color: #3b82f6;
}

.answer-comparison {
  margin-top: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  overflow: hidden;
}

.comparison-header {
  background: #f8fafc;
  padding: 8px 12px;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e5e7eb;
}

.comparison-header .el-icon {
  color: #10b981;
}

.comparison-content {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.answer-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.answer-label {
  font-weight: 600;
  color: #1f2937;
  font-size: 14px;
}

.my-answer {
  color: #059669; /* Green for my answer */
}

.correct-answer {
  color: #3b82f6; /* Blue for correct answer */
}

.answer-value {
  flex: 1;
  color: #374151;
  font-size: 14px;
  line-height: 1.6;
  word-break: break-word;
}

.score-section {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px dashed #e5e7eb;
}

.score-display {
  font-weight: 600;
  color: #059669;
  font-size: 14px;
}

.submit-section {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: sticky;
  bottom: 20px;
}

.submit-info {
  margin-bottom: 16px;
}

.completion-status {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.completion-status .el-icon {
  font-size: 18px;
  color: #6b7280;
}

.completion-status .el-icon.completed {
  color: #10b981;
}

.submit-warning {
  margin-bottom: 16px;
}

.submit-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400px;
}

@media (max-width: 768px) {
  .homework-detail-container {
    padding: 12px;
  }
  
  .info-header {
    flex-direction: column;
    gap: 12px;
  }
  
  .questions-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  .progress-info {
    width: 100%;
  }
  
  .submit-actions {
    flex-direction: column;
  }
}
</style> 