import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/layout/Layout.vue'
import Login from '@/views/Login.vue'
import Home from '@/views/home/index.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/voice-demo',
    name: 'VoiceDemo',
    component: () => import('@/views/VoiceNavigationDemo.vue'),
    meta: { title: '语音导航演示' }
  },
  {
    path: '/voice-ai-demo',
    name: 'VoiceAIDemo',
    component: () => import('@/views/VoiceAIDemo.vue'),
    meta: { title: '语音AI助手演示' }
  },
  {
    path: '/dashboard',
    component: Layout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',  // 默认子路由
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue')
      },
      {
        path: 'writing-assistant',
        name: 'WritingAssistant',
        component: () => import('@/views/WritingAssistant.vue'),
        meta: { 
          title: 'AI写作助手',
          requiresAuth: true
        }
      },
      {
        path: 'courses',
        name: 'MyCourses',
        component: () => {
          // 根据用户角色动态加载不同的组件
          const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
          console.log('用户信息:', userInfo)
          if (userInfo.role === 'student') {
            return import('@/views/courses/StudentCourse.vue')
          } else {
            return import('@/views/courses/MyCourse.vue')
          }
        },
        meta: { title: '我的课程' }
      },
      {
        path: 'all-courses',
        name: 'AllCourses',
        component: () => import('@/views/courses/AllCourses.vue'),
        meta: { title: '全部课程' }
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/profile/index.vue')
      },
      {
        path: 'class-management',
        name: 'ClassManage',
        component: () => import('@/views/teacher/ClassManagement.vue'),
        meta: { 
          title: '班级管理',
          requiresAuth: true,
          roles: ['teacher']
        }
      },
      {
        path: 'preparation',
        name: 'Preparation',
        component: () => import('@/views/teacher/Preparation.vue'),
        meta: { 
          title: '智能备课',
          requiresAuth: true,
          roles: ['teacher']
        }
      },
      {
        path: 'preparation-manage',
        name: 'PreparationManage',
        component: () => import('@/views/teacher/PreparationManage.vue'),
        meta: { 
          title: '教案管理',
          requiresAuth: true,
          roles: ['teacher']
        }
      },
      {
        path: 'ppt-generation',
        name: 'PPTGeneration',
        component: () => import('@/views/teacher/PPTGeneration.vue'),
        meta: { 
          title: 'PPT生成',
          requiresAuth: true,
          roles: ['teacher']
        }
      },
      // 题目中心路由
      {
        path: 'ai-question-generator',
        name: 'AIQuestionGenerator',
        component: () => import('@/views/teacher/AIQuestionGenerator.vue'),
        meta: { 
          title: 'AI智能出题',
          requiresAuth: true,
          roles: ['teacher']
        }
      },
      {
        path: 'question-bank',
        name: 'QuestionBank',
        component: () => import('@/views/teacher/QuestionBank.vue'),
        meta: { 
          title: '题库管理',
          requiresAuth: true,
          roles: ['teacher', 'admin']
        }
      },
      // 作业管理路由
      {
        path: 'homework-list',
        name: 'HomeworkList',
        component: () => import('@/views/teacher/HomeworkList.vue'),
        meta: { 
          title: '作业列表',
          requiresAuth: true,
          roles: ['teacher']
        }
      },
      {
        path: 'learning-analysis/:id',
        name: 'LearningAnalysis',
        component: () => import('@/views/teacher/AssignmentAnalysis.vue'),
        meta: { 
          title: '学情分析',
          requiresAuth: true,
          roles: ['teacher']
        }
      },
      {
        path: 'assignment-detail/:id/:submissionId',
        name: 'AssignmentDetail',
        component: () => import('@/views/teacher/AssignmentDetail.vue'),
        meta: { 
          title: '作业详情',
          requiresAuth: true,
          roles: ['teacher']
        }
      },
      // 学生端路由
      {
        path: 'my-homework',
        name: 'MyHomework',
        component: () => import('@/views/student/MyHomework.vue'),
        meta: { 
          title: '我的作业',
          requiresAuth: true,
          roles: ['student']
        }
      },
      {
        path: 'homework-detail/:id',
        name: 'HomeworkDetail',
        component: () => import('@/views/student/HomeworkDetail.vue'),
        meta: { 
          title: '作业详情',
          requiresAuth: true,
          roles: ['student']
        }
      },
      // 实时练习路由
      {
        path: 'student/real-time-practice',
        name: 'RealTimePractice',
        component: () => import('@/views/student/RealTimePractice.vue'),
        meta: { 
          title: '实时智能练习',
          requiresAuth: true,
          roles: ['student']
        }
      },
      {
        path: 'student/practice/:id',
        name: 'PracticeDetail',
        component: () => import('@/views/student/PracticeDetail.vue'),
        meta: { 
          title: '练习答题',
          requiresAuth: true,
          roles: ['student']
        }
      },
      {
        path: 'student/practice/:id/result',
        name: 'PracticeResult',
        component: () => import('@/views/student/PracticeResult.vue'),
        meta: { 
          title: '练习结果',
          requiresAuth: true,
          roles: ['student']
        }
      },
      {
        path: 'student/practice/:id/analysis',
        name: 'StudentLearningAnalysis',
        component: () => import('@/views/student/LearningAnalysisReport.vue'),
        meta: { 
          title: '学情分析报告',
          requiresAuth: true,
          roles: ['student']
        }
      },
      // 学生成绩查询页面
      {
        path: 'grades',
        name: 'StudentGrades',
        component: () => import('@/views/student/GradeAnalysis.vue'),
        meta: { 
          title: '成绩查询与分析',
          requiresAuth: true,
          roles: ['student']
        }
      },
      // 学习助手路由
      {
        path: 'learning-assistant',
        name: 'LearningAssistant',
        component: () => import('@/views/student/LearningAssistant.vue'),
        meta: { 
          title: '学习助手',
          requiresAuth: true,
          roles: ['student']
        }
      },
      // 知识图谱路由
      {
        path: 'knowledge-graph',
        name: 'KnowledgeGraph',
        component: () => import('@/views/student/KnowledgeGraph.vue'),
        meta: { 
          title: '知识图谱',
          requiresAuth: true,
          roles: ['student']
        }
      },
      // 节点详情路由
      {
        path: 'node-detail/:nodeId/:nodeData?',
        name: 'NodeDetail',
        component: () => import('@/views/student/NodeDetail.vue'),
        meta: { 
          title: '节点详情',
          requiresAuth: true,
          roles: ['student']
        }
      },
      // 拍照搜题路由
      {
        path: 'photo-search-question',
        name: 'PhotoSearchQuestion',
        component: () => import('@/views/dashboard/PhotoSearchQuestion.vue'),
        meta: { 
          title: '拍照搜题',
          requiresAuth: true,
          roles: ['student', 'teacher']
        }
      },
      {
        path:'overallview',
        name: 'OverallView',
        component: () => import('@/views/admin/OverallView.vue'),
        meta: {
          title: '系统总览',
          requiresAuth: true,
          roles: ['admin']
        }
      },
      {
        path: 'users',
        name: 'UserManagement',
        component: () => import('@/views/admin/UserManagement.vue'),
        meta: {
          title: '用户管理',
          requiresAuth: true,
          roles: ['admin']
        }
      },
      {
        path: 'admin-courses',
        name: 'CourseManagement',
        component: () => import('@/views/admin/CourseManagement.vue'),
        meta: {
          title: '课程管理',
          requiresAuth: true,
          roles: ['admin']
        }
      },
      {
        path: 'chat-management',
        name: 'ChatManagement',
        component: () => import('@/views/admin/ChatManagement.vue'),
        meta: {
          title: '聊天助手管理',
          requiresAuth: true,
          roles: ['admin']
        }
      },
      {
        path: 'model-configuration',
        name: 'ModelConfiguration',
        component: () => import('@/views/admin/ModelConfiguration.vue'),
        meta: {
          title: '模型配置',
          requiresAuth: true,
          roles: ['admin']
        }
      },
      {
        path: 'chat-detail/:chatId',
        name: 'ChatDetailEdit',
        component: () => import('@/views/admin/ChatDetailEdit.vue'),
        meta: {
          title: '聊天助手详情',
          requiresAuth: true,
          roles: ['admin']
        }
      },
      // 现有路由
      {
        path: 'class-management/:course_id',
        name: 'ClassManageDetail',
        component: () => import('@/views/teacher/ClassManageDetail.vue'),
        meta: { 
          title: '课程学生管理',
          requiresAuth: true,
          roles: ['teacher']
        }
      },
      {
        path: 'teaching-plan-board',
        name: 'TeachingPlanBoard',
        component: () => import('@/views/teacher/TeachingPlanBoard.vue'),
        meta: { 
          title: '教学计划看板',
          requiresAuth: true,
          roles: ['teacher']
        }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 增强路由守卫，添加角色检查
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
  
  // 如果是访问首页或登录页，直接放行
  if (to.path === '/' || to.path === '/login') {
    // 如果已登录且访问登录页，重定向到仪表盘
    if (token && to.path === '/login') {
      next('/dashboard')
    } else {
      next()
    }
  } 
  // 其他需要认证的页面
  else if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!token) {
      next('/login')
    } else {
      // 检查角色权限
      const requiredRoles = to.meta.roles
      if (requiredRoles && requiredRoles.length > 0) {
        if (!requiredRoles.includes(userInfo.role)) {
          // 没有权限，重定向到仪表盘
          next('/dashboard')
          return
        }
      }
      next()
    }
  } else {
    next()
  }
})

export default router