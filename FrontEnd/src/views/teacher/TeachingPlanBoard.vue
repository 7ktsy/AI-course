<template>
  <div class="teaching-plan-board">
    <!-- 头部工具栏 -->
    <div class="board-header">
      <div class="header-left">
        <h2>📋 教学计划看板</h2>
        <p class="subtitle">协作式教学计划管理（所有教师共用）</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="showAddEventDialog = true">
          <el-icon><Plus /></el-icon>
          添加教学事件
        </el-button>
        <el-button @click="exportBoard">
          <el-icon><Download /></el-icon>
          导出看板
        </el-button>
      </div>
    </div>

    <!-- 看板主体 -->
    <div class="board-container">
      <!-- 左侧事件列表 -->
      <div class="events-panel">
        <div class="panel-header">
          <h3>📝 教学事件库</h3>
          <el-input
            v-model="searchKeyword"
            placeholder="搜索事件..."
            prefix-icon="Search"
            clearable
            size="small"
            style="margin-top: 8px;"
          />
        </div>
        <div class="events-list">
          <div
            v-for="event in filteredEvents"
            :key="event.id"
            class="event-item"
            :style="{ borderLeftColor: event.color }"
            draggable="true"
            @dragstart="handleDragStart(event, $event)"
          >
            <div class="event-content">
              <h4>{{ event.title }}</h4>
              <p>{{ event.description }}</p>
              <div class="event-meta">
                <el-tag size="small" :type="getEventTypeTag(event.type)">
                  {{ getEventTypeName(event.type) }}
                </el-tag>
                <span class="event-duration">{{ event.duration }}分钟</span>
              </div>
            </div>
            <div class="event-actions">
              <el-button size="small" @click="editEvent(event)">
                <el-icon><Edit /></el-icon>
              </el-button>
              <el-button size="small" type="danger" @click="deleteEvent(event.id)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
        </div>

      </div>

      <!-- 右侧看板区域 -->
      <div class="board-area">
        <div class="board-header-info">
          <div class="board-info">
            <h3>📅 教学计划周视图</h3>
            <p>拖拽事件到时间表中，调整教学安排</p>
          </div>
          <div class="board-controls">
            <el-button-group>
              <el-button 
                size="small" 
                :type="selectedView === 'week' ? 'primary' : ''"
                @click="selectedView = 'week'"
              >
                周视图
              </el-button>
              <el-button 
                size="small" 
                :type="selectedView === 'day' ? 'primary' : ''"
                @click="selectedView = 'day'"
              >
                日视图
              </el-button>
            </el-button-group>
            <el-date-picker
              v-model="selectedDate"
              type="week"
              size="small"
              placeholder="选择周次"
              format="YYYY 第 WW 周"
              value-format="YYYY-MM-DD"
              @change="handleDateChange"
            />
            <el-button-group>
              <el-button 
                size="small" 
                :type="isExpanded ? '' : 'primary'"
                @click="isExpanded = false"
              >
                <el-icon><ZoomOut /></el-icon>
                正常
              </el-button>
              <el-button 
                size="small" 
                :type="isExpanded ? 'primary' : ''"
                @click="isExpanded = true"
              >
                <el-icon><ZoomIn /></el-icon>
                展开
              </el-button>
            </el-button-group>
          </div>
        </div>

        <!-- 周视图时间表 -->
        <div class="week-timeline-container">
          <!-- 时间轴头部 -->
          <div class="timeline-header">
            <div class="time-column">时间</div>
            <div 
              v-for="day in weekDays" 
              :key="day.date"
              class="day-column"
            >
              <div class="day-header">
                <div class="day-name">{{ day.name }}</div>
                <div class="day-date">{{ day.date }}</div>
              </div>
            </div>
          </div>

          <!-- 时间表主体 -->
          <div class="timeline-body">
            <div 
              v-for="hour in 13" 
              :key="hour + 8"
              class="time-row"
            >
              <!-- 时间标签 -->
              <div class="time-label">
                {{ (hour + 8).toString().padStart(2, '0') }}:00
              </div>
              
              <!-- 每天的时段 -->
              <div 
                v-for="day in weekDays" 
                :key="day.date"
                class="day-slot"
                :data-day="day.date"
                :data-hour="hour + 8"
                @dragover="handleDragOver"
                @drop="handleDrop"
              >
                <!-- 已放置的事件 -->
                <div
                  v-for="placedEvent in getPlacedEventsForDayAndHour(day.date, hour + 8)"
                  :key="placedEvent.id"
                  class="placed-event-card"
                  :style="{
                    backgroundColor: getEventBackgroundColor(placedEvent.color),
                    borderLeftColor: placedEvent.color,
                    borderLeftWidth: '4px',
                    height: `${Math.max(70, (placedEvent.duration / 60) * 70)}px`,
                    top: `${getEventOffset(placedEvent)}px`
                  }"
                  @click="editPlacedEvent(placedEvent)"
                >
                  <div class="event-card-content">
                    <div class="event-card-title">{{ placedEvent.title }}</div>
                    <div class="event-card-time">
                      {{ formatEventTime(placedEvent.startHour) }} - {{ formatEventEndTime(placedEvent) }}
                    </div>
                    <div class="event-card-teacher">{{ placedEvent.teacherName }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 展开控制 -->
      </div>
    </div>

    <!-- 添加/编辑事件对话框 -->
    <el-dialog
      v-model="showAddEventDialog"
      :title="editingEvent ? '编辑教学事件' : '添加教学事件'"
      width="600px"
    >
      <el-form :model="eventForm" :rules="eventRules" ref="eventFormRef" label-width="100px">
        <el-form-item label="事件标题" prop="title">
          <el-input v-model="eventForm.title" placeholder="请输入事件标题" />
        </el-form-item>
        <el-form-item label="事件描述" prop="description">
          <el-input
            v-model="eventForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入事件描述"
          />
        </el-form-item>
        <el-form-item label="事件类型" prop="type">
          <el-select v-model="eventForm.type" placeholder="选择事件类型">
            <el-option label="理论课" value="lecture" />
            <el-option label="实验课" value="lab" />
            <el-option label="讨论课" value="discussion" />
            <el-option label="考试" value="exam" />
            <el-option label="作业" value="homework" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="持续时间" prop="duration">
          <el-input-number
            v-model="eventForm.duration"
            :min="15"
            :max="480"
            :step="15"
            placeholder="分钟"
          />
          <span class="ml-2">分钟</span>
        </el-form-item>
        <el-form-item label="事件颜色" prop="color">
          <div class="color-picker-container">
            <el-color-picker v-model="eventForm.color" />
            <div class="preset-colors">
              <div 
                v-for="color in presetColors" 
                :key="color"
                class="color-option"
                :style="{ backgroundColor: color }"
                @click="eventForm.color = color"
              ></div>
            </div>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddEventDialog = false">取消</el-button>
        <el-button type="primary" @click="saveEvent">保存</el-button>
      </template>
    </el-dialog>

    <!-- 编辑已放置事件对话框 -->
    <el-dialog
      v-model="showEditPlacedEventDialog"
      title="编辑已放置事件"
      width="500px"
    >
      <el-form :model="placedEventForm" label-width="100px">
        <el-form-item label="选择日期">
          <el-select v-model="placedEventForm.selectedDay" placeholder="选择日期">
            <el-option 
              v-for="day in weekDays" 
              :key="day.date" 
              :label="day.name + ' ' + day.date" 
              :value="day.date" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="开始时间">
          <el-time-picker
            v-model="placedEventForm.startTime"
            format="HH:mm"
            placeholder="选择开始时间"
          />
        </el-form-item>
        <el-form-item label="持续时间">
          <el-input-number
            v-model="placedEventForm.duration"
            :min="15"
            :max="480"
            :step="15"
            placeholder="分钟"
          />
          <span class="ml-2">分钟</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditPlacedEventDialog = false">取消</el-button>
        <el-button type="primary" @click="updatePlacedEvent">保存</el-button>
      </template>
    </el-dialog>

    <!-- 展开的详细视图 -->
    <el-dialog
      v-model="isExpanded"
      title="教学计划详细视图"
      width="95%"
      :close-on-click-modal="false"
      :close-on-press-escape="true"
      class="expanded-view-dialog"
    >
      <div class="expanded-timeline-container">
        <!-- 展开视图的时间轴头部 -->
        <div class="expanded-timeline-header">
          <div class="expanded-time-column">时间</div>
          <div 
            v-for="day in weekDays" 
            :key="day.date"
            class="expanded-day-column"
          >
            <div class="expanded-day-header">
              <div class="expanded-day-name">{{ day.name }}</div>
              <div class="expanded-day-date">{{ day.date }}</div>
            </div>
          </div>
        </div>

        <!-- 展开视图的时间表主体 -->
        <div class="expanded-timeline-body">
          <div 
            v-for="hour in 13" 
            :key="hour + 8"
            class="expanded-time-row"
          >
            <!-- 时间标签 -->
            <div class="expanded-time-label">
              {{ (hour + 8).toString().padStart(2, '0') }}:00
            </div>
            
            <!-- 每天的时段 -->
            <div 
              v-for="day in weekDays" 
              :key="day.date"
              class="expanded-day-slot"
              :data-day="day.date"
              :data-hour="hour + 8"
              @dragover="handleDragOver"
              @drop="handleDrop"
            >
              <!-- 已放置的事件 -->
              <div
                v-for="placedEvent in getPlacedEventsForDayAndHour(day.date, hour + 8)"
                :key="placedEvent.id"
                class="expanded-event-card"
                :style="{
                  backgroundColor: getEventBackgroundColor(placedEvent.color),
                  borderLeftColor: placedEvent.color,
                  borderLeftWidth: '4px',
                  height: `${Math.max(60, (placedEvent.duration / 60) * 60)}px`,
                  top: `${getExpandedEventOffset(placedEvent)}px`
                }"
                @click="editPlacedEvent(placedEvent)"
              >
                <div class="expanded-event-card-content">
                  <div class="expanded-event-card-title">{{ placedEvent.title }}</div>
                  <div class="expanded-event-card-time">
                    {{ formatEventTime(placedEvent.startHour) }} - {{ formatEventEndTime(placedEvent) }}
                  </div>
                  <div class="expanded-event-card-teacher">{{ placedEvent.teacherName }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Download, Edit, Delete, Search, ZoomIn, ZoomOut } from '@element-plus/icons-vue'
