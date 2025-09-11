<template>
  <div class="app-wrapper">
    <!-- 顶部导航栏 -->
    <el-header class="header">
      <div class="header-left">
        <div class="logo">
          <img :src="logo" alt="Logo" class="logo-img">
          <span class="logo-text">AI Course</span>
        </div>
        <div class="search-container">
          <el-input
            v-model="searchQuery"
            placeholder="搜索课程..."
            :prefix-icon="Search"
            clearable
            @keyup.enter="handleSearch"
          />
        </div>
      </div>
      <div class="header-right">
        <!-- AI对话开关 -->
        <div class="ai-chat-switch" @click="toggleAIChat">
          <div class="switch-track" :class="{ 'active': showAIChat }">
            <div class="switch-thumb" :class="{ 'active': showAIChat }">
              <el-icon v-if="showAIChat"><ChatDotRound /></el-icon>
              <el-icon v-else><ChatLineRound /></el-icon>
            </div>
          </div>
          <span class="switch-label">AI助手</span>
        </div>
        
        <!-- 语音AI助手开关 -->
        <div class="voice-ai-chat-switch" @click="toggleVoiceAIChat">
          <div class="switch-track" :class="{ 'active': showVoiceAIChat }">
            <div class="switch-thumb" :class="{ 'active': showVoiceAIChat }">
              <el-icon v-if="showVoiceAIChat"><Microphone /></el-icon>
              <el-icon v-else><Microphone /></el-icon>
            </div>
          </div>
          <span class="switch-label">语音助手</span>
        </div>
        <el-badge :value="notificationCount" class="notification">
          <div class="notification-icon">
            <el-icon><Bell /></el-icon>
          </div>
        </el-badge>
        <div class="user-info">
          <el-avatar :src="userAvatar" :size="40" />
          <span class="user-name">{{ userName }}</span>
          <span class="user-role">{{ userRole }}</span>
        </div>
        <div class="logout" @click="handleLogout">
          <i class="bi bi-box-arrow-right"></i>
          <span>退出登录</span>
        </div>
      </div>
    </el-header>

    <div class="main-container">
      <!-- 侧边栏 -->
      <el-aside width="220px" class="sidebar">
        <el-menu
          :default-active="activeMenu"
          class="menu"
          :collapse="isCollapse"
          @select="handleSelect"
        >
          <template v-for="menu in menus" :key="menu.path">
            <el-menu-item v-if="!menu.children" :index="menu.path">
              <i :class="menu.icon"></i>
              <template #title>{{ menu.title }}</template>
            </el-menu-item>

            
            <el-sub-menu v-else :index="menu.path">
              <template #title>
                <i :class="menu.icon"></i>
                <span>{{ menu.title }}</span>
              </template>
              <el-menu-item 
                v-for="child in menu.children"
                :key="child.path"
                :index="child.path"
              >
                {{ child.title }}
              </el-menu-item>
            </el-sub-menu>
          </template>
        </el-menu>
      </el-aside>

      <!-- 主内容区域 -->
      <el-main class="main-content">
        <el-breadcrumb class="breadcrumb">
          <el-breadcrumb-item>首页</el-breadcrumb-item>
          <el-breadcrumb-item v-if="currentMenuTitle !== '首页概览'">{{ currentMenuTitle }}</el-breadcrumb-item>
        </el-breadcrumb>
        
        <div class="content-body">
          <!-- 所有页面的内容都通过路由视图显示 -->
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </div>
      </el-main>
    </div>

    <!-- 底部信息 -->
    <el-footer class="footer">
      <div class="footer-content">
        <span class="copyright">版权所有 © 2025 AI Course 智能教学系统</span>
        <span class="divider">|</span>
        <el-link type="primary" href="/about" class="footer-link">关于我们</el-link>
        <span class="divider">|</span>
        <el-link type="primary" href="/contact" class="footer-link">联系我们</el-link>
        <span class="divider">|</span>
        <el-link type="primary" href="/help" class="footer-link">帮助中心</el-link>
      </div>
    </el-footer>

    <!-- AI对话抽屉 -->
    <AIChatDrawer v-model="showAIChat" />
    <VoiceAIChatDrawer v-model="showVoiceAIChat" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search,
  Bell,
  House,
  Document,
  User,
  Setting,
  SwitchButton,
  ChatDotRound,
  ChatLineRound,
  Microphone
} from '@element-plus/icons-vue'
import AIChatDrawer from '@/components/AIChatDrawer.vue'
import VoiceAIChatDrawer from '@/components/VoiceAIChatDrawer.vue'

