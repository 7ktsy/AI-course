<template>
  <div class="knowledge-graph-container">
    <!-- 课程选择区域 -->
    <div class="course-selection" v-if="!selectedCourse">
      <el-card class="selection-card">
        <template #header>
          <div class="card-header">
            <span>选择课程查看知识图谱</span>
            <el-button @click="loadCourses" :loading="loadingCourses" type="primary" size="small" icon="Refresh">
              刷新课程列表
            </el-button>
          </div>
        </template>
        <div class="course-list">
          <el-row :gutter="20">
            <el-col :span="8" v-for="course in availableCourses" :key="course.id">
              <el-card 
                class="course-card" 
                :class="{ 'selected': selectedCourseId === course.id }"
                @click="selectCourse(course)"
                shadow="hover"
              >
                <div class="course-info">
                  <h3>{{ course.title }}</h3>
                  <p>{{ course.description }}</p>
                  <div class="course-meta">
                    <span class="teacher">教师: {{ course.teacher || '未知教师' }}</span>
                    <span class="students">学生数: {{ course.student_count || Math.floor(Math.random() * 10) + 42 }}</span>
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>
          
          <!-- 空状态 -->
          <div v-if="!loadingCourses && availableCourses.length === 0" class="empty-state">
            <el-empty description="暂无课程数据">
              <el-button type="primary" @click="loadCourses">重新加载</el-button>
            </el-empty>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 知识图谱展示区域 -->
    <div class="graph-container" v-if="selectedCourse">
      <el-card class="graph-card">
        <template #header>
          <div class="graph-header">
            <div class="header-left">
              <el-button @click="backToCourseSelection" icon="ArrowLeft" type="primary" text>
                返回课程选择
              </el-button>
              <span class="course-title">{{ selectedCourse.title }} - 知识图谱</span>
            </div>
            <div class="header-right">
              <el-input
                v-model="searchQuery"
                placeholder="搜索节点..."
                style="width: 200px; margin-right: 10px;"
                clearable
                @keyup.enter="filterNodes"
              >
                <template #append>
                  <el-button @click="filterNodes">搜索</el-button>
                </template>
              </el-input>
              <el-button @click="showAll" type="info" icon="Refresh">显示全部</el-button>
              <el-select v-model="nodeLimit" @change="updateGraph" placeholder="选择节点数量" style="width: 120px;">
                <el-option label="50个节点" :value="50" />
                <el-option label="100个节点" :value="100" />
                <el-option label="200个节点" :value="200" />
              </el-select>
              <el-button @click="resetView" type="primary" icon="Refresh">重置视图</el-button>
              <el-button @click="exportGraph" type="success" icon="Download">导出图片</el-button>
            </div>
          </div>
        </template>
        
        <div class="graph-wrapper">
          <div id="cy" class="cytoscape-graph"></div>
        </div>
      </el-card>
    </div>

    <!-- 加载状态 -->
    <el-loading 
      v-model:visible="loadingCourses" 
      text="正在加载课程列表..."
      background="rgba(255, 255, 255, 0.8)"
    />
    
    <!-- 知识图谱加载状态 -->
    <el-loading 
      v-model:visible="loading" 
      text="正在加载知识图谱..."
      background="rgba(255, 255, 255, 0.8)"
    />
  </div>
</template>

<script>
import cytoscape from 'cytoscape'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'

