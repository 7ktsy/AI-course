<template>
  <div class="node-detail-container">
    <el-card class="detail-card">
      <template #header>
        <div class="card-header">
          <el-button @click="goBack" icon="ArrowLeft" type="text">
            返回知识图谱
          </el-button>
          <h2>{{ nodeInfo.title || nodeInfo.id }}</h2>
        </div>
      </template>

      <!-- 节点基本信息 -->
      <div class="node-info-section">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="节点ID">
            {{ nodeInfo.id }}
          </el-descriptions-item>
          <el-descriptions-item label="节点类型">
            <el-tag :type="getNodeTypeColor(nodeInfo.label)">
              {{ nodeInfo.label }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="重要性排名" v-if="nodeInfo.rank">
            {{ nodeInfo.rank }}
          </el-descriptions-item>
          <el-descriptions-item label="PageRank值" v-if="nodeInfo.pagerank">
            {{ nodeInfo.pagerank.toFixed(6) }}
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 关键词 -->
      <div class="keywords-section" v-if="nodeInfo.important_keywords && nodeInfo.important_keywords.length">
        <h3>关键词</h3>
        <div class="keywords-list">
          <el-tag 
            v-for="keyword in nodeInfo.important_keywords" 
            :key="keyword"
            size="large"
            type="info"
            style="margin-right: 12px; margin-bottom: 12px;"
          >
            {{ keyword }}
          </el-tag>
        </div>
      </div>

      <!-- AI详细讲解 -->
      <div class="ai-explanation-section">
        <h3>AI详细讲解</h3>
        <div class="explanation-content">
          <div v-if="loading" class="loading-container">
            <el-skeleton :rows="6" animated />
          </div>
          <div v-else-if="aiExplanation" class="explanation-text">
            <div class="markdown-content" v-html="renderedExplanation"></div>
          </div>
          <div v-else class="no-explanation">
            <el-empty description="暂无AI讲解内容" />
          </div>
        </div>
      </div>

      <!-- 相关连接 -->
      <div class="connections-section" v-if="relatedNodes.length">
        <h3>相关连接</h3>
        <div class="related-nodes">
          <el-card 
            v-for="node in relatedNodes" 
            :key="node.id"
            class="related-node-card"
            @click="viewRelatedNode(node)"
          >
            <div class="related-node-content">
              <h4>{{ node.title || node.id }}</h4>
              <el-tag size="small" :type="getNodeTypeColor(node.label)">
                {{ node.label }}
              </el-tag>
              <p v-if="node.description" class="node-description">
                {{ node.description }}
              </p>
            </div>
          </el-card>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

export default {
  name: 'NodeDetail',
  setup() {
    const route = useRoute()
    const router = useRouter()
    
    const nodeInfo = ref({})
    const aiExplanation = ref('')
    const loading = ref(false)
    const relatedNodes = ref([])

    // 简单的Markdown渲染函数
    const renderMarkdown = (text) => {
      if (!text) return ''
      
      return text
        // 处理标题
        .replace(/^### (.*$)/gim, '<h3 class="markdown-h3">$1</h3>')
        .replace(/^## (.*$)/gim, '<h2 class="markdown-h2">$1</h2>')
        .replace(/^# (.*$)/gim, '<h1 class="markdown-h1">$1</h1>')
        // 处理粗体
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        // 处理斜体
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        // 处理列表项（包括数字列表和项目符号）
        .replace(/^\d+\.\s+(.*$)/gim, '<li class="markdown-li">$1</li>')
        .replace(/^-\s+(.*$)/gim, '<li class="markdown-li">$1</li>')
        // 处理段落分隔
        .replace(/\n\n/g, '</p><p class="markdown-p">')
        // 处理换行
        .replace(/\n/g, '<br>')
        // 包装段落（排除已经是标题或列表项的行）
        .replace(/^(?!<[h|li|p])(.*?)$/gm, '<p class="markdown-p">$1</p>')
        // 清理多余的标签
        .replace(/<p class="markdown-p"><\/p>/g, '')
        .replace(/<p class="markdown-p"><br><\/p>/g, '')
        // 处理列表包装（将连续的li标签包装在ul中）
        .replace(/(<li class="markdown-li">.*?<\/li>)(?=<li class="markdown-li">|$)/gs, '<ul class="markdown-ul">$1</ul>')
        // 清理多余的ul标签
        .replace(/<\/ul>\s*<ul class="markdown-ul">/g, '')
        // 处理特殊格式
        .replace(/•\s+(.*?)(?=\n|$)/g, '<li class="markdown-li">$1</li>')
        // 处理总结部分
        .replace(/### 总结\n(.*?)(?=\n\n|$)/gs, '<div class="markdown-summary"><h3 class="markdown-h3">总结</h3><p class="markdown-p">$1</p></div>')
    }

    // 渲染后的AI讲解内容
    const renderedExplanation = computed(() => {
      if (!aiExplanation.value) return ''
      return renderMarkdown(aiExplanation.value)
    })

    // 获取节点类型颜色
    const getNodeTypeColor = (label) => {
      const colorMap = {
        'CATEGORY': 'primary',
        'EVENT': 'danger',
        'ORGANIZATION': 'success',
        'PERSON': 'warning',
        'LOCATION': 'info',
        'CONCEPT': 'primary',
        'PROTOCOL': 'danger',
        'DEVICE': 'warning',
        'TECHNOLOGY': 'info'
      }
      return colorMap[label] || 'info'
    }

    // 返回知识图谱
    const goBack = () => {
      router.push('/dashboard/knowledge-graph')
    }

    // 查看相关节点
    const viewRelatedNode = (node) => {
      router.push({
        name: 'NodeDetail',
        params: { 
          nodeId: node.id,
          nodeData: encodeURIComponent(JSON.stringify(node))
        }
      })
    }

    // 调用AI接口获取详细讲解
    const getAIExplanation = async () => {
      loading.value = true
      try {
        const token = localStorage.getItem('token')
        const question = `请详细讲解知识图谱中的节点"${nodeInfo.value.id}"，包括其定义、重要性、应用场景和相关知识。如果该节点有描述信息"${nodeInfo.value.description || ''}"，请基于这些信息进行详细解释。请使用清晰的格式，包括标题、要点和总结。要求返回的格式正确。`
        
        // 构建查询参数
        const params = new URLSearchParams({
          question: question,
          chat_name: '计算机网络问题解答助手'
        })
        
        const response = await fetch(`http://127.0.0.1:8000/chat/simple?${params}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          }
        })

        if (response.ok) {
          const data = await response.json()
          if (data.code === 0 && data.data) {
            aiExplanation.value = data.data.answer || '抱歉，AI暂时无法提供该节点的详细讲解。'
          } else {
            aiExplanation.value = '抱歉，AI暂时无法提供该节点的详细讲解。'
          }
        } else {
          const errorData = await response.json()
          console.error('AI接口错误:', errorData)
          aiExplanation.value = '抱歉，AI服务暂时不可用，请稍后再试。'
        }
      } catch (error) {
        console.error('获取AI讲解失败:', error)
        aiExplanation.value = '抱歉，AI服务暂时不可用，请稍后再试。如果问题持续存在，请联系管理员。'
      } finally {
        loading.value = false
      }
    }

    // 获取相关节点
    const getRelatedNodes = async () => {
      try {
        // 从localStorage获取知识图谱数据
        const graphDataStr = localStorage.getItem('knowledgeGraphData')
        if (!graphDataStr) {
          console.log('未找到知识图谱数据')
          return
        }

        const graphData = JSON.parse(graphDataStr)
        const currentNodeId = nodeInfo.value.id
        
        // 找到与当前节点相连的边
        const relatedEdges = graphData.edges.filter(edge => 
          edge.data.source === currentNodeId || edge.data.target === currentNodeId
        )
        
        // 获取相关节点的ID
        const relatedNodeIds = new Set()
        relatedEdges.forEach(edge => {
          if (edge.data.source === currentNodeId) {
            relatedNodeIds.add(edge.data.target)
          } else {
            relatedNodeIds.add(edge.data.source)
          }
        })
        
        // 获取相关节点的详细信息
        const relatedNodesData = graphData.nodes
          .filter(node => relatedNodeIds.has(node.data.id))
          .slice(0, 6) // 限制显示6个相关节点
          .map(node => ({
            id: node.data.id,
            title: node.data.title || node.data.id,
            label: node.data.label,
            description: node.data.description,
            pagerank: node.data.pagerank,
            rank: node.data.rank
          }))
        
        relatedNodes.value = relatedNodesData
        console.log('找到相关节点:', relatedNodesData.length)
      } catch (error) {
        console.error('获取相关节点失败:', error)
        // 如果获取失败，使用默认数据
        relatedNodes.value = [
          {
            id: 'related_node_1',
            title: '相关概念',
            label: 'CONCEPT',
            description: '这是一个相关的概念节点'
          },
          {
            id: 'related_node_2',
            title: '相关技术',
            label: 'TECHNOLOGY',
            description: '这是一个相关的技术节点'
          }
        ]
      }
    }

    // 初始化页面数据
    const initPageData = () => {
      const nodeId = route.params.nodeId
      const nodeData = route.params.nodeData

      if (nodeData) {
        try {
          nodeInfo.value = JSON.parse(decodeURIComponent(nodeData))
        } catch (error) {
          console.error('解析节点数据失败:', error)
          ElMessage.error('节点数据解析失败')
          goBack()
          return
        }
      } else if (nodeId) {
        // 如果只有nodeId，可以从localStorage或其他地方获取节点数据
        nodeInfo.value = { id: nodeId, label: 'Unknown' }
      } else {
        ElMessage.error('缺少节点信息')
        goBack()
        return
      }

      // 获取AI讲解和相关节点
      getAIExplanation()
      getRelatedNodes()
    }

    onMounted(() => {
      initPageData()
    })

    return {
      nodeInfo,
      aiExplanation,
      loading,
      relatedNodes,
      renderedExplanation,
      getNodeTypeColor,
      goBack,
      viewRelatedNode
    }
  }
}
</script>

<style scoped>
.node-detail-container {
  padding: 20px;
  min-height: calc(100vh - 120px);
  background: #f5f7fa;
}

.detail-card {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 16px;
}

.card-header h2 {
  margin: 0;
  color: #303133;
}

.node-info-section {
  margin-bottom: 24px;
}

.keywords-section {
  margin-bottom: 24px;
}

.keywords-section h3 {
  margin-bottom: 16px;
  color: #303133;
  font-size: 18px;
}

.keywords-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.ai-explanation-section {
  margin-bottom: 24px;
}

.ai-explanation-section h3 {
  margin-bottom: 16px;
  color: #303133;
  font-size: 18px;
}

.explanation-content {
  background: #fafafa;
  border-radius: 8px;
  padding: 20px;
  min-height: 200px;
}

.loading-container {
  padding: 20px;
}

.explanation-text {
  line-height: 1.8;
  color: #606266;
  font-size: 14px;
}

.no-explanation {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
}

.connections-section {
  margin-bottom: 24px;
}

.connections-section h3 {
  margin-bottom: 16px;
  color: #303133;
  font-size: 18px;
}

.related-nodes {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.related-node-card {
  cursor: pointer;
  transition: all 0.3s ease;
}

.related-node-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.related-node-content h4 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 16px;
}

.node-description {
  margin: 8px 0 0 0;
  color: #909399;
  font-size: 12px;
  line-height: 1.4;
}

:deep(.el-descriptions__label) {
  font-weight: 600;
}

:deep(.el-card__header) {
  padding: 16px 20px;
  border-bottom: 1px solid #ebeef5;
}

:deep(.el-card__body) {
  padding: 20px;
}

/* Markdown样式 */
.markdown-content {
  line-height: 1.8;
  color: #606266;
  font-size: 14px;
}

.markdown-content .markdown-h1 {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin: 20px 0 16px 0;
  border-bottom: 2px solid #409EFF;
  padding-bottom: 8px;
}

.markdown-content .markdown-h2 {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
  margin: 18px 0 14px 0;
  border-left: 4px solid #409EFF;
  padding-left: 12px;
}

.markdown-content .markdown-h3 {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  margin: 16px 0 12px 0;
}

.markdown-content .markdown-p {
  margin: 12px 0;
  line-height: 1.8;
}

.markdown-content .markdown-ul {
  margin: 12px 0;
  padding-left: 20px;
}

.markdown-content .markdown-li {
  margin: 8px 0;
  line-height: 1.6;
  list-style-type: disc;
}

.markdown-content strong {
  color: #409EFF;
  font-weight: bold;
}

.markdown-content em {
  color: #67C23A;
  font-style: italic;
}

.markdown-content .markdown-summary {
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border: 1px solid #bae6fd;
  border-radius: 8px;
  padding: 16px;
  margin: 20px 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.markdown-content .markdown-summary .markdown-h3 {
  color: #0369a1;
  margin-top: 0;
  border-left: 4px solid #0369a1;
  padding-left: 12px;
}
</style> 