import axios from 'axios'

export default {
  name: 'TeachingPlanBoard',
  components: {
    Plus,
    Download,
    Edit,
    Delete,
    Search,
    ZoomIn,
    ZoomOut
  },
  setup() {
    // 响应式数据
    const searchKeyword = ref('')
    const selectedView = ref('week') // 默认使用周视图
    const selectedDate = ref(new Date())
    const showAddEventDialog = ref(false)
    const showEditPlacedEventDialog = ref(false)
    const editingEvent = ref(null)
    const editingPlacedEvent = ref(null)
    const eventFormRef = ref(null)
    const currentBoardId = ref(null)
    const isExpanded = ref(false) // 新增：控制缩放状态

    // 事件表单
    const eventForm = reactive({
      title: '',
      description: '',
      type: 'lecture',
      duration: 45,
      color: '#409EFF'
    })

    // 已放置事件表单
    const placedEventForm = reactive({
      startTime: null,
      duration: 45,
      selectedDay: null
    })

    // 表单验证规则
    const eventRules = {
      title: [
        { required: true, message: '请输入事件标题', trigger: 'blur' }
      ],
      description: [
        { required: true, message: '请输入事件描述', trigger: 'blur' }
      ],
      type: [
        { required: true, message: '请选择事件类型', trigger: 'change' }
      ],
      duration: [
        { required: true, message: '请输入持续时间', trigger: 'blur' }
      ]
    }

    // 事件数据
    const events = ref([])
    const placedEvents = ref([])

    // 计算属性
    const filteredEvents = computed(() => {
      if (!searchKeyword.value) return events.value
      return events.value.filter(event => 
        event.title.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        event.description.toLowerCase().includes(searchKeyword.value.toLowerCase())
      )
    })

    // 计算周视图的日期
    const weekDays = computed(() => {
      const days = []
      const startOfWeek = new Date(selectedDate.value)
      startOfWeek.setDate(startOfWeek.getDate() - startOfWeek.getDay() + 1) // 本周一

      for (let i = 0; i < 7; i++) {
        const date = new Date(startOfWeek)
        date.setDate(startOfWeek.getDate() + i)
        days.push({
          name: date.toLocaleDateString('zh-CN', { weekday: 'short' }), // 如：周一
          date: date.toISOString().split('T')[0] // 如：2023-10-23
        })
      }
      return days
    })

    // API配置
    const API_BASE_URL = 'http://localhost:8000/api/teaching-board'
    const token = localStorage.getItem('token')
    const headers = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }

    // 方法
    const getEventTypeName = (type) => {
      const typeMap = {
        lecture: '理论课',
        lab: '实验课',
        discussion: '讨论课',
        exam: '考试',
        homework: '作业',
        other: '其他'
      }
      return typeMap[type] || '其他'
    }

    const getEventTypeTag = (type) => {
      const tagMap = {
        lecture: 'primary',
        lab: 'success',
        discussion: 'warning',
        exam: 'danger',
        homework: 'info',
        other: ''
      }
      return tagMap[type] || ''
    }

    // 获取事件背景颜色
    const getEventBackgroundColor = (color) => {
      // 将颜色转换为浅色背景
      const colorMap = {
        '#409EFF': '#e6f4ff', // 蓝色 -> 浅蓝色
        '#67C23A': '#f0f9eb', // 绿色 -> 浅绿色
        '#E6A23C': '#fdf6ec', // 橙色 -> 浅橙色
        '#F56C6C': '#fef0f0', // 红色 -> 浅红色
        '#909399': '#f4f4f5', // 灰色 -> 浅灰色
        '#C0C4CC': '#f4f4f5', // 浅灰色
        '#9C27B0': '#f3e5f5', // 紫色 -> 浅紫色
        '#FF9800': '#fff3e0', // 深橙色 -> 浅橙色
        '#4CAF50': '#e8f5e8', // 深绿色 -> 浅绿色
        '#2196F3': '#e3f2fd', // 深蓝色 -> 浅蓝色
        '#FF5722': '#ffebee', // 深红色 -> 浅红色
        '#607D8B': '#eceff1'  // 蓝灰色 -> 浅蓝灰色
      }
      
      // 如果颜色在映射表中，返回对应的浅色
      if (colorMap[color]) {
        return colorMap[color]
      }
      
      // 如果不在映射表中，尝试生成浅色版本
      if (color.startsWith('#')) {
        // 简单的颜色变浅逻辑
        const hex = color.substring(1)
        const r = parseInt(hex.substr(0, 2), 16)
        const g = parseInt(hex.substr(2, 2), 16)
        const b = parseInt(hex.substr(4, 2), 16)
        
        // 将颜色变浅（增加亮度）
        const lighten = (c) => Math.min(255, c + (255 - c) * 0.7)
        const lightR = Math.round(lighten(r))
        const lightG = Math.round(lighten(g))
        const lightB = Math.round(lighten(b))
        
        return `#${lightR.toString(16).padStart(2, '0')}${lightG.toString(16).padStart(2, '0')}${lightB.toString(16).padStart(2, '0')}`
      }
      
      return '#f4f4f5' // 默认浅灰色
    }

    // 加载教学事件
    const loadEvents = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/events`, { headers })
        if (response.data.success) {
          events.value = response.data.data
        }
      } catch (error) {
        console.error('加载教学事件失败:', error)
        ElMessage.error('加载教学事件失败')
      }
    }

    // 加载或创建看板
    const loadOrCreateBoard = async () => {
      try {
        const dateStr = selectedDate.value.toISOString().split('T')[0]
        const response = await axios.get(`${API_BASE_URL}/boards?board_date=${dateStr}`, { headers })
        
        if (response.data.success && response.data.data.length > 0) {
          // 使用现有的看板
          const board = response.data.data[0]
          currentBoardId.value = board.id
          await loadBoardDetail(board.id)
        } else {
          // 创建新的看板
          const boardData = {
            title: `${dateStr} 教学计划`,
            description: '教学计划看板（所有教师共用）',
            board_date: dateStr,
            view_type: selectedView.value
          }
          
          const createResponse = await axios.post(`${API_BASE_URL}/boards`, boardData, { headers })
          if (createResponse.data.success) {
            currentBoardId.value = createResponse.data.data.id
            placedEvents.value = []
          }
        }
      } catch (error) {
        console.error('加载看板失败:', error)
        ElMessage.error('加载看板失败')
      }
    }

    // 加载看板详情
    const loadBoardDetail = async (boardId) => {
      try {
        const response = await axios.get(`${API_BASE_URL}/boards/${boardId}`, { headers })
        if (response.data.success) {
          placedEvents.value = response.data.data.placed_events
        }
      } catch (error) {
        console.error('加载看板详情失败:', error)
        ElMessage.error('加载看板详情失败')
      }
    }

    const handleDragStart = (event, e) => {
      e.dataTransfer.setData('application/json', JSON.stringify(event))
      e.dataTransfer.effectAllowed = 'copy'
    }

    const handleDragOver = (e) => {
      e.preventDefault()
      e.dataTransfer.dropEffect = 'copy'
    }

    const handleDrop = async (e) => {
      e.preventDefault()
      if (!currentBoardId.value) {
        ElMessage.warning('请先选择或创建看板')
        return
      }

      const eventData = JSON.parse(e.dataTransfer.getData('application/json'))
      const dayDate = e.currentTarget.dataset.day
      const hour = parseInt(e.currentTarget.dataset.hour)
      
      // 检查时间是否在8-21点范围内
      if (hour < 8 || hour > 21) {
        ElMessage.warning('只能在8:00-21:00时间段内安排事件')
        return
      }
      
      // 检查时间冲突
      const hasConflict = placedEvents.value.some(placed => {
        if (placed.board_date !== dayDate) return false
        const placedEnd = placed.startHour + placed.duration / 60
        const newEnd = hour + eventData.duration / 60
        return (hour < placedEnd && newEnd > placed.startHour)
      })

      if (hasConflict) {
        ElMessage.warning('该时间段已有其他事件安排')
        return
      }

      try {
        const placeData = {
          event_id: eventData.id,
          startHour: hour,
          duration: eventData.duration,
          position_x: 0,
          position_y: 0,
          board_date: dayDate
        }

        const response = await axios.post(`${API_BASE_URL}/boards/${currentBoardId.value}/events`, placeData, { headers })
        if (response.data.success) {
          const newPlacedEvent = response.data.data
          newPlacedEvent.board_date = dayDate // 添加日期信息
          placedEvents.value.push(newPlacedEvent)
          ElMessage.success('事件已添加到时间表')
        }
      } catch (error) {
        console.error('放置事件失败:', error)
        ElMessage.error('放置事件失败')
      }
    }

    const handlePlacedEventDragStart = (event, e) => {
      e.dataTransfer.setData('application/json', JSON.stringify(event))
      e.dataTransfer.effectAllowed = 'move'
    }

    const editEvent = (event) => {
      editingEvent.value = event
      Object.assign(eventForm, {
        title: event.title,
        description: event.description,
        type: event.type,
        duration: event.duration,
        color: event.color
      })
      showAddEventDialog.value = true
    }

    const deleteEvent = async (eventId) => {
      try {
        await ElMessageBox.confirm('确定要删除这个事件吗？', '确认删除', {
          type: 'warning'
        })
        
        const response = await axios.delete(`${API_BASE_URL}/events/${eventId}`, { headers })
        if (response.data.success) {
          events.value = events.value.filter(e => e.id !== eventId)
          placedEvents.value = placedEvents.value.filter(e => e.id !== eventId)
          ElMessage.success('事件已删除')
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('删除事件失败:', error)
          ElMessage.error('删除事件失败')
        }
      }
    }

    const saveEvent = async () => {
      try {
        await eventFormRef.value.validate()
        
        const eventData = {
          title: eventForm.title,
          description: eventForm.description,
          type: eventForm.type,
          duration: eventForm.duration,
          color: eventForm.color
        }

        let response
        if (editingEvent.value) {
          // 编辑现有事件
          response = await axios.put(`${API_BASE_URL}/events/${editingEvent.value.id}`, eventData, { headers })
        } else {
          // 添加新事件
          response = await axios.post(`${API_BASE_URL}/events`, eventData, { headers })
        }

        if (response.data.success) {
          if (editingEvent.value) {
            // 更新现有事件
            const index = events.value.findIndex(e => e.id === editingEvent.value.id)
            if (index !== -1) {
              events.value[index] = response.data.data
            }
            editingEvent.value = null
          } else {
            // 添加新事件
            events.value.push(response.data.data)
          }

          // 重置表单
          Object.assign(eventForm, {
            title: '',
            description: '',
            type: 'lecture',
            duration: 45,
            color: '#409EFF'
          })
          
          showAddEventDialog.value = false
          ElMessage.success(editingEvent.value ? '事件已更新' : '事件已添加')
        }
      } catch (error) {
        console.error('保存事件失败:', error)
        ElMessage.error('保存事件失败')
      }
    }

    const editPlacedEvent = (event) => {
      editingPlacedEvent.value = event
      placedEventForm.startTime = new Date()
      placedEventForm.startTime.setHours(Math.floor(event.startHour))
      placedEventForm.startTime.setMinutes((event.startHour % 1) * 60)
      placedEventForm.duration = event.duration
      placedEventForm.selectedDay = event.board_date // 设置选中的日期
      showEditPlacedEventDialog.value = true
    }

    const updatePlacedEvent = async () => {
      if (!editingPlacedEvent.value || !currentBoardId.value) return

      const startHour = placedEventForm.startTime.getHours() + 
                       placedEventForm.startTime.getMinutes() / 60
      const selectedDay = placedEventForm.selectedDay

      // 检查时间是否在8-21点范围内
      if (startHour < 8 || startHour > 21) {
        ElMessage.warning('只能在8:00-21:00时间段内安排事件')
        return
      }

      // 检查时间冲突
      const hasConflict = placedEvents.value.some(placed => {
        if (placed.id === editingPlacedEvent.value.id) return false
        if (placed.board_date !== selectedDay) return false
        const placedEnd = placed.startHour + placed.duration / 60
        const newEnd = startHour + placedEventForm.duration / 60
        return (startHour < placedEnd && newEnd > placed.startHour)
      })

      if (hasConflict) {
        ElMessage.warning('该时间段已有其他事件安排')
        return
      }

      try {
        const updateData = {
          id: editingPlacedEvent.value.id,
          event_id: editingPlacedEvent.value.id,
          startHour: Math.max(8, Math.min(21, startHour)),
          duration: placedEventForm.duration,
          position_x: 0,
          position_y: 0,
          board_date: selectedDay
        }

        const response = await axios.post(`${API_BASE_URL}/boards/${currentBoardId.value}/events`, updateData, { headers })
        if (response.data.success) {
          // 更新事件
          const index = placedEvents.value.findIndex(e => e.id === editingPlacedEvent.value.id)
          if (index !== -1) {
            placedEvents.value[index] = response.data.data
            placedEvents.value[index].board_date = selectedDay
          }

          showEditPlacedEventDialog.value = false
          editingPlacedEvent.value = null
          ElMessage.success('事件已更新')
        }
      } catch (error) {
        console.error('更新事件失败:', error)
        ElMessage.error('更新事件失败')
      }
    }

    const exportBoard = () => {
      const boardData = {
        date: selectedDate.value,
        events: placedEvents.value,
        exportTime: new Date().toISOString()
      }
      
      const dataStr = JSON.stringify(boardData, null, 2)
      const dataBlob = new Blob([dataStr], { type: 'application/json' })
      const url = URL.createObjectURL(dataBlob)
      
      const link = document.createElement('a')
      link.href = url
      link.download = `教学计划看板_${selectedDate.value.toISOString().split('T')[0]}.json`
      link.click()
      
      URL.revokeObjectURL(url)
      ElMessage.success('看板已导出')
    }

    // 监听日期变化
    const handleDateChange = () => {
      loadOrCreateBoard()
    }

    // 获取指定日期和小时的所有已放置事件
    const getPlacedEventsForDayAndHour = (dayDate, hour) => {
      return placedEvents.value.filter(placed => 
        placed.board_date === dayDate && 
        Math.floor(placed.startHour) === hour
      )
    }

    // 获取事件的顶部偏移量
    const getEventOffset = (event) => {
      const minutes = (event.startHour % 1) * 60
      return (minutes / 60) * 70 // 基于70px的行高计算偏移
    }

    // 获取展开视图事件的顶部偏移量
    const getExpandedEventOffset = (event) => {
      const minutes = (event.startHour % 1) * 60
      return (minutes / 60) * 60 // 基于60px的行高计算偏移
    }

    // 格式化事件时间
    const formatEventTime = (hour) => {
      return hour.toString().padStart(2, '0') + ':00'
    }

    // 格式化事件结束时间
    const formatEventEndTime = (event) => {
      const endHour = event.startHour + event.duration / 60
      const hours = Math.floor(endHour)
      const minutes = Math.round((endHour % 1) * 60)
      return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`
    }

    // 预设颜色
    const presetColors = [
      '#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399',
      '#C0C4CC', '#9C27B0', '#FF9800', '#4CAF50', '#2196F3',
      '#FF5722', '#607D8B'
    ]

    // 组件挂载时加载数据
    onMounted(() => {
      loadEvents()
      loadOrCreateBoard()
    })

    return {
      searchKeyword,
      selectedView,
      selectedDate,
      showAddEventDialog,
      showEditPlacedEventDialog,
      editingEvent,
      editingPlacedEvent,
      eventFormRef,
      eventForm,
      placedEventForm,
      eventRules,
      events,
      placedEvents,
      filteredEvents,
      getEventTypeName,
      getEventTypeTag,
      handleDragStart,
      handleDragOver,
      handleDrop,
      handlePlacedEventDragStart,
      editEvent,
      deleteEvent,
      saveEvent,
      editPlacedEvent,
      updatePlacedEvent,
      exportBoard,
      handleDateChange,
      weekDays,
      getPlacedEventsForDayAndHour,
      getEventOffset,
      formatEventTime,
      formatEventEndTime,
      isExpanded, // 暴露缩放状态
      getEventBackgroundColor, // 暴露背景颜色获取方法
      presetColors, // 暴露预设颜色
      getExpandedEventOffset // 暴露展开视图的偏移量获取方法
    }
  }
}
</script>

