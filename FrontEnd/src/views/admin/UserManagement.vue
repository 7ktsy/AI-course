<template>
  <div class="user-management">
    <!-- 页面状态提示 -->
    <el-alert
      title="用户管理页面已就绪"
      description="您可以查看、创建、编辑和删除用户账户"
      type="success"
      :closable="false"
      show-icon
      style="margin-bottom: 20px;"
    />
    
    <!-- 用户状态信息 -->
    <el-card class="status-card" shadow="hover">
      <template #header>
        <div class="status-header">
          <el-icon><UserFilled /></el-icon>
          <span>当前用户状态</span>
        </div>
      </template>
      <div class="status-content">
        <div class="status-item">
          <el-icon class="status-icon"><User /></el-icon>
          <div class="status-info">
            <div class="status-label">用户角色</div>
            <div class="status-value">
              <el-tag :type="getRoleType(userInfo.role)" size="small">
                {{ getRoleLabel(userInfo.role) }}
              </el-tag>
            </div>
          </div>
        </div>
        <div class="status-item">
          <el-icon class="status-icon"><Location /></el-icon>
          <div class="status-info">
            <div class="status-label">当前路由</div>
            <div class="status-value">{{ $route.path }}</div>
          </div>
        </div>
        <div class="status-item">
          <el-icon class="status-icon"><Key /></el-icon>
          <div class="status-info">
            <div class="status-label">登录状态</div>
            <div class="status-value">
              <el-tag :type="token ? 'success' : 'danger'" size="small">
                {{ token ? '已登录' : '未登录' }}
              </el-tag>
            </div>
          </div>
        </div>
      </div>
    </el-card>
    
    <!-- 顶部导航栏 -->
    <div class="top-nav">
      <div class="nav-left">
        <h1 class="page-title">
          <el-icon class="title-icon"><User /></el-icon>
          用户管理
        </h1>
        <p class="page-subtitle">管理系统中的所有用户账户</p>
      </div>
      <div class="nav-right">
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon> 添加用户
        </el-button>
        <el-button @click="refreshData">
          <el-icon><Refresh /></el-icon> 刷新
        </el-button>
        <el-button @click="router.push('/dashboard/overallview')">
          <el-icon><Back /></el-icon> 返回总览
        </el-button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <div class="search-section">
      <el-card shadow="never" class="search-card">
        <div class="search-row">
          <el-input
            v-model="searchQuery"
            placeholder="搜索用户名、手机号或学校"
            class="search-input"
            clearable
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          
          <el-select v-model="roleFilter" placeholder="角色筛选" clearable @change="handleSearch">
            <el-option label="全部角色" value="" />
            <el-option label="管理员" value="admin" />
            <el-option label="教师" value="teacher" />
            <el-option label="学生" value="student" />
          </el-select>
          
          <el-select v-model="statusFilter" placeholder="状态筛选" clearable @change="handleSearch">
            <el-option label="全部状态" value="" />
            <el-option label="活跃" value="active" />
            <el-option label="禁用" value="inactive" />
          </el-select>
        </div>
      </el-card>
    </div>

    <!-- 用户列表 -->
    <div class="user-list-section">
      <el-card shadow="never" class="list-card">
        <template #header>
          <div class="list-header">
            <span>用户列表 ({{ totalUsers }} 个用户)</span>
            <div class="header-actions">
              <el-dropdown @command="handleExportCommand">
                <el-button size="small">
                  <el-icon><Download /></el-icon> 导出
                  <el-icon class="el-icon--right"><ArrowDown /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="csv">导出为CSV</el-dropdown-item>
                    <el-dropdown-item command="selected">导出选中用户</el-dropdown-item>
                    <el-dropdown-item command="all">导出全部用户</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </template>

        <el-table
          :data="filteredUsers"
          v-loading="loading"
          stripe
          class="user-table"
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="55" />
          
          <el-table-column label="用户信息" min-width="200">
            <template #default="{ row }">
              <div class="user-info">
                <el-avatar :size="40" :src="row.avatar" class="user-avatar">
                  {{ row.username?.charAt(0).toUpperCase() }}
                </el-avatar>
                <div class="user-details">
                  <div class="user-name">{{ row.username }}</div>
                  <div class="user-phone">{{ row.phone }}</div>
                </div>
              </div>
            </template>
          </el-table-column>

          <el-table-column prop="university" label="学校/单位" width="150" />
          
          <el-table-column prop="role" label="角色" width="100">
            <template #default="{ row }">
              <el-tag :type="getRoleType(row.role)" size="small">
                {{ getRoleLabel(row.role) }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status === 'active' ? 'success' : 'danger'" size="small">
                {{ row.status === 'active' ? '活跃' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="created_at" label="注册时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>

          <el-table-column prop="last_login" label="最后登录" width="180">
            <template #default="{ row }">
              {{ row.last_login ? formatDate(row.last_login) : '1天前登录' }}
            </template>
          </el-table-column>

          <el-table-column label="操作" width="180" fixed="right">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-tooltip content="查看详情" placement="top">
                  <el-button 
                    size="small" 
                    type="info" 
                    text
                    @click="viewUserDetail(row)"
                    class="action-btn"
                  >
                    <el-icon><View /></el-icon>
                  </el-button>
                </el-tooltip>
                <el-tooltip content="编辑用户" placement="top">
                  <el-button 
                    size="small" 
                    type="primary" 
                    text
                    @click="editUser(row)"
                    class="action-btn"
                  >
                    <el-icon><Edit /></el-icon>
                  </el-button>
                </el-tooltip>
                <el-tooltip 
                  :content="row.role === 'admin' ? '不能删除管理员' : '删除用户'" 
                  placement="top"
                >
                  <el-button 
                    size="small" 
                    type="danger" 
                    text
                    @click="deleteUser(row)"
                    :disabled="row.role === 'admin'"
                    class="action-btn"
                  >
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </el-tooltip>
              </div>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination-wrapper">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="totalUsers"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </el-card>
    </div>

    <!-- 用户详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="用户详情"
      width="600px"
      :close-on-click-modal="false"
    >
      <div v-if="selectedUser" class="user-detail">
        <div class="detail-section">
          <h3>基本信息</h3>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="用户名">{{ selectedUser.username }}</el-descriptions-item>
            <el-descriptions-item label="手机号">{{ selectedUser.phone }}</el-descriptions-item>
            <el-descriptions-item label="学校/单位">{{ selectedUser.university || '未设置' }}</el-descriptions-item>
            <el-descriptions-item label="角色">
              <el-tag :type="getRoleType(selectedUser.role)">
                {{ getRoleLabel(selectedUser.role) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="职称">{{ selectedUser.title || '未设置' }}</el-descriptions-item>
            <el-descriptions-item label="部门">{{ selectedUser.department || '未设置' }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="selectedUser.status === 'active' ? 'success' : 'danger'">
                {{ selectedUser.status === 'active' ? '活跃' : '禁用' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="注册时间">{{ formatDate(selectedUser.created_at) }}</el-descriptions-item>
            <el-descriptions-item label="最后登录">
              {{ selectedUser.last_login ? formatDate(selectedUser.last_login) : '一天前登录' }}
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <div class="detail-section" v-if="selectedUser.role === 'student'">
          <h3>学习统计</h3>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="参与课程">{{ selectedUser.stats?.courses_enrolled || 0 }}门</el-descriptions-item>
            <el-descriptions-item label="完成作业">{{ selectedUser.stats?.assignments_completed || 0 }}个</el-descriptions-item>
            <el-descriptions-item label="总学习时长">{{ selectedUser.stats?.total_study_time || 0 }}小时</el-descriptions-item>
            <el-descriptions-item label="平均成绩">{{ selectedUser.stats?.average_score || 0 }}分</el-descriptions-item>
          </el-descriptions>
        </div>

        <div class="detail-section" v-if="selectedUser.role === 'teacher'">
          <h3>教学统计</h3>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="创建课程">{{ selectedUser.stats?.courses_created || 0 }}门</el-descriptions-item>
            <el-descriptions-item label="发布作业">{{ selectedUser.stats?.assignments_created || 0 }}个</el-descriptions-item>
            <el-descriptions-item label="学生数量">{{ selectedUser.stats?.total_students || 0 }}人</el-descriptions-item>
            <el-descriptions-item label="教案数量">{{ selectedUser.stats?.lessons_created || 0 }}个</el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
    </el-dialog>

    <!-- 创建/编辑用户对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingUser ? '编辑用户' : '创建用户'"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="userFormRef"
        :model="userForm"
        :rules="userFormRules"
        label-width="100px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" placeholder="请输入用户名" />
        </el-form-item>
        
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="userForm.phone" placeholder="请输入手机号" />
        </el-form-item>
        
        <el-form-item label="学校/单位" prop="university">
          <el-input v-model="userForm.university" placeholder="请输入学校或单位名称" />
        </el-form-item>
        
        <el-form-item label="职称" prop="title">
          <el-input v-model="userForm.title" placeholder="请输入职称" />
        </el-form-item>
        
        <el-form-item label="部门" prop="department">
          <el-input v-model="userForm.department" placeholder="请输入部门" />
        </el-form-item>
        
        <el-form-item label="角色" prop="role">
          <el-select v-model="userForm.role" placeholder="请选择角色">
            <el-option label="学生" value="student" />
            <el-option label="教师" value="teacher" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="密码" prop="password" v-if="!editingUser">
          <el-input v-model="userForm.password" type="password" placeholder="请输入密码" />
        </el-form-item>
        
        <el-form-item label="状态" prop="status">
          <el-select v-model="userForm.status" placeholder="请选择状态">
            <el-option label="活跃" value="active" />
            <el-option label="禁用" value="inactive" />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="submitUserForm" :loading="submitting">
          {{ editingUser ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  User, Plus, Refresh, Back, Search, Download, View, Edit, Delete,
  UserFilled, Location, Key, ArrowDown
} from '@element-plus/icons-vue'
import { exportUsers } from '@/utils/exportUtils'

// 获取router实例
const router = useRouter()

// 获取用户信息和token
const token = localStorage.getItem('token')
const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')

// 响应式数据
const loading = ref(false)
const users = ref([])
const selectedUser = ref(null)
const detailDialogVisible = ref(false)
const showCreateDialog = ref(false)
const editingUser = ref(null)
const submitting = ref(false)
const selectedUsers = ref([]) // 添加选中用户数组

// 搜索和筛选
const searchQuery = ref('')
const roleFilter = ref('')
const statusFilter = ref('')

// 分页
const currentPage = ref(1)
const pageSize = ref(20)
const totalUsers = ref(0)

// 表单
const userFormRef = ref()
const userForm = reactive({
  username: '',
  real_name: '',
  email: '',
  phone: '',
  role: 'student',
  password: '',
  status: 'active',
  university: '',
  title: '',
  department: ''
})

const userFormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号格式', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于 6 个字符', trigger: 'blur' }
  ],
  status: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ]
}

// 计算属性
const filteredUsers = computed(() => {
  let filtered = users.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(user => 
      user.username?.toLowerCase().includes(query) ||
      user.phone?.toLowerCase().includes(query) ||
      user.university?.toLowerCase().includes(query)
    )
  }

  if (roleFilter.value) {
    filtered = filtered.filter(user => user.role === roleFilter.value)
  }

  if (statusFilter.value) {
    filtered = filtered.filter(user => user.status === statusFilter.value)
  }

  return filtered
})

// API调用函数
const apiCall = async (url, options = {}) => {
  const token = localStorage.getItem('token')
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    }
  }
  
  const response = await fetch(`http://127.0.0.1:8000${url}`, {
    ...defaultOptions,
    ...options
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || '请求失败')
  }
  
  return response.json()
}

// 方法
const loadUsers = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams({
      page: currentPage.value.toString(),
      per_page: pageSize.value.toString()
    })
    
    if (searchQuery.value) params.append('search', searchQuery.value)
    if (roleFilter.value) params.append('role', roleFilter.value)
    if (statusFilter.value) params.append('status', statusFilter.value)
    
    const response = await apiCall(`/user/admin/users?${params}`)
    users.value = response.data.users || []
    totalUsers.value = response.data.total || 0
  } catch (error) {
    ElMessage.error('加载用户列表失败')
    console.error('Load users error:', error)
  } finally {
    loading.value = false
  }
}

