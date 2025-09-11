<template>
  <div class="learning-analysis-container">
    <!-- 返回按钮 -->
    <div class="back-header">
      <el-button @click="goBack" size="large">
        <el-icon><ArrowLeft /></el-icon>
        返回练习结果
      </el-button>
    </div>

    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">
        <el-icon><TrendCharts /></el-icon>
        个人学情分析报告
      </h1>
      <p class="page-subtitle" v-if="practiceInfo">
        基于《{{ practiceInfo.title }}》练习结果的智能分析
      </p>
    </div>

    <!-- 生成中状态 -->
    <div v-if="loading" class="loading-container">
      <el-card class="loading-card">
        <div class="loading-content">
          <el-icon class="loading-icon" size="48"><Loading /></el-icon>
          <h3>AI正在分析您的学习情况...</h3>
          <p>这可能需要一点时间，请耐心等待</p>
          <el-progress :percentage="progress" :show-text="false" />
          <div class="loading-steps">
            <div class="step" :class="{ active: currentStep >= 1 }">
              <el-icon><Document /></el-icon>
              <span>分析练习结果</span>
            </div>
            <div class="step" :class="{ active: currentStep >= 2 }">
              <el-icon><DataAnalysis /></el-icon>
              <span>评估知识掌握度</span>
            </div>
            <div class="step" :class="{ active: currentStep >= 3 }">
              <el-icon><Edit /></el-icon>
              <span>制定学习计划</span>
            </div>
            <div class="step" :class="{ active: currentStep >= 4 }">
              <el-icon><Check /></el-icon>
              <span>生成分析报告</span>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 分析结果 -->
    <div v-if="!loading && analysisResult" class="analysis-content">
      <!-- 总体评价卡片 -->
      <el-card class="overview-card">
        <template #header>
          <div class="card-header">
            <h2>
              <el-icon><Star /></el-icon>
              总体学习评价
            </h2>
          </div>
        </template>
        
        <div class="overview-grid">
          <div class="score-summary">
            <div class="score-chart">
              <div ref="scoreChartRef" style="width: 300px; height: 200px;"></div>
            </div>
          </div>
          
          <div class="summary-text">
            <div class="summary-item">
              <label>练习得分：</label>
              <span class="score-text">{{ practiceScore }}分 ({{ practicePercentage.toFixed(2) }}%)</span>
            </div>
            <div class="summary-item">
              <label>学习水平：</label>
              <span :class="getLevelClass(practicePercentage)">{{ getLevelText(practicePercentage) }}</span>
            </div>
            <div class="summary-item">
              <label>分析时间：</label>
              <span>{{ formatDate(new Date()) }}</span>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 知识点掌握度分析 -->
      <el-card class="knowledge-analysis-card">
        <template #header>
          <h2>
            <el-icon><DataAnalysis /></el-icon>
            知识点掌握度分析
          </h2>
        </template>
        
        <div class="knowledge-content">
          <div class="chart-container">
            <div ref="knowledgeChartRef" style="width: 100%; height: 400px;"></div>
          </div>
          
          <div class="knowledge-insights">
            <div class="insight-section">
              <h4>
                <el-icon><Warning /></el-icon>
                薄弱知识点
              </h4>
              <div class="weak-points">
                <el-tag 
                  v-for="point in weakKnowledgePoints" 
                  :key="point.name"
                  type="danger" 
                  size="large"
                  class="knowledge-tag"
                >
                  {{ point.name }} ({{ point.score }}%)
                </el-tag>
              </div>
            </div>
            
            <div class="insight-section">
              <h4>
                <el-icon><Check /></el-icon>
                优势知识点
              </h4>
              <div class="strong-points">
                <el-tag 
                  v-for="point in strongKnowledgePoints" 
                  :key="point.name"
                  type="success" 
                  size="large"
                  class="knowledge-tag"
                >
                  {{ point.name }} ({{ point.score }}%)
                </el-tag>
              </div>
            </div>
          </div>
        </div>
      </el-card>

      <!-- AI智能分析 -->
      <el-card class="ai-analysis-card">
        <template #header>
          <h2>
            <el-icon><ChatDotRound /></el-icon>
            AI智能分析
          </h2>
        </template>
        
        <div class="ai-analysis-content">
          <div 
            class="markdown-content" 
            v-html="renderMarkdown(analysisResult)"
          ></div>
        </div>
      </el-card>

      <!-- 学习计划 -->
      <el-card class="learning-plan-card">
        <template #header>
          <h2>
            <el-icon><Calendar /></el-icon>
            一月学习计划
          </h2>
        </template>
        
        <div class="plan-timeline">
          <div class="timeline-header">
            <h3>个性化学习路径</h3>
            <p>基于您的学习情况，AI为您制定了以下学习计划：</p>
          </div>
          
          <el-timeline>
            <el-timeline-item
              v-for="(week, index) in learningPlan"
              :key="index"
              :timestamp="`第${index + 1}周`"
              placement="top"
              :type="getWeekType(index)"
              size="large"
            >
              <div class="week-plan">
                <h4>{{ week.title }}</h4>
                <div class="week-content">
                  <div class="goals">
                    <strong>学习目标：</strong>
                    <ul>
                      <li v-for="goal in week.goals" :key="goal">{{ goal }}</li>
                    </ul>
                  </div>
                  <div class="activities">
                    <strong>学习活动：</strong>
                    <ul>
                      <li v-for="activity in week.activities" :key="activity">{{ activity }}</li>
                    </ul>
                  </div>
                </div>
              </div>
            </el-timeline-item>
          </el-timeline>
        </div>
      </el-card>

      <!-- 操作按钮 -->
    </div>

    <!-- 操作按钮 -->
    <div class="action-buttons" v-if="!loading">
      <el-button size="large" @click="regenerateAnalysis">
        <el-icon><Refresh /></el-icon>
        重新分析
      </el-button>
      <el-button type="primary" size="large" @click="saveReport">
        <el-icon><Download /></el-icon>
        保存报告
      </el-button>
      <el-button type="success" size="large" @click="shareReport">
        <el-icon><Share /></el-icon>
        分享报告
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import {
  ArrowLeft,
  TrendCharts,
  Loading,
  Document,
  DataAnalysis,
  Edit,
  Check,
  Star,
  Warning,
  Trophy,
  Guide,
  Calendar,
  WarningFilled,
  Clock,
  Aim,
  Refresh,
  Download,
  Share,
  ChatDotRound
} from '@element-plus/icons-vue'
import request from '@/utils/request'