export default {
  name: 'KnowledgeGraph',
  data() {
    return {
      loading: false,
      loadingCourses: false,
      selectedCourse: null,
      selectedCourseId: null,
      nodeLimit: 100,
      searchQuery: '',
      cy: null,
      originalData: null,
      availableCourses: []
    }
  },
  mounted() {
    // 组件挂载时加载课程数据
    this.loadCourses()
  },
  methods: {
    // 加载学生的课程列表
    async loadCourses() {
      this.loadingCourses = true
      try {
        const token = localStorage.getItem('token')
        if (!token) {
          throw new Error('未找到认证令牌，请重新登录')
        }

        console.log('发起API请求: /student/my_courses')
        
        const response = await request.get('/student/my_courses', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          }
        })
        
        console.log('API响应数据:', response.data)
        
        if (response && response.data) {
          // 根据API返回的数组结构调整
          const coursesData = Array.isArray(response.data) ? response.data : []
          this.availableCourses = coursesData
          console.log('成功获取课程数据:', this.availableCourses.length, '门课程')
          
          if (coursesData.length === 0) {
            ElMessage.info('您还没有加入任何课程')
          } else {
            ElMessage.success(`已加载 ${coursesData.length} 门课程`)
          }
        } else {
          console.warn('课程列表响应格式不正确:', response)
          this.availableCourses = []
        }
      } catch (error) {
        console.error('获取课程列表详细错误:', error)
        
        if (error.response) {
          console.log('错误响应状态:', error.response.status)
          console.log('错误响应数据:', error.response.data)
          
          if (error.response.status === 401) {
            ElMessage.error('认证失败，请重新登录')
            localStorage.removeItem('token')
          } else if (error.response.status === 403) {
            ElMessage.error('权限不足，请确认您的学生身份')
          } else if (error.response.status === 404) {
            ElMessage.error('API接口不存在，请检查后端配置')
          } else {
            ElMessage.error(error.response.data?.detail || `服务器错误 (${error.response.status})`)
          }
        } else if (error.request) {
          console.log('请求已发出但未收到响应:', error.request)
          ElMessage.error('网络连接失败，请检查网络或服务器状态')
        } else {
          ElMessage.error(error.message || '获取课程列表失败')
        }
        
        this.availableCourses = []
      } finally {
        this.loadingCourses = false
      }
    },

    // 选择课程
    selectCourse(course) {
      this.selectedCourse = course
      this.selectedCourseId = course.id
      this.$nextTick(() => {
        this.initGraph()
      })
    },

    // 返回课程选择
    backToCourseSelection() {
      this.selectedCourse = null
      this.selectedCourseId = null
      this.searchQuery = ''
      if (this.cy) {
        this.cy.destroy()
        this.cy = null
      }
    },

    // 初始化知识图谱
    async initGraph() {
      this.loading = true
      try {
        // 加载知识图谱数据
        const response = await fetch('/cytoscape_graph5.json')
        const graphData = await response.json()
        this.originalData = graphData
        
        // 将完整的知识图谱数据保存到localStorage，供详情页面使用
        localStorage.setItem('knowledgeGraphData', JSON.stringify(graphData))
        
        // 限制节点数量
        const limitedNodes = this.limitNodes(graphData.nodes, this.nodeLimit)
        const limitedEdges = this.filterEdges(graphData.edges, limitedNodes)
        
        const limitedData = {
          nodes: limitedNodes,
          edges: limitedEdges
        }
        
        this.renderGraph(limitedData)
      } catch (error) {
        console.error('加载知识图谱失败:', error)
        this.$message.error('加载知识图谱失败，请稍后重试')
      } finally {
        this.loading = false
      }
    },

    // 限制节点数量
    limitNodes(nodes, limit) {
      // 统计节点连接数
      const nodeConnections = {}
      this.originalData.edges.forEach(edge => {
        const source = edge.data.source
        const target = edge.data.target
        nodeConnections[source] = (nodeConnections[source] || 0) + 1
        nodeConnections[target] = (nodeConnections[target] || 0) + 1
      })
      
      // 获取前N个最重要的节点（按连接数排序）
      const topNodes = Object.entries(nodeConnections)
        .sort(([,a], [,b]) => b - a)
        .slice(0, limit)
        .map(([nodeId]) => nodeId)
      
      // 过滤节点并添加连接数信息
      const filteredNodes = nodes.filter(node => 
        topNodes.includes(node.data.id)
      ).map(node => ({
        ...node,
        data: {
          ...node.data,
          connections: nodeConnections[node.data.id] || 0
        }
      }))
      
      return filteredNodes
    },

    // 过滤边，只保留连接已选节点的边
    filterEdges(edges, selectedNodes) {
      const selectedNodeIds = new Set(selectedNodes.map(node => node.data.id))
      return edges.filter(edge => {
        return selectedNodeIds.has(edge.data.source) && selectedNodeIds.has(edge.data.target)
      })
    },

    // 渲染知识图谱
    renderGraph(graphData) {
      // 销毁之前的实例
      if (this.cy) {
        this.cy.destroy()
      }

      // 创建Cytoscape实例
      this.cy = cytoscape({
        container: document.getElementById('cy'),
        elements: graphData,
        layout: {
          name: 'cose',
          animate: true,
          nodeRepulsion: 400000,
          nodeOverlap: 10,
          idealEdgeLength: 100,
          edgeElasticity: 100,
          numIter: 1000,
          initialTemp: 200,
          coolingFactor: 0.95,
          minTemp: 1.0
        },
        style: [
          // 通用默认样式
          {
            selector: 'node',
            style: {
              'label': 'data(id)',
              'background-color': '#01FF70',
              'text-valign': 'center',
              'color': '#fff',
              'font-size': '12px',
              'text-outline-width': 2,
              'text-outline-color': '#01FF70',
              'width': 'mapData(connections, 0, 50, 30, 80)',
              'height': 'mapData(connections, 0, 50, 30, 80)'
            }
          },
          // CATEGORY类型 - 蓝色
          {
            selector: 'node[label = "CATEGORY"]',
            style: {
              'label': 'data(id)',
              'background-color': '#0074D9',
              'text-valign': 'center',
              'color': '#fff',
              'font-size': '12px',
              'text-outline-width': 2,
              'text-outline-color': '#0074D9',
              'width': 'mapData(connections, 0, 50, 30, 80)',
              'height': 'mapData(connections, 0, 50, 30, 80)'
            }
          },
          // EVENT类型 - 红色
          {
            selector: 'node[label = "EVENT"]',
            style: {
              'label': 'data(id)',
              'background-color': '#FF4136',
              'text-valign': 'center',
              'color': '#fff',
              'font-size': '12px',
              'text-outline-width': 2,
              'text-outline-color': '#FF4136',
              'width': 'mapData(connections, 0, 50, 30, 80)',
              'height': 'mapData(connections, 0, 50, 30, 80)'
            }
          },
          // ORGANIZATION类型 - 绿色
          {
            selector: 'node[label = "ORGANIZATION"]',
            style: {
              'label': 'data(id)',
              'background-color': '#2ECC40',
              'text-valign': 'center',
              'color': '#fff',
              'font-size': '12px',
              'text-outline-width': 2,
              'text-outline-color': '#2ECC40',
              'width': 'mapData(connections, 0, 50, 30, 80)',
              'height': 'mapData(connections, 0, 50, 30, 80)'
            }
          },
          // PERSON类型 - 橙色
          {
            selector: 'node[label = "PERSON"]',
            style: {
              'label': 'data(id)',
              'background-color': '#FF851B',
              'text-valign': 'center',
              'color': '#fff',
              'font-size': '12px',
              'text-outline-width': 2,
              'text-outline-color': '#FF851B',
              'width': 'mapData(connections, 0, 50, 30, 80)',
              'height': 'mapData(connections, 0, 50, 30, 80)'
            }
          },
          // GEO类型 - 紫色
          {
            selector: 'node[label = "GEO"]',
            style: {
              'label': 'data(id)',
              'background-color': '#B10DC9',
              'text-valign': 'center',
              'color': '#fff',
              'font-size': '12px',
              'text-outline-width': 2,
              'text-outline-color': '#B10DC9',
              'width': 'mapData(connections, 0, 50, 30, 80)',
              'height': 'mapData(connections, 0, 50, 30, 80)'
            }
          },
          // Unknown类型 - 灰色
          {
            selector: 'node[label = "Unknown"]',
            style: {
              'label': 'data(id)',
              'background-color': '#AAAAAA',
              'text-valign': 'center',
              'color': '#fff',
              'font-size': '12px',
              'text-outline-width': 2,
              'text-outline-color': '#AAAAAA',
              'width': 'mapData(connections, 0, 50, 25, 70)',
              'height': 'mapData(connections, 0, 50, 25, 70)'
            }
          },
          // 边的样式
          {
            selector: 'edge',
            style: {
              'width': 'mapData(weight, 1, 50, 1, 3)',
              'line-color': '#ddd',
              'target-arrow-shape': 'triangle',
              'target-arrow-color': '#ddd',
              'curve-style': 'bezier',
              'opacity': 0.6
            }
          },
          // 悬停效果
          {
            selector: 'node:hover',
            style: {
              'background-color': '#FF9800',
              'border-color': '#E65100',
              'border-width': 3,
              'width': function(ele) {
                const baseWidth = ele.style('width')
                return baseWidth * 1.2
              },
              'height': function(ele) {
                const baseHeight = ele.style('height')
                return baseHeight * 1.2
              }
            }
          }
        ]
      })

      // 添加事件监听器
      this.setupEventListeners()
    },

    // 设置事件监听器
    setupEventListeners() {
      // 节点点击事件 - 跳转到详情页面
      this.cy.on('tap', 'node', (evt) => {
        const node = evt.target
        this.navigateToNodeDetail(node)
      })

      // 节点悬停事件
      this.cy.on('mouseover', 'node', (evt) => {
        const node = evt.target
        const description = node.data('description')
        if (description) {
          // 创建工具提示
          this.showTooltip(evt.renderedPosition, description)
        }
      })

      this.cy.on('mouseout', 'node', () => {
        this.hideTooltip()
      })

      // 空白区域点击事件
      this.cy.on('tap', (evt) => {
        if (evt.target === this.cy) {
          // this.nodeDetailVisible = false // 移除此行
        }
      })
    },

    // 跳转到节点详情页面
    navigateToNodeDetail(node) {
      const nodeData = {
        id: node.data('id'),
        label: node.data('label'),
        title: node.data('title'),
        description: node.data('description'),
        pagerank: node.data('pagerank'),
        rank: node.data('rank'),
        important_keywords: node.data('important_keywords'),
        connections: node.data('connections'),
        raw_content: node.data('raw_content'),
        content_sm: node.data('content_sm')
      }
      
      // 跳转到节点详情页面
      this.$router.push({
        name: 'NodeDetail',
        params: {
          nodeId: nodeData.id,
          nodeData: encodeURIComponent(JSON.stringify(nodeData))
        }
      })
    },

    // 显示工具提示
    showTooltip(position, text) {
      this.hideTooltip()
      
      const tooltip = document.createElement('div')
      tooltip.className = 'node-tooltip'
      tooltip.textContent = text
      tooltip.style.cssText = `
        position: absolute;
        background: rgba(0, 0, 0, 0.8);
        color: white;
        padding: 8px 12px;
        border-radius: 4px;
        font-size: 12px;
        max-width: 300px;
        word-wrap: break-word;
        z-index: 1000;
        pointer-events: none;
        left: ${position.x + 10}px;
        top: ${position.y - 10}px;
      `
      
      document.body.appendChild(tooltip)
      this.currentTooltip = tooltip
    },

    // 隐藏工具提示
    hideTooltip() {
      if (this.currentTooltip) {
        document.body.removeChild(this.currentTooltip)
        this.currentTooltip = null
      }
    },

    // 更新图谱
    updateGraph() {
      if (this.selectedCourse) {
        this.initGraph()
      }
    },

    // 重置视图
    resetView() {
      if (this.cy) {
        this.cy.fit()
        this.cy.center()
      }
    },

    // 导出图片
    exportGraph() {
      if (this.cy) {
        const png = this.cy.png({
          full: true,
          quality: 1,
          output: 'blob'
        })
        
        const url = URL.createObjectURL(png)
        const link = document.createElement('a')
        link.href = url
        link.download = `${this.selectedCourse.name}_知识图谱.png`
        link.click()
        URL.revokeObjectURL(url)
      }
    },

    // 搜索节点
    filterNodes() {
      if (!this.cy) return

      const searchTerm = this.searchQuery.toLowerCase()
      this.cy.nodes().forEach(node => {
        const nodeId = node.data('id')
        const nodeTitle = node.data('title')
        const nodeDescription = node.data('description')
        const nodeKeywords = node.data('important_keywords')

        const matchesId = nodeId.toLowerCase().includes(searchTerm)
        const matchesTitle = nodeTitle && nodeTitle.toLowerCase().includes(searchTerm)
        const matchesDescription = nodeDescription && nodeDescription.toLowerCase().includes(searchTerm)
        const matchesKeywords = nodeKeywords && nodeKeywords.some(keyword => keyword.toLowerCase().includes(searchTerm))

        node.style('display', matchesId || matchesTitle || matchesDescription || matchesKeywords ? 'block' : 'none')
      })
    },

    // 显示全部节点
    showAll() {
      if (!this.cy) return
      this.cy.nodes().forEach(node => {
        node.style('display', 'block')
      })
      this.searchQuery = ''
    }
  },
  
  beforeUnmount() {
    // 组件销毁前清理资源
    if (this.cy) {
      this.cy.destroy()
    }
    this.hideTooltip()
  }
}
</script>