const refreshData = () => {
  loadUsers()
}

const handleSearch = () => {
  currentPage.value = 1
  loadUsers()
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  loadUsers()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  loadUsers()
}

const viewUserDetail = async (user) => {
  try {
    const response = await apiCall(`/user/admin/users/${user.id}`)
    selectedUser.value = response.data
    detailDialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取用户详情失败')
    console.error('Get user detail error:', error)
  }
}

const editUser = (user) => {
  editingUser.value = user
  Object.assign(userForm, {
    username: user.username,
    phone: user.phone,
    role: user.role,
    status: user.status,
    university: user.university || '',
    title: user.title || '',
    department: user.department || '',
    password: ''
  })
  showCreateDialog.value = true
}

const deleteUser = async (user) => {
  if (user.role === 'admin') {
    ElMessage.warning('不能删除管理员账户')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${user.username}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await apiCall(`/user/admin/users/${user.id}`, { method: 'DELETE' })
    ElMessage.success('用户删除成功')
    loadUsers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除用户失败')
      console.error('Delete user error:', error)
    }
  }
}

const submitUserForm = async () => {
  try {
    await userFormRef.value.validate()
    submitting.value = true

    const userData = {
      username: userForm.username,
      phone: userForm.phone,
      role: userForm.role,
      status: userForm.status,
      university: userForm.university,
      title: userForm.title,
      department: userForm.department
    }

    if (!editingUser.value) {
      userData.password = userForm.password
    }

    if (editingUser.value) {
      await apiCall(`/user/admin/users/${editingUser.value.id}`, {
        method: 'PUT',
        body: JSON.stringify(userData)
      })
      ElMessage.success('用户更新成功')
    } else {
      await apiCall('/user/admin/users', {
        method: 'POST',
        body: JSON.stringify(userData)
      })
      ElMessage.success('用户创建成功')
    }

    showCreateDialog.value = false
    resetUserForm()
    loadUsers()
  } catch (error) {
    if (error !== false) {
      ElMessage.error(editingUser.value ? '更新用户失败' : '创建用户失败')
      console.error('Submit user form error:', error)
    }
  } finally {
    submitting.value = false
  }
}

