<template>
  <div class="assignment-analysis">
    <el-card class="analysis-card" v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>{{ assignment?.title || '作业' }} - 学情分析</span>
          <el-button type="primary" @click="analyzeWithAI" :disabled="loading">AI分析</el-button>
        </div>
      </template>

      <!-- 统计数据卡片 -->
      <div class="statistics-cards" v-if="!loading">
        <el-card class="stat-card">
          <h3>完成率</h3>
          <div class="stat-value">{{ statistics?.completion_rate?.toFixed(1) || '0' }}%</div>
          <div class="stat-detail">
            已提交: {{ statistics?.submitted_count || 0 }} / 总人数: {{ statistics?.total_students || 0 }}
          </div>
        </el-card>
        <el-card class="stat-card">
          <h3>平均得分率</h3>
          <div class="stat-value">{{ statistics?.average_score?.toFixed(1) || '0' }}%</div>
          <div class="stat-detail">
            总分: {{ statistics?.total_points || 0 }}
          </div>
        </el-card>
      </div>

      <!-- AI分析结果 -->
      <div v-if="aiAnalysis" class="ai-analysis-section">
        <el-button 
          type="primary" 
          size="large" 
          @click="showAnalysisDrawer = true"
          class="analysis-trigger-btn"
        >
          <el-icon><Document /></el-icon>
          查看AI学情分析报告
        </el-button>
      </div>
        <!-- 图表展示 -->
        <div class="charts-container" v-if="!loading && submissions.length > 0">
        <div class="chart" ref="completionChart"></div>
        <div class="chart" ref="scoreDistChart"></div>
      </div>
      <el-empty v-else-if="!loading" description="暂无提交数据"></el-empty>
      <!-- 学生提交列表 -->
      <div class="submissions-list" v-if="!loading">
        <h3>学生提交情况</h3>
        <el-table :data="submissions" style="width: 100%">
          <el-table-column prop="student_name" label="学生姓名" width="120" />
          <el-table-column prop="score" label="得分" width="100">
            <template #default="scope">
              {{ scope.row.score }} / {{ statistics.total_points }}
            </template>
          </el-table-column>
          <el-table-column prop="score_percentage" label="得分率" width="100">
            <template #default="scope">
              {{ (scope.row.score_percentage || 0).toFixed(1) }}%
            </template>
          </el-table-column>
          <el-table-column prop="submit_time" label="提交时间" width="180">
            <template #default="scope">
              {{ formatDate(scope.row.submit_time) }}
            </template>
          </el-table-column>
          <el-table-column label="答题详情" min-width="300">
            <template #default="scope">
              <el-collapse>
                <el-collapse-item title="查看详情">
                  <div v-for="detail in scope.row.answer_details" :key="detail.question_id" class="answer-detail">
                    <div class="question-content">
                      <strong>题目{{ detail.question_id }}：</strong>{{ detail.question_content }}
                    </div>
                    <div class="score-info">
                      <span class="score">得分：{{ detail.score }} / {{ detail.max_points }}</span>
                      <span class="score-percentage">
                        ({{ ((detail.score / detail.max_points) * 100).toFixed(1) }}%)
                      </span>
                    </div>
                    <div class="feedback">
                      <strong>反馈：</strong>{{ detail.feedback }}
                    </div>
                    <el-divider></el-divider>
                  </div>
                </el-collapse-item>
              </el-collapse>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="scope">
              <el-button 
                type="primary" 
                link 
                @click="viewDetail(scope.row)"
              >
                编辑评分
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>

    <!-- AI分析抽屉 -->
    <el-drawer
      v-model="showAnalysisDrawer"
      :size="'70%'"
      direction="rtl"
      class="analysis-drawer"
    >
      <template #header>
        <div class="drawer-header">
          <div class="drawer-title">
            <el-icon style="margin-right: 12px; font-size: 24px;"><Document /></el-icon>
            <span>AI学情分析报告</span>
          </div>
          <div class="drawer-actions">
            <el-button 
              type="primary" 
              @click="exportAnalysis"
              size="small"
            >
              <el-icon><Download /></el-icon>
              导出报告
            </el-button>
            <el-button 
              type="info" 
              @click="showAnalysisDrawer = false"
              size="small"
            >
              <el-icon><Close /></el-icon>
              关闭
            </el-button>
          </div>
        </div>
      </template>
      
      <div class="drawer-content">
        <div class="analysis-meta">
          <div class="meta-item">
            <span class="meta-label">生成时间：</span>
            <span class="meta-value">{{ new Date().toLocaleString() }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">作业标题：</span>
            <span class="meta-value">{{ assignment?.title || '未知作业' }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">分析对象：</span>
            <span class="meta-value">{{ statistics?.submitted_count || 0 }}份学生提交</span>
          </div>
        </div>
        
        <div class="analysis-content-wrapper">
          <div class="ai-analysis-content" v-html="renderedAiAnalysis"></div>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Download, Close, Document } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import axios from 'axios'
import { marked } from 'marked'
import mermaid from 'mermaid'

const route = useRoute()
const router = useRouter()
const loading = ref(true)
const assignment = ref({})
const statistics = ref({
  completion_rate: 0,
  average_score: 0,
  total_students: 0,
  submitted_count: 0,
  total_points: 0
})
const submissions = ref([])
const aiAnalysis = ref('')
const completionChart = ref(null)
const scoreDistChart = ref(null)
const isReportExpanded = ref(true) // 新增：控制报告是否展开
const showAnalysisDrawer = ref(false) // 新增：控制抽屉是否打开

// 图表实例引用
let completionChartInstance = null
let scoreDistChartInstance = null

// AI分析渲染相关
const renderedAiAnalysis = computed(() => {
  if (!aiAnalysis.value) return ''
  return renderMarkdown(aiAnalysis.value)
})

// 重新调整图表大小
const resizeCharts = () => {
  if (completionChartInstance) {
    completionChartInstance.resize()
  }
  if (scoreDistChartInstance) {
    scoreDistChartInstance.resize()
  }
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

// 渲染 Mermaid 图表
const renderMermaidCharts = async () => {
  await nextTick()
  
  // 渲染AI分析内容中的 mermaid 图表
  const mermaidElements = document.querySelectorAll('.ai-analysis-content .mermaid')
  for (let i = 0; i < mermaidElements.length; i++) {
    const element = mermaidElements[i]
    if (element.getAttribute('data-processed') !== 'true') {
      try {
        const graphDefinition = element.textContent
        const { svg } = await mermaid.render(`mermaid-analysis-${i}`, graphDefinition)
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

// 获取作业提交数据
const fetchData = async () => {
  loading.value = true
  try {
    // 获取提交数据（包含统计信息）
    const { data } = await axios.get(`/assignment/${route.params.id}/submissions`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    statistics.value = data.statistics || {
      completion_rate: 0,
      average_score: 0,
      total_students: 0,
      submitted_count: 0,
      total_points: 0
    }
    submissions.value = data.data || []
    
    // 设置作业基本信息（从提交数据中推断）
    assignment.value = {
      id: route.params.id,
      title: `作业 ${route.params.id}` // 临时标题，因为没有单独的作业信息接口
    }
    
    // 使用 nextTick 确保 DOM 更新后再初始化图表
    await nextTick()
    if (submissions.value.length > 0) {
      setTimeout(() => {
        initCharts()
      }, 100)
    }
  } catch (error) {
    ElMessage.error('获取数据失败：' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

// 初始化图表
const initCharts = () => {
  console.log('正在初始化图表...')
  console.log('completionChart DOM:', completionChart.value)
  console.log('scoreDistChart DOM:', scoreDistChart.value)
  console.log('statistics:', statistics.value)
  
  if (!completionChart.value || !scoreDistChart.value) {
    console.error('图表DOM元素未找到')
    return
  }

  try {
    // 完成率饼图
    completionChartInstance = echarts.init(completionChart.value)
    const completionData = [
      { 
        value: statistics.value.submitted_count || 0, 
        name: '已提交',
        itemStyle: { color: '#7dd3c0' }
      },
      { 
        value: (statistics.value.total_students || 0) - (statistics.value.submitted_count || 0), 
        name: '未提交',
        itemStyle: { color: '#c0c0c0' }
      }
    ]
    
    console.log('完成率数据:', completionData)
    
    completionChartInstance.setOption({
      title: {
        text: '作业完成情况',
        left: 'center'
      },
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c} ({d}%)'
      },
      series: [{
        type: 'pie',
        radius: '50%',
        data: completionData,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(125, 211, 192, 0.3)'
          }
        }
      }]
    })

    // 得分分布柱状图
    const scoreRanges = calculateScoreRanges()
    console.log('得分分布数据:', scoreRanges)
    
    scoreDistChartInstance = echarts.init(scoreDistChart.value)
    scoreDistChartInstance.setOption({
      title: {
        text: '得分分布',
        left: 'center'
      },
      tooltip: {
        trigger: 'axis',
        formatter: '{b}: {c}人'
      },
      xAxis: {
        type: 'category',
        data: ['0-60', '60-70', '70-80', '80-90', '90-100']
      },
      yAxis: {
        type: 'value',
        name: '人数',
        minInterval: 1
      },
      series: [{
        data: scoreRanges.map((value, index) => ({
          value: value,
          itemStyle: {
            color: ['#e3f2fd', '#bbdefb', '#90caf9', '#64b5f6', '#42a5f5'][index]
          }
        })),
        type: 'bar'
      }]
    })

    console.log('图表初始化成功')

    // 监听窗口大小变化
    window.addEventListener('resize', resizeCharts)

    // 组件卸载时移除事件监听
    onUnmounted(() => {
      window.removeEventListener('resize', resizeCharts)
      if (completionChartInstance) {
        completionChartInstance.dispose()
      }
      if (scoreDistChartInstance) {
        scoreDistChartInstance.dispose()
      }
    })
  } catch (error) {
    console.error('图表初始化失败:', error)
  }
}

// 计算得分区间分布
const calculateScoreRanges = () => {
  const ranges = [0, 0, 0, 0, 0] // 0-60, 60-70, 70-80, 80-90, 90-100
  submissions.value.forEach(sub => {
    const score = sub.score_percentage || 0
    if (score < 60) ranges[0]++
    else if (score < 70) ranges[1]++
    else if (score < 80) ranges[2]++
    else if (score < 90) ranges[3]++
    else ranges[4]++
  })
  return ranges
}

// AI学情分析
const analyzeWithAI = async () => {
  loading.value = true
  try {
    // 构建分析提示
    const analysisPrompt = `请对以下作业情况进行全面分析：

作业ID：${route.params.id}
作业标题：${assignment.value.title || '未知'}
作业描述：${assignment.value.description || '暂无描述'}

统计数据：
- 总学生数：${statistics.value.total_students}人
- 提交人数：${statistics.value.submitted_count}人
- 完成率：${statistics.value.completion_rate.toFixed(1)}%
- 平均得分率：${statistics.value.average_score.toFixed(1)}%

学生答题情况：
${submissions.value.map(sub => {
  return `
学生${sub.student_name}：
得分率：${sub.score_percentage.toFixed(1)}%
题目反馈：
${sub.answer_details.map(detail => `- 题目${detail.question_id}: ${detail.feedback}`).join('\n')}
`
}).join('\n')}

请从以下几个方面进行分析：
1. 整体完成情况分析（提交率、平均分析等）
2. 知识点掌握情况（基于反馈分析学生对各知识点的理解程度）
3. 典型错误分析（总结常见错误和误区）
4. 针对性建议（为教师提供改进建议）
`

    const response = await axios.post(
      `/chat/simple`,
      null, // 不发送JSON body
      {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        params: {
          question: analysisPrompt,
          chat_name: '教师学情分析助手'
        },
        timeout: 120000
      }
    )

    if (response?.data?.code === 0 && response?.data?.data?.answer) {
      // 保存分析结果
      aiAnalysis.value = response.data.data.answer
      ElMessage.success('学情分析完成')
      
      // AI分析完成后，重新渲染图表
      await nextTick()
      setTimeout(() => {
        resizeCharts()
      }, 300)
    } else {
      console.error('API响应错误:', response.data)
      let errorMsg = '生成学情分析失败'
      if (response?.data?.message) {
        errorMsg += `: ${response.data.message}`
      }
      if (response?.data?.code === 100) {
        errorMsg = '服务器正忙，请稍后再试'
      }
      ElMessage.error(errorMsg)
    }
  } catch (error) {
    console.error('生成学情分析失败:', error)
    if (error.code === 'ECONNABORTED') {
      ElMessage.error('响应时间过长，请稍后重试')
    } else {
      ElMessage.error(error.response?.data?.message || '生成学情分析失败')
    }
  } finally {
    loading.value = false
  }
}

// 查看详情
const viewDetail = (submission) => {
  router.push({
    name: 'AssignmentDetail',
    params: { 
      id: route.params.id,
      submissionId: submission.id 
    }
  })
}

// 格式化日期
const formatDate = (date) => {
  if (!date) return '未知时间'
  return new Date(date).toLocaleString()
}

// 切换报告展开/收起
const toggleReportExpand = () => {
  isReportExpanded.value = !isReportExpanded.value
}

// 导出分析报告
const exportAnalysis = () => {
  if (!aiAnalysis.value) {
    ElMessage.warning('暂无分析内容可导出')
    return
  }
  
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19)
  const filename = `AI学情分析报告_${assignment.value.title || '作业'}_${timestamp}.md`
  
  let content = `# AI学情分析报告\n\n`
  content += `**作业标题：** ${assignment.value.title || '未知作业'}\n`
  content += `**生成时间：** ${new Date().toLocaleString()}\n`
  content += `**分析对象：** ${statistics.value?.submitted_count || 0}份学生提交\n\n`
  content += `---\n\n`
  content += aiAnalysis.value
  
  const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
  
  ElMessage.success('分析报告已导出')
}

onMounted(() => {
  fetchData()
  initMermaid() // 在组件挂载时初始化 Mermaid
})
</script>

<style scoped>
.assignment-analysis {
  padding: 20px;
}

.analysis-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.statistics-cards {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  flex: 1;
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
  margin: 10px 0;
}

.stat-detail {
  color: #666;
  font-size: 14px;
}

.charts-container {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.chart {
  flex: 1;
  height: 300px;
  min-width: 300px;
}

.ai-analysis-section {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  padding: 0 20px;
}

.analysis-report-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  max-width: 1200px;
  width: 100%;
  border: 1px solid #e4e7ed;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 30px;
  cursor: pointer;
  background: linear-gradient(135deg, #ff7b54 0%, #ffb347 100%);
  color: white;
  transition: all 0.3s ease;
}

.report-header:hover {
  background: linear-gradient(135deg, #ff6b47 0%, #ffa726 100%);
}

.report-title {
  display: flex;
  align-items: center;
  font-size: 20px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.report-title i {
  margin-right: 12px;
  font-size: 24px;
  opacity: 0.9;
}

.report-actions {
  display: flex;
  align-items: center;
}

.report-actions .el-button {
  color: white !important;
  font-size: 16px;
  font-weight: 500;
}

.report-content-wrapper {
  padding: 40px;
  background: #fafbfc;
}

.ai-analysis-content {
  background: white;
  border-radius: 8px;
  padding: 40px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  line-height: 1.8;
  font-size: 16px;
  color: #333;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', sans-serif;
}

/* AI分析内容样式 - 暖色调 */
.ai-analysis-content :deep(.main-title) {
  text-align: center;
  background: linear-gradient(135deg, #ff7b54 0%, #ffb347 100%);
  color: white;
  padding: 30px;
  border-radius: 12px;
  margin-bottom: 40px;
  font-size: 3em;
  font-weight: 700;
  box-shadow: 0 6px 20px rgba(255, 123, 84, 0.3);
  letter-spacing: 1px;
}

.ai-analysis-content :deep(.section-header-h2) {
  background: linear-gradient(135deg, #ffe0b3 0%, #ffeaa7 100%);
  color: #2c3e50;
  padding: 20px 25px;
  border-radius: 10px;
  margin: 35px 0 20px 0;
  position: relative;
  box-shadow: 0 4px 15px rgba(255, 179, 71, 0.3);
  border-left: 6px solid #ff8c42;
  font-size: 1.8em;
  font-weight: 600;
}

.ai-analysis-content :deep(.section-header-h2::before) {
  content: '📚';
  position: absolute;
  left: -18px;
  top: 50%;
  transform: translateY(-50%);
  background: white;
  border-radius: 50%;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.ai-analysis-content :deep(.section-header) {
  background: linear-gradient(135deg, #ffcc80 0%, #ffe0b2 100%);
  color: #2c3e50;
  padding: 16px 22px;
  border-radius: 8px;
  margin: 28px 0 16px 0;
  position: relative;
  border-left: 5px solid #ff8c42;
  box-shadow: 0 3px 10px rgba(255, 140, 66, 0.3);
  font-size: 1.5em;
  font-weight: 600;
}

.ai-analysis-content :deep(.section-header::before) {
  content: '📝';
  margin-right: 10px;
  font-size: 1.1em;
}

.ai-analysis-content :deep(.subsection-header) {
  color: #2c3e50;
  background: #fff8f0;
  padding: 12px 16px;
  margin: 20px 0 12px 0;
  border-radius: 6px;
  border-left: 4px solid #ff8c42;
  font-weight: 600;
  font-size: 1.3em;
  box-shadow: 0 2px 6px rgba(255, 140, 66, 0.1);
}

.ai-analysis-content :deep(h4) {
  color: #2c3e50;
  font-size: 1.2em;
  font-weight: 600;
  margin: 18px 0 10px 0;
  padding-left: 12px;
  border-left: 3px solid #ffb347;
}

.ai-analysis-content :deep(h5) {
  color: #2c3e50;
  font-size: 1.1em;
  font-weight: 600;
  margin: 16px 0 8px 0;
  color: #d35400;
}

.ai-analysis-content :deep(h6) {
  color: #e67e22;
  font-size: 1em;
  font-weight: 600;
  margin: 14px 0 6px 0;
}

.ai-analysis-content :deep(.table-container) {
  overflow-x: auto;
  margin: 20px 0;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.ai-analysis-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 0;
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.ai-analysis-content :deep(th),
.ai-analysis-content :deep(td) {
  border: none;
  padding: 15px;
  text-align: left;
  border-bottom: 1px solid #ebeef5;
}

.ai-analysis-content :deep(th) {
  background: linear-gradient(135deg, #b7bedb 0%, #dde1f5 100%);
  color: #2c3e50;
  font-weight: 600;
  font-size: 1.1em;
}

.ai-analysis-content :deep(tr:nth-child(even)) {
  background-color: #f9fafc;
}

.ai-analysis-content :deep(tr:hover) {
  background-color: #e8f4fd;
  transform: translateY(-1px);
  transition: all 0.2s ease;
}

.ai-analysis-content :deep(.info-box) {
  background: linear-gradient(135deg, #fff3e0 0%, #ffe8d1 100%);
  border-left: 5px solid #ff8c42;
  padding: 20px;
  margin: 20px 0;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(255, 140, 66, 0.1);
}

.ai-analysis-content :deep(.warning-box) {
  background: linear-gradient(135deg, #ffebcd 0%, #ffeaa7 100%);
  border-left: 5px solid #ff7b54;
  padding: 20px;
  margin: 20px 0;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(255, 123, 84, 0.1);
}

.ai-analysis-content :deep(.task-item) {
  background: linear-gradient(135deg, #fff8f0 0%, #ffebcd 100%);
  border-left: 5px solid #d35400;
  padding: 20px;
  margin: 20px 0;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(211, 84, 0, 0.1);
}

.ai-analysis-content :deep(.highlight-box) {
  background: linear-gradient(135deg, #ffeaa7 0%, #ffe0b3 100%);
  border: 1px solid #ffcc80;
  border-radius: 8px;
  padding: 20px;
  margin: 20px 0;
  box-shadow: 0 2px 8px rgba(255, 204, 128, 0.1);
}

.ai-analysis-content :deep(pre) {
  background: #fff8f0;
  padding: 20px;
  border-radius: 8px;
  overflow-x: auto;
  border-left: 5px solid #ff8c42;
  margin: 20px 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.ai-analysis-content :deep(code) {
  background: #ffebcd;
  padding: 4px 8px;
  border-radius: 4px;
  font-family: 'Consolas', 'Monaco', monospace;
  color: #d35400;
  font-size: 0.9em;
}

.ai-analysis-content :deep(ul),
.ai-analysis-content :deep(ol) {
  padding-left: 30px;
  margin: 16px 0;
}

.ai-analysis-content :deep(li) {
  margin: 10px 0;
  line-height: 1.8;
}

.ai-analysis-content :deep(hr) {
  border: none;
  height: 3px;
  background: linear-gradient(90deg, transparent, #ff8c42, transparent);
  margin: 40px 0;
  border-radius: 1.5px;
}

.ai-analysis-content :deep(.mermaid-container) {
  background: white;
  border: 2px solid #e9ecef;
  border-radius: 10px;
  padding: 30px;
  margin: 25px 0;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.ai-analysis-content :deep(blockquote) {
  border-left: 5px solid #ff8c42;
  background: linear-gradient(135deg, #fff8f0 0%, #ffebcd 100%);
  padding: 20px;
  margin: 20px 0;
  font-style: italic;
  border-radius: 0 8px 8px 0;
  box-shadow: 0 2px 8px rgba(255, 140, 66, 0.1);
}

/* 段落样式 */
.ai-analysis-content :deep(p) {
  margin: 16px 0;
  line-height: 1.8;
  font-size: 16px;
}

/* 强调文本 */
.ai-analysis-content :deep(strong) {
  color: #2c3e50;
  font-weight: 700;
}

.ai-analysis-content :deep(em) {
  color: #576574;
  font-style: italic;
}

/* 链接样式 */
.ai-analysis-content :deep(a) {
  color: #ff8c42;
  text-decoration: none;
  border-bottom: 1px solid transparent;
  transition: all 0.3s ease;
  font-weight: 500;
}

.ai-analysis-content :deep(a:hover) {
  color: #d35400;
  border-bottom-color: #ff8c42;
}

/* 抽屉样式 */
.analysis-drawer :deep(.el-drawer__header) {
  background: linear-gradient(135deg, #ffb67a 0%, #ffd89b 100%);
  padding: 0;
  margin: 0;
  border-radius: 0;
}

.drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 20px 30px;
  background: linear-gradient(135deg, #ffb67a 0%, #ffd89b 100%);
}

.drawer-title {
  display: flex;
  align-items: center;
  color: white;
  font-size: 20px;
  font-weight: 600;
  margin: 0;
}

.drawer-title i {
  margin-right: 12px;
  font-size: 24px;
}

.drawer-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.drawer-actions .el-button {
  color: white !important;
  border-color: rgba(255, 255, 255, 0.7) !important;
  background: rgba(255, 255, 255, 0.15) !important;
  font-weight: 500;
}

.drawer-actions .el-button:hover {
  background: rgba(255, 255, 255, 0.25) !important;
  border-color: rgba(255, 255, 255, 0.9) !important;
  color: white !important;
}

.drawer-actions .el-button .el-icon {
  color: white !important;
}

.drawer-content {
  padding: 0;
  height: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.analysis-meta {
  background: #f8f9fa;
  padding: 20px 30px;
  border-bottom: 1px solid #ebeef5;
  display: flex;
  gap: 30px;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.meta-label {
  color: #666;
  font-weight: 500;
}

.meta-value {
  color: #2c3e50;
  font-weight: 600;
}

.analysis-content-wrapper {
  flex: 1;
  overflow-y: auto;
  padding: 30px;
  background: white;
}

.analysis-trigger-btn {
  background: linear-gradient(135deg, #ffb67a 0%, #ffd89b 100%);
  border: none;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(255, 182, 122, 0.3);
  transition: all 0.3s ease;
}

.analysis-trigger-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(255, 182, 122, 0.4);
  background: linear-gradient(135deg, #ffa85c 0%, #ffcc7a 100%);
}

.analysis-trigger-btn i {
  margin-right: 8px;
}

.submissions-list {
  margin-top: 20px;
}

.answer-detail {
  margin-bottom: 15px;
}

.question-content {
  margin-bottom: 8px;
  line-height: 1.5;
}

.score-info {
  margin: 8px 0;
  color: #409EFF;
}

.score {
  margin-right: 10px;
}

.score-percentage {
  color: #67C23A;
}

.feedback {
  background-color: #f8f9fa;
  padding: 8px;
  border-radius: 4px;
  margin-top: 8px;
  line-height: 1.5;
}

.el-divider {
  margin: 12px 0;
}

/* 表格固定列样式优化 */
:deep(.el-table .el-table__fixed-right) {
  height: 100% !important;
  background-color: var(--el-bg-color);
}

/* 确保折叠面板内容不会溢出 */
:deep(.el-collapse-item__content) {
  padding: 15px;
  background-color: var(--el-bg-color-page);
  border-radius: 4px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .statistics-cards,
  .charts-container {
    flex-direction: column;
  }
  
  .chart {
    width: 100%;
  }
  
  .ai-analysis-section {
    padding: 0 10px;
  }
  
  .analysis-meta {
    flex-direction: column;
    gap: 15px;
  }
  
  .drawer-actions {
    flex-direction: column;
    gap: 8px;
  }
  
  .ai-analysis-content {
    padding: 20px;
  }
  
  .ai-analysis-content :deep(.main-title) {
    font-size: 2.2em;
    padding: 20px;
  }
  
  .ai-analysis-content :deep(.section-header-h2) {
    font-size: 1.5em;
    padding: 15px 20px;
  }
  
  .ai-analysis-content :deep(.section-header) {
    font-size: 1.3em;
    padding: 12px 18px;
  }
}
</style> 