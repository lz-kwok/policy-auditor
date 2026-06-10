# -*- coding: utf-8 -*-
"""
data_loader.py - 加载Excel制度数据，输出结构化JSON

Usage:
  python data_loader.py --excel <excel_path> --output <output_json>
"""

import os
import sys
import json
import argparse
import pandas as pd

# 确保stdout使用UTF-8
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

# Excel列映射（0-indexed）
COLUMN_MAP = {
    0: "index",           # 序号
    1: "original_name",   # 原文件名称
    2: "policy_id",       # 制度编号
    3: "hierarchy",       # 制度层级
    4: "knowledge_domain",# 知识域
    5: "category",        # 类别
    6: "department",      # 发文部门
    7: "scope",           # 适用范围/单位
    8: "scenario",        # 适用场景
    9: "confidential",    # 密级
    10: "effective_date", # 生效日期
    11: "version",        # 版本号
    12: "obsolete_note",  # 废止/修订说明
    13: "has_conflict",   # 前置制度是否冲突
    14: "replaces",       # 替代的制度名称
    15: "keywords",       # 关键词
    16: "summary",        # 摘要
    17: "attachments",    # 附件
    18: "security_check", # 安全性审核
    19: "submitter"       # 提交人
}

def load_policies(excel_path):
    """加载Excel中的制度数据"""
    df = pd.read_excel(excel_path, sheet_name=0, header=None)
    
    # 数据从第3行开始（索引2），第2行是表头
    data = df.iloc[2:].reset_index(drop=True)
    
    policies = []
    for i in range(len(data)):
        row = data.iloc[i]
        policy = {}
        for col_idx, field_name in COLUMN_MAP.items():
            val = row.iloc[col_idx]
            # 处理NaN值
            if pd.isna(val):
                policy[field_name] = None
            else:
                policy[field_name] = str(val)
        policies.append(policy)
    
    return policies

def load_encoding_rules(excel_path):
    """加载编码规则"""
    df = pd.read_excel(excel_path, sheet_name=1, header=None)
    
    # 跳过标题行，从第2行开始
    data = df.iloc[1:].reset_index(drop=True)
    
    rules = []
    current_category = None
    
    for i in range(len(data)):
        row = data.iloc[i]
        
        # 列0: 类别, 列1: 前缀, 列2: 模块名称, 列3: 模块代码
        category = row.iloc[0] if pd.notna(row.iloc[0]) else None
        prefix = row.iloc[1] if pd.notna(row.iloc[1]) else None
        module_name = row.iloc[2] if pd.notna(row.iloc[2]) else None
        module_code = row.iloc[3] if pd.notna(row.iloc[3]) else None
        
        # 更新当前类别
        if category:
            current_category = str(category)
        
        if module_name and module_code:
            rules.append({
                "category": current_category,
                "prefix": str(prefix) if prefix else None,
                "module_name": str(module_name),
                "module_code": str(int(module_code)) if isinstance(module_code, (int, float)) else str(module_code)
            })
    
    return rules

def main():
    parser = argparse.ArgumentParser(description="加载Excel制度数据，输出JSON")
    parser.add_argument("--excel", required=True, help="Excel文件路径")
    parser.add_argument("--output", required=True, help="输出JSON文件路径")
    args = parser.parse_args()
    
    if not os.path.exists(args.excel):
        print(f"错误：Excel文件不存在: {args.excel}")
        sys.exit(1)
    
    print(f"正在加载Excel文件: {args.excel}")
    
    # 加载制度数据
    policies = load_policies(args.excel)
    print(f"已加载 {len(policies)} 条制度")
    
    # 加载编码规则
    encoding_rules = load_encoding_rules(args.excel)
    print(f"已加载 {len(encoding_rules)} 条编码规则")
    
    # 统计字段填充率
    print("\n=== 字段填充率 ===")
    for field in ["scope", "keywords", "summary", "category", "department"]:
        filled = sum(1 for p in policies if p.get(field))
        print(f"{field}: {filled}/{len(policies)} ({filled/len(policies)*100:.0f}%)")
    
    # 输出JSON
    output = {
        "total": len(policies),
        "policies": policies,
        "encoding_rules": encoding_rules
    }
    
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n已输出JSON到: {args.output}")

if __name__ == "__main__":
    main()