const resetUserForm = () => {
  editingUser.value = null
  Object.assign(userForm, {
    username: '',
    phone: '',
    role: 'student',
    password: '',
    status: 'active',
    university: '',
    title: '',
    department: ''
  })
  userFormRef.value?.resetFields()
}

const handleExportCommand = (command) => {
  try {
    if (command === 'csv') {
      const count = exportUsers(filteredUsers.value, '用户管理')
      ElMessage.success(`成功导出 ${count} 条用户记录`)
    } else if (command === 'selected') {
      // 导出选中用户
      if (selectedUsers.value.length === 0) {
        ElMessage.warning('请先选择要导出的用户')
        return
      }
      const count = exportUsers(selectedUsers.value, '选中用户')
      ElMessage.success(`成功导出 ${count} 条选中用户记录`)
    } else if (command === 'all') {
      // 导出全部用户
      const count = exportUsers(users.value, '全部用户')
      ElMessage.success(`成功导出 ${count} 条用户记录`)
    }
  } catch (error) {
    ElMessage.error('导出失败：' + error.message)
  }
}

const getRoleType = (role) => {
  const types = {
    admin: 'danger',
    teacher: 'warning',
    student: 'success'
  }
  return types[role] || 'info'
}

const getRoleLabel = (role) => {
  const labels = {
    admin: '管理员',
    teacher: '教师',
    student: '学生'
  }
  return labels[role] || role
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString('zh-CN')
}

