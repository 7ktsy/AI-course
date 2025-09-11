<template>
  <div class="real-time-practice-container">
    <!-- 标题 -->
    <div class="page-header">
      <h1 class="page-title">实时智能练习</h1>
      <p class="page-subtitle">根据您的掌握程度，智能生成个性化练习题目</p>
    </div>

    <!-- 步骤指示器 -->
    <div class="steps-container">
      <el-steps :active="currentStep" align-center>
        <el-step title="选择课程" />
        <el-step title="掌握程度评估" />
        <el-step title="题目设置" />
        <el-step title="开始练习" />
      </el-steps>
    </div>

    <!-- 第一步：课程选择 -->
    <div v-if="currentStep === 0" class="step-content">
      <h2 class="step-title">选择要练习的课程</h2>
      <div class="course-grid" v-loading="coursesLoading">
        <div v-if="courses.length === 0" class="empty-state">
          <el-empty description="您还没有加入任何课程" />
        </div>
        <div
          v-for="course in courses"
          :key="course.id"
          class="course-card"
          :class="{ 'selected': selectedCourse?.id === course.id }"
          @click="selectCourse(course)"
        >
          <div class="course-content">
            <div class="course-icon">
              <el-icon size="24"><School /></el-icon>
            </div>
            <h3 class="course-title">{{ course.title }}</h3>
            <p class="course-teacher">教师：{{ course.teacher }}</p>
            <div class="course-actions">
              <el-button
                v-if="selectedCourse?.id === course.id"
                type="primary"
                size="small"
              >
                已选择
              </el-button>
              <el-button
                v-else
                type="default"
                size="small"
              >
                选择课程
              </el-button>
            </div>
          </div>
        </div>
      </div>
      <div class="step-actions">
        <el-button
          type="primary"
          size="large"
          :disabled="!selectedCourse"
          @click="nextStep"
        >
          下一步
        </el-button>
      </div>
    </div>

    <!-- 第二步：掌握程度评估 -->
    <div v-if="currentStep === 1" class="step-content">
      <h2 class="step-title">评估您对各知识点的掌握程度</h2>
      <p class="step-subtitle">请拖动滑块来表示您对每个知识点的掌握程度（0-100分）</p>
      
      <div class="knowledge-points-container">
        <div
          v-for="(point, index) in knowledgePoints"
          :key="index"
          class="knowledge-point-item"
        >
          <div class="point-header">
            <h4 class="point-name">{{ point.knowledge_point }}</h4>
            <span class="point-score">{{ point.mastery_score }}分</span>
          </div>
          <div class="point-slider">
            <el-slider
              v-model="point.mastery_score"
              :min="0"
              :max="100"
              :step="5"
              show-stops
              :format-tooltip="formatTooltip"
            />
          </div>
          <div class="mastery-level">
            <span :class="getMasteryLevelClass(point.mastery_score)">
              {{ getMasteryLevelText(point.mastery_score) }}
            </span>
          </div>
        </div>
      </div>

      <div class="step-actions">
        <el-button size="large" @click="prevStep">上一步</el-button>
        <el-button type="primary" size="large" @click="nextStep">下一步</el-button>
      </div>
    </div>

    <!-- 第三步：题目设置 -->
    <div v-if="currentStep === 2" class="step-content">
      <h2 class="step-title">设置练习题目</h2>
      <p class="step-subtitle">选择您想要练习的题目类型和数量</p>

      <div class="question-settings">
        <div
          v-for="(setting, index) in questionSettings"
          :key="index"
          class="question-type-card"
        >
          <div class="type-header">
            <el-icon size="20" class="type-icon">
              <component :is="getQuestionTypeIcon(setting.type)" />
            </el-icon>
            <h4 class="type-name">{{ setting.type }}</h4>
          </div>
          <div class="type-counter">
            <el-input-number
              v-model="setting.amount"
              :min="0"
              :max="20"
              controls-position="right"
              size="large"
            />
          </div>
        </div>
      </div>

      <div class="practice-deadline">
        <h4>练习时长设置</h4>
        <el-date-picker
          v-model="practiceDeadline"
          type="datetime"
          placeholder="选择练习结束时间"
          value-format="YYYY-MM-DD HH:mm:ss"
          :disabled-date="disabledDate"
        />
      </div>

      <div class="step-actions">
        <el-button size="large" @click="prevStep">上一步</el-button>
        <el-button
          type="primary"
          size="large"
          :disabled="totalQuestions === 0"
          @click="nextStep"
        >
          下一步
        </el-button>
      </div>
    </div>

    <!-- 第四步：生成练习 -->
    <div v-if="currentStep === 3" class="step-content">
      <div class="generation-summary">
        <h2 class="step-title">练习准备完成</h2>
        <div class="summary-card">
          <div class="summary-item">
            <label>选择课程：</label>
            <span>{{ selectedCourse?.title }}</span>
          </div>
          <div class="summary-item">
            <label>题目总数：</label>
            <span>{{ totalQuestions }} 题</span>
          </div>
          <div class="summary-item">
            <label>重点知识点：</label>
            <span>{{ weakestPoints }}</span>
          </div>
          <div class="summary-item">
            <label>练习时长：</label>
            <span>{{ practiceDeadline ? formatDateTime(practiceDeadline) : '不限时' }}</span>
          </div>
        </div>
      </div>

      <div class="step-actions">
        <el-button size="large" @click="prevStep">上一步</el-button>
        <el-button
          type="primary"
          size="large"
          :loading="generating"
          @click="generatePractice"
        >
          {{ generating ? '正在生成练习...' : '开始练习' }}
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  School,
  Document,
  Edit,
  QuestionFilled,
  Clock
} from '@element-plus/icons-vue'
import request from '@/utils/request'

