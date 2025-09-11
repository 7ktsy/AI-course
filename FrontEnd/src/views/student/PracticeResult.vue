<template>
  <div class="practice-result-container">
    <!-- 返回按钮 -->
    <div class="back-header">
      <el-button @click="goBack" size="large">
        <el-icon><ArrowLeft /></el-icon>
        返回练习列表
      </el-button>
    </div>

    <!-- 总体评分卡片 -->
    <div class="result-overview" v-if="practiceResult">
      <el-card class="overview-card">
        <template #header>
          <div class="card-header">
            <h2>{{ practiceInfo.title }}</h2>
            <el-tag type="success" size="large">练习完成</el-tag>
          </div>
        </template>
        
        <div class="score-section">
          <div class="score-display">
            <div class="score-circle" :class="getScoreLevel(practiceResult.percentage)">
              <div class="score-number">{{ practiceResult.total_score }}</div>
              <div class="score-total">/ {{ practiceResult.total_points }}</div>
              <div class="score-percentage">{{ practiceResult.percentage.toFixed(1) }}%</div>
            </div>
          </div>
          
          <div class="score-details">
            <div class="detail-item">
              <span class="label">答题情况：</span>
              <span class="value">{{ practiceResult.results.length }} 题全部完成</span>
            </div>
            <div class="detail-item">
              <span class="label">正确题数：</span>
              <span class="value">{{ correctCount }} / {{ practiceResult.results.length }}</span>
            </div>
            <div class="detail-item">
              <span class="label">正确率：</span>
              <span class="value">{{ (correctCount / practiceResult.results.length * 100).toFixed(1) }}%</span>
            </div>
            <div class="detail-item">
              <span class="label">答题用时：</span>
              <span class="value">{{ formatDuration() }}</span>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 题目详细评分 -->
    <div class="questions-analysis" v-if="practiceResult">
      <h3 class="section-title">
        <el-icon><Document /></el-icon>
        逐题分析
      </h3>
      
      <div class="question-cards">
        <el-card 
          v-for="(result, index) in practiceResult.results" 
          :key="result.question_id"
          class="question-card"
          :class="getQuestionCardClass(result)"
        >
          <template #header>
            <div class="question-header">
              <div class="question-info">
                <span class="question-number">第 {{ index + 1 }} 题</span>
                <el-tag :type="getQuestionTypeColor(result.type)" size="small">
                  {{ result.type }}
                </el-tag>
              </div>
              <div class="question-score">
                <span class="score-text" :class="getScoreClass(result.score, result.max_points)">
                  {{ result.score }} / {{ result.max_points }} 分
                </span>
                <el-tag 
                  :type="result.score === result.max_points ? 'success' : (result.score > 0 ? 'warning' : 'danger')"
                  size="small"
                >
                  {{ getScoreLabel(result.score, result.max_points) }}
                </el-tag>
              </div>
            </div>
          </template>
          
          <div class="question-content">
            <!-- 题目内容 -->
            <div class="question-text">
              <strong>题目：</strong>
              <div v-html="getQuestionContent(result.question_id)"></div>
            </div>
            
            <!-- 学生答案 -->
            <div class="student-answer">
              <strong>我的答案：</strong>
              <div class="answer-content">{{ getStudentAnswer(result.question_id) }}</div>
            </div>
            
            <!-- 正确答案（如果是客观题） -->
            <div v-if="result.type !== '简答'" class="correct-answer">
              <strong>正确答案：</strong>
              <div class="answer-content correct">{{ getCorrectAnswer(result.question_id) }}</div>
            </div>
            
            <!-- AI评分反馈 -->
            <div class="ai-feedback" v-if="result.feedback && result.feedback !== '正确' && result.feedback !== '错误'">
              <div class="feedback-header">
                <el-icon><ChatDotRound /></el-icon>
                <strong>AI智能评析</strong>
              </div>
              <div class="feedback-content">
                <div class="feedback-text">{{ result.feedback }}</div>
                
                <!-- 如果是简答题，解析更详细的反馈 -->
                <div v-if="result.type === '简答'" class="detailed-feedback">
                  <div class="feedback-sections">
                    <div v-if="getStrengths(result.feedback).length > 0" class="feedback-section positive">
                      <div class="section-title">
                        <el-icon><Check /></el-icon>
                        做得好的地方
                      </div>
                      <ul>
                        <li v-for="strength in getStrengths(result.feedback)" :key="strength">
                          {{ strength }}
                        </li>
                      </ul>
                    </div>
                    
                    <div v-if="getImprovements(result.feedback).length > 0" class="feedback-section improvement">
                      <div class="section-title">
                        <el-icon><Warning /></el-icon>
                        需要改进
                      </div>
                      <ul>
                        <li v-for="improvement in getImprovements(result.feedback)" :key="improvement">
                          {{ improvement }}
                        </li>
                      </ul>
                    </div>
                    
                    <div v-if="getSuggestions(result.feedback).length > 0" class="feedback-section suggestion">
                      <div class="section-title">
                        <el-icon><Guide /></el-icon>
                        学习建议
                      </div>
                      <ul>
                        <li v-for="suggestion in getSuggestions(result.feedback)" :key="suggestion">
                          {{ suggestion }}
                        </li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 学习分析与建议 -->
    <div class="learning-analysis" v-if="practiceResult">
      <h3 class="section-title">
        <el-icon><TrendCharts /></el-icon>
        学习分析与建议
      </h3>
      
      <div class="analysis-grid">
        <!-- 知识点掌握情况 -->
        <el-card class="analysis-card">
          <template #header>
            <h4>知识点掌握情况</h4>
          </template>
          <div class="knowledge-analysis">
            <div v-if="weakKnowledgePoints.length > 0" class="weak-points">
              <div class="points-title">
                <el-icon><Warning /></el-icon>
                需要加强的知识点
              </div>
              <div class="points-list">
                <el-tag 
                  v-for="point in weakKnowledgePoints" 
                  :key="point"
                  type="warning" 
                  size="small"
                  class="knowledge-tag"
                >
                  {{ point }}
                </el-tag>
              </div>
            </div>
            
            <div v-if="strongKnowledgePoints.length > 0" class="strong-points">
              <div class="points-title">
                <el-icon><Check /></el-icon>
                掌握良好的知识点
              </div>
              <div class="points-list">
                <el-tag 
                  v-for="point in strongKnowledgePoints" 
                  :key="point"
                  type="success" 
                  size="small"
                  class="knowledge-tag"
                >
                  {{ point }}
                </el-tag>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 总体评价 -->
        <el-card class="analysis-card">
          <template #header>
            <h4>总体评价</h4>
          </template>
          <div class="overall-evaluation">
            <div class="evaluation-item">
              <el-icon><Star /></el-icon>
              <span>{{ getOverallEvaluation() }}</span>
            </div>
            <div class="recommendations">
              <div class="rec-title">学习建议：</div>
              <ul>
                <li v-for="rec in getRecommendations()" :key="rec">{{ rec }}</li>
              </ul>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="action-buttons">
      <el-button size="large" @click="retryPractice">
        <el-icon><Refresh /></el-icon>
        再次练习
      </el-button>
      <el-button type="primary" size="large" @click="goToHomework">
        <el-icon><Document /></el-icon>
        查看更多练习
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ArrowLeft,
  Document,
  ChatDotRound,
  Check,
  Warning,
  Guide,
  TrendCharts,
  Star,
  Refresh
} from '@element-plus/icons-vue'
import request from '@/utils/request'

