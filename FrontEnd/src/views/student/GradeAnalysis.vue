<template>
  <div class="grade-analysis-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">
        <el-icon><TrendCharts /></el-icon>
        成绩查询与分析
      </h1>
      <p class="page-subtitle">查看你的学习成绩趋势和获得个性化学习建议</p>
    </div>

    <!-- 筛选和控制区域 -->
    <el-card class="filter-card">
      <div class="filter-controls">
        <div class="filter-group">
          <label>课程筛选：</label>
          <el-select v-model="selectedCourse" placeholder="选择课程" clearable style="width: 200px;">
            <el-option 
              v-for="course in courses" 
              :key="course.id" 
              :label="course.name" 
              :value="course.id"
            />
          </el-select>
        </div>
        
        <div class="filter-group">
          <label>分析范围：</label>
          <el-select v-model="analysisRange" style="width: 150px;">
            <el-option label="最近7天" :value="7" />
            <el-option label="最近30天" :value="30" />
            <el-option label="最近90天" :value="90" />
          </el-select>
        </div>

        <div class="action-buttons">
          <el-button type="primary" @click="generateAnalysis" :loading="analysisLoading">
            <el-icon><DataAnalysis /></el-icon>
            生成分析报告
          </el-button>
          <el-button @click="refreshData">
            <el-icon><Refresh /></el-icon>
            刷新数据
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 成绩概览 -->
    <div class="overview-section">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon average">
                <el-icon><Trophy /></el-icon>
              </div>
              <div class="stat-text">
                <h3>{{ recentSummary.average_score }}%</h3>
                <p>平均成绩</p>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon highest">
                <el-icon><Star /></el-icon>
              </div>
              <div class="stat-text">
                <h3>{{ recentSummary.highest_score }}%</h3>
                <p>最高成绩</p>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon total">
                <el-icon><Document /></el-icon>
              </div>
              <div class="stat-text">
                <h3>{{ recentSummary.total_assignments }}</h3>
                <p>完成作业</p>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon trend" :class="recentSummary.trend">
                <el-icon v-if="recentSummary.trend === 'improving'"><Top /></el-icon>
                <el-icon v-else-if="recentSummary.trend === 'declining'"><Bottom /></el-icon>
                <el-icon v-else><Minus /></el-icon>
              </div>
              <div class="stat-text">
                <h3>{{ getTrendText(recentSummary.trend) }}</h3>
                <p>成绩趋势</p>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 成绩曲线图 -->
    <el-card class="chart-card">
      <template #header>
        <h2>
          <el-icon><TrendCharts /></el-icon>
          成绩趋势图
        </h2>
      </template>
      <div ref="gradeChartRef" class="grade-chart"></div>
    </el-card>

    <!-- AI分析报告 -->
    <el-card v-if="analysisReport" class="analysis-card">
      <template #header>
        <h2>
          <el-icon><ChatDotRound /></el-icon>
          AI学习分析报告
        </h2>
      </template>
      
      <div class="analysis-content">
        <!-- 总体表现 -->
        <div class="analysis-section">
          <h3>
            <el-icon><Star /></el-icon>
            总体学习表现
          </h3>
          <p class="analysis-text">{{ analysisReport.analysis.overall_performance }}</p>
        </div>

        <!-- 趋势分析 -->
        <div class="analysis-section">
          <h3>
            <el-icon><TrendCharts /></el-icon>
            成绩变化趋势
          </h3>
          <p class="analysis-text">{{ analysisReport.analysis.trend_analysis }}</p>
        </div>

        <!-- 薄弱知识点 -->
        <div class="analysis-section" v-if="analysisReport.analysis.weak_points.length > 0">
          <h3>
            <el-icon><Warning /></el-icon>
            需要重点关注的知识点
          </h3>
          <div class="weak-points">
            <el-tag 
              v-for="point in analysisReport.analysis.weak_points" 
              :key="point"
              type="warning"
              size="large"
              class="weak-point-tag"
            >
              {{ point }}
            </el-tag>
          </div>
        </div>

        <!-- 学习建议 -->
        <div class="analysis-section">
          <h3>
            <el-icon><Guide /></el-icon>
            个性化学习建议
          </h3>
          <div class="suggestions">
            <div 
              v-for="suggestion in analysisReport.analysis.suggestions"
              :key="suggestion.suggestion"
              class="suggestion-item"
              :class="suggestion.priority"
            >
              <div class="priority-badge">
                {{ getPriorityText(suggestion.priority) }}
              </div>
              <p>{{ suggestion.suggestion }}</p>
            </div>
          </div>
        </div>

        <!-- 学习计划 -->
        <div class="analysis-section">
          <h3>
            <el-icon><Calendar /></el-icon>
            学习计划建议
          </h3>
          <p class="analysis-text">{{ analysisReport.analysis.study_plan }}</p>
        </div>
      </div>
    </el-card>

    <!-- 详细成绩列表 -->
    <el-card class="grades-table-card">
      <template #header>
        <div class="table-header">
          <h2>
            <el-icon><Document /></el-icon>
            详细成绩记录
          </h2>
          <el-button @click="exportGrades" size="small">
            <el-icon><Download /></el-icon>
            导出成绩
          </el-button>
        </div>
      </template>

      <el-table 
        :data="allGrades" 
        v-loading="tableLoading"
        @row-click="viewGradeDetail"
        class="grades-table"
      >
        <el-table-column prop="assignment_title" label="作业名称" min-width="200" />
        <el-table-column prop="course_name" label="所属课程" width="150" />
        <el-table-column label="成绩" width="120">
          <template #default="{ row }">
            <span class="score-display">
              {{ row.score }}/{{ row.total_points }}
            </span>
            <div class="percentage">{{ row.percentage }}%</div>
          </template>
        </el-table-column>
        <el-table-column label="等级" width="100">
          <template #default="{ row }">
            <el-tag :type="getGradeType(row.percentage)" size="small">
              {{ getGradeText(row.percentage) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="submit_time" label="提交时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.submit_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button 
              size="small" 
              type="primary" 
              link
              @click.stop="viewGradeDetail(row)"
            >
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50]"
          :total="totalGrades"
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="loadGrades"
          @size-change="loadGrades"
        />
      </div>
    </el-card>

    <!-- 成绩详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="成绩详情"
      width="80%"
      :close-on-click-modal="false"
    >
      <div v-if="gradeDetail" class="grade-detail-content">
        <!-- 基本信息 -->
        <div class="detail-header">
          <h3>{{ gradeDetail.submission_info.assignment_title }}</h3>
          <div class="detail-stats">
            <div class="stat-item">
              <label>总分：</label>
              <span class="score">{{ gradeDetail.submission_info.score }}/{{ gradeDetail.submission_info.total_points }}</span>
            </div>
            <div class="stat-item">
              <label>得分率：</label>
              <span :class="getPercentageClass(gradeDetail.submission_info.percentage)">
                {{ gradeDetail.submission_info.percentage }}%
              </span>
            </div>
            <div class="stat-item">
              <label>提交时间：</label>
              <span>{{ formatDate(gradeDetail.submission_info.submit_time) }}</span>
            </div>
          </div>
        </div>

        <!-- 题目详情 -->
        <div class="questions-detail">
          <h4>答题详情</h4>
          <div 
            v-for="(question, index) in gradeDetail.question_details"
            :key="question.question_id"
            class="question-item"
          >
            <div class="question-header">
              <span class="question-number">第{{ index + 1 }}题</span>
              <span class="question-type">{{ question.question_type }}</span>
              <span class="question-score">
                {{ question.score }}/{{ question.max_points }}分
              </span>
            </div>
            
            <div class="question-content">
              <p><strong>题目：</strong>{{ question.question_content }}</p>
              
              <div v-if="question.options" class="question-options">
                <p><strong>选项：</strong></p>
                <div class="options-list">
                  <div v-for="(option, idx) in question.options" :key="idx">
                    {{ String.fromCharCode(65 + idx) }}. {{ option }}
                  </div>
                </div>
              </div>
              
              <p><strong>你的答案：</strong>
                <span class="student-answer">{{ question.student_answer || '未作答' }}</span>
              </p>
              
              <p><strong>正确答案：</strong>
                <span class="correct-answer">{{ question.correct_answer }}</span>
              </p>
              
              <div v-if="question.feedback" class="feedback">
                <p><strong>评语：</strong></p>
                <div class="feedback-text">{{ question.feedback }}</div>
              </div>
              
              <div v-if="question.key_knowledge" class="knowledge-point">
                <el-tag size="small" type="info">{{ question.key_knowledge }}</el-tag>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import {
  TrendCharts,
  DataAnalysis,
  Refresh,
  Trophy,
  Star,
  Document,
  Top,
  Bottom,
  Minus,
  ChatDotRound,
  Warning,
  Guide,
  Calendar,
  Download
} from '@element-plus/icons-vue'
import request from '@/utils/request'

// 数据定义
const selectedCourse = ref(null)
const analysisRange = ref(30)
const courses = ref([])
const recentSummary = ref({
  total_assignments: 0,
  average_score: 0,
  highest_score: 0,
  lowest_score: 100,
  trend: 'stable'
})

const chartData = ref([])
const allGrades = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const totalGrades = ref(0)
const tableLoading = ref(false)
const analysisLoading = ref(false)
const analysisReport = ref(null)

const gradeChartRef = ref(null)
let gradeChartInstance = null

const detailDialogVisible = ref(false)
const gradeDetail = ref(null)

// 工具函数
const getTrendText = (trend) => {
  const trendMap = {
    'improving': '上升',
    'declining': '下降',
    'stable': '稳定'
  }
  return trendMap[trend] || '稳定'
}

const getPriorityText = (priority) => {
  const priorityMap = {
    'high': '重要',
    'medium': '中等',
    'low': '一般'
  }
  return priorityMap[priority] || '一般'
}

const getGradeType = (percentage) => {
  if (percentage >= 90) return 'success'
  if (percentage >= 80) return 'primary'
  if (percentage >= 70) return 'warning'
  if (percentage >= 60) return 'info'
  return 'danger'
}

const getGradeText = (percentage) => {
  if (percentage >= 90) return '优秀'
  if (percentage >= 80) return '良好'
  if (percentage >= 70) return '中等'
  if (percentage >= 60) return '及格'
  return '不及格'
}

const getPercentageClass = (percentage) => {
  if (percentage >= 80) return 'high-score'
  if (percentage >= 60) return 'medium-score'
  return 'low-score'
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

// 数据加载
const loadRecentScores = async () => {
  try {
    const params = {
      limit: 10,
      course_id: selectedCourse.value
    }
    
    const { data } = await request.get('/assignment/grades/recent', { params })
    chartData.value = data.chart_data
    recentSummary.value = data.summary
    
    await nextTick()
    initGradeChart()
  } catch (error) {
    console.error('加载最近成绩失败:', error)
    ElMessage.error('加载最近成绩失败')
  }
}

const loadGrades = async () => {
  try {
    tableLoading.value = true
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      course_id: selectedCourse.value
    }
    
    const { data } = await request.get('/assignment/grades/my-scores', { params })
    allGrades.value = data.data
    totalGrades.value = data.pagination.total
  } catch (error) {
    console.error('加载成绩列表失败:', error)
    ElMessage.error('加载成绩列表失败')
  } finally {
    tableLoading.value = false
  }
}

const loadCourses = async () => {
  try {
    // 调用真实的学生课程列表接口
    const { data } = await request.get('/student/my_courses')
    courses.value = data.map(course => ({
      id: course.id,
      name: course.title,  // 映射title到name字段以匹配前端使用
      title: course.title
    }))
  } catch (error) {
    console.error('加载课程列表失败:', error)
    ElMessage.error('加载课程列表失败')
    // 如果接口调用失败，使用空数组
    courses.value = []
  }
}

// 图表初始化
const initGradeChart = () => {
  if (!gradeChartRef.value || !chartData.value.length) return
  
  if (gradeChartInstance) {
    gradeChartInstance.dispose()
  }
  
  gradeChartInstance = echarts.init(gradeChartRef.value)
  
  const option = {
    title: {
      text: '成绩趋势',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
        const item = params[0]
        return `${item.name}<br/>成绩：${item.value}%`
      }
    },
    legend: {
      data: ['成绩百分比'],
      top: '10%'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '20%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: chartData.value.map(item => item.submit_time)
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 100,
      axisLabel: {
        formatter: '{value}%'
      }
    },
    series: [
      {
        name: '成绩百分比',
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        itemStyle: {
          color: '#409EFF'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
              { offset: 1, color: 'rgba(64, 158, 255, 0.1)' }
            ]
          }
        },
        data: chartData.value.map(item => item.percentage)
      }
    ]
  }
  
  gradeChartInstance.setOption(option)
}

