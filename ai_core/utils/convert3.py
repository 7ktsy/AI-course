import json

def load_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def convert_to_cytoscape(data):
    nodes = {}
    edges = []

    print("开始处理数据...")
    
    for i, hit in enumerate(data["hits"]["hits"]):
        source = hit["_source"]

        # 处理实体节点
        if "entity_kwd" in source or "entity_name" in source:
            node_id = source.get("entity_kwd") or source.get("entity_name")
            node_type = source.get("entity_type_kwd", "Entity")
            
            # 解析详细信息
            description = ""
            pagerank = 0.0
            rank = 0
            
            if "content_with_weight" in source:
                try:
                    content = json.loads(source["content_with_weight"])
                    description = content.get("description", "")
                    pagerank = content.get("pagerank", 0.0)
                    rank = content.get("rank", 0)
                    if description:
                        print(f"节点 {node_id} 有描述，长度: {len(description)}")
                except Exception as e:
                    print(f"解析content_with_weight失败: {e}")

            if node_id and node_id not in nodes:
                nodes[node_id] = {
                    "data": {
                        "id": node_id,
                        "label": node_type,
                        "description": description,
                        "pagerank": pagerank,
                        "rank": rank,
                        "title": source.get("title_tks", ""),
                        "important_keywords": source.get("important_kwd", []),
                        "raw_content": source.get("content_ltks", ""),
                        "content_sm": source.get("content_sm_ltks", "")
                    }
                }

        # 处理关系边
        if "from_entity_kwd" in source and "to_entity_kwd" in source:
            src = source["from_entity_kwd"]
            tgt = source["to_entity_kwd"]
            label = source.get("knowledge_graph_kwd", "relation")

            # **重要：只有在节点不存在时才创建Unknown节点**
            for node_id in [src, tgt]:
                if node_id not in nodes:
                    print(f"警告：为关系边创建缺失节点: {node_id}")
                    nodes[node_id] = {
                        "data": {
                            "id": node_id,
                            "label": "Unknown",
                            "description": "",
                            "pagerank": 0.0,
                            "rank": 0,
                            "title": "",
                            "important_keywords": [],
                            "raw_content": "",
                            "content_sm": ""
                        }
                    }

            # 添加边
            weight = 1.0
            if "content_with_weight" in source:
                try:
                    content = json.loads(source["content_with_weight"])
                    weight = content.get("weight", 1.0)
                except:
                    weight = 1.0

            edges.append({
                "data": {
                    "source": src,
                    "target": tgt,
                    "label": label,
                    "weight": weight
                }
            })

        if i % 500 == 0:
            print(f"已处理 {i} 条记录...")

    print(f"处理完成！总节点数: {len(nodes)}, 总边数: {len(edges)}")
    
    # 统计有描述的节点数量
    nodes_with_description = sum(1 for node in nodes.values() 
                               if node["data"]["description"])
    print(f"有描述的节点数: {nodes_with_description}")

    return {
        "nodes": list(nodes.values()),
        "edges": edges
    }

def save_output(output_path, graph):
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(graph, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    input_file = "exported_knowledge_graph.json"
    output_file = "cytoscape_graph5.json"

    data = load_data(input_file)
    graph = convert_to_cytoscape(data)
    save_output(output_file, graph)

    print(f"✅ 转换完成，输出文件已保存为：{output_file}")
    print(f"📊 节点数: {len(graph['nodes'])}, 边数: {len(graph['edges'])}")