const route = useRoute()
const router = useRouter()

// 数据定义
const practiceResult = ref(null)
const practiceInfo = ref(null)
const questions = ref([])
const studentAnswers = ref({})
const loading = ref(false)

// 计算属性
const correctCount = computed(() => {
  if (!practiceResult.value) return 0
  return practiceResult.value.results.filter(r => r.score === r.max_points).length
})

const weakKnowledgePoints = computed(() => {
  if (!practiceResult.value) return []
  return practiceResult.value.results
    .filter(r => r.score < r.max_points * 0.6)
    .map(r => getQuestionKnowledge(r.question_id))
    .filter(Boolean)
})

const strongKnowledgePoints = computed(() => {
  if (!practiceResult.value) return []
  return practiceResult.value.results
    .filter(r => r.score === r.max_points)
    .map(r => getQuestionKnowledge(r.question_id))
    .filter(Boolean)
})

// API调用
const loadPracticeResult = async () => {
  try {
    loading.value = true
    
    // 从URL参数中获取评分结果和学生答案
    if (route.query.result) {
      practiceResult.value = JSON.parse(decodeURIComponent(route.query.result))
    }
    
    if (route.query.answers) {
      studentAnswers.value = JSON.parse(decodeURIComponent(route.query.answers))
    }
    
    // 获取练习基本信息
    const assignmentResponse = await request.get(`/student/assignment/list`)
    const assignment = assignmentResponse.data.find(a => a.id == route.params.id)
    if (assignment) {
      practiceInfo.value = assignment
    }
    
    // 获取题目详情
    const questionsResponse = await request.get(`/assignment/${route.params.id}/questions`)
    if (questionsResponse.data) {
      questions.value = questionsResponse.data.questions || []
    }
    
    console.log('📊 练习结果加载完成:', {
      练习信息: practiceInfo.value?.title,
      评分结果: practiceResult.value,
      题目数量: questions.value.length,
      学生答案: Object.keys(studentAnswers.value).length
    })
    
  } catch (error) {
    console.error('获取练习结果失败:', error)
    ElMessage.error('获取练习结果失败')
  } finally {
    loading.value = false
  }
}