<style scoped>
.teaching-plan-board {
  padding: 24px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: 100vh;
}

.board-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e4e7ed;
}

.header-left h2 {
  margin: 0 0 8px 0;
  color: #2c3e50;
  font-size: 28px;
  font-weight: 600;
}

.subtitle {
  margin: 0;
  color: #6c757d;
  font-size: 16px;
}

.header-right {
  display: flex;
  gap: 12px;
}

.board-container {
  display: flex;
  gap: 20px;
  height: calc(100vh - 200px);
}

.events-panel {
  width: 300px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  border: 1px solid #e4e7ed;
}

.panel-header {
  padding: 20px;
  border-bottom: 1px solid #e9ecef;
}

.panel-header h3 {
  margin: 0 0 12px 0;
  color: #2c3e50;
  font-size: 18px;
  font-weight: 600;
}

.events-list {
  flex: 1;
  overflow-y: auto;
  padding: 0;
}

.event-item {
  margin: 8px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid;
  cursor: grab;
  transition: all 0.3s ease;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  border: 1px solid #e9ecef;
}

.event-item:hover {
  background: #e9ecef;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.event-item:active {
  cursor: grabbing;
}

.event-content h4 {
  margin: 0 0 8px 0;
  color: #2c3e50;
  font-size: 14px;
  font-weight: 600;
}