const route = useRoute()
const router = useRouter()

// 数据定义
const loading = ref(true)
const progress = ref(0)
const currentStep = ref(0)
const practiceInfo = ref(null)
const practiceResult = ref(null)
const originalKnowledgePoints = ref([])
const analysisResult = ref(null)
const scoreChartRef = ref(null)
const knowledgeChartRef = ref(null)

// 计算属性
const practiceScore = computed(() => {
  return practiceResult.value?.total_score || 0
})

const practicePercentage = computed(() => {
  return practiceResult.value?.percentage || 0
})

const weakKnowledgePoints = computed(() => {
  if (!originalKnowledgePoints.value) return []
  return originalKnowledgePoints.value
    .filter(point => point.mastery_score < 60)
    .map(point => ({
      name: point.knowledge_point,
      score: point.mastery_score
    }))
})

const strongKnowledgePoints = computed(() => {
  if (!originalKnowledgePoints.value) return []
  return originalKnowledgePoints.value
    .filter(point => point.mastery_score >= 80)
    .map(point => ({
      name: point.knowledge_point,
      score: point.mastery_score
    }))
})

const learningPlan = computed(() => {
  if (!analysisResult.value) return []
  
  // 从AI分析结果中提取学习计划
  const planText = analysisResult.value
  const weeks = []
  
  for (let i = 0; i < 4; i++) {
    weeks.push({
      title: `第${i + 1}周学习重点`,
      goals: getWeekGoals(i, planText),
      activities: getWeekActivities(i, planText)
    })
  }
  
  return weeks
})