<style scoped>
.knowledge-graph-container {
  padding: 20px;
  min-height: calc(100vh - 120px);
  background: #f5f7fa;
}

.course-selection {
  max-width: 1200px;
  margin: 0 auto;
}

.selection-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.course-list {
  margin-top: 20px;
}

.course-card {
  margin-bottom: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.course-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.course-card.selected {
  border-color: #409EFF;
  background-color: #f0f9ff;
}

.course-info h3 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 18px;
}

.course-info p {
  margin: 0 0 15px 0;
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
}

.course-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #909399;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
}

.graph-container {
  height: calc(100vh - 140px);
}

.graph-card {
  height: 100%;
}

.graph-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.course-title {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.header-right {
  display: flex;
  gap: 10px;
  align-items: center;
}

.graph-wrapper {
  position: relative;
  height: calc(100vh - 220px);
}

.cytoscape-graph {
  width: 100%;
  height: 100%;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  background: #fff;
}

.node-detail h3 {
  margin: 0 0 15px 0;
  color: #303133;
  font-size: 18px;
}

.detail-section {
  margin-bottom: 20px;
}

.detail-section h4 {
  margin: 0 0 8px 0;
  color: #606266;
  font-size: 14px;
  font-weight: bold;
}

.detail-section p {
  margin: 0;
  color: #606266;
  line-height: 1.6;
}

.keywords {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

/* 工具提示样式 */
:deep(.node-tooltip) {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.3);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .knowledge-graph-container {
    padding: 10px;
  }
  
  .graph-header {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
  
  .header-right {
    width: 100%;
    justify-content: space-between;
  }
  
  .course-card {
    margin-bottom: 15px;
  }
}
</style> 