.event-content p {
  margin: 0 0 8px 0;
  color: #6c757d;
  font-size: 12px;
  line-height: 1.4;
}

.event-meta {
  display: flex;
  gap: 6px;
  align-items: center;
}

.event-meta .el-tag {
  min-width: 60px;
  text-align: center;
  font-size: 12px;
  padding: 0 8px;
  height: 24px;
  line-height: 22px;
  border-radius: 12px;
  font-weight: 500;
}

.event-duration {
  color: #6c757d;
  font-size: 12px;
}

.event-actions {
  display: flex;
  gap: 2px;
}

.board-area {
  flex: 1;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  border: 1px solid #e4e7ed;
}

.board-header-info {
  padding: 24px;
  border-bottom: 1px solid #e9ecef;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.board-info h3 {
  margin: 0 0 8px 0;
  color: #2c3e50;
  font-size: 20px;
  font-weight: 600;
}

.board-info p {
  margin: 0;
  color: #6c757d;
  font-size: 14px;
}

.board-controls {
  display: flex;
  gap: 12px;
}

.week-timeline-container {
  flex: 1;
  position: relative;
  overflow: hidden;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e4e7ed;
}

.timeline-header {
  position: sticky;
  top: 0;
  left: 0;
  right: 0;
  height: 70px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  color: #495057;
  display: flex;
  z-index: 10;
  align-items: center;
  padding: 0 20px;
  border-radius: 12px 12px 0 0;
  border-bottom: 2px solid #dee2e6;
}

