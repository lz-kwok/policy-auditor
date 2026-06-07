# -*- coding: utf-8 -*-
"""
batch_audit.py - Aggregates policy audit JSON results into a Markdown Risk Map and a matplotlib Heatmap.

Usage:
  python batch_audit.py --input-dir <dir_with_jsons> --out-dir <output_dir>
"""

import os
import sys
import json
import argparse
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# Ensure stdout uses UTF-8 to prevent encoding issues with Chinese characters
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

# Set up matplotlib to display Chinese characters correctly on Windows
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun']
plt.rcParams['axes.unicode_minus'] = False

DIMENSIONS = [
    "合法性", "合规性", "完整性", "一致性", "可执行性",
    "风险性", "权责清晰", "审批合理", "数据合规", "AI合规"
]

def load_audit_results(input_dir):
    results = []
    if not os.path.exists(input_dir):
        print(f"Error: Input directory {input_dir} does not exist.")
        return results

    for f in os.listdir(input_dir):
        if f.endswith(".json") and not f.endswith(".metadata.json") and f != "tokens.json" and f != "content.json":
            path = os.path.join(input_dir, f)
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    if "filename" in data and "risks" in data:
                        results.append(data)
            except Exception as e:
                print(f"Warning: Failed to load {f}: {e}")
    return results

def generate_markdown_map(results, out_path):
    lines = []
    lines.append("# 🗺️ 企业制度合规与管理风险地图 (Risk Map)")
    lines.append("")
    lines.append("本风险地图基于企业制度库的批量审计结果自动生成，展现各维度下存在的漏洞级别（数值越大风险越高，范围 0 - 3）。")
    lines.append("")
    
    # Header
    header = "| 制度文件名称 | " + " | ".join(DIMENSIONS) + " | 平均风险 |"
    divider = "| :--- | " + " | ".join([":---:"] * len(DIMENSIONS)) + " | :---: |"
    lines.append(header)
    lines.append(divider)
    
    # Rows
    for r in results:
        scores = []
        row = f"| {r['filename']} |"
        for dim in DIMENSIONS:
            score = r["risks"].get(dim, 0)
            scores.append(score)
            # Add visual indicators for markdown readability
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
    
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))
    print(f"Markdown risk map generated at: {out_path}")
    return "\n".join(lines)

def generate_heatmap(results, out_path):
    if not results:
        print("No audit results found to plot.")
        return

    # Extract data for plotting
    filenames = [r["filename"] for r in results]
    # Reverse so top file is plotted at the top of y-axis
    filenames.reverse()
    
    data_matrix = []
    for f_name in filenames:
        r = next(item for item in results if item["filename"] == f_name)
        row_data = [r["risks"].get(dim, 0) for dim in DIMENSIONS]
        data_matrix.append(row_data)

    # Re-reverse filenames for labels mapping correctly to rows
    # data_matrix is indexed by rows. Row 0 corresponds to filenames[0]
    
    # Plotting
    fig, ax = plt.subplots(figsize=(12, max(6, len(filenames) * 0.8)))
    
    # Colormap: Green -> Yellow -> Orange -> Red
    colors = ["#2ecc71", "#f1c40f", "#e67e22", "#e74c3c"]
    cmap = mcolors.ListedColormap(colors)
    bounds = [-0.5, 0.5, 1.5, 2.5, 3.5]
    norm = mcolors.BoundaryNorm(bounds, cmap.N)
    
    im = ax.imshow(data_matrix, cmap=cmap, norm=norm, aspect='auto')
    
    # Axis labels
    ax.set_xticks(range(len(DIMENSIONS)))
    ax.set_xticklabels(DIMENSIONS, fontsize=10, rotation=45, ha='right')
    ax.set_yticks(range(len(filenames)))
    # Truncate long filenames for visual clarity in the chart
    truncated_labels = [f[:25] + "..." if len(f) > 25 else f for f in filenames]
    ax.set_yticklabels(truncated_labels, fontsize=10)
    
    # Grid lines and spines
    ax.spines[:].set_color('#bdc3c7')
    ax.set_xticks([x - 0.5 for x in range(len(DIMENSIONS) + 1)], minor=True)
    ax.set_yticks([y - 0.5 for y in range(len(filenames) + 1)], minor=True)
    ax.grid(which="minor", color="#ffffff", linestyle='-', linewidth=3)
    ax.tick_params(which="minor", bottom=False, left=False)
    
    # Annotate numbers in cells
    for i in range(len(filenames)):
        for j in range(len(DIMENSIONS)):
            val = data_matrix[i][j]
            ax.text(j, i, str(val), ha="center", va="center", 
                    color="white" if val >= 2 else "black", 
                    fontweight="bold")
                    
    # Colorbar legends
    cbar = fig.colorbar(im, ax=ax, ticks=[0, 1, 2, 3], shrink=0.7)
    cbar.ax.set_yticklabels(['0 (无风险)', '1 (低风险)', '2 (中风险)', '3 (高风险)'], fontsize=9)
    cbar.outline.set_visible(False)
    
    ax.set_title("企业制度管理风险热力图 (Policy Risk Heatmap)", fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    
    plt.savefig(out_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"Risk heatmap image saved at: {out_path}")

def main():
    parser = argparse.ArgumentParser(description="Batch audit aggregator")
    parser.add_argument("--input-dir", required=True, help="Directory containing audit json files")
    parser.add_argument("--out-dir", required=True, help="Output directory for results")
    args = parser.parse_args()
    
    if not os.path.exists(args.out_dir):
        os.makedirs(args.out_dir)
        
    results = load_audit_results(args.input_dir)
    if not results:
        print("No valid JSON audit results found.")
        sys.exit(0)
        
    map_path = os.path.join(args.out_dir, "risk_map.md")
    generate_markdown_map(results, map_path)
    
    heatmap_path = os.path.join(args.out_dir, "risk_heatmap.png")
    generate_heatmap(results, heatmap_path)
    print("Batch aggregation completed successfully.")

if __name__ == "__main__":
    main()