// 工具函数
const getScoreLevel = (percentage) => {
  if (percentage >= 90) return 'excellent'
  if (percentage >= 80) return 'good'
  if (percentage >= 60) return 'average'
  return 'poor'
}

const getQuestionCardClass = (result) => {
  if (result.score === result.max_points) return 'correct'
  if (result.score > 0) return 'partial'
  return 'incorrect'
}

const getQuestionTypeColor = (type) => {
  const colorMap = {
    '选择': 'primary',
    '填空': 'success',
    '简答': 'warning'
  }
  return colorMap[type] || 'info'
}

const getScoreClass = (score, maxPoints) => {
  if (score === maxPoints) return 'score-perfect'
  if (score > 0) return 'score-partial'
  return 'score-zero'
}

const getScoreLabel = (score, maxPoints) => {
  if (score === maxPoints) return '完全正确'
  if (score > 0) return '部分正确'
  return '答错了'
}

const getQuestionContent = (questionId) => {
  const question = questions.value.find(q => q.id === questionId)
  return question?.content || ''
}

const getStudentAnswer = (questionId) => {
  const answer = studentAnswers.value[questionId]
  if (!answer || answer.trim() === '') {
    return '未作答'
  }
  return answer
}

const getCorrectAnswer = (questionId) => {
  const question = questions.value.find(q => q.id === questionId)
  return question?.answer || ''
}

const getQuestionKnowledge = (questionId) => {
  const question = questions.value.find(q => q.id === questionId)
  return question?.key_knowledge || ''
}

// 解析AI反馈的详细信息
const getStrengths = (feedback) => {
  // 解析反馈中的优点
  const strengths = []
  if (feedback.includes('正确指出') || feedback.includes('做得好')) {
    const match = feedback.match(/正确指出了([^，。；]+)/)
    if (match) strengths.push(match[1])
  }
  return strengths
}

const getImprovements = (feedback) => {
  // 解析反馈中的改进点
  const improvements = []
  if (feedback.includes('不足') || feedback.includes('缺少')) {
    const patterns = [
      /(\d+\.?[^；。]+)/g,
      /未([^；。]+)/g,
      /缺少([^；。]+)/g
    ]
    
    patterns.forEach(pattern => {
      const matches = feedback.match(pattern)
      if (matches) {
        improvements.push(...matches)
      }
    })
  }
  return improvements.slice(0, 3) // 最多3个改进点
}

const getSuggestions = (feedback) => {
  // 解析反馈中的建议
  const suggestions = []
  if (feedback.includes('建议')) {
    const match = feedback.match(/建议([^。]+)/)
    if (match) suggestions.push(match[1])
  }
  return suggestions
}

const getOverallEvaluation = () => {
  const percentage = practiceResult.value?.percentage || 0
  if (percentage >= 90) return '优秀！您对这些知识点掌握得很好'
  if (percentage >= 80) return '良好！您基本掌握了相关知识点'
  if (percentage >= 60) return '及格，但还有提升空间'
  return '需要加强学习，建议重点复习薄弱知识点'
}

const getRecommendations = () => {
  const recs = []
  const percentage = practiceResult.value?.percentage || 0
  
  if (percentage < 60) {
    recs.push('建议回顾基础概念，巩固理论知识')
    recs.push('多做相关练习题，加深理解')
  } else if (percentage < 80) {
    recs.push('继续保持，重点关注薄弱环节')
    recs.push('可以尝试更有挑战性的题目')
  } else {
    recs.push('继续保持优秀的学习状态')
    recs.push('可以尝试帮助其他同学学习')
  }
  
  if (weakKnowledgePoints.value.length > 0) {
    recs.push(`重点复习：${weakKnowledgePoints.value.join('、')}`)
  }
  
  return recs
}

const formatDuration = () => {
  // 这里可以根据实际的答题时间计算
  return '约15分钟'
}

// 事件处理
const goBack = () => {
  router.push('/dashboard/student/homework')
}

const retryPractice = () => {
  router.push('/dashboard/student/real-time-practice')
}

const goToHomework = () => {
  router.push('/dashboard/student/homework')
}

// 生命周期
onMounted(() => {
  loadPracticeResult()
})
</script>

<style scoped>
.practice-result-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.back-header {
  margin-bottom: 20px;
}