.time-column {
  width: 80px;
  text-align: center;
  font-size: 14px;
  color: #495057;
  font-weight: 600;
}

.day-column {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 10px;
}

.day-header {
  width: 100%;
  text-align: center;
  margin-bottom: 8px;
}

.day-name {
  font-size: 16px;
  color: #495057;
  font-weight: 600;
  margin-bottom: 4px;
}

.day-date {
  font-size: 12px;
  color: #6c757d;
}

.timeline-body {
  position: relative;
  height: calc(100% - 70px);
  overflow-y: auto;
  padding: 0 20px;
  transition: transform 0.3s ease;
  background: #ffffff;
}

.timeline-body.zoomed {
  transform: scale(1.2);
  transform-origin: top left;
  overflow-y: hidden;
}

.time-row {
  display: flex;
  height: 70px;
  border-bottom: 1px solid #f1f3f4;
  position: relative;
  transition: background-color 0.2s ease;
}

.time-row:hover {
  background-color: #f8f9fa;
}

.time-row:last-child {
  border-bottom: none;
}

.time-label {
  width: 80px;
  text-align: center;
  font-size: 13px;
  color: #6c757d;
  font-weight: 500;
  padding-top: 25px;
  background: #f8f9fa;
  border-right: 1px solid #e9ecef;
}

