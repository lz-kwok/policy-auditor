# -*- coding: utf-8 -*-
"""
graph_generator.py - 基于制度数据自动生成Mermaid制度图谱

Usage:
  python graph_generator.py --input <policies.json> --output <graph.mmd> [--format mermaid|json]
"""

import os
import sys
import json
import argparse
from collections import defaultdict

# 确保stdout使用UTF-8
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

def load_policies(json_path):
    """加载policies.json"""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get("policies", [])

def build_graph(policies):
    """基于字段建立制度关系图"""
    
    # 按知识域分组
    by_domain = defaultdict(list)
    for p in policies:
        domain = p.get("knowledge_domain", "未知")
        by_domain[domain].append(p)
    
    # 按类别分组
    by_category = defaultdict(list)
    for p in policies:
        category = p.get("category", "未知")
        by_category[category].append(p)
    
    # 建立替代关系
    replaces_map = {}
    for p in policies:
        replaces = p.get("replaces")
        if replaces:
            # 尝试在policies中找到被替代的制度
            for p2 in policies:
                if p2.get("original_name") and replaces in p2["original_name"]:
                    replaces_map[p["index"]] = p2["index"]
                    break
    
    # 建立冲突关系
    conflict_map = {}
    for p in policies:
        has_conflict = p.get("has_conflict")
        if has_conflict and "是" in str(has_conflict):
            conflict_map[p["index"]] = True
    
    return {
        "by_domain": by_domain,
        "by_category": by_category,
        "replaces": replaces_map,
        "conflicts": conflict_map
    }

def generate_mermaid(graph_data, policies):
    """生成Mermaid格式的制度图谱"""
    
    lines = []
    lines.append("graph TD")
    lines.append("")
    
    # 建立index到policy的映射
    policy_map = {p["index"]: p for p in policies}
    
    # 按知识域生成子图
    for domain, domain_policies in graph_data["by_domain"].items():
        # 清理域名用于Mermaid标签
        safe_domain = domain.replace(" ", "_").replace("-", "_") if domain else "未知"
        lines.append(f"    subgraph {safe_domain}[\"{domain}\"]")
        
        for p in domain_policies[:10]:  # 限制每个域最多显示10个
            idx = p["index"]
            name = p.get("original_name", f"制度{idx}")
            # 截断长名称
            short_name = name[:20] + "..." if len(name) > 20 else name
            safe_name = short_name.replace('"', "'")
            lines.append(f"        P{idx}[\"{safe_name}\"]")
        
        if len(domain_policies) > 10:
            lines.append(f"        P{domain}_more[\"...还有{len(domain_policies)-10}条\"]")
        
        lines.append("    end")
        lines.append("")
    
    # 生成替代关系
    if graph_data["replaces"]:
        lines.append("    %% 替代关系")
        for new_idx, old_idx in graph_data["replaces"].items():
            if new_idx in policy_map and old_idx in policy_map:
                lines.append(f"    P{new_idx} -.->|替代| P{old_idx}")
        lines.append("")
    
    # 生成冲突关系
    if graph_data["conflicts"]:
        lines.append("    %% 冲突关系")
        for idx in list(graph_data["conflicts"].keys())[:5]:  # 限制显示5个
            if idx in policy_map:
                lines.append(f"    P{idx} -->|冲突| P{idx}_conflict[\"需要检查\"]")
        lines.append("")
    
    # 添加样式
    lines.append("    %% 样式")
    lines.append("    classDef default fill:#f9f9f9,stroke:#333,stroke-width:1px")
    
    return "\n".join(lines)

def generate_json(graph_data, policies):
    """生成JSON格式的图谱数据"""
    
    nodes = []
    edges = []
    
    # 建立节点
    for p in policies:
        nodes.append({
            "id": p["index"],
            "name": p.get("original_name", f"制度{p['index']}"),
            "domain": p.get("knowledge_domain"),
            "category": p.get("category"),
            "department": p.get("department")
        })
    
    # 建立替代关系边
    for new_idx, old_idx in graph_data["replaces"].items():
        edges.append({
            "source": new_idx,
            "target": old_idx,
            "type": "replaces",
            "label": "替代"
        })
    
    # 建立同类别关系边（限制数量）
    category_groups = defaultdict(list)
    for p in policies:
        category = p.get("category")
        if category:
            category_groups[category].append(p["index"])
    
    for category, indices in category_groups.items():
        # 每个类别最多建5条边
        for i in range(min(5, len(indices)-1)):
            edges.append({
                "source": indices[i],
                "target": indices[i+1],
                "type": "same_category",
                "label": f"同属{category}"
            })
    
    return {
        "nodes": nodes,
        "edges": edges,
        "statistics": {
            "total_policies": len(policies),
            "domains": len(graph_data["by_domain"]),
            "categories": len(graph_data["by_category"]),
            "replaces_relations": len(graph_data["replaces"]),
            "conflict_relations": len(graph_data["conflicts"])
        }
    }

def main():
    parser = argparse.ArgumentParser(description="生成制度图谱")
    parser.add_argument("--input", required=True, help="policies.json文件路径")
    parser.add_argument("--output", required=True, help="输出文件路径")
    parser.add_argument("--format", choices=["mermaid", "json"], default="mermaid", help="输出格式")
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"错误：输入文件不存在: {args.input}")
        sys.exit(1)
    
    print(f"正在加载制度数据: {args.input}")
    policies = load_policies(args.input)
    print(f"已加载 {len(policies)} 条制度")
    
    # 构建图谱
    graph_data = build_graph(policies)
    
    print(f"\n=== 图谱统计 ===")
    print(f"知识域数量: {len(graph_data['by_domain'])}")
    print(f"类别数量: {len(graph_data['by_category'])}")
    print(f"替代关系: {len(graph_data['replaces'])}")
    print(f"冲突关系: {len(graph_data['conflicts'])}")
    
    # 生成输出
    if args.format == "mermaid":
        output = generate_mermaid(graph_data, policies)
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
    else:
        output = generate_json(graph_data, policies)
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n已输出{args.format.upper()}格式到: {args.output}")

if __name__ == "__main__":
    main()
