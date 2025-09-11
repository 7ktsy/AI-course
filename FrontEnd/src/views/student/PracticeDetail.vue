<template>
  <div class="practice-detail-container">
    <!-- 顶部信息栏 -->
    <div class="practice-header" v-if="practiceInfo" v-loading="loading">
      <div class="header-left">
        <el-button @click="goBack" size="large" class="back-btn">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <div class="practice-title">
          <h1>{{ practiceInfo.title }}</h1>
          <div class="practice-meta">
            <el-tag type="success" size="large">实时智能练习</el-tag>
            <el-tag v-if="isCompleted" type="info" size="large">已完成</el-tag>
            <el-tag v-else-if="isOverdue" type="danger" size="large">已过期</el-tag>
          </div>
        </div>
      </div>
      
      <div class="header-right">
        <div class="timer" v-if="!isCompleted && !isOverdue">
          <el-icon><Clock /></el-icon>
          <span class="timer-text">剩余时间: {{ timeRemaining }}</span>
        </div>
        <div class="progress-info">
          <span>进度：{{ answeredCount }}/{{ questions.length }}</span>
          <el-progress 
            :percentage="progressPercentage" 
            :stroke-width="6"
            style="width: 150px"
          />
        </div>
      </div>
    </div>

    <!-- 练习信息卡片 -->
    <div class="practice-info-card" v-if="practiceInfo">
      <div class="info-grid">
        <div class="info-item">
          <el-icon><School /></el-icon>
          <span>课程：{{ practiceInfo.course_title }}</span>
        </div>
        <div class="info-item">
          <el-icon><Document /></el-icon>
          <span>题目数量：{{ questions.length }} 题</span>
        </div>
        <div class="info-item">
          <el-icon><Trophy /></el-icon>
          <span>总分：{{ totalScore }} 分</span>
        </div>
        <div class="info-item" v-if="practiceInfo.deadline">
          <el-icon><Clock /></el-icon>
          <span>结束时间：{{ formatDate(practiceInfo.deadline) }}</span>
        </div>
      </div>
    </div>

    <!-- 题目区域 -->
    <div class="questions-section" v-if="questions.length > 0" v-loading="questionsLoading">
      <!-- 题目导航 -->
      <div class="question-navigation">
        <div class="nav-buttons">
          <el-button
            v-for="(question, index) in questions"
            :key="question.id"
            :type="getQuestionNavType(question.id, index)"
            size="small"
            class="nav-button"
            @click="scrollToQuestion(index)"
          >
            {{ index + 1 }}
          </el-button>
        </div>
      </div>

      <!-- 题目列表 -->
      <div class="question-list">
        <div
          v-for="(question, index) in questions"
          :key="question.id"
          :id="`question-${index}`"
          class="question-item"
          :class="{ 'answered': answers[question.id] }"
        >
          <div class="question-header">
            <span class="question-number">第 {{ index + 1 }} 题</span>
            <el-tag :type="getQuestionTypeColor(question.type)" size="small">
              {{ question.type }}
            </el-tag>
            <span class="question-points">{{ question.points }} 分</span>
          </div>

          <div class="question-content">
            <div class="question-text" v-html="formatQuestionContent(question.content)"></div>
            
            <!-- 选择题 -->
            <div v-if="question.type === '选择'" class="question-options">
              <el-radio-group
                v-model="answers[question.id]"
                :disabled="isCompleted"
                size="large"
              >
                <el-radio
                  v-for="(option, optIndex) in question.options"
                  :key="optIndex"
                  :label="option"
                  class="radio-option"
                >
                  {{ option }}
                </el-radio>
              </el-radio-group>
            </div>

            <!-- 填空题 -->
            <div v-else-if="question.type === '填空'" class="question-input">
              <el-input
                v-model="answers[question.id]"
                :disabled="isCompleted"
                placeholder="请输入答案"
                size="large"
                maxlength="200"
                show-word-limit
                clearable
              />
            </div>

            <!-- 简答题 -->
            <div v-else-if="question.type === '简答'" class="question-textarea">
              <el-input
                v-model="answers[question.id]"
                :disabled="isCompleted"
                type="textarea"
                :rows="6"
                placeholder="请详细回答问题..."
                maxlength="1000"
                show-word-limit
                resize="vertical"
              />
            </div>

            <!-- 显示评分结果（完成后） -->
            <div v-if="isCompleted && gradingResults[question.id]" class="grading-result">
              <div class="result-header">
                <span class="result-score">
                  得分：{{ gradingResults[question.id].score }} / {{ gradingResults[question.id].max_points }}
                </span>
                <el-tag 
                  :type="gradingResults[question.id].score === gradingResults[question.id].max_points ? 'success' : 'warning'"
                  size="small"
                >
                  {{ gradingResults[question.id].score === gradingResults[question.id].max_points ? '正确' : '部分正确' }}
                </el-tag>
              </div>
              <div class="result-feedback" v-if="gradingResults[question.id].feedback">
                <strong>反馈：</strong>{{ gradingResults[question.id].feedback }}
              </div>
              <div class="correct-answer" v-if="question.answer && question.type !== '简答'">
                <strong>正确答案：</strong>{{ question.answer }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 提交按钮 -->
      <div class="submit-section" v-if="!isCompleted && !isOverdue">
        <div class="submit-info">
          <p>已完成 {{ answeredCount }} / {{ questions.length }} 题</p>
          <p v-if="answeredCount < questions.length" class="warning-text">
            还有 {{ questions.length - answeredCount }} 题未完成
          </p>
        </div>
        <el-button
          type="primary"
          size="large"
          :loading="submitting"
          @click="submitPractice"
          class="submit-btn"
        >
          {{ submitting ? '正在提交...' : '提交练习' }}
        </el-button>
      </div>
    </div>

    <!-- 评分结果弹窗 -->
    <el-dialog
      v-model="showResultDialog"
      title="练习完成"
      width="600px"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
    >
      <div class="result-dialog-content" v-if="finalResult">
        <div class="result-summary">
          <div class="score-display">
            <div class="score-circle">
              <div class="score-text">
                <span class="score">{{ finalResult.total_score }}</span>
                <span class="total">/ {{ finalResult.total_points }}</span>
              </div>
              <div class="percentage">{{ finalResult.percentage.toFixed(1) }}%</div>
            </div>
          </div>
          
          <div class="result-stats">
            <div class="stat-item">
              <span class="label">完成题数：</span>
              <span class="value">{{ questions.length }} 题</span>
            </div>
            <div class="stat-item">
              <span class="label">正确题数：</span>
              <span class="value">{{ correctCount }} 题</span>
            </div>
            <div class="stat-item">
              <span class="label">正确率：</span>
              <span class="value">{{ (correctCount / questions.length * 100).toFixed(1) }}%</span>
            </div>
          </div>
        </div>

        <div class="performance-analysis">
          <h4>表现分析</h4>
          <div class="analysis-item">
            <el-icon><TrendCharts /></el-icon>
            <span>{{ getPerformanceText(finalResult.percentage) }}</span>
          </div>
          
          <div class="weakness-analysis" v-if="weaknessPoints.length > 0">
            <h5>需要加强的知识点：</h5>
            <el-tag
              v-for="point in weaknessPoints"
              :key="point"
              type="warning"
              size="small"
              class="weakness-tag"
            >
              {{ point }}
            </el-tag>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="retryPractice">再次练习</el-button>
          <el-button 
            v-if="finalResult" 
            type="success" 
            @click="goToLearningAnalysis"
          >
            <el-icon><TrendCharts /></el-icon>
            学情分析报告
          </el-button>
          <el-button type="info" @click="goToDetailedResult">查看详细结果</el-button>
          <el-button type="primary" @click="goToPracticeList">查看练习列表</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft,
  School,
  Document,
  Trophy,
  Clock,
  TrendCharts
} from '@element-plus/icons-vue'
import request from '@/utils/request'

