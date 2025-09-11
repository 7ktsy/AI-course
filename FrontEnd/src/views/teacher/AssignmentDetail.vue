<template>
  <div class="assignment-detail">
    <el-card class="detail-card">
      <template #header>
        <div class="card-header">
          <span>{{ student.student_name }} 的作业详情</span>
          <div class="header-actions">
            <el-button type="primary" @click="saveChanges">保存修改</el-button>
            <el-button @click="goBack">返回</el-button>
          </div>
        </div>
      </template>

      <!-- 基本信息 -->
      <div class="basic-info">
        <el-descriptions :column="3" border>
          <el-descriptions-item label="提交时间">
            {{ formatDate(submission.submit_time) }}
          </el-descriptions-item>
          <el-descriptions-item label="总分">
            <el-input-number 
              v-model="submission.score" 
              :min="0" 
              :max="statistics.total_points"
              :precision="1"
              size="small"
            />
            / {{ statistics.total_points }}
          </el-descriptions-item>
          <el-descriptions-item label="得分率">
            {{ ((submission.score / statistics.total_points) * 100).toFixed(1) }}%
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 答题详情 -->
      <div class="answer-details">
        <el-collapse v-model="activeQuestions">
          <el-collapse-item 
            v-for="detail in submission.answer_details" 
            :key="detail.question_id"
            :title="'题目 ' + detail.question_id"
            :name="detail.question_id"
          >
            <div class="question-detail">
              <!-- 题目内容 -->
              <div class="question-content">
                <h4>题目内容：</h4>
                <div class="content-text">{{ detail.question_content }}</div>
              </div>

              <!-- 得分和反馈 -->
              <div class="score-feedback">
                <div class="score-input">
                  <span>得分：</span>
                  <el-input-number 
                    v-model="detail.score" 
                    :min="0" 
                    :max="detail.max_points"
                    :precision="1"
                    size="small"
                  />
                  <span>/ {{ detail.max_points }}</span>
                </div>
                
                <div class="feedback-input">
                  <h4>反馈意见：</h4>
                  <el-input
                    v-model="detail.feedback"
                    type="textarea"
                    :rows="3"
                    placeholder="请输入反馈意见"
                  />
                </div>
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const submission = ref({})
const student = ref({})
const statistics = ref({})
const activeQuestions = ref([])

// 获取提交详情
const fetchSubmissionDetail = async () => {
  try {
    const { data } = await axios.get(`/assignment/${route.params.id}/submissions`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    const submissionData = data.data.find(s => s.id === parseInt(route.params.submissionId))
    if (submissionData) {
      submission.value = submissionData
      student.value = {
        student_id: submissionData.student_id,
        student_name: submissionData.student_name
      }
      statistics.value = data.statistics
    } else {
      ElMessage.error('未找到提交记录')
      goBack()
    }
  } catch (error) {
    ElMessage.error('获取数据失败')
  }
}

// 保存修改
const saveChanges = async () => {
  try {
    await axios.put(`/assignment/${route.params.id}/submission/${route.params.submissionId}`, {
      score: submission.value.score,
      answer_details: submission.value.answer_details
    }, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    ElMessage.success('保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

// 返回上一页
const goBack = () => {
  router.push({
    name: 'LearningAnalysis',
    params: { id: route.params.id }
  })
}

// 格式化日期
const formatDate = (date) => {
  return new Date(date).toLocaleString()
}

onMounted(() => {
  fetchSubmissionDetail()
})
</script>

<style scoped>
.assignment-detail {
  padding: 20px;
}

.detail-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.basic-info {
  margin-bottom: 20px;
}

.question-detail {
  padding: 10px;
}

.question-content {
  margin-bottom: 20px;
}

.content-text {
  padding: 10px;
  background: #f8f9fa;
  border-radius: 4px;
}

.score-feedback {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.score-input {
  display: flex;
  align-items: center;
  gap: 10px;
}

.feedback-input {
  width: 100%;
}

.feedback-input h4 {
  margin-bottom: 10px;
}
</style> 