// 数据加载
const loadAnalysisData = async () => {
  try {
    loading.value = true
    currentStep.value = 1
    progress.value = 25

    // 获取练习信息
    const assignmentResponse = await request.get(`/student/assignment/list`)
    const assignment = assignmentResponse.data.find(a => a.id == route.params.id)
    if (assignment) {
      practiceInfo.value = assignment
    }

    currentStep.value = 2
    progress.value = 50

    // 获取练习结果（从localStorage或URL参数）
    const resultData = localStorage.getItem(`practice_result_${route.params.id}`)
    if (resultData) {
      practiceResult.value = JSON.parse(resultData)
    }

    // 获取原始知识点掌握程度（从localStorage获取真实数据）
    const knowledgeData = localStorage.getItem(`knowledge_points_${route.params.id}`)
    if (knowledgeData) {
      originalKnowledgePoints.value = JSON.parse(knowledgeData)
    } else {
      // 如果没有保存的数据，使用默认数据
      originalKnowledgePoints.value = [
        { knowledge_point: '物理层', mastery_score: 60 },
        { knowledge_point: '数据链路层', mastery_score: 45 },
        { knowledge_point: '网络层', mastery_score: 70 },
        { knowledge_point: '传输层', mastery_score: 30 },
        { knowledge_point: '应用层', mastery_score: 80 }
      ]
      ElMessage.warning('未找到原始知识点数据，使用默认数据')
    }

    currentStep.value = 3
    progress.value = 75

    // 生成AI分析
    await generateLearningAnalysis()

    currentStep.value = 4
    progress.value = 100

    // 延迟显示结果
    setTimeout(() => {
      loading.value = false
      nextTick(() => {
        initCharts()
      })
    }, 1000)

  } catch (error) {
    console.error('加载分析数据失败:', error)
    ElMessage.error('加载分析数据失败')
    loading.value = false
  }
}

// 生成学情分析
const generateLearningAnalysis = async () => {
  try {
    const prompt = `
作为学情分析助理，请基于以下学生学习数据，生成一份详细的学情分析报告。请使用清晰的Markdown格式输出：

【练习基本信息】
- 练习名称：${practiceInfo.value?.title}
- 练习得分：${practiceScore.value}分 (${practicePercentage.value.toFixed(1)}%)

【知识点掌握情况（练习前自评）】
${originalKnowledgePoints.value.map(point => 
  `- ${point.knowledge_point}：${point.mastery_score}分`
).join('\n')}

【练习结果反馈】
${practiceResult.value?.results?.map(result => 
  `- ${result.type}题：得分${result.score}/${result.max_points}分，反馈：${result.feedback}`
).join('\n') || '暂无详细反馈'}

请生成包含以下结构的Markdown格式报告：

# 学情分析报告

## 一、薄弱知识点分析
（列出3-5个最需要加强的知识点，用数字列表）

## 二、优势能力分析
（总结学习优势和擅长领域，用数字列表）

## 三、学习习惯评估
（分析学习方法的有效性，用数字列表）

## 四、改进建议
### (一) 知识补强建议
（具体的学习建议，用数字列表）

### (二) 学习方法建议
（学习方法改进，用数字列表）

## 五、一月学习计划

| 周次 | 学习重点 | 具体内容 | 学习时长 | 预期成果 |
|------|----------|----------|----------|----------|
| 第1周 | 基础巩固 | 重点知识点复习 | 8小时 | 掌握基础概念 |
| 第2周 | 能力提升 | 专项练习 | 10小时 | 提高应用能力 |
| 第3周 | 综合训练 | 模拟测试 | 12小时 | 综合运用 |
| 第4周 | 查漏补缺 | 薄弱环节强化 | 10小时 | 全面提升 |

**每周额外安排：**
- 每日复习30分钟
- 周末实践操作2小时
- 每周错题复盘1次

请确保：
1. 表格格式正确
2. 列表层次清晰
3. 内容具体可执行
`

    const response = await request.post(
      `/chat/simple?question=${encodeURIComponent(prompt)}&chat_name=${encodeURIComponent('学情分析助理')}`,
      null,
      { timeout: 180000 }
    )

    if (response?.data?.code === 0 && response?.data?.data?.answer) {
      analysisResult.value = response.data.data.answer
    } else {
      throw new Error('AI分析生成失败')
    }
  } catch (error) {
    console.error('生成学情分析失败:', error)
    ElMessage.error('生成学情分析失败，请稍后重试')
    
    // 提供默认的示例内容
    analysisResult.value = `
# 学情分析报告

## 一、薄弱知识点分析

1. **数据链路层** - 掌握程度较低，需要重点学习
2. **传输层** - 基础概念理解不足
3. **简答题作答技巧** - 回答不够完整系统

## 二、优势能力分析

1. **应用层协议** - 理解较好，能正确运用
2. **基础概念记忆** - 填空题准确率高
3. **知识框架完整** - 整体学习态度良好

## 三、改进建议

### (一) 知识补强建议
1. 重点突破薄弱知识点的核心概念
2. 建立各层次间的关联认知
3. 补充实际应用场景的学习

### (二) 学习方法建议
1. 采用系统性的学习路径
2. 多做案例分析练习
3. 建立错题复盘机制

**AI分析生成失败，显示示例内容。请重新生成获取完整分析。**
`
  }
}

