<template>
  <div class="profile-container">
    <el-card class="profile-card">
      <template #header>
        <div class="card-header">
          <span>个人资料</span>
          <el-button type="primary" @click="handleEdit">编辑资料</el-button>
        </div>
      </template>
      
      <el-form :model="userInfo" label-width="100px" v-if="!isEditing">
        <el-form-item label="用户名">
          <span>{{ userInfo.username }}</span>
        </el-form-item>
        <el-form-item label="手机号">
          <span>{{ userInfo.phone }}</span>
        </el-form-item>
        <el-form-item label="角色">
          <span>{{ roleMap[userInfo.role] || '未知角色' }}</span>
        </el-form-item>
        <el-form-item label="所属院校" v-if="userInfo.university">
          <span>{{ userInfo.university }}</span>
        </el-form-item>
        <el-form-item label="职称" v-if="userInfo.title">
          <span>{{ userInfo.title }}</span>
        </el-form-item>
        <el-form-item label="所属院系" v-if="userInfo.department">
          <span>{{ userInfo.department }}</span>
        </el-form-item>
      </el-form>

      <el-form
        v-else
        ref="formRef"
        :model="editForm"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="editForm.username" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="editForm.phone" disabled />
        </el-form-item>
        <el-form-item label="所属院校" prop="university">
          <el-input v-model="editForm.university" />
        </el-form-item>
        <el-form-item label="职称" prop="title" v-if="userInfo.role === 'teacher'">
          <el-input v-model="editForm.title" />
        </el-form-item>
        <el-form-item label="所属院系" prop="department">
          <el-input v-model="editForm.department" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSave">保存</el-button>
          <el-button @click="isEditing = false">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

const isEditing = ref(false)
const formRef = ref(null)

const roleMap = {
  student: '学生',
  teacher: '教师',
  admin: '管理员'
}

const userInfo = reactive(JSON.parse(localStorage.getItem('userInfo') || '{}'))

const editForm = reactive({
  username: userInfo.username || '',
  phone: userInfo.phone || '',
  university: userInfo.university || '',
  title: userInfo.title || '',
  department: userInfo.department || ''
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
  ],
  university: [
    { required: true, message: '请输入所属院校', trigger: 'blur' }
  ],
  department: [
    { required: true, message: '请输入所属院系', trigger: 'blur' }
  ]
}

const handleEdit = () => {
  isEditing.value = true
}

const handleSave = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    // TODO: 调用更新用户信息的API
    
    Object.assign(userInfo, editForm)
    localStorage.setItem('userInfo', JSON.stringify(userInfo))
    
    ElMessage({
      type: 'success',
      message: '保存成功'
    })
    
    isEditing.value = false
  } catch (error) {
    ElMessage({
      type: 'error',
      message: '表单验证失败'
    })
  }
}
</script>

<style scoped>
.profile-container {
  padding: 20px;
}

.profile-card {
  max-width: 800px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

:deep(.el-form-item__label) {
  font-weight: bold;
}
</style> 