const handleSelectionChange = (selection) => {
  selectedUsers.value = selection
  console.log('Selected users:', selection)
}

// 生命周期
onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.user-management {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.top-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.nav-left {
  display: flex;
  flex-direction: column;
}

.page-title {
  display: flex;
  align-items: center;
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.title-icon {
  margin-right: 8px;
  color: #409eff;
}

.page-subtitle {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.nav-right {
  display: flex;
  gap: 12px;
}

.search-section {
  margin-bottom: 20px;
}

.search-card {
  border: none;
}

.search-row {
  display: flex;
  gap: 16px;
  align-items: center;
}

.search-input {
  flex: 1;
  max-width: 300px;
}

.user-list-section {
  margin-bottom: 20px;
}

.list-card {
  border: none;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.user-table {
  margin-bottom: 20px;
}

.user-table :deep(.el-table__header) {
  background-color: #f8f9fa;
}

.user-table :deep(.el-table__header th) {
  background-color: #f8f9fa;
  color: #606266;
  font-weight: 600;
  border-bottom: 2px solid #e4e7ed;
}

.user-table :deep(.el-table__row:hover) {
  background-color: #f5f7fa;
}

.user-table :deep(.el-table__row td) {
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  flex-shrink: 0;
}

.user-details {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-weight: 600;
  color: #303133;
}

.user-phone {
  font-size: 12px;
  color: #909399;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.user-detail {
  padding: 20px 0;
}

.detail-section {
  margin-bottom: 24px;
}

.detail-section h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  border-bottom: 2px solid #409eff;
  padding-bottom: 8px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .user-management {
    padding: 10px;
  }
  
  .top-nav {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .search-row {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-input {
    max-width: none;
  }
}

/* 状态卡片样式 */
.status-card {
  margin-bottom: 20px;
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.status-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #303133;
}

.status-header .el-icon {
  color: #409eff;
}

.status-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  transition: all 0.3s ease;
}

.status-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.status-icon {
  font-size: 20px;
  color: #409eff;
  background: #e6f7ff;
  padding: 8px;
  border-radius: 6px;
}

.status-info {
  flex: 1;
}

.status-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
  font-weight: 500;
}

.status-value {
  font-size: 14px;
  color: #303133;
  font-weight: 600;
}

/* 操作按钮样式 */
.action-buttons {
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: center;
}

.action-btn {
  padding: 6px 8px;
  border-radius: 6px;
  transition: all 0.3s ease;
  min-width: 32px;
  height: 32px;
}

.action-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.action-btn .el-icon {
  font-size: 16px;
}
</style> 