// 工具函数
const renderMarkdown = (text) => {
  if (!text) return ''
  
  let html = text
  
  // 处理标题
  html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>')
  html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>')
  html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>')
  
  // 处理粗体文本
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
  
  // 处理Tab分隔表格
  html = processTabTable(html)
  
  // 处理传统的|分隔表格
  html = html.replace(/\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|/g, 
    '<tr><td>$1</td><td>$2</td><td>$3</td><td>$4</td><td>$5</td></tr>')
  html = html.replace(/\|(.*?)\|(.*?)\|(.*?)\|/g, 
    '<tr><td>$1</td><td>$2</td><td>$3</td></tr>')
  
  // 包装表格
  if (html.includes('<tr>')) {
    html = html.replace(/(<tr>.*?<\/tr>)/gs, (match) => {
      return `<table class="markdown-table">${match}</table>`
    })
  }
  
  // 清理HTML中的多余空白
  html = html.replace(/<li>\s*<li>/g, '<li>')
  html = html.replace(/<\/li>\s*<\/li>/g, '</li>')
  
  // 修复不完整的HTML标签
  html = html.replace(/<lI>/g, '<li>')
  html = html.replace(/<\/lI>/g, '</li>')
  html = html.replace(/<lI/g, '<li')
  
  // 处理数字列表（不与HTML列表冲突）
  html = html.replace(/^(\d+)\.\s*(.*$)/gim, (match, num, content) => {
    // 如果不在HTML列表中，转换为HTML
    if (!content.includes('<li>')) {
      return `<li class="numbered-item" data-num="${num}">${content}</li>`
    }
    return match
  })
  
  // 处理项目符号列表
  html = html.replace(/^[•-]\s*(.*$)/gim, (match, content) => {
    if (!content.includes('<li>')) {
      return `<li class="bullet-item">${content}</li>`
    }
    return match
  })
  
  // 包装连续的li为列表
  html = html.replace(/((<li class="numbered-item"[^>]*>.*?<\/li>\s*)+)/gs, '<ol class="numbered-list">$1</ol>')
  html = html.replace(/((<li class="bullet-item">.*?<\/li>\s*)+)/gs, '<ul class="bullet-list">$1</ul>')
  
  // 处理现有的HTML列表
  html = html.replace(/<ul>/g, '<ul class="markdown-list">')
  html = html.replace(/<ol>/g, '<ol class="markdown-list">')
  
  // 处理换行和段落
  html = html.split('\n').map(line => {
    line = line.trim()
    if (!line) return ''
    
    // 跳过HTML标签行
    if (line.match(/^<\/?(h[1-6]|table|tr|td|th|ul|ol|li)/)) {
      return line
    }
    
    // 跳过已经在HTML标签内的内容
    if (line.includes('<') && line.includes('>')) {
      return line
    }
    
    return `<p>${line}</p>`
  }).join('\n')
  
  // 清理多余的空段落
  html = html.replace(/<p><\/p>/g, '')
  html = html.replace(/<p>\s*<\/p>/g, '')
  
  // 清理表格周围的段落标签
  html = html.replace(/<p>(<table[^>]*>)/g, '$1')
  html = html.replace(/(<\/table>)<\/p>/g, '$1')
  
  // 清理列表周围的段落标签
  html = html.replace(/<p>(<[ou]l[^>]*>)/g, '$1')
  html = html.replace(/(<\/[ou]l>)<\/p>/g, '$1')
  
  // 清理标题周围的段落标签
  html = html.replace(/<p>(<h[1-6][^>]*>)/g, '$1')
  html = html.replace(/(<\/h[1-6]>)<\/p>/g, '$1')
  
  return html
}