// AI分析
const generateAnalysis = async () => {
  try {
    analysisLoading.value = true
    
    const requestData = {
      time_range: analysisRange.value,
      include_suggestions: true
    }
    
    const { data } = await request.post('/assignment/grades/analysis', requestData)
    analysisReport.value = data
    
    ElMessage.success('分析报告生成成功！')
  } catch (error) {
    console.error('生成分析报告失败:', error)
    ElMessage.error('生成分析报告失败')
  } finally {
    analysisLoading.value = false
  }
}

// 查看成绩详情
const viewGradeDetail = async (row) => {
  try {
    // 使用现有的student接口获取成绩详情
    const { data } = await request.get(`/student/assignment/${row.assignment_id}/my_result`)
    
    // 转换数据格式以匹配当前的显示结构
    const formattedDetail = {
      submission_info: {
        id: row.submission_id,
        assignment_title: row.assignment_title,
        course_name: row.course_name,
        submit_time: data.submit_time,
        deadline: row.deadline,
        score: row.score,
        total_points: row.total_points,
        percentage: row.percentage
      },
      question_details: []
    }
    
    // 解析反馈数据
    if (data.feedback) {
      try {
        const feedbackData = JSON.parse(data.feedback)
        const answerData = JSON.parse(data.answer || '{}')
        
        formattedDetail.question_details = feedbackData.map((item, index) => ({
          question_id: item.question_id,
          question_content: `第${index + 1}题`, // 简化显示，因为现有接口可能不包含完整题目信息
          question_type: "未知类型",
          student_answer: answerData[item.question_id] || '未作答',
          correct_answer: "查看作业详情获取完整信息",
          score: item.score,
          max_points: item.max_points,
          feedback: item.feedback || "无反馈",
          key_knowledge: null,
          difficulty: null,
          options: null
        }))
      } catch (e) {
        console.error('解析反馈数据失败:', e)
      }
    }
    
    gradeDetail.value = formattedDetail
    detailDialogVisible.value = true
  } catch (error) {
    console.error('加载成绩详情失败:', error)
    ElMessage.error('加载成绩详情失败')
  }
}