const route = useRoute()
const router = useRouter()

// 数据定义
const loading = ref(false)
const questionsLoading = ref(false)
const submitting = ref(false)
const practiceInfo = ref(null)
const questions = ref([])
const answers = ref({})
const gradingResults = ref({})
const finalResult = ref(null)
const showResultDialog = ref(false)
const timeRemaining = ref('')
const timerInterval = ref(null)

// 计算属性
const totalScore = computed(() => {
  return questions.value.reduce((total, q) => total + q.points, 0)
})

const answeredCount = computed(() => {
  return Object.keys(answers.value).filter(id => answers.value[id]?.trim()).length
})

const progressPercentage = computed(() => {
  return questions.value.length > 0 ? Math.round((answeredCount.value / questions.value.length) * 100) : 0
})

const isCompleted = computed(() => {
  return finalResult.value !== null
})

const isOverdue = computed(() => {
  if (!practiceInfo.value?.deadline) return false
  return new Date() > new Date(practiceInfo.value.deadline)
})

const correctCount = computed(() => {
  if (!finalResult.value) return 0
  return finalResult.value.results.filter(r => r.score === r.max_points).length
})

const weaknessPoints = computed(() => {
  if (!finalResult.value) return []
  return finalResult.value.results
    .filter(r => r.score < r.max_points * 0.6)
    .map(r => questions.value.find(q => q.id === r.question_id)?.key_knowledge)
    .filter(Boolean)
})

