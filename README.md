# 📋 企业制度与流程审计工具 (policy-auditor)

![Version](https://img.shields.io/badge/version-1.2.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)

`policy-auditor` 是一款用于对企业起草或修订的**管理制度、业务流程、管理办法、操作规程、问责条例、奖惩机制**等文本进行体系化审计的 Skill 与工具集。

在最新版本中，工具集引入了基于 **Progressive Disclosure（渐进式披露）** 原则的动态分流机制，支持根据制度文本的内容特征，自动分类并动态加载对应的**职能领域规则集**与**行业规范知识库**进行交叉合规审计，实现了极高的审计针对性与 Token 利用效率。

---

## 🚀 功能特性

- **双维度正交审计**：
  - **职能维度**：包含人力资源合规（劳动法及个保法专项优化）、采购与招标管理、**数智化建设与运营**（涵盖ITGC审计、BI指标治理、AI/Agent分类分级、外包及SaaS控制、数字化价值管理及业务连续性灾备等）。
  - **行业维度**：支持生猪养殖与生物安全管理，涵盖《动物防疫法》、《畜牧法》等国家法律红线、三级防疫洗消、出栏休药期硬校验、活体资产周盘点、现场养殖数据多源校验等。
- **核心大脑调度 (SKILL.md)**：包含通用评估模型与分流器，根据输入文本的关键字自动分流并使用 `view_file` 工具以绝对路径加载子规则。
- **数智化成熟度评估模型**：融合了涵盖 IT/安全、数据/资产、AI/Agent、BI/价值实现、SAP核心系统、IoT现场等六大维度的五级成熟度（L1 - L5）评估指标与 24 个月演进路线规划。
- **风险量化与成熟度评估**：基于 P0-P3 的风险量化分级模型，以及基于 COBIT/CMMI 的 L1-L5 制度成熟度评估。
- **批量汇总与可视化**：支持将多个制度审计的 JSON 结果一键聚合，自动生成 Markdown 格式的**风险地图**以及直观的**风险热力图**。

---

## 📂 项目结构

```text
policy-auditor/
├── SKILL.md                         # 🧠 核心大脑：定义通用内控逻辑、评估模型、动态加载调度器及审计报告模板
├── README.md                        # 本说明文档
├── scripts/                         # 自动工具脚本
│   └── batch_audit.py               # 批量审计 JSON 数据聚合与可视化脚本
└── references/                      # 📚 动态加载的子规则库 (核心扩展点)
    ├── rulesets/                    # 维度一：按职能领域分类的规则集 (Rulesets)
    │   ├── hr.md                    # 人力资源合规（中国劳动法专项优化）
    │   ├── procurement.md           # 采购与招标：招投标额度门槛、职责分离、单一来源审查
    │   └── digitalization.md        # 数智化与IT治理：ITGC内控、指标治理、AI与Agent分级、SaaS/外包控制、数字化价值审计、灾备与业务连续性
    └── industries/                  # 维度二：按行业场景分类的知识库 (Industries)
        └── swine_farming.md         # 生猪养殖：动物防疫法、三级洗消屏障、病死猪处理、休药期、RFID盘点、数据四方交叉核对
```

---

## ⚙️ 动态加载与路由机制

当您在 AI Agent 环境中激活本 Skill 并上传待审计制度时，Agent 会自动通读文本并按如下规则路由：

### 1. 职能路由规则
* **采购与招投标** (包含关键字：“采购、招标、招投标、供应商、询比价、定标”等)：
  - **动态加载**：`[procurement.md](references/rulesets/procurement.md)`
* **人力资源** (包含关键字：“考勤、绩效、薪酬、加班、录用、离职、劳动合同”等)：
  - **动态加载**：`[hr.md](references/rulesets/hr.md)`
* **数智化建设与运营** (包含关键字：“数智化、信息化、数字化、智能化、产品开发、系统运维、变更发布、主数据、IoT、物联网、AI、大模型、软件正版化”等)：
  - **动态加载**：`[digitalization.md](references/rulesets/digitalization.md)`

### 2. 行业路由规则
* **生猪养殖与生物安全** (包含关键字：“生猪、猪场、猪只、母猪、育肥、饲料、兽药、洗消、疫病、无害化”等)：
  - **动态加载**：`[swine_farming.md](references/industries/swine_farming.md)`

---

## 📄 审计报告产出格式

审计完成后，Agent 会生成符合模板要求的审计报告，并在前言中明示本次审计所加载的规则包，例如：
```markdown
# 📌 牧原养殖·猪场现场物资采购管理办法 审计与合规评估报告

**评估人**：Claude (使用 policy-auditor 技能)  
**评估日期**：2026年06月10日  
**加载规则库**：
- 核心底座：policy-auditor/SKILL.md
- 职能规则集：rulesets/procurement.md
- 行业知识库：industries/swine_farming.md
**评估结论**：需局部修改后发布
```

---

## 📖 批量结果可视化脚本使用

在对大批量的制度文件进行自动分析并获得了各个制度的得分 JSON 结果后，可以使用 `batch_audit.py` 生成可视化的地图。

### 环境要求与依赖安装
```bash
pip install matplotlib
```

### 运行脚本
```bash
python scripts/batch_audit.py --input-dir <存放JSON结果的目录> --out-dir <报告输出目录>
```
运行后会在输出目录下生成：
1. **`risk_map.md`**：Markdown 表格格式的风险地图，直观展示每个制度在合法性、合规性、审批合理性等 10 个维度下的得分（🔴 🟠 🟡 🟢 标示）。
2. **`risk_heatmap.png`**：直观的风险热力图，对比各制度的内控漏洞分布。

---

## 👤 作者与许可证

- **Author**：郭良志
- **License**：MIT License