const logo = 'https://i.imgur.com/SuVI48o.png' // 使用在线图片URL替代本地图片
const router = useRouter()
const searchQuery = ref('')
const isCollapse = ref(false)
const notificationCount = ref(0)
const showAIChat = ref(false)
const showVoiceAIChat = ref(false) // 新增语音助手开关状态

// 用户信息
const userInfo = computed(() => {
  return JSON.parse(localStorage.getItem('userInfo') || '{}')
})

const userName = computed(() => userInfo.value.username || '未登录')
const userRole = computed(() => {
  const roles = {
    student: '学生',
    teacher: '教师',
    admin: '管理员'
  }
  return roles[userInfo.value.role] || '未知角色'
})
const userAvatar = computed(() => userInfo.value.avatar || '/default-avatar.png')

// 菜单配置
const menus = computed(() => {
  const role = userInfo.value.role
  return menuConfig[role] || []
})

// 当前菜单标题
const currentMenuTitle = ref('首页概览')

// 当前日期
const currentDate = computed(() => {
  return new Date().toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  })
})

// 菜单配置，使用 Bootstrap Icons
const menuConfig = {
  student: [
    { path: '/dashboard', title: '首页概览', icon: 'bi bi-house' },
    { path: '/dashboard/courses', title: '我的课程', icon: 'bi bi-book' },
    { path: '/dashboard/all-courses', title: '全部课程', icon: 'bi bi-search' },
    { path: '/dashboard/writing-assistant', title: 'AI写作助手', icon: 'bi bi-pen' },
    { path: '/dashboard/my-homework', title: '我的作业', icon: 'bi bi-pencil-square' },
    { path: '/dashboard/student/real-time-practice', title: '实时智能练习', icon: 'bi bi-lightning' },
    { path: '/dashboard/photo-search-question', title: '拍照搜题', icon: 'bi bi-camera' },
    { path: '/dashboard/grades', title: '成绩查询', icon: 'bi bi-graph-up' },
    { path: '/dashboard/learning-assistant', title: '学习助手', icon: 'bi bi-robot' },
    { path: '/dashboard/knowledge-graph', title: '知识图谱', icon: 'bi bi-diagram-3' }
  ],
  teacher: [
    { path: '/dashboard', title: '首页概览', icon: 'bi bi-house' },
    { path: '/dashboard/courses', title: '我的课程', icon: 'bi bi-book' },
    { path: '/dashboard/writing-assistant', title: 'AI写作助手', icon: 'bi bi-pen' },
    { path: '/dashboard/class-management', title: '班级管理', icon: 'bi bi-people' },
    { path: '/dashboard/teaching-plan-board', title: '教学计划看板', icon: 'bi bi-calendar-check' },
    { path: '/dashboard/prepare-lesson', 
      title: '备课帮助', 
      icon: 'bi bi-journal-text',
      children: [
        {path: '/dashboard/preparation', title: '智能备课'},
        {path: '/dashboard/ppt-generation', title: 'PPT生成'},
        {path: '/dashboard/preparation-manage', title: '教案管理'}
      ]
    },
    { 
      path: '/dashboard/question-center', 
      title: '题目中心', 
      icon: 'bi bi-collection',
      children: [
        { path: '/dashboard/ai-question-generator', title: 'AI智能出题' },
        { path: '/dashboard/question-bank', title: '题库管理' }
      ]
    },
    { path: '/dashboard/homework-management', 
      title: '作业管理', 
      icon: 'bi bi-pencil-square',
      children:[
        {path: '/dashboard/homework-list', title: '作业列表'}
      ]
    }
  ],
  admin: [
    { path: '/dashboard/overallview', title: '系统概览', icon: 'bi bi-house' },
    { path: '/dashboard/users', title: '用户管理', icon: 'bi bi-people' },
    { path: '/dashboard/admin-courses', title: '课程管理', icon: 'bi bi-book' },
    { path: '/dashboard/writing-assistant', title: 'AI写作助手', icon: 'bi bi-pen' },
    { path: '/dashboard/chat-management', title: '聊天助手管理', icon: 'bi bi-chat-dots' },
    { path: '/dashboard/model-configuration', title: '模型配置', icon: 'bi bi-gear' },
    { path: '/dashboard/system-settings', title: '系统设置', icon: 'bi bi-gear' }
  ]
}