.result-overview {
  margin-bottom: 30px;
}

.overview-card {
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  color: #2c3e50;
}

.score-section {
  display: flex;
  align-items: center;
  gap: 40px;
}

.score-display {
  flex-shrink: 0;
}

.score-circle {
  width: 160px;
  height: 160px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 8px solid;
  position: relative;
}

.score-circle.excellent {
  border-color: #67c23a;
  background: linear-gradient(135deg, #f0f9ff 0%, #e6f4ff 100%);
}

.score-circle.good {
  border-color: #409eff;
  background: linear-gradient(135deg, #f0f7ff 0%, #e6f4ff 100%);
}

.score-circle.average {
  border-color: #e6a23c;
  background: linear-gradient(135deg, #fef9e7 0%, #fdf5e6 100%);
}

.score-circle.poor {
  border-color: #f56c6c;
  background: linear-gradient(135deg, #fef0f0 0%, #fde2e2 100%);
}

.score-number {
  font-size: 36px;
  font-weight: bold;
  color: #2c3e50;
}

.score-total {
  font-size: 18px;
  color: #909399;
  margin-top: -5px;
}

.score-percentage {
  font-size: 20px;
  font-weight: 600;
  color: #67c23a;
  margin-top: 5px;
}

.score-details {
  flex: 1;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
  padding: 10px 0;
  border-bottom: 1px solid #f5f7fa;
}

.detail-item:last-child {
  border-bottom: none;
}

.label {
  font-weight: 600;
  color: #606266;
}

.value {
  color: #2c3e50;
  font-weight: 500;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 20px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 20px;
}

.question-cards {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.question-card {
  border-radius: 8px;
  transition: all 0.3s ease;
}

.question-card.correct {
  border-left: 4px solid #67c23a;
}

.question-card.partial {
  border-left: 4px solid #e6a23c;
}

.question-card.incorrect {
  border-left: 4px solid #f56c6c;
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.question-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.question-number {
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
}

.question-score {
  display: flex;
  align-items: center;
  gap: 10px;
}

.score-text {
  font-weight: 600;
}

.score-perfect { color: #67c23a; }
.score-partial { color: #e6a23c; }
.score-zero { color: #f56c6c; }

.question-content {
  margin-top: 15px;
}

.question-text,
.student-answer,
.correct-answer {
  margin-bottom: 15px;
  padding: 10px;
  border-radius: 6px;
  background: #f8f9fa;
}

.question-text {
  background: #f0f7ff;
  border-left: 3px solid #409eff;
}

.student-answer {
  background: #fef9e7;
  border-left: 3px solid #e6a23c;
}

.correct-answer {
  background: #f0f9ff;
  border-left: 3px solid #67c23a;
}

.answer-content {
  margin-top: 5px;
  color: #2c3e50;
}

.ai-feedback {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 15px;
  border: 1px solid #e4e7ed;
}

.feedback-header {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #409eff;
  margin-bottom: 10px;
}

.feedback-content {
  line-height: 1.6;
}

.feedback-text {
  color: #606266;
  margin-bottom: 15px;
}

.detailed-feedback {
  margin-top: 15px;
}

.feedback-sections {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.feedback-section {
  padding: 12px;
  border-radius: 6px;
  border-left: 4px solid;
}

.feedback-section.positive {
  background: #f0f9ff;
  border-left-color: #67c23a;
}

.feedback-section.improvement {
  background: #fef9e7;
  border-left-color: #e6a23c;
}

.feedback-section.suggestion {
  background: #f0f7ff;
  border-left-color: #409eff;
}

.feedback-section .section-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 8px;
}

.feedback-section ul {
  margin: 0;
  padding-left: 20px;
}

.feedback-section li {
  margin-bottom: 5px;
  color: #606266;
}

.analysis-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.analysis-card {
  border-radius: 8px;
}

.knowledge-analysis .points-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  margin-bottom: 10px;
  color: #2c3e50;
}

.points-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 20px;
}

.knowledge-tag {
  margin: 2px;
}

.overall-evaluation {
  line-height: 1.6;
}

.evaluation-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  color: #2c3e50;
  margin-bottom: 15px;
}

.recommendations .rec-title {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 8px;
}

.recommendations ul {
  margin: 0;
  padding-left: 20px;
}

.recommendations li {
  margin-bottom: 5px;
  color: #606266;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 40px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .score-section {
    flex-direction: column;
    text-align: center;
    gap: 20px;
  }
  
  .analysis-grid {
    grid-template-columns: 1fr;
  }
  
  .action-buttons {
    flex-direction: column;
    align-items: center;
  }
}
</style> 