// 导出成绩
const exportGrades = () => {
  const csvContent = [
    ['作业名称', '课程', '得分', '总分', '得分率(%)', '提交时间'].join(','),
    ...allGrades.value.map(grade => [
      grade.assignment_title,
      grade.course_name,
      grade.score,
      grade.total_points,
      grade.percentage,
      formatDate(grade.submit_time)
    ].join(','))
  ].join('\n')
  
  const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', `成绩单_${new Date().toLocaleDateString()}.csv`)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  
  ElMessage.success('成绩导出成功！')
}

// 刷新数据
const refreshData = () => {
  loadRecentScores()
  loadGrades()
  ElMessage.success('数据已刷新')
}

// 监听筛选变化
watch([selectedCourse], () => {
  loadRecentScores()
  loadGrades()
})

// 组件挂载
onMounted(() => {
  loadCourses()
  loadRecentScores()
  loadGrades()
  
  // 监听窗口大小变化
  window.addEventListener('resize', () => {
    if (gradeChartInstance) {
      gradeChartInstance.resize()
    }
  })
})
</script>

<style scoped>
.grade-analysis-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-title {
  font-size: 28px;
  color: #2c3e50;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.page-subtitle {
  color: #7f8c8d;
  font-size: 16px;
  margin: 0;
}