const router = useRouter()

// 数据定义
const currentStep = ref(0)
const coursesLoading = ref(false)
const generating = ref(false)

// 课程相关
const courses = ref([])
const selectedCourse = ref(null)

// 知识点掌握程度
const knowledgePoints = ref([
  { knowledge_point: '物理层', mastery_score: 60 },
  { knowledge_point: '数据链路层', mastery_score: 45 },
  { knowledge_point: '网络层', mastery_score: 70 },
  { knowledge_point: '传输层', mastery_score: 30 },
  { knowledge_point: '应用层', mastery_score: 80 }
])

// 题目设置
const questionSettings = ref([
  { type: '选择', amount: 5 },
  { type: '填空', amount: 3 },
  { type: '简答', amount: 2 }
])

const practiceDeadline = ref('')

// 计算属性
const totalQuestions = computed(() => {
  return questionSettings.value.reduce((total, setting) => total + setting.amount, 0)
})

const weakestPoints = computed(() => {
  const sorted = [...knowledgePoints.value].sort((a, b) => a.mastery_score - b.mastery_score)
  return sorted.slice(0, 3).map(p => p.knowledge_point).join('、')
})

// API调用函数
const api = {
  // 获取学生课程列表
  async getStudentCourses() {
    try {
      coursesLoading.value = true
      const response = await request.get('/student/my_courses')
      courses.value = response.data || []
    } catch (error) {
      console.error('获取课程列表失败:', error)
      ElMessage.error('获取课程列表失败')
      courses.value = []
    } finally {
      coursesLoading.value = false
    }
  },

  // 自动生成练习
  async generateAssignment() {
    try {
      generating.value = true
      
      // 准备请求数据
      const knowledge_points = knowledgePoints.value.map(kp => ({
        knowledge_point: kp.knowledge_point,
        mastery_score: kp.mastery_score / 100 // 转换为0-1范围
      }))

      const question_amount = questionSettings.value.filter(qs => qs.amount > 0)

      const deadline = practiceDeadline.value 
        ? new Date(practiceDeadline.value).toISOString()
        : new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString() // 默认2小时后

      const requestData = {
        course_id: selectedCourse.value.id,
        knowledge_points,
        question_amount,
        title: `智能练习 - ${selectedCourse.value.title}-${Date.now()}`,
        description: `基于掌握程度生成的个性化练习，重点针对：${weakestPoints.value}`,
        deadline
      }

      console.log('生成练习请求数据:', requestData)

      const response = await request.post('/assignment/auto-generate', requestData)
      
      if (response.data && response.data.assignment_id) {
        ElMessage.success('练习生成成功！')
        
        // 保存原始知识点掌握程度到localStorage，供学情分析使用
        localStorage.setItem(`knowledge_points_${response.data.assignment_id}`, JSON.stringify(knowledgePoints.value))
        
        // 跳转到练习界面
        router.push(`/dashboard/student/practice/${response.data.assignment_id}`)
      } else {
        throw new Error('生成练习失败')
      }
    } catch (error) {
      console.error('生成练习失败:', error)
      const errorMsg = error.response?.data?.detail || error.message || '生成练习失败'
      ElMessage.error(errorMsg)
    } finally {
      generating.value = false
    }
  }
}

