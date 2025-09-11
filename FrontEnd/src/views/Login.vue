<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <img :src="logo" alt="Logo" class="logo">
        <h2>AI Course 智能教学系统</h2>
      </div>
      
      <el-tabs v-model="activeTab" class="login-tabs">
        <el-tab-pane label="学生登录" name="student">
          <el-form ref="studentFormRef" :model="studentForm" :rules="rules">
            <el-form-item prop="phone">
              <el-input 
                v-model="studentForm.phone"
                placeholder="请输入手机号"
                :prefix-icon="Phone"
              />
            </el-form-item>
            <el-form-item prop="password">
              <el-input 
                v-model="studentForm.password"
                type="password"
                placeholder="请输入密码"
                :prefix-icon="Lock"
                show-password
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleLogin('student')" :loading="loading" class="login-button">
                登录
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="教师登录" name="teacher">
          <el-form ref="teacherFormRef" :model="teacherForm" :rules="rules">
            <el-form-item prop="phone">
              <el-input 
                v-model="teacherForm.phone"
                placeholder="请输入手机号"
                :prefix-icon="Phone"
              />
            </el-form-item>
            <el-form-item prop="password">
              <el-input 
                v-model="teacherForm.password"
                type="password"
                placeholder="请输入密码"
                :prefix-icon="Lock"
                show-password
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleLogin('teacher')" :loading="loading" class="login-button">
                登录
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="管理员登录" name="admin">
          <el-form ref="adminFormRef" :model="adminForm" :rules="rules">
            <el-form-item prop="username">
              <el-input 
                v-model="adminForm.username"
                placeholder="请输入管理员账号"
                :prefix-icon="User"
              />
            </el-form-item>
            <el-form-item prop="password">
              <el-input 
                v-model="adminForm.password"
                type="password"
                placeholder="请输入密码"
                :prefix-icon="Lock"
                show-password
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleLogin('admin')" :loading="loading" class="login-button">
                登录
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>

      <div class="login-footer">
        <el-link type="primary" href="/register">立即注册</el-link>
        <el-divider direction="vertical" />
        <el-link type="primary" href="/forgot-password">忘记密码</el-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { Phone, Lock, User } from '@element-plus/icons-vue'

const router = useRouter()
const activeTab = ref('student')
const loading = ref(false)

// 表单引用
const studentFormRef = ref(null)
const teacherFormRef = ref(null)
const adminFormRef = ref(null)

const logo = 'https://i.imgur.com/SuVI48o.png'

// 表单数据
const studentForm = reactive({
  phone: '',
  password: ''
})

const teacherForm = reactive({
  phone: '',
  password: ''
})

const adminForm = reactive({
  username: '',
  password: ''
})

// 表单验证规则
const rules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { min: 1, message: '手机号不能为空', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能小于6位', trigger: 'blur' }
  ],
  username: [
    { required: true, message: '请输入管理员账号', trigger: 'blur' }
  ]
}

// 登录处理
const handleLogin = async (role) => {
  const formRef = role === 'admin' ? adminFormRef : (role === 'teacher' ? teacherFormRef : studentFormRef)
  const form = role === 'admin' ? adminForm : (role === 'teacher' ? teacherForm : studentForm)

  if (!formRef.value) return

  try {
    loading.value = true
    await formRef.value.validate()

    // 构建请求数据，管理员登录时将username映射为phone
    const requestData = role === 'admin' 
      ? { phone: form.username, password: form.password }
      : { ...form }

    // 调用登录API
    const response = await fetch('http://localhost:8000/user/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestData)
    })

    const data = await response.json()
    
    if (response.ok) {
      ElMessage({
        type: 'success',
        message: '登录成功'
      })
      // 存储用户信息和token
      localStorage.setItem('token', data.data.access_token)
      localStorage.setItem('userInfo', JSON.stringify(data.data.user))
      
      // 跳转到仪表盘
      router.push('/dashboard')
    } else {
      throw new Error(data.message || '登录失败')
    }
  } catch (error) {
    ElMessage({
      type: 'error',
      message: error.message || '登录失败，请重试'
    })
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
}

.login-box {
  width: 400px;
  padding: 30px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.logo {
  width: 80px;
  margin-bottom: 15px;
}

.login-tabs {
  margin-bottom: 20px;
}

.login-button {
  width: 100%;
}

.login-footer {
  margin-top: 20px;
  text-align: center;
}

:deep(.el-tabs__nav) {
  width: 100%;
  display: flex;
  justify-content: space-around;
}

:deep(.el-tabs__item) {
  flex: 1;
  text-align: center;
}
</style> 