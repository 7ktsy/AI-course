<template>
  <div class="dashboard-container">
    <OverallView v-if="userInfo.role === 'admin'" />
    <StudentDashboard v-else-if="userInfo.role === 'student'" />
    <TeacherDashboard v-else-if="userInfo.role === 'teacher'" />
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import OverallView from '@/views/admin/OverallView.vue'
import StudentDashboard from '@/views/student/StudentDashboard.vue'
import TeacherDashboard from '@/views/teacher/TeacherDashboard.vue'

export default {
  name: 'Dashboard',
  components: {
    OverallView,
    StudentDashboard,
    TeacherDashboard
  },
  setup() {
    const userInfo = ref({})

    onMounted(() => {
      const storedUserInfo = localStorage.getItem('userInfo')
      if (storedUserInfo) {
        userInfo.value = JSON.parse(storedUserInfo)
      }
    })

    return {
      userInfo
    }
  }
}
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
}

.welcome-card {
  margin-bottom: 20px;
}

.welcome-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.welcome-header h2 {
  margin: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.statistics {
  display: flex;
  justify-content: space-around;
  text-align: center;
}

.statistic-item h3 {
  margin: 0;
  font-size: 24px;
  color: #409EFF;
}

.statistic-item p {
  margin: 5px 0 0;
  color: #909399;
}

:deep(.el-timeline-item__content) {
  color: #606266;
}

:deep(.el-timeline-item__timestamp) {
  font-size: 12px;
}

:deep(.el-table) {
  font-size: 13px;
}
</style>