.day-slot {
  flex: 1;
  position: relative;
  border-right: 1px solid #f1f3f4;
  min-height: 70px;
  padding: 1px;
  transition: background-color 0.2s ease;
  box-sizing: border-box;
}

.day-slot:hover {
  background-color: #f8f9fa;
}

.day-slot:last-child {
  border-right: none;
}

.placed-event-card {
  position: absolute;
  width: calc(100% - 6px);
  border-radius: 6px;
  border: 1px solid #e4e7ed;
  border-left: 3px solid;
  cursor: pointer;
  transition: all 0.3s ease;
  overflow: hidden;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  padding: 0 4px;
  margin: 3px;
  backdrop-filter: blur(10px);
  box-sizing: border-box;
}

.placed-event-card:hover {
  transform: translateY(-1px) scale(1.01);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 20;
  border-color: #d1d5db;
}

.event-card-content {
  width: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  color: #2c3e50;
  font-weight: 500;
  padding: 6px 0;
  min-height: 25px;
  overflow: hidden;
}

.event-card-title {
  font-size: 13px;
  line-height: 1.2;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: 2px;
  font-weight: 600;
  color: #2c3e50;
  max-width: 100%;
}

.event-card-time {
  font-size: 11px;
  opacity: 0.8;
  margin-bottom: 2px;
  font-weight: 500;
  color: #6c757d;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100%;
  padding: 1px 4px;
  border-radius: 3px;
  display: inline-block;
}

