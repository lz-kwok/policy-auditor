# -*- coding: utf-8 -*-
"""
batch_audit.py - 汇总批量审计结果，生成风险地图和热力图

Usage:
  python batch_audit.py --input-dir <dir_with_jsons> --out-dir <output_dir>
"""

import os
import sys
import json
import argparse
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# 确保stdout使用UTF-8
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

# 设置matplotlib中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun']
plt.rcParams['axes.unicode_minus'] = False

# 十大审计维度
DIMENSIONS = [
    "合法性", "合规性", "完整性", "一致性", "可执行性",
    "风险性", "权责清晰", "审批合理", "数据合规", "AI合规"
]

def load_audit_results(input_dir):
    """加载目录中的审计结果JSON文件"""
    results = []
    if not os.path.exists(input_dir):
        print(f"错误：输入目录不存在: {input_dir}")
        return results

    for f in sorted(os.listdir(input_dir)):
        if f.endswith(".json") and not f.endswith(".metadata.json") and f != "tokens.json" and f != "content.json":
            path = os.path.join(input_dir, f)
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    # 验证必要字段
                    if "policy_name" in data and "risks" in data:
                        results.append(data)
                    elif "filename" in data and "risks" in data:
                        # 兼容v1格式
                        results.append(data)
            except Exception as e:
                print(f"警告：加载失败 {f}: {e}")
    return results

def generate_markdown_map(results, out_path):
    """生成Markdown格式的风险地图"""
    lines = []
    lines.append("# 🗺️ 企业制度合规与管理风险地图 (Risk Map)")
    lines.append("")
    lines.append("本风险地图基于企业制度库的批量审计结果自动生成，展现各维度下存在的漏洞级别（数值越大风险越高，范围 0 - 3）。")
    lines.append("")
    lines.append(f"**审计制度总数**：{len(results)}")
    lines.append("")
    
    # 计算统计数据
    total_risks = {dim: 0 for dim in DIMENSIONS}
    high_risk_count = 0
    
    for r in results:
        for dim in DIMENSIONS:
            score = r.get("risks", {}).get(dim, 0)
            total_risks[dim] += score
            if score >= 2:
                high_risk_count += 1
    
    lines.append("### 风险分布统计")
    lines.append("")
    lines.append("| 维度 | 总分 | 平均分 | 风险等级 |")
    lines.append("| :--- | :---: | :---: | :---: |")
    
    for dim in DIMENSIONS:
        total = total_risks[dim]
        avg = total / len(results) if results else 0
        if avg >= 2:
            level = "🔴 高"
        elif avg >= 1:
            level = "🟠 中"
        else:
            level = "🟢 低"
        lines.append(f"| {dim} | {total} | {avg:.2f} | {level} |")
    
    lines.append("")
    lines.append(f"**高风险制度数量**：{high_risk_count}")
    lines.append("")
    
    # Header
    header = "| 制度文件名称 | " + " | ".join(DIMENSIONS) + " | 平均风险 |"
    divider = "| :--- | " + " | ".join([":---:"] * len(DIMENSIONS)) + " | :---: |"
    lines.append(header)
    lines.append(divider)
    
    # Rows
    for r in results:
        scores = []
        name = r.get("policy_name", r.get("filename", "未知"))
        # 截断长名称
        short_name = name[:30] + "..." if len(name) > 30 else name
        row = f"| {short_name} |"
        
        for dim in DIMENSIONS:
            score = r.get("risks", {}).get(dim, 0)
            scores.append(score)
            if score == 3:
                row += " 🔴 3 |"
            elif score == 2:
                row += " 🟠 2 |"
            elif score == 1:
                row += " 🟡 1 |"
            else:
                row += " 🟢 0 |"
        
        avg_score = sum(scores) / len(scores) if scores else 0
        row += f" **{avg_score:.1f}** |"
        lines.append(row)
        
    lines.append("")
    lines.append("👉 *注：🔴 高风险（须立即修订）；🟠 中风险（建议限期整改）；🟡 低风险（待优化）；🟢 无风险/已对齐。*")
    
    # 添加风险项汇总
    all_risk_items = []
    for r in results:
        risk_items = r.get("risk_items", [])
        for item in risk_items:
            item["source_policy"] = r.get("policy_name", r.get("filename", "未知"))
            all_risk_items.append(item)
    
    if all_risk_items:
        lines.append("")
        lines.append("### 高频风险项 Top 10")
        lines.append("")
        lines.append("| 风险等级 | 维度 | 涉及制度 | 风险描述 |")
        lines.append("| :---: | :--- | :--- | :--- |")
        
        # 按风险等级排序
        level_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
        sorted_items = sorted(all_risk_items, key=lambda x: level_order.get(x.get("level", "P3"), 99))
        
        for item in sorted_items[:10]:
            level = item.get("level", "P3")
            dimension = item.get("dimension", "未知")
            source = item.get("source_policy", "未知")
            desc = item.get("description", "未知")
            short_desc = desc[:30] + "..." if len(desc) > 30 else desc
            lines.append(f"| {level} | {dimension} | {source[:20]}... | {short_desc} |")
    
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))
    print(f"Markdown风险地图已生成: {out_path}")
    return "\n".join(lines)