// 当前激活的菜单项
const activeMenu = computed(() => {
  return router.currentRoute.value.path
})

// 面包屑导航
const breadcrumbs = computed(() => {
  const route = router.currentRoute.value
  const result = [{ path: '/dashboard', title: '首页' }]
  
  if (route.path !== '/dashboard') {
    const menu = menus.value.find(m => m.path === route.path)
    if (menu) {
      result.push({ path: route.path, title: menu.title })
    }
  }
  
  return result
})

// 处理搜索
const handleSearch = () => {
  if (!searchQuery.value.trim()) return
  // 实现搜索逻辑
  console.log('搜索:', searchQuery.value)
}

// 处理菜单选择
const handleSelect = (path) => {
  // 从菜单配置中找到对应的菜单项
  const role = userInfo.value.role
  const menuItems = menuConfig[role] || []
  
  // 查找匹配的菜单项（包括子菜单）
  const findMenuItem = (items) => {
    for (const item of items) {
      if (item.path === path) {
        return item
      }
      if (item.children) {
        const found = item.children.find(child => child.path === path)
        if (found) {
          return found
        }
      }
    }
    return null
  }

  const selectedMenu = findMenuItem(menuItems)
  if (selectedMenu) {
    currentMenuTitle.value = selectedMenu.title
  }
  
  // 导航到选中的路径
  router.push(path)
}

// 处理用户下拉菜单命令
const handleCommand = async (command) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'settings':
      router.push('/settings')
      break
    case 'logout':
      try {
        await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        // 清除用户信息和token
        localStorage.removeItem('token')
        localStorage.removeItem('userInfo')
        
        ElMessage({
          type: 'success',
          message: '已成功退出登录'
        })
        
        router.push('/login')
      } catch {
        // 用户取消退出
      }
      break
  }
}

// 独立的退出登录处理函数
const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    // 清除所有相关的本地存储
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
    localStorage.removeItem('isLoggedIn')
    localStorage.removeItem('userRole')
    localStorage.removeItem('accessToken')
    
    ElMessage({
      type: 'success',
      message: '已成功退出登录'
    })
    
    // 修改为跳转到首页
    router.push('/')
  } catch {
    // 用户取消退出
  }
}

// 切换AI对话开关
const toggleAIChat = () => {
  showAIChat.value = !showAIChat.value
}

// 切换语音AI助手开关
const toggleVoiceAIChat = () => {
  showVoiceAIChat.value = !showVoiceAIChat.value
}

// 监听语音导航事件
const handleVoiceNavigationEvent = (event) => {
  const { type } = event
  
  switch (type) {
    case 'voiceNavigation:openAIChat':
      showAIChat.value = true
      break
    case 'voiceNavigation:openVoiceAIChat':
      showVoiceAIChat.value = true
      break
  }
}

// 组件挂载时添加事件监听
onMounted(() => {
  window.addEventListener('voiceNavigation:openAIChat', handleVoiceNavigationEvent)
  window.addEventListener('voiceNavigation:openVoiceAIChat', handleVoiceNavigationEvent)
})

// 组件卸载时移除事件监听
onUnmounted(() => {
  window.removeEventListener('voiceNavigation:openAIChat', handleVoiceNavigationEvent)
  window.removeEventListener('voiceNavigation:openVoiceAIChat', handleVoiceNavigationEvent)
})
</script>