.event-card-teacher {
  background: rgba(0, 0, 0, 0.08);
  padding: 1px 4px;
  border-radius: 3px;
  font-size: 8px;
  opacity: 0.9;
  align-self: flex-start;
  backdrop-filter: blur(5px);
  color: #495057;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100%;
}

.color-picker-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.preset-colors {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.color-option {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  cursor: pointer;
  border: 2px solid #e4e7ed;
  transition: all 0.2s ease;
}

.color-option:hover {
  transform: scale(1.1);
  border-color: #409EFF;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

/* 展开视图样式 */
.expanded-view-dialog .el-dialog__body {
  padding: 0;
  max-height: 100vh;
  overflow: hidden;
}

.expanded-view-dialog .el-dialog {
  max-height: 100vh;
  margin-top: 2vh !important;
  margin-bottom: 3vh !important;
}

.expanded-timeline-container {
  height: 100vh;
  background: #ffffff;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.expanded-timeline-header {
  height: 60px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  color: #495057;
  display: flex;
  align-items: center;
  padding: 0 20px;
  border-bottom: 2px solid #dee2e6;
  flex-shrink: 0;
  position: sticky;
  top: 0;
  z-index: 10;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.expanded-time-column {
  width: 80px;
  text-align: center;
  font-size: 14px;
  color: #495057;
  font-weight: 600;
}

.expanded-day-column {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 10px;
}

.expanded-day-header {
  width: 100%;
  text-align: center;
  margin-bottom: 4px;
}

.expanded-day-name {
  font-size: 16px;
  color: #495057;
  font-weight: 600;
  margin-bottom: 2px;
}

.expanded-day-date {
  font-size: 12px;
  color: #6c757d;
}

.expanded-timeline-body {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 0 20px;
  background: #ffffff;
  display: flex;
  flex-direction: column;
  min-height: 780px; /* 13行 * 60px = 780px */
}

/* 自定义滚动条样式 */
.expanded-timeline-body::-webkit-scrollbar {
  width: 8px;
}

.expanded-timeline-body::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.expanded-timeline-body::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.expanded-timeline-body::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.expanded-time-row {
  display: flex;
  height: 60px;
  border-bottom: 1px solid #f1f3f4;
  position: relative;
  transition: background-color 0.2s ease;
  flex-shrink: 0;
}

.expanded-time-row:hover {
  background-color: #f8f9fa;
}

.expanded-time-row:last-child {
  border-bottom: none;
}

.expanded-time-label {
  width: 80px;
  text-align: center;
  font-size: 13px;
  color: #6c757d;
  font-weight: 500;
  padding-top: 20px;
  background: #f8f9fa;
  border-right: 1px solid #e9ecef;
  flex-shrink: 0;
  position: sticky;
  left: 0;
  z-index: 5;
}

.expanded-day-slot {
  flex: 1;
  position: relative;
  border-right: 1px solid #f1f3f4;
  min-height: 60px;
  padding: 1px;
  transition: background-color 0.2s ease;
  box-sizing: border-box;
}

.expanded-day-slot:hover {
  background-color: #f8f9fa;
}

.expanded-day-slot:last-child {
  border-right: none;
}

.expanded-event-card {
  position: absolute;
  width: calc(100% - 4px);
  border-radius: 4px;
  border: 1px solid #e4e7ed;
  border-left: 3px solid;
  cursor: pointer;
  transition: all 0.3s ease;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  padding: 0 4px;
  margin: 2px;
  backdrop-filter: blur(10px);
  box-sizing: border-box;
  min-height: 25px;
}

.expanded-event-card:hover {
  transform: translateY(-1px) scale(1.01);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  z-index: 20;
  border-color: #d1d5db;
}

.expanded-event-card-content {
  width: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  color: #2c3e50;
  font-weight: 500;
  padding: 4px 0;
  min-height: 25px;
  overflow: hidden;
}

.expanded-event-card-title {
  font-size: 12px;
  line-height: 1.2;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: 2px;
  font-weight: 600;
  color: #2c3e50;
  max-width: 100%;
}

.expanded-event-card-time {
  font-size: 10px;
  opacity: 0.8;
  margin-bottom: 2px;
  font-weight: 500;
  color: #6c757d;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100%;
  background: rgba(255, 255, 255, 0.7);
  padding: 1px 3px;
  border-radius: 2px;
  display: inline-block;
}

.expanded-event-card-teacher {
  background: rgba(0, 0, 0, 0.08);
  padding: 1px 3px;
  border-radius: 2px;
  font-size: 9px;
  opacity: 0.9;
  align-self: flex-start;
  backdrop-filter: blur(5px);
  color: #495057;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100%;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .board-container {
    flex-direction: column;
    height: auto;
  }
  
  .events-panel {
    width: 100%;
    height: 300px;
  }
  
  .board-area {
    height: 600px;
  }
  
  .timeline-header {
    height: 60px;
  }
  
  .time-column, .time-label {
    width: 60px;
  }
  
  .time-row {
    height: 60px;
  }
  
  .day-slot {
    min-height: 60px;
  }
  
  .day-name {
    font-size: 14px;
  }
  
  .day-date {
    font-size: 11px;
  }
  
  /* 展开视图响应式 */
  .expanded-view-dialog .el-dialog {
    width: 98% !important;
    margin: 1vh auto !important;
  }
  
  .expanded-timeline-container {
    height: 85vh;
  }
  
  .expanded-timeline-body {
    min-height: 720px; /* 12行 * 60px */
  }
}

@media (max-width: 768px) {
  .board-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
  
  .header-right {
    width: 100%;
    justify-content: flex-end;
  }
  
  .board-header-info {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
  
  .board-controls {
    width: 100%;
    justify-content: flex-end;
  }
  
  .timeline-header {
    padding: 0 10px;
  }
  
  .timeline-body {
    padding: 0 10px;
  }
  
  .time-column, .time-label {
    width: 50px;
    font-size: 11px;
  }
  
  .day-name {
    font-size: 12px;
  }
  
  .day-date {
    font-size: 10px;
  }
  
  .event-card-title {
    font-size: 12px;
  }
  
  .event-card-time {
    font-size: 10px;
  }
  
  .event-card-teacher {
    font-size: 9px;
  }
  
  /* 展开视图移动端优化 */
  .expanded-view-dialog .el-dialog {
    width: 100% !important;
    margin: 0 !important;
    height: 100vh !important;
  }
  
  .expanded-timeline-container {
    height: 100vh;
    border-radius: 0;
  }
  
  .expanded-timeline-header {
    height: 50px;
    padding: 0 10px;
  }
  
  .expanded-time-column {
    width: 60px;
    font-size: 12px;
  }
  
  .expanded-day-column {
    padding: 0 5px;
  }
  
  .expanded-day-name {
    font-size: 14px;
  }
  
  .expanded-day-date {
    font-size: 10px;
  }
  
  .expanded-timeline-body {
    padding: 0 10px;
    min-height: 600px; /* 10行 * 60px */
  }
  
  .expanded-time-label {
    width: 60px;
    font-size: 11px;
    padding-top: 15px;
  }
  
  .expanded-time-row {
    height: 50px;
  }
  
  .expanded-day-slot {
    min-height: 50px;
  }
}
</style> 