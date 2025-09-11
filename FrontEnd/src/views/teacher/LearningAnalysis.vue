<template>
  <div class="learning-analysis">
    <!-- 顶部操作栏 -->
    <el-card shadow="never" class="header-card">
      <div class="header-content">
        <div class="header-left">
          <h2>学情分析</h2>
          <el-tag type="info">数据统计与分析</el-tag>
        </div>
        <div class="header-right">
          <el-button @click="refreshData">
            <i class="bi bi-arrow-clockwise"></i>
            刷新数据
          </el-button>
          <el-button @click="exportReport">
            <i class="bi bi-download"></i>
            导出报告
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 筛选条件 -->
    <el-card shadow="never" class="filter-card">
      <el-form :model="filterForm" inline>
        <el-form-item label="课程">
          <el-select v-model="filterForm.courseId" placeholder="选择课程">
            <el-option 
              v-for="course in courseList" 
              :key="course.id"
              :label="course.name" 
              :value="course.id" 
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="班级">
          <el-select v-model="filterForm.classId" placeholder="选择班级">
            <el-option 
              v-for="classItem in classList" 
              :key="classItem.id"
              :label="classItem.name" 
              :value="classItem.id" 
            />
          </el-select>
        </el-form-item>

        <el-form-item label="时间范围">
          <el-date-picker
            v-model="filterForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleFilter">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 统计概览 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover" class="stats-card">
          <div class="stats-content">
            <div class="stats-icon">
              <i class="bi bi-people-fill"></i>
            </div>
            <div class="stats-data">
              <div class="stats-number">{{ totalStudents }}</div>
              <div class="stats-label">总学生数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover" class="stats-card">
          <div class="stats-content">
            <div class="stats-icon">
              <i class="bi bi-file-earmark-text-fill"></i>
            </div>
            <div class="stats-data">
              <div class="stats-number">{{ totalAssignments }}</div>
              <div class="stats-label">作业总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover" class="stats-card">
          <div class="stats-content">
            <div class="stats-icon">
              <i class="bi bi-graph-up"></i>
            </div>
            <div class="stats-data">
              <div class="stats-number">{{ averageScore }}%</div>
              <div class="stats-label">平均分</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover" class="stats-card">
          <div class="stats-content">
            <div class="stats-icon">
              <i class="bi bi-check-circle-fill"></i>
            </div>
            <div class="stats-data">
              <div class="stats-number">{{ completionRate }}%</div>
              <div class="stats-label">完成率</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表分析 -->
    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card shadow="never" title="成绩分布统计">
          <template #header>
            <span>成绩分布统计</span>
          </template>
          <div class="chart-container" ref="scoreChartRef"></div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>
            <span>学习进度趋势</span>
          </template>
          <div class="chart-container" ref="progressChartRef"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="charts-row">
      <el-col :span="24">
        <el-card shadow="never">
          <template #header>
            <span>知识点掌握情况</span>
          </template>
          <div class="chart-container" ref="knowledgeChartRef"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 学生详细分析 -->
    <el-card shadow="never" class="detail-card">
      <template #header>
        <div class="detail-header">
          <span>学生详细分析</span>
          <el-button @click="showStudentAnalysis = !showStudentAnalysis">
            {{ showStudentAnalysis ? '隐藏' : '展开' }}详情
          </el-button>
        </div>
      </template>
      
      <div v-if="showStudentAnalysis">
        <el-table :data="studentAnalysisData" style="width: 100%">
          <el-table-column prop="name" label="学生姓名" width="120" />
          <el-table-column prop="studentId" label="学号" width="120" />
          <el-table-column label="平均分" width="100">
            <template #default="scope">
              <el-tag :type="getScoreType(scope.row.averageScore)">
                {{ scope.row.averageScore }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="completedAssignments" label="完成作业数" width="120" />
          <el-table-column prop="totalAssignments" label="总作业数" width="120" />
          <el-table-column label="完成率" width="100">
            <template #default="scope">
              <el-progress 
                :percentage="Math.round((scope.row.completedAssignments / scope.row.totalAssignments) * 100)"
                :stroke-width="6"
                size="small"
              />
            </template>
          </el-table-column>
          <el-table-column prop="weakPoints" label="薄弱知识点" min-width="200" />
          <el-table-column label="操作" width="150">
            <template #default="scope">
              <el-button size="small" @click="viewStudentDetail(scope.row)">
                详细分析
              </el-button>
              <el-button size="small" type="primary" @click="generateAdvice(scope.row)">
                学习建议
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>

    <!-- 学习建议对话框 -->
    <el-dialog v-model="showAdviceDialog" title="学习建议" width="50%">
      <div v-if="currentStudent" class="advice-content">
        <h4>{{ currentStudent.name }} 的学习建议</h4>
        <div class="advice-section">
          <h5>学习表现分析：</h5>
          <ul>
            <li>平均分：{{ currentStudent.averageScore }}分</li>
            <li>作业完成率：{{ Math.round((currentStudent.completedAssignments / currentStudent.totalAssignments) * 100) }}%</li>
            <li>薄弱知识点：{{ currentStudent.weakPoints }}</li>
          </ul>
        </div>
        <div class="advice-section">
          <h5>改进建议：</h5>
          <ol>
            <li>针对薄弱知识点进行专项练习</li>
            <li>及时完成作业，保持学习连续性</li>
            <li>多参与课堂讨论，提高理解深度</li>
            <li>寻求老师或同学帮助解决疑难问题</li>
          </ol>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'

const showStudentAnalysis = ref(false)
const showAdviceDialog = ref(false)
const currentStudent = ref(null)

// 统计数据
const totalStudents = ref(45)
const totalAssignments = ref(12)
const averageScore = ref(78)
const completionRate = ref(85)

// 筛选表单
const filterForm = reactive({
  courseId: '',
  classId: '',
  dateRange: []
})

const courseList = ref([
  { id: 1, name: '人工智能基础' },
  { id: 2, name: '机器学习' },
  { id: 3, name: '深度学习' }
])

const classList = ref([
  { id: 1, name: '计算机科学2021-1班' },
  { id: 2, name: '计算机科学2021-2班' }
])

const studentAnalysisData = ref([
  {
    name: '张三',
    studentId: '2021001',
    averageScore: 85,
    completedAssignments: 10,
    totalAssignments: 12,
    weakPoints: '深度学习算法'
  },
  {
    name: '李四',
    studentId: '2021002',
    averageScore: 72,
    completedAssignments: 9,
    totalAssignments: 12,
    weakPoints: '数据预处理'
  },
  {
    name: '王五',
    studentId: '2021003',
    averageScore: 90,
    completedAssignments: 12,
    totalAssignments: 12,
    weakPoints: '模型优化'
  }
])

// 图表引用
const scoreChartRef = ref()
const progressChartRef = ref()
const knowledgeChartRef = ref()

onMounted(() => {
  nextTick(() => {
    initCharts()
  })
})

// 初始化图表（这里使用模拟数据，实际项目中可以集成 ECharts 等图表库）
const initCharts = () => {
  // 模拟图表初始化
  if (scoreChartRef.value) {
    scoreChartRef.value.innerHTML = '<div style="height: 300px; display: flex; align-items: center; justify-content: center; background: #f5f5f5; border-radius: 4px;">成绩分布图表区域</div>'
  }
  if (progressChartRef.value) {
    progressChartRef.value.innerHTML = '<div style="height: 300px; display: flex; align-items: center; justify-content: center; background: #f5f5f5; border-radius: 4px;">学习进度图表区域</div>'
  }
  if (knowledgeChartRef.value) {
    knowledgeChartRef.value.innerHTML = '<div style="height: 300px; display: flex; align-items: center; justify-content: center; background: #f5f5f5; border-radius: 4px;">知识点掌握图表区域</div>'
  }
}

// 辅助函数
const getScoreType = (score) => {
  if (score >= 90) return 'success'
  if (score >= 80) return 'primary'
  if (score >= 70) return 'warning'
  return 'danger'
}

// 事件处理
const handleFilter = () => {
  ElMessage.success('数据筛选功能开发中...')
}

const resetFilter = () => {
  Object.keys(filterForm).forEach(key => {
    if (key === 'dateRange') {
      filterForm[key] = []
    } else {
      filterForm[key] = ''
    }
  })
}

const refreshData = () => {
  ElMessage.success('数据已刷新')
}

const exportReport = () => {
  ElMessage.success('报告导出功能开发中...')
}

const viewStudentDetail = (student) => {
  ElMessage.info(`查看 ${student.name} 的详细分析`)
}

const generateAdvice = (student) => {
  currentStudent.value = student
  showAdviceDialog.value = true
}
</script>

<style scoped>
.learning-analysis {
  padding: 20px 0;
}

.header-card,
.filter-card,
.stats-row,
.charts-row,
.detail-card {
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

.stats-card {
  height: 120px;
}

.stats-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.stats-icon {
  font-size: 48px;
  color: #409EFF;
  margin-right: 20px;
}

.stats-data {
  flex: 1;
}

.stats-number {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
}

.stats-label {
  font-size: 14px;
  color: #909399;
  margin-top: 8px;
}

.chart-container {
  height: 300px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.advice-content {
  line-height: 1.6;
}

.advice-content h4 {
  margin-top: 0;
  color: #303133;
}

.advice-content h5 {
  margin: 20px 0 10px 0;
  color: #606266;
}

.advice-section {
  margin-bottom: 20px;
}

.advice-section ul,
.advice-section ol {
  margin: 10px 0;
  padding-left: 20px;
}

.advice-section li {
  margin: 5px 0;
}
</style>