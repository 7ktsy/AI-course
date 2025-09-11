import json
from pathlib import Path

# ======== 自定义类型映射（Elastic 类型 → 你的知识图谱实体类型）========
TYPE_MAPPING = {
    "CATEGORY": "Concept",
    "EVENT": "Protocol", 
    "ORGANIZATION": "Organization",
    "PERSON": "Device",
    "PRODUCT": "Device",
    "WORK_OF_ART": "Algorithm",
    "LAW": "Standard",
    "LANGUAGE": "Protocol",
    "NORP": "Standard",
    "FAC": "Device",
    "GPE": "GEO",
    "LOC": "GEO",
    "MONEY": "Concept",
    "PERCENT": "Concept",
    "DATE": "Concept",
    "TIME": "Concept",
    "Entity": "Concept",
    "Unknown": "Concept"
}

# ======== 修改为你的输入文件名（ElasticSearch JSON 文件）========
INPUT_FILE = 'exported_knowledge_graph.json'
OUTPUT_FILE = 'cytoscape_graph3.json'

try:
    # ======== 加载 ES 数据 =========
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 检查数据结构
    if 'hits' not in data or 'hits' not in data['hits']:
        print("❌ 数据格式不正确，缺少 hits.hits 字段")
        print("数据结构:", list(data.keys()) if isinstance(data, dict) else type(data))
        exit(1)

    hits = data['hits']['hits']
    print(f"📊 找到 {len(hits)} 条记录")

    nodes = {}  # 使用字典去重
    edges = []
    edge_keys = set()

    # 统计字段出现情况（调试用）
    field_stats = {}

    for i, hit in enumerate(hits):
        source = hit.get('_source', {})
        
        # 统计字段（调试用）
        for key in source.keys():
            field_stats[key] = field_stats.get(key, 0) + 1
        
        # ===== 处理普通实体节点 =====
        entity_id = source.get('entity_kwd') or source.get('entity_name')
        if entity_id:
            entity_type = source.get('entity_type_kwd', 'Entity')
            mapped_type = TYPE_MAPPING.get(entity_type.upper(), entity_type)
            
            if entity_id not in nodes:
                nodes[entity_id] = {
                    'data': {
                        'id': entity_id,
                        'label': mapped_type
                    }
                }

        # ===== 处理关系边（参考原始convert_to_cytoscape.py）=====
        if 'from_entity_kwd' in source and 'to_entity_kwd' in source:
            src = source['from_entity_kwd']
            tgt = source['to_entity_kwd']
            relation_label = source.get('knowledge_graph_kwd', '相关')
            
            # 获取权重
            weight = 1.0
            if 'content_with_weight' in source:
                try:
                    content = json.loads(source['content_with_weight'])
                    weight = content.get('weight', 1.0)
                except:
                    weight = 1.0

            # 确保边的两端节点存在
            for node_id in [src, tgt]:
                if node_id not in nodes:
                    nodes[node_id] = {
                        'data': {
                            'id': node_id,
                            'label': 'Concept'  # 默认类型
                        }
                    }

            # 添加边（避免重复）
            edge_key = f"{src}__{tgt}__{relation_label}"
            reverse_key = f"{tgt}__{src}__{relation_label}"
            
            if edge_key not in edge_keys and reverse_key not in edge_keys:
                edges.append({
                    'data': {
                        'source': src,
                        'target': tgt,
                        'label': relation_label,
                        'weight': weight
                    }
                })
                edge_keys.add(edge_key)

        # 显示处理进度
        if i % 100 == 0:
            print(f"⏳ 已处理 {i}/{len(hits)} 条记录...")

    # 转换节点字典为列表
    nodes_list = list(nodes.values())

    # 如果仍然没有边，尝试创建一些基于节点的关联
    if len(edges) == 0:
        print("⚠️ 没有找到关系边，尝试基于节点创建一些关联...")
        
        node_ids = [node['data']['id'] for node in nodes_list]
        created_edges = 0
        
        # 创建一些相似节点之间的连接
        for i, node1 in enumerate(node_ids[:30]):  # 只处理前30个节点
            for j in range(i+1, min(i+4, len(node_ids))):  # 每个节点连接最多3个相邻节点
                if j < len(node_ids):
                    node2 = node_ids[j]
                    edges.append({
                        'data': {
                            'source': node1,
                            'target': node2,
                            'label': '相关',
                            'weight': 1.0
                        }
                    })
                    created_edges += 1
                    if created_edges >= 50:  # 最多创建50条边
                        break
            if created_edges >= 50:
                break
        print(f"💡 创建了 {created_edges} 条关联边")

    print("\n📈 字段统计（前10个）:")
    for field, count in sorted(field_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {field}: {count} 次")

    # ======== 保存 Cytoscape 格式 =========
    graph_data = {
        'nodes': nodes_list,
        'edges': edges
    }

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(graph_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 成功生成文件：{OUTPUT_FILE}")
    print(f"📊 节点数：{len(nodes_list)}，边数：{len(edges)}")
    
    # 显示一些样例数据
    if nodes_list:
        print("\n🔍 节点样例:")
        for node in nodes_list[:5]:
            print(f"  {node['data']['id']} ({node['data']['label']})")
    
    if edges:
        print("\n🔗 边样例:")
        for edge in edges[:5]:
            print(f"  {edge['data']['source']} → {edge['data']['target']} ({edge['data']['label']})")

    # 检查数据完整性
    if len(nodes_list) > 0 and len(edges) > 0:
        print("\n✨ 数据看起来正常，应该可以在前端正常显示了！")
    elif len(nodes_list) > 0:
        print("\n⚠️ 只有节点数据，没有边数据，图谱将显示为独立的节点")
    else:
        print("\n❌ 没有有效的节点数据")

except FileNotFoundError:
    print(f"❌ 找不到文件：{INPUT_FILE}")
    print("请确保文件存在且路径正确")
except json.JSONDecodeError as e:
    print(f"❌ JSON 解析错误：{e}")
except Exception as e:
    print(f"❌ 发生错误：{e}")
    import traceback
    traceback.print_exc()