// API调用函数
const api = {
  // 获取练习信息
  async getPracticeInfo() {
    try {
      loading.value = true
      const response = await request.get(`/assignment/${route.params.id}/questions`)
      
      if (response.data) {
        questions.value = response.data.questions || []
        // 初始化答案对象
        questions.value.forEach(q => {
          if (!answers.value[q.id]) {
            answers.value[q.id] = ''
          }
        })
      }
      
      // 获取作业基本信息
      const assignmentResponse = await request.get(`/student/assignment/list`)
      const assignment = assignmentResponse.data.find(a => a.id == route.params.id)
      if (assignment) {
        practiceInfo.value = assignment
      }
    } catch (error) {
      console.error('获取练习信息失败:', error)
      ElMessage.error('获取练习信息失败')
    } finally {
      loading.value = false
    }
  },

  // 自动评分
  async autoGradePractice() {
    try {
      submitting.value = true
      
      const answersArray = Object.keys(answers.value).map(questionId => ({
        question_id: parseInt(questionId),
        answer: answers.value[questionId] || ''
      }))

      console.log('🚀 提交练习答案:', {
        assignment_id: route.params.id,
        answers_count: answersArray.length,
        answers: answersArray
      })

      const response = await request.post(`/assignment/auto-grade/${route.params.id}`, {
        answers: answersArray
      })

      if (response.data) {
        finalResult.value = response.data
        
        // 处理每题的评分结果
        response.data.results.forEach(result => {
          gradingResults.value[result.question_id] = result
        })
        
        // 保存练习结果到localStorage，供学情分析使用
        localStorage.setItem(`practice_result_${route.params.id}`, JSON.stringify(response.data))
        
        console.log('✅ 自动评分完成:', {
          总分: response.data.total_score,
          满分: response.data.total_points,
          得分率: response.data.percentage.toFixed(1) + '%',
          提交ID: response.data.submission_id
        })
        
        ElMessage.success('练习评分完成！')
        
        // 显示结果弹窗而不是跳转
        showResultDialog.value = true
      }
    } catch (error) {
      console.error('❌ 自动评分失败:', error)
      
      // 处理具体的错误情况
      if (error.response?.status === 400) {
        const errorMsg = error.response.data?.detail || '提交失败'
        if (errorMsg.includes('已经提交过')) {
          ElMessage.warning('该练习已经提交过，无法重复提交')
          // 可以选择跳转到结果页面或作业列表
          setTimeout(() => {
            router.push('/dashboard/student/homework')
          }, 2000)
        } else {
          ElMessage.error(errorMsg)
        }
      } else if (error.response?.status === 404) {
        ElMessage.error('练习不存在')
      } else {
        ElMessage.error('提交失败，请检查网络连接后重试')
      }
    } finally {
      submitting.value = false
    }
  }
}