// 事件处理函数
const selectCourse = (course) => {
  selectedCourse.value = course
}

const nextStep = () => {
  if (currentStep.value < 3) {
    currentStep.value++
  } else {
    generatePractice()
  }
}

const prevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

const generatePractice = async () => {
  await api.generateAssignment()
}

// 工具函数
const formatTooltip = (value) => {
  return `${value}分`
}

const getMasteryLevelClass = (score) => {
  if (score >= 80) return 'mastery-excellent'
  if (score >= 60) return 'mastery-good'
  if (score >= 40) return 'mastery-average'
  return 'mastery-poor'
}

const getMasteryLevelText = (score) => {
  if (score >= 80) return '掌握良好'
  if (score >= 60) return '基本掌握'
  if (score >= 40) return '需要提高'
  return '薄弱环节'
}

const getQuestionTypeIcon = (type) => {
  const iconMap = {
    '选择': QuestionFilled,
    '填空': Edit,
    '简答': Document
  }
  return iconMap[type] || Document
}

const formatDateTime = (dateTime) => {
  return new Date(dateTime).toLocaleString('zh-CN')
}

const disabledDate = (time) => {
  return time.getTime() < Date.now()
}

// 生命周期
onMounted(() => {
  api.getStudentCourses()
})
</script>

<style scoped>
.real-time-practice-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 40px;
}

.page-title {
  font-size: 32px;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 10px;
}

.page-subtitle {
  font-size: 16px;
  color: #7f8c8d;
  margin: 0;
}

.steps-container {
  margin-bottom: 40px;
}

.step-content {
  min-height: 500px;
}

.step-title {
  font-size: 24px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 10px;
  text-align: center;
}

.step-subtitle {
  font-size: 14px;
  color: #7f8c8d;
  text-align: center;
  margin-bottom: 30px;
}

/* 课程选择样式 */
.course-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.course-card {
  border: 2px solid #e1e8ed;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: white;
}

.course-card:hover {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
  transform: translateY(-2px);
}

.course-card.selected {
  border-color: #409eff;
  background: #f0f7ff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
}

.course-content {
  text-align: center;
}

.course-icon {
  margin-bottom: 15px;
  color: #409eff;
}

.course-title {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 8px;
}

.course-teacher {
  font-size: 14px;
  color: #7f8c8d;
  margin-bottom: 20px;
}

/* 知识点掌握程度样式 */
.knowledge-points-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 25px;
  margin-bottom: 40px;
}

.knowledge-point-item {
  background: white;
  border: 1px solid #e1e8ed;
  border-radius: 8px;
  padding: 20px;
}

.point-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.point-name {
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
}

.point-score {
  font-size: 18px;
  font-weight: bold;
  color: #409eff;
}

.point-slider {
  margin-bottom: 10px;
}

.mastery-level {
  text-align: center;
}

.mastery-excellent { color: #67c23a; font-weight: 600; }
.mastery-good { color: #409eff; font-weight: 600; }
.mastery-average { color: #e6a23c; font-weight: 600; }
.mastery-poor { color: #f56c6c; font-weight: 600; }

/* 题目设置样式 */
.question-settings {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.question-type-card {
  background: white;
  border: 1px solid #e1e8ed;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
}

.type-header {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}

.type-icon {
  margin-right: 8px;
  color: #409eff;
}

.type-name {
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
}

.practice-deadline {
  background: white;
  border: 1px solid #e1e8ed;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 40px;
}

.practice-deadline h4 {
  margin-bottom: 15px;
  color: #2c3e50;
}

/* 生成总结样式 */
.generation-summary {
  text-align: center;
}

.summary-card {
  background: white;
  border: 1px solid #e1e8ed;
  border-radius: 8px;
  padding: 30px;
  margin-bottom: 40px;
  display: inline-block;
  text-align: left;
  min-width: 400px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
  padding: 10px 0;
  border-bottom: 1px solid #f5f7fa;
}

.summary-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.summary-item label {
  font-weight: 600;
  color: #606266;
  min-width: 120px;
}

.summary-item span {
  color: #2c3e50;
  text-align: right;
}

/* 步骤操作按钮 */
.step-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 40px;
}

.empty-state {
  grid-column: 1 / -1;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .course-grid {
    grid-template-columns: 1fr;
  }
  
  .knowledge-points-container {
    grid-template-columns: 1fr;
  }
  
  .question-settings {
    grid-template-columns: 1fr;
  }
  
  .summary-card {
    min-width: auto;
    width: 100%;
  }
}
</style> 