def generate_heatmap(results, out_path):
    """生成风险热力图"""
    if not results:
        print("没有审计结果可供绘图。")
        return

    # 提取数据
    filenames = [r.get("policy_name", r.get("filename", f"制度{i}")) for i, r in enumerate(results)]
    # 截断长名称
    filenames = [f[:15] + "..." if len(f) > 15 else f for f in filenames]
    filenames.reverse()
    
    data_matrix = []
    for i, r in enumerate(results):
        row_data = [r.get("risks", {}).get(dim, 0) for dim in DIMENSIONS]
        data_matrix.append(row_data)
    data_matrix.reverse()

    # 绘图
    fig, ax = plt.subplots(figsize=(14, max(8, len(filenames) * 0.6)))
    
    # 颜色映射：绿 -> 黄 -> 橙 -> 红
    colors = ["#2ecc71", "#f1c40f", "#e67e22", "#e74c3c"]
    cmap = mcolors.ListedColormap(colors)
    bounds = [-0.5, 0.5, 1.5, 2.5, 3.5]
    norm = mcolors.BoundaryNorm(bounds, cmap.N)
    
    im = ax.imshow(data_matrix, cmap=cmap, norm=norm, aspect='auto')
    
    # 坐标轴标签
    ax.set_xticks(range(len(DIMENSIONS)))
    ax.set_xticklabels(DIMENSIONS, fontsize=10, rotation=45, ha='right')
    ax.set_yticks(range(len(filenames)))
    ax.set_yticklabels(filenames, fontsize=8)
    
    # 网格线
    ax.spines[:].set_color('#bdc3c7')
    ax.set_xticks([x - 0.5 for x in range(len(DIMENSIONS) + 1)], minor=True)
    ax.set_yticks([y - 0.5 for y in range(len(filenames) + 1)], minor=True)
    ax.grid(which="minor", color="#ffffff", linestyle='-', linewidth=2)
    ax.tick_params(which="minor", bottom=False, left=False)
    
    # 单元格标注
    for i in range(len(filenames)):
        for j in range(len(DIMENSIONS)):
            val = data_matrix[i][j]
            ax.text(j, i, str(val), ha="center", va="center", 
                    color="white" if val >= 2 else "black", 
                    fontsize=8, fontweight="bold")
                    
    # 图例
    cbar = fig.colorbar(im, ax=ax, ticks=[0, 1, 2, 3], shrink=0.7)
    cbar.ax.set_yticklabels(['0 (无风险)', '1 (低风险)', '2 (中风险)', '3 (高风险)'], fontsize=9)
    cbar.outline.set_visible(False)
    
    ax.set_title("企业制度管理风险热力图 (Policy Risk Heatmap)", fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    
    plt.savefig(out_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"风险热力图已保存: {out_path}")

def main():
    parser = argparse.ArgumentParser(description="批量审计结果汇总")
    parser.add_argument("--input-dir", required=True, help="审计结果JSON目录")
    parser.add_argument("--out-dir", required=True, help="输出目录")
    args = parser.parse_args()
    
    if not os.path.exists(args.out_dir):
        os.makedirs(args.out_dir)
        
    results = load_audit_results(args.input_dir)
    if not results:
        print("未找到有效的审计结果JSON文件。")
        sys.exit(0)
    
    print(f"已加载 {len(results)} 条审计结果")
    
    # 生成风险地图
    map_path = os.path.join(args.out_dir, "risk_map.md")
    generate_markdown_map(results, map_path)
    
    # 生成热力图
    heatmap_path = os.path.join(args.out_dir, "risk_heatmap.png")
    generate_heatmap(results, heatmap_path)
    
    print("\n批量汇总完成。")

if __name__ == "__main__":
    main()