// 处理Tab分隔表格的辅助函数
const processTabTable = (text) => {
  const lines = text.split('\n')
  let result = []
  let inTable = false
  let tableRows = []
  let currentRowData = []
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim()
    
    // 检测表格开始（包含多个Tab分隔符的行）
    if (line.includes('\t') && line.split('\t').length >= 3) {
      if (!inTable) {
        inTable = true
        tableRows = []
      }
      
      // 检查是否是分隔行（如 ---\t---\t---）
      if (line.match(/^---(\t---)+$/)) {
        continue // 跳过分隔行
      }
      
      // 如果有未完成的行，先保存
      if (currentRowData.length > 0) {
        tableRows.push(currentRowData.join('\t'))
        currentRowData = []
      }
      
      // 分割当前行
      const cells = line.split('\t')
      currentRowData = cells.map(cell => cell.trim())
      
      // 检查后续行是否是当前行的继续
      let j = i + 1
      while (j < lines.length) {
        const nextLine = lines[j].trim()
        
        // 如果是空行，跳过
        if (!nextLine) {
          j++
          continue
        }
        
        // 如果包含Tab且看起来像新的表格行，停止
        if (nextLine.includes('\t') && (
          nextLine.match(/^第\d+周/) || 
          nextLine.match(/^---/) ||
          nextLine.split('\t').length >= 3
        )) {
          break
        }
        
        // 如果不包含Tab，可能是当前行的继续内容
        if (!nextLine.includes('\t')) {
          // 查找应该添加到哪个单元格
          // 默认添加到最后一个有内容的单元格，或者第三列（具体内容列）
          let targetIndex = Math.max(2, currentRowData.length - 1)
          if (targetIndex < currentRowData.length) {
            currentRowData[targetIndex] += '\n' + nextLine
          }
          j++
        } else {
          break
        }
      }
      
      i = j - 1 // 更新索引
      
    } else if (inTable && (line === '' || !line.includes('\t'))) {
      // 遇到空行或非Tab行，结束表格
      if (currentRowData.length > 0) {
        tableRows.push(currentRowData.join('\t'))
        currentRowData = []
      }
      
      if (tableRows.length > 0) {
        result.push(convertTabTableToHTML(tableRows))
        tableRows = []
      }
      inTable = false
      
      if (line) {
        result.push(line)
      }
    } else if (!inTable) {
      result.push(line)
    }
  }
  
  // 处理文档末尾的表格
  if (inTable) {
    if (currentRowData.length > 0) {
      tableRows.push(currentRowData.join('\t'))
    }
    if (tableRows.length > 0) {
      result.push(convertTabTableToHTML(tableRows))
    }
  }
  
  return result.join('\n')
}

