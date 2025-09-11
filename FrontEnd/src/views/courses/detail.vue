<template>
  <div class="course-detail">
    <div class="course-header">
      <h1>{{ course.name }}</h1>
      <el-tag>{{ course.status }}</el-tag>
    </div>

    <el-tabs v-model="activeTab" class="course-tabs">
      <el-tab-pane label="课程介绍" name="intro">
        <div class="course-info">
          <h3>课程简介</h3>
          <p>{{ course.description }}</p>
          
          <h3>课程目标</h3>
          <ul>
            <li v-for="(goal, index) in course.goals" :key="index">
              {{ goal }}
            </li>
          </ul>
        </div>
      </el-tab-pane>

      <el-tab-pane label="课程内容" name="content">
        <el-tree
          :data="course.chapters"
          :props="defaultProps"
          @node-click="handleNodeClick"
        />
      </el-tab-pane>

      <el-tab-pane label="作业" name="homework">
        <el-table :data="course.homework" style="width: 100%">
          <el-table-column prop="title" label="作业名称" />
          <el-table-column prop="deadline" label="截止日期" />
          <el-table-column prop="status" label="状态" />
          <el-table-column label="操作">
            <template #default="scope">
              <el-button type="primary" size="small" @click="handleHomework(scope.row)">
                查看
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const activeTab = ref('intro')

// 模拟课程数据
const course = reactive({
  id: route.params.id,
  name: '人工智能导论',
  status: '进行中',
  description: '本课程将介绍人工智能的基本概念、发展历史、主要应用领域等内容。通过本课程的学习，学生将掌握人工智能的基础知识，了解人工智能的最新发展动态。',
  goals: [
    '理解人工智能的基本概念和发展历史',
    '掌握人工智能的主要应用领域',
    '了解人工智能的最新发展动态',
    '能够运用人工智能解决实际问题'
  ],
  chapters: [
    {
      label: '第一章：人工智能概述',
      children: [
        { label: '1.1 人工智能的定义' },
        { label: '1.2 人工智能的发展历史' },
        { label: '1.3 人工智能的应用领域' }
      ]
    },
    {
      label: '第二章：机器学习基础',
      children: [
        { label: '2.1 机器学习概念' },
        { label: '2.2 监督学习' },
        { label: '2.3 无监督学习' }
      ]
    }
  ],
  homework: [
    {
      title: '第一次作业',
      deadline: '2024-03-20',
      status: '已提交'
    },
    {
      title: '第二次作业',
      deadline: '2024-03-27',
      status: '未提交'
    }
  ]
})

const defaultProps = {
  children: 'children',
  label: 'label'
}

const handleNodeClick = (data) => {
  console.log(data)
}

const handleHomework = (homework) => {
  console.log('查看作业:', homework)
}
</script>

<style scoped>
.course-detail {
  padding: 20px;
}

.course-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 30px;
}

.course-header h1 {
  margin: 0;
}

.course-tabs {
  margin-top: 20px;
}

.course-info {
  max-width: 800px;
}

.course-info h3 {
  margin: 20px 0 10px;
}

.course-info ul {
  padding-left: 20px;
}

.course-info li {
  margin: 10px 0;
}
</style> 