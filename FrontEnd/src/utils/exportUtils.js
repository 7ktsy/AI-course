/**
 * 导出工具函数
 */

/**
 * 导出数据为CSV文件
 * @param {Array} data - 要导出的数据数组
 * @param {string} filename - 文件名（不包含扩展名）
 * @param {string} encoding - 编码格式，默认为utf-8
 */
export const exportToCSV = (data, filename, encoding = 'utf-8') => {
  if (!data || data.length === 0) {
    throw new Error('没有数据可导出')
  }

  // 生成CSV内容
  const headers = Object.keys(data[0])
  const csvContent = [
    headers.join(','),
    ...data.map(row => 
      headers.map(header => {
        const value = row[header] || ''
        // 确保值是字符串类型
        const stringValue = String(value)
        // 处理包含逗号、换行符或双引号的值
        if (stringValue.includes(',') || stringValue.includes('\n') || stringValue.includes('"')) {
          return `"${stringValue.replace(/"/g, '""')}"`
        }
        return stringValue
      }).join(',')
    )
  ].join('\n')

  // 创建下载链接
  const blob = new Blob([`\ufeff${csvContent}`], { 
    type: `text/csv;charset=${encoding};` 
  })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${filename}_${new Date().toLocaleDateString()}.csv`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)

  return data.length
}

/**
 * 导出用户数据
 * @param {Array} users - 用户数据数组
 * @param {string} filename - 文件名前缀
 */
export const exportUsers = (users, filename = '用户管理') => {
  const exportData = users.map(user => ({
    用户名: user.username,
    手机号: user.phone,
    学校单位: user.university || '未设置',
    角色: getRoleLabel(user.role),
    职称: user.title || '未设置',
    部门: user.department || '未设置',
    状态: user.status === 'active' ? '活跃' : '禁用',
    注册时间: formatDate(user.created_at),
    最后登录: user.last_login ? formatDate(user.last_login) : '一天前登录'
  }))

  return exportToCSV(exportData, filename)
}

/**
 * 导出课程数据
 * @param {Array} courses - 课程数据数组
 * @param {string} filename - 文件名前缀
 */
export const exportCourses = (courses, filename = '课程管理') => {
  const exportData = courses.map(course => ({
    课程标题: course.title,
    课程描述: course.description,
    教师姓名: course.teacher?.username || '未分配',
    教师手机: course.teacher?.phone || '未分配',
    教师单位: course.teacher?.university || '未分配',
    学生数量: course.student_count || 0,
    资料数量: course.materials_count || 0,
    任务数量: course.assignments_count || 0,
    创建时间: formatDate(course.created_at)
  }))

  return exportToCSV(exportData, filename)
}

/**
 * 导出课程资料数据
 * @param {Array} materials - 资料数据数组
 * @param {string} courseTitle - 课程标题
 */
export const exportMaterials = (materials, courseTitle = '课程资料') => {
  const exportData = materials.map(material => ({
    资料ID: material.id,
    标题: material.title,
    描述: material.description,
    文件名: material.filename,
    状态: getStatusLabel(material.status),
    上传时间: formatDate(material.uploadtime),
    RAG文档ID: material.rag_doc_id || '未设置'
  }))

  return exportToCSV(exportData, `${courseTitle}_课程资料`)
}

/**
 * 格式化日期
 * @param {string} dateString - 日期字符串
 * @returns {string} 格式化后的日期
 */
const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString('zh-CN')
}

/**
 * 获取角色标签
 * @param {string} role - 角色代码
 * @returns {string} 角色标签
 */
const getRoleLabel = (role) => {
  const labels = {
    admin: '管理员',
    teacher: '教师',
    student: '学生'
  }
  return labels[role] || role
}

/**
 * 获取状态标签
 * @param {string} status - 状态代码
 * @returns {string} 状态标签
 */
const getStatusLabel = (status) => {
  const labels = {
    'pending': '待处理',
    'parsing': '解析中',
    'parsed': '已解析',
    'failed': '解析失败'
  }
  return labels[status] || status
}

/**
 * 下载文件
 * @param {string} url - 文件URL
 * @param {string} filename - 文件名
 * @param {Object} options - 请求选项
 */
export const downloadFile = async (url, filename, options = {}) => {
  try {
    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
        ...options.headers
      },
      ...options
    })
    
    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`下载失败 (${response.status}): ${errorText}`)
    }
    
    const blob = await response.blob()
    
    // 检查blob是否为空
    if (blob.size === 0) {
      throw new Error('下载的文件为空')
    }
    
    const downloadUrl = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(downloadUrl)
    
    return true
  } catch (error) {
    console.error('Download error:', error)
    throw error
  }
}

/**
 * 批量下载文件
 * @param {Array} fileIds - 文件ID数组
 * @param {string} filename - 压缩包文件名
 */
export const batchDownloadFiles = async (fileIds, filename = '批量下载') => {
  try {
    const response = await fetch('http://127.0.0.1:8000/material/batch-download/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({ material_ids: fileIds })
    })

    if (!response.ok) {
      throw new Error('批量下载失败')
    }

    const blob = await response.blob()
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${filename}_${new Date().toLocaleDateString()}.zip`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)

    return fileIds.length
  } catch (error) {
    console.error('Batch download error:', error)
    throw error
  }
} 