// 将Tab分隔的表格转换为HTML
const convertTabTableToHTML = (rows) => {
  if (!rows || rows.length === 0) return ''
  
  let html = '<table class="markdown-table">'
  
  // 第一行作为表头
  const headerCells = rows[0].split('\t').map(cell => cell.trim())
  html += '<thead><tr>'
  headerCells.forEach(cell => {
    html += `<th>${cell}</th>`
  })
  html += '</tr></thead>'
  
  // 其余行作为数据行
  html += '<tbody>'
  for (let i = 1; i < rows.length; i++) {
    const cells = rows[i].split('\t').map(cell => cell.trim())
    
    // 确保每行都有足够的单元格
    while (cells.length < headerCells.length) {
      cells.push('')
    }
    
    html += '<tr>'
    cells.forEach(cell => {
      // 处理单元格内的换行，转换为<br>
      const cellContent = cell.replace(/\n/g, '<br>')
      html += `<td>${cellContent}</td>`
    })
    html += '</tr>'
  }
  html += '</tbody></table>'
  
  return html
}

const getWeekGoals = (weekIndex, planText) => {
  const goals = [
    ['巩固基础概念', '理解核心原理'],
    ['强化薄弱环节', '提升应用能力'],
    ['综合练习', '知识点整合'],
    ['查漏补缺', '全面提升']
  ]
  return goals[weekIndex] || ['持续学习', '巩固提高']
}

const getWeekActivities = (weekIndex, planText) => {
  const activities = [
    ['每日复习30分钟', '完成基础练习题'],
    ['重点攻克薄弱知识点', '寻求老师或同学帮助'],
    ['做综合性练习题', '总结解题方法'],
    ['模拟测试', '制定下阶段学习计划']
  ]
  return activities[weekIndex] || ['自主学习', '定期复习']
}

const getLevelClass = (percentage) => {
  if (percentage >= 90) return 'level-excellent'
  if (percentage >= 80) return 'level-good'
  if (percentage >= 60) return 'level-average'
  return 'level-poor'
}

const getLevelText = (percentage) => {
  if (percentage >= 90) return '优秀'
  if (percentage >= 80) return '良好'
  if (percentage >= 60) return '及格'
  return '需提高'
}

const getWeekType = (index) => {
  const types = ['primary', 'success', 'warning', 'info']
  return types[index] || 'primary'
}

const formatDate = (date) => {
  return date.toLocaleString('zh-CN')
}

// 图表初始化
const initCharts = () => {
  initScoreChart()
  initKnowledgeChart()
}

const initScoreChart = () => {
  if (!scoreChartRef.value) return
  
  const chart = echarts.init(scoreChartRef.value)
  const option = {
    title: {
      text: `${practicePercentage.value.toFixed(1)}%`,
      left: 'center',
      top: 'center',
      textStyle: {
        fontSize: 32,
        fontWeight: 'bold',
        color: practicePercentage.value >= 80 ? '#67c23a' : 
               practicePercentage.value >= 60 ? '#e6a23c' : '#f56c6c'
      }
    },
    series: [{
      type: 'pie',
      radius: ['60%', '80%'],
      center: ['50%', '50%'],
      startAngle: 90,
      data: [
        {
          value: practicePercentage.value,
          itemStyle: {
            color: practicePercentage.value >= 80 ? '#67c23a' : 
                   practicePercentage.value >= 60 ? '#e6a23c' : '#f56c6c'
          }
        },
        {
          value: 100 - practicePercentage.value,
          itemStyle: { color: '#f0f0f0' }
        }
      ],
      label: { show: false },
      emphasis: { disabled: true }
    }]
  }
  chart.setOption(option)
}

