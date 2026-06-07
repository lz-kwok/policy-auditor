# 📋 企业制度与流程审计工具 (policy-auditor)

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)

`policy-auditor` 是一款用于对企业起草或修订的**管理制度、业务流程、管理办法、操作规程、问责条例、奖惩机制**等文本进行体系化审计的 Skill 与工具集。通过融合 7 大核心能力、10 大审核维度、风险评分模型、成熟度模型、制度关系图谱、数字化落地检查器及核心内控矩阵，帮助企业有效识别管理漏洞，并输出强执行力的整改与数字化落地方案。

---

## 🚀 功能特性

- **7 大核心能力**：法律合规检查、内部制度一致性检查、完整性检查、可执行性检查、风险提示、数字化落地建议、自动生成修订建议。
- **10 大审计维度**：合法性、合规性、完整性、一致性、可执行性、风险性、权责清晰、审批合理、数据合规、AI合规。
- **内控红线扫描**：强制扫描职责分离 (SoD)、授权矩阵 (LOA)、审批权限、资金控制、印章管理、合同管理、库存管理等七大内控红线。
- **数字化落地检查**：针对 SAP/OA/多维表等系统，提供硬校验、表单刚性锁定、自动流控路由、多维数据看板等具体系统配置建议。
- **风险量化与成熟度评估**：基于 P0-P3 的风险量化分级与 COBIT/CMMI 的 L1-L5 制度成熟度定位。
- **批量汇总与可视化**：支持将多个制度审计的 JSON 结果一键聚合，自动生成 Markdown 格式的**风险地图**以及直观的**风险热力图**。

---

## 🛠️ 技术栈

- **Skill 核心逻辑**：Markdown (由 `SKILL.md` 承载，符合 Agent 提示词规范)
- **批量脚本**：Python 3
- **可视化库**：Matplotlib (用于生成风险热力图)

---

## ⚙️ 快速开始

### 环境要求

- Python 3.8 或更高版本
- 操作系统：Windows / macOS / Linux

### 安装依赖

脚本的可视化组件依赖 `matplotlib`。在终端中运行以下命令安装所需依赖：

```bash
pip install matplotlib
```

---

## 📖 使用方法

### 1. 单个制度审计 (作为 Agent Skill)

当你在支持 AI Agent 工作的环境中使用本 Skill 时，Agent 会自动加载 [SKILL.md](file:///c:/Users/GXY/.trae-cn/skills/policy-auditor/SKILL.md) 规则：
1. **启动审计**：向 Agent 投递待审计的制度草案文本。
2. **审计过程**：Agent 将自动进行结构拆解、依赖图谱建模（使用 Mermaid）、内控扫描及风险量化。
3. **输出报告**：Agent 会输出符合 [SKILL.md](file:///c:/Users/GXY/.trae-cn/skills/policy-auditor/SKILL.md) 中规定模板的《审计与合规评估报告》，包括条款修改对比（`diff` 格式）及数字化落地建议。

### 2. 批量审计结果汇总与可视化 (Python 脚本)

当你在对大量制度文件进行批量化自动审计，并输出了各文件的审计结果 JSON（格式见下方）时，可以使用 `batch_audit.py` 对结果进行可视化汇总。

#### 运行脚本

```bash
python scripts/batch_audit.py --input-dir <存放JSON结果的目录> --out-dir <报告输出目录>
```

#### JSON 输入格式示例

输入文件夹中的每个 JSON 文件（代表一个文件的审计得分）格式应包含 `filename` 和 `risks` 对象，例如 `audit_report_1.json`：

```json
{
  "filename": "采购与招标管理制度.docx",
  "risks": {
    "合法性": 1,
    "合规性": 2,
    "完整性": 0,
    "一致性": 1,
    "可执行性": 3,
    "风险性": 2,
    "权责清晰": 3,
    "审批合理": 2,
    "数据合规": 0,
    "AI合规": 0
  }
}
```
*注：风险评分为 0 至 3 之间的整数，数值越大表示该维度下的缺陷/漏洞风险越高（3 代表 P0 违法违规/极高风险）。*

#### 产出物

运行脚本后，将在 `--out-dir` 指定的目录中生成：
1. **`risk_map.md`**：Markdown 格式的风险地图，以表格形式汇总各制度文件在 10 大维度上的具体得分，并带有 🔴 🟠 🟡 🟢 状态指示灯。
2. **`risk_heatmap.png`**：PNG 图片格式的风险热力图，清晰直观地对比不同文件、不同维度下的内控风险分布。

---

## 📂 项目结构

```
policy-auditor/
├── SKILL.md                 # Skill 核心能力定义、审计指南与输出报告模板
├── README.md                # 本说明文档
└── scripts/
    └── batch_audit.py       # 批量审计 JSON 数据聚合与可视化脚本
```

---

## 📝 贡献指南

1. **修改审计规则**：如果您需要更新内控检查点或报告模板，请直接修改 [SKILL.md](file:///c:/Users/GXY/.trae-cn/skills/policy-auditor/SKILL.md)。
2. **优化数据可视化**：若需要调整热力图颜色、字体或支持新的导出格式，请编辑 [scripts/batch_audit.py](file:///c:/Users/GXY/.trae-cn/skills/policy-auditor/scripts/batch_audit.py)。

---

## 👤 作者

- **Author**：郭良志
- **License**：MIT License