<style scoped>
.app-wrapper {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.header {
  flex-shrink: 0;
  background-color: #000000;
  color: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 60px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 30px;
  flex: 1;
}

.logo {
  display: flex;
  align-items: center;
  gap: 15px;
  min-width: 180px;
}

.logo-img {
  height: 40px;
  width: auto;
}

.logo-text {
  font-family: "Snap ITC";
  font-size: 20px;
  color: #fff;
  white-space: nowrap; /* 防止文字换行 */
}

.search-container {
  width: 400px;
  margin: 0 20px;
}

:deep(.el-input__wrapper) {
  background-color: #1f1f1f;
  border: none;
  box-shadow: none;
}

:deep(.el-input__inner) {
  color: #fff;
}

:deep(.el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.7);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.ai-chat-switch {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  user-select: none;
  padding: 4px 8px;
  border-radius: 6px;
  transition: background-color 0.3s ease;
}

.ai-chat-switch:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.voice-ai-chat-switch {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  user-select: none;
  padding: 4px 8px;
  border-radius: 6px;
  transition: background-color 0.3s ease;
}

.voice-ai-chat-switch:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.switch-track {
  width: 50px;
  height: 28px;
  border-radius: 14px;
  background-color: #e0e0e0;
  position: relative;
  transition: background-color 0.3s ease;
}

.switch-track.active {
  background-color: #409EFF;
}

.switch-thumb {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: #fff;
  position: absolute;
  top: 2px;
  left: 2px;
  transition: transform 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.switch-thumb.active {
  transform: translateX(22px);
}

.switch-thumb .el-icon {
  font-size: 12px;
  color: #666;
}

.switch-thumb.active .el-icon {
  color: #409EFF;
}

.switch-label {
  font-size: 14px;
  color: #fff;
  font-weight: 500;
}

.notification {
  cursor: pointer;
  margin: 0 10px;
}

.notification-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px;
  border-radius: 50%;
  transition: background-color 0.3s ease;
  width: 36px;
  height: 36px;
}

.notification-icon:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.notification-icon .el-icon {
  font-size: 18px;
  color: #fff !important;
  display: block !important;
  visibility: visible !important;
}

:deep(.el-badge__content) {
  background-color: #e84118;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0 10px;
}

.user-name, .user-role {
  color: #fff;
  font-size: 14px;
}

.user-role {
  color: rgba(255, 255, 255, 0.7);
}

.logout {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #fff;
  cursor: pointer;
  padding: 8px 15px;
  border-radius: 4px;
  transition: all 0.3s;
  background-color: transparent;
}

.logout:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.logout i {
  font-size: 18px;
}

.logout span {
  font-size: 14px;
}

.content-loading {
  text-align: center;
  padding: 40px;
  color: #666;
}

.content-loading h2 {
  font-size: 24px;
  font-weight: normal;
}

.content-body {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  min-height: calc(100vh - 200px);
}

.content-body h2 {
  font-size: 24px;
  color: #666;
  font-weight: normal;
}

.main-container {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.sidebar {
  background: white;
  border-right: 1px solid #e4e7ed;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
  overflow-y: auto;
}

.menu {
  border-right: none;
}

.main-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background: #f5f7fa;
}

.breadcrumb {
  margin-bottom: 20px;
  padding: 10px 0;
  background: white;
  border-radius: 8px;
  padding-left: 15px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.footer {
  flex-shrink: 0;
  background-color: #000000;
  color: #fff;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.footer-content {
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  font-size: 14px;
}

.copyright {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 400;
}

.divider {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.4);
  margin: 0 5px;
}

.footer-link {
  font-size: 14px;
  color: #fdfdfd !important;
  text-decoration: none;
  transition: color 0.3s ease;
}

.footer-link:hover {
  color: #ffffff !important;
  text-decoration: underline;
}

:deep(.el-divider--vertical) {
  background-color: rgba(255, 255, 255, 0.5);
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

:deep(.el-menu-item i),
:deep(.el-sub-menu i) {
  margin-right: 5px;
  width: 24px;
  text-align: center;
  font-size: 18px;
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