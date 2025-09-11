import json

def load_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def convert_to_cytoscape(data):
    nodes = {}
    edges = []

    for hit in data["hits"]["hits"]:
        source = hit["_source"]

        # 处理实体节点
        if "entity_kwd" in source or "entity_name" in source:
            node_id = source.get("entity_kwd") or source.get("entity_name")
            node_type = source.get("entity_type_kwd", "Entity")

            if node_id and node_id not in nodes:
                nodes[node_id] = {
                    "data": {
                        "id": node_id,
                        "label": node_type
                    }
                }

        # 处理关系边
        if "from_entity_kwd" in source and "to_entity_kwd" in source:
            src = source["from_entity_kwd"]
            tgt = source["to_entity_kwd"]
            label = source.get("knowledge_graph_kwd", "relation")

            weight = None
            if "content_with_weight" in source:
                try:
                    content = json.loads(source["content_with_weight"])
                    weight = content.get("weight", 1.0)
                except:
                    weight = 1.0

            # 添加边
            edges.append({
                "data": {
                    "source": src,
                    "target": tgt,
                    "label": label,
                    "weight": weight or 1.0
                }
            })

            # 确保边两端的节点也存在
            for node_id in [src, tgt]:
                if node_id not in nodes:
                    nodes[node_id] = {
                        "data": {
                            "id": node_id,
                            "label": "Unknown"
                        }
                    }

    return {
        "nodes": list(nodes.values()),
        "edges": edges
    }

def save_output(output_path, graph):
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(graph, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    input_file = "exported_knowledge_graph.json"
    output_file = "cytoscape_graph.json"

    data = load_data(input_file)
    graph = convert_to_cytoscape(data)
    save_output(output_file, graph)

    print(f"✅ 转换完成，输出文件已保存为：{output_file}")