// 事件处理函数
const goBack = () => {
  router.push('/dashboard/student/homework')
}

const submitPractice = async () => {
  if (answeredCount.value === 0) {
    ElMessage.warning('请至少回答一道题目')
    return
  }

  try {
    if (answeredCount.value < questions.value.length) {
      await ElMessageBox.confirm(
        `您还有 ${questions.value.length - answeredCount.value} 题未完成，确定要提交吗？`,
        '确认提交',
        { type: 'warning' }
      )
    }
    
    await api.autoGradePractice()
  } catch (error) {
    if (error === 'cancel') return
    console.error('提交失败:', error)
  }
}

const scrollToQuestion = (index) => {
  const element = document.getElementById(`question-${index}`)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }
}

const getQuestionNavType = (questionId, index) => {
  if (answers.value[questionId]?.trim()) {
    return 'success'
  }
  return 'default'
}

const getQuestionTypeColor = (type) => {
  const colorMap = {
    '选择': 'primary',
    '填空': 'success',
    '简答': 'warning'
  }
  return colorMap[type] || 'info'
}

const formatQuestionContent = (content) => {
  return content.replace(/\n/g, '<br>')
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

const getPerformanceText = (percentage) => {
  if (percentage >= 90) return '优秀！您对这些知识点掌握得很好'
  if (percentage >= 80) return '良好！您基本掌握了相关知识点'
  if (percentage >= 60) return '及格，但还有提升空间'
  return '需要加强学习，建议重点复习薄弱知识点'
}

const updateTimer = () => {
  if (!practiceInfo.value?.deadline) {
    timeRemaining.value = '无限制'
    return
  }

  const deadline = new Date(practiceInfo.value.deadline)
  const now = new Date()
  const diff = deadline - now

  if (diff <= 0) {
    timeRemaining.value = '已过期'
    if (timerInterval.value) {
      clearInterval(timerInterval.value)
    }
    // 自动提交
    if (!isCompleted.value) {
      ElMessage.warning('练习时间已到，自动提交')
      submitPractice()
    }
    return
  }

  const hours = Math.floor(diff / (1000 * 60 * 60))
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
  const seconds = Math.floor((diff % (1000 * 60)) / 1000)

  timeRemaining.value = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
}

const goToPracticeList = () => {
  router.push('/dashboard/student/homework')
}

const retryPractice = () => {
  router.push('/dashboard/student/real-time-practice')
}

const goToLearningAnalysis = () => {
  router.push({
    name: 'StudentLearningAnalysis',
    params: { id: route.params.id },
    query: {
      result: encodeURIComponent(JSON.stringify(finalResult.value)),
      answers: encodeURIComponent(JSON.stringify(answers.value))
    }
  })
}

const goToDetailedResult = () => {
  router.push({
    name: 'PracticeResult',
    params: { id: route.params.id },
    query: {
      result: encodeURIComponent(JSON.stringify(finalResult.value)),
      answers: encodeURIComponent(JSON.stringify(answers.value))
    }
  })
}

// 生命周期
onMounted(() => {
  api.getPracticeInfo()
  
  // 启动计时器
  updateTimer()
  timerInterval.value = setInterval(updateTimer, 1000)
})

onUnmounted(() => {
  if (timerInterval.value) {
    clearInterval(timerInterval.value)
  }
})
</script>

<style scoped>
.practice-detail-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.practice-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.back-btn {
  min-width: auto;
}

.practice-title h1 {
  font-size: 24px;
  color: #2c3e50;
  margin: 0 0 10px 0;
}

.practice-meta {
  display: flex;
  gap: 10px;
}

.header-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 10px;
}