.filter-card {
  margin-bottom: 20px;
}

.filter-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 20px;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-group label {
  font-weight: 500;
  color: #606266;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.overview-section {
  margin-bottom: 20px;
}

.stat-card {
  height: 100px;
}

.stat-content {
  display: flex;
  align-items: center;
  height: 100%;
  padding: 10px;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  font-size: 24px;
  color: white;
}

.stat-icon.average {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-icon.highest {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.total {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-icon.trend {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-icon.trend.improving {
  background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%);
}

.stat-icon.trend.declining {
  background: linear-gradient(135deg, #ff6b6b 0%, #ffa8a8 100%);
}

.stat-text h3 {
  margin: 0;
  font-size: 24px;
  font-weight: bold;
  color: #2c3e50;
}

.stat-text p {
  margin: 5px 0 0 0;
  color: #7f8c8d;
  font-size: 14px;
}

.chart-card {
  margin-bottom: 20px;
}

.grade-chart {
  width: 100%;
  height: 400px;
}

.analysis-card {
  margin-bottom: 20px;
}

.analysis-content {
  padding: 20px 0;
}

.analysis-section {
  margin-bottom: 30px;
}

.analysis-section h3 {
  color: #2c3e50;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.analysis-text {
  color: #606266;
  line-height: 1.6;
  margin-bottom: 15px;
}

.weak-points {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.weak-point-tag {
  margin-right: 8px;
  margin-bottom: 8px;
}

.suggestions {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.suggestion-item {
  padding: 15px;
  border-radius: 8px;
  border-left: 4px solid #409EFF;
  background: #f8faff;
  position: relative;
}

.suggestion-item.high {
  border-left-color: #f56c6c;
  background: #fef0f0;
}

.suggestion-item.medium {
  border-left-color: #e6a23c;
  background: #fdf6ec;
}

.suggestion-item.low {
  border-left-color: #67c23a;
  background: #f0f9ff;
}

.priority-badge {
  position: absolute;
  top: -8px;
  right: 15px;
  background: #409EFF;
  color: white;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
}

.suggestion-item.high .priority-badge {
  background: #f56c6c;
}

.suggestion-item.medium .priority-badge {
  background: #e6a23c;
}

.suggestion-item.low .priority-badge {
  background: #67c23a;
}

.suggestion-item p {
  margin: 0;
  color: #606266;
  line-height: 1.5;
}

.grades-table-card {
  margin-bottom: 20px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.table-header h2 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.grades-table .score-display {
  font-weight: bold;
  color: #2c3e50;
}

.grades-table .percentage {
  font-size: 12px;
  color: #909399;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.grade-detail-content {
  max-height: 70vh;
  overflow-y: auto;
}

.detail-header {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
}

.detail-header h3 {
  margin: 0 0 15px 0;
  color: #2c3e50;
  font-size: 20px;
}

.detail-stats {
  display: flex;
  gap: 30px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stat-item label {
  color: #909399;
  font-weight: 500;
}

.stat-item .score {
  font-weight: bold;
  color: #2c3e50;
}

.high-score {
  color: #67c23a;
  font-weight: bold;
}

.medium-score {
  color: #e6a23c;
  font-weight: bold;
}

.low-score {
  color: #f56c6c;
  font-weight: bold;
}

.questions-detail h4 {
  color: #2c3e50;
  margin-bottom: 20px;
}

.question-item {
  margin-bottom: 25px;
  padding: 20px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  background: #fafafa;
}

.question-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e4e7ed;
}

.question-number {
  background: #409EFF;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}

.question-type {
  background: #e4e7ed;
  color: #606266;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.question-score {
  background: #67c23a;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}

.question-content p {
  margin: 10px 0;
  line-height: 1.5;
}

.question-options {
  margin: 15px 0;
}

.options-list {
  margin-left: 20px;
  margin-top: 5px;
}

.options-list div {
  margin-bottom: 5px;
  color: #606266;
}

.student-answer {
  color: #409EFF;
  font-weight: 500;
  background: #ecf5ff;
  padding: 2px 6px;
  border-radius: 4px;
}

.correct-answer {
  color: #67c23a;
  font-weight: 500;
  background: #f0f9ff;
  padding: 2px 6px;
  border-radius: 4px;
}

.feedback {
  margin-top: 15px;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 4px;
  border-left: 4px solid #409EFF;
}

.feedback-text {
  color: #606266;
  line-height: 1.5;
}

.knowledge-point {
  margin-top: 10px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .filter-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .action-buttons {
    justify-content: center;
  }
  
  .detail-stats {
    flex-direction: column;
    gap: 10px;
  }
  
  .grade-chart {
    height: 300px;
  }
}
</style> 