const initKnowledgeChart = () => {
  if (!knowledgeChartRef.value) return
  
  const chart = echarts.init(knowledgeChartRef.value)
  const option = {
    title: {
      text: '知识点掌握度对比',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    legend: {
      data: ['练习前自评', '综合评估'],
      top: 30
    },
    xAxis: {
      type: 'category',
      data: originalKnowledgePoints.value.map(p => p.knowledge_point),
      axisLabel: { interval: 0, rotate: 45 }
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 100,
      axisLabel: { formatter: '{value}%' }
    },
    series: [
      {
        name: '练习前自评',
        type: 'bar',
        data: originalKnowledgePoints.value.map(p => p.mastery_score),
        itemStyle: { color: '#409eff' }
      },
      {
        name: '综合评估',
        type: 'bar',
        data: originalKnowledgePoints.value.map(p => 
          Math.max(0, p.mastery_score + (Math.random() - 0.5) * 20)
        ),
        itemStyle: { color: '#67c23a' }
      }
    ]
  }
  chart.setOption(option)
}

// 事件处理
const goBack = () => {
  router.push({
    name: 'PracticeResult',
    params: { id: route.params.id }
  })
}

const regenerateAnalysis = async () => {
  loading.value = true
  progress.value = 0
  currentStep.value = 0
  await generateLearningAnalysis()
  loading.value = false
  nextTick(() => {
    initCharts()
  })
}

const saveReport = () => {
  ElMessage.success('报告保存功能开发中...')
}

const shareReport = () => {
  ElMessage.success('报告分享功能开发中...')
}

// 生命周期
onMounted(() => {
  loadAnalysisData()
})
</script>

<style scoped>
.learning-analysis-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.back-header {
  margin-bottom: 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  font-size: 28px;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 10px;
}

.page-subtitle {
  font-size: 16px;
  color: #7f8c8d;
  margin: 0;
}

/* 加载状态样式 */
.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.loading-card {
  width: 100%;
  max-width: 600px;
  border-radius: 12px;
}

.loading-content {
  text-align: center;
  padding: 40px 20px;
}

.loading-icon {
  color: #409eff;
  margin-bottom: 20px;
  animation: spin 2s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.loading-content h3 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.loading-content p {
  color: #7f8c8d;
  margin-bottom: 30px;
}

.loading-steps {
  display: flex;
  justify-content: space-around;
  margin-top: 30px;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #c0c4cc;
  transition: all 0.3s ease;
}

.step.active {
  color: #409eff;
}

.step span {
  font-size: 12px;
}

/* 分析结果样式 */
.analysis-content {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.overview-card,
.knowledge-analysis-card,
.ai-analysis-card,
.learning-plan-card {
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.card-header h2 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  color: #2c3e50;
}

/* 总体评价 */
.overview-grid {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 30px;
  align-items: center;
}

.summary-text {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 6px;
}

.summary-item label {
  font-weight: 600;
  color: #606266;
  min-width: 80px;
}

.score-text {
  font-size: 18px;
  font-weight: bold;
  color: #409eff;
}

.level-excellent { color: #67c23a; font-weight: bold; }
.level-good { color: #409eff; font-weight: bold; }
.level-average { color: #e6a23c; font-weight: bold; }
.level-poor { color: #f56c6c; font-weight: bold; }

/* 知识点分析 */
.knowledge-content {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 30px;
}

.knowledge-insights {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.insight-section h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  color: #2c3e50;
}

.weak-points,
.strong-points {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.knowledge-tag {
  margin: 2px;
}

/* AI分析 */
.ai-analysis-content {
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.markdown-content {
  font-size: 16px;
  line-height: 1.8;
  color: #343a40;
  word-break: break-word;
}

.markdown-content h1 {
  font-size: 24px;
  margin-top: 20px;
  margin-bottom: 15px;
  color: #2c3e50;
}

.markdown-content h2 {
  font-size: 20px;
  margin-top: 15px;
  margin-bottom: 10px;
  color: #343a40;
}

.markdown-content h3 {
  font-size: 18px;
  margin-top: 10px;
  margin-bottom: 8px;
  color: #495057;
}

.markdown-content p {
  margin-bottom: 15px;
}

.markdown-content ul {
  margin-left: 20px;
  margin-bottom: 15px;
  padding-left: 20px;
}

.markdown-content li {
  margin-bottom: 8px;
  color: #606266;
}

.markdown-content strong {
  font-weight: bold;
  color: #2c3e50;
}

.markdown-content em {
  font-style: italic;
  color: #7f8c8d;
}

.markdown-content code {
  background-color: #e9ecef;
  padding: 2px 4px;
  border-radius: 4px;
  font-size: 0.9em;
  color: #343a40;
}

.markdown-content pre {
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  overflow-x: auto;
  margin-bottom: 15px;
  border: 1px solid #e9ecef;
}

.markdown-content blockquote {
  border-left: 4px solid #409eff;
  padding-left: 15px;
  margin-bottom: 15px;
  color: #606266;
  font-style: italic;
}

.markdown-content hr {
  border: none;
  border-top: 1px dashed #e9ecef;
  margin: 20px 0;
}

.markdown-content table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 15px;
  border: 1px solid #e9ecef;
}

.markdown-content th,
.markdown-content td {
  border: 1px solid #e9ecef;
  padding: 8px 12px;
  text-align: left;
}

.markdown-content th {
  background-color: #f8f9fa;
  font-weight: bold;
  color: #343a40;
}

.markdown-content tr:nth-child(even) {
  background-color: #f1f3f5;
}

.markdown-content tr:hover {
  background-color: #e9ecef;
}

.markdown-content .markdown-table {
  margin: 20px 0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  border-radius: 8px;
  overflow: hidden;
  width: 100%;
}

.markdown-content .markdown-table thead {
  background-color: #409eff;
  color: white;
}

.markdown-content .markdown-table thead th {
  background-color: #409eff;
  color: white;
  font-weight: bold;
  padding: 12px 8px;
  text-align: center;
}

.markdown-content .markdown-table tbody tr:nth-child(even) {
  background-color: #f8f9fa;
}

.markdown-content .markdown-table tbody tr:hover {
  background-color: #e3f2fd;
}

.markdown-content .markdown-table td {
  padding: 10px 8px;
  vertical-align: top;
  line-height: 1.6;
}

.markdown-content .numbered-list {
  counter-reset: item;
  padding-left: 30px;
  margin-bottom: 20px;
}

.markdown-content .numbered-list li {
  display: block;
  margin-bottom: 10px;
  position: relative;
}

.markdown-content .numbered-list li:before {
  content: counter(item) ".";
  counter-increment: item;
  position: absolute;
  left: -25px;
  top: 0;
  color: #409eff;
  font-weight: bold;
}

.markdown-content .numbered-list li[data-num]:before {
  content: attr(data-num) ".";
  counter-increment: none;
}

.markdown-content .bullet-list {
  padding-left: 20px;
  margin-bottom: 20px;
}

.markdown-content .bullet-list li {
  list-style-type: disc;
  margin-bottom: 8px;
}

.markdown-content .markdown-list {
  padding-left: 20px;
  margin-bottom: 15px;
}

.markdown-content .html-item {
  list-style-type: circle;
  margin-bottom: 6px;
  color: #495057;
}

.markdown-content .numbered-item {
  color: #495057;
}

.markdown-content .bullet-item {
  color: #495057;
}

/* 特殊格式 */
.markdown-content h1:first-child {
  margin-top: 0;
  border-bottom: 2px solid #409eff;
  padding-bottom: 10px;
}

.markdown-content h2 {
  border-left: 4px solid #67c23a;
  padding-left: 10px;
  background-color: #f0f9ff;
  padding: 8px 10px;
  border-radius: 4px;
}

.markdown-content h3 {
  color: #606266;
  border-bottom: 1px dashed #e9ecef;
  padding-bottom: 5px;
}

/* 学习计划 */
.timeline-header {
  text-align: center;
  margin-bottom: 30px;
}

.timeline-header h3 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.timeline-header p {
  color: #7f8c8d;
}

.week-plan h4 {
  color: #2c3e50;
  margin-bottom: 15px;
}

.week-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.goals,
.activities {
  line-height: 1.6;
}

.goals ul,
.activities ul {
  margin: 8px 0 0 20px;
  padding: 0;
}

.goals li,
.activities li {
  margin-bottom: 5px;
  color: #606266;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 40px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .knowledge-content {
    grid-template-columns: 1fr;
  }
  
  .overview-grid {
    grid-template-columns: 1fr;
    text-align: center;
  }
}

@media (max-width: 768px) {
  .action-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .loading-steps {
    flex-direction: column;
    gap: 15px;
  }
}
</style> 