.timer {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #f56c6c;
  font-weight: 600;
}

.timer-text {
  font-size: 16px;
}

.progress-info {
  display: flex;
  align-items: center;
  gap: 15px;
  font-size: 14px;
}

.practice-info-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #606266;
}

.questions-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.question-navigation {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e4e7ed;
}

.nav-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.nav-button {
  width: 40px;
  height: 40px;
  border-radius: 50%;
}

.question-item {
  margin-bottom: 40px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 25px;
  transition: all 0.3s ease;
}

.question-item:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.question-item.answered {
  border-color: #67c23a;
  background: #f0f9ff;
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e4e7ed;
}

.question-number {
  font-size: 18px;
  font-weight: 600;
  color: #409eff;
}

.question-points {
  font-size: 14px;
  color: #909399;
}

.question-content {
  line-height: 1.6;
}

.question-text {
  font-size: 16px;
  color: #2c3e50;
  margin-bottom: 20px;
  white-space: pre-wrap;
}

.question-options {
  margin-bottom: 20px;
}

.radio-option {
  display: block;
  margin-bottom: 15px;
  padding: 12px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.radio-option:hover {
  border-color: #409eff;
  background: #f0f7ff;
}

.question-input,
.question-textarea {
  margin-bottom: 20px;
}

.grading-result {
  margin-top: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 6px;
  border-left: 4px solid #409eff;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.result-score {
  font-weight: 600;
  color: #2c3e50;
}

.result-feedback {
  margin-bottom: 10px;
  color: #606266;
}

.correct-answer {
  color: #67c23a;
  font-weight: 500;
}

.submit-section {
  text-align: center;
  margin-top: 40px;
  padding: 30px;
  border: 2px dashed #e4e7ed;
  border-radius: 8px;
  background: #fafafa;
}

.submit-info {
  margin-bottom: 20px;
}

.submit-info p {
  margin: 5px 0;
  color: #606266;
}

.warning-text {
  color: #f56c6c !important;
  font-weight: 500;
}

.submit-btn {
  min-width: 150px;
  height: 50px;
  font-size: 16px;
}

.result-dialog-content {
  text-align: center;
}

.result-summary {
  margin-bottom: 30px;
}

.score-display {
  margin-bottom: 30px;
}

.score-circle {
  display: inline-block;
  width: 150px;
  height: 150px;
  border: 8px solid #409eff;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f0f7ff 0%, #e6f4ff 100%);
}

.score-text {
  font-size: 24px;
  font-weight: bold;
  color: #2c3e50;
}

.score {
  color: #409eff;
}

.total {
  color: #909399;
}

.percentage {
  font-size: 18px;
  font-weight: 600;
  color: #67c23a;
  margin-top: 5px;
}

.result-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.stat-item {
  text-align: center;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 6px;
}

.stat-item .label {
  display: block;
  color: #909399;
  font-size: 14px;
  margin-bottom: 5px;
}

.stat-item .value {
  display: block;
  color: #2c3e50;
  font-size: 18px;
  font-weight: 600;
}

.performance-analysis {
  text-align: left;
}

.performance-analysis h4 {
  margin-bottom: 15px;
  color: #2c3e50;
}

.analysis-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
  color: #606266;
}

.weakness-analysis {
  margin-top: 20px;
}

.weakness-analysis h5 {
  margin-bottom: 10px;
  color: #f56c6c;
}

.weakness-tag {
  margin: 0 5px 5px 0;
}

.dialog-footer {
  display: flex;
  justify-content: center;
  gap: 15px;
  flex-wrap: wrap;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .practice-header {
    flex-direction: column;
    align-items: stretch;
    gap: 20px;
  }
  
  .header-left {
    order: 2;
  }
  
  .header-right {
    order: 1;
    align-items: stretch;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .result-stats {
    grid-template-columns: 1fr;
  }
  
  .nav-buttons {
    justify-content: center;
  }

  .dialog-footer {
    flex-direction: column;
    align-items: center;
  }
}
</style> 