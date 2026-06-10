# FinSight — 金融研报多Agent分析系统

> 面向AI应用开发实习岗位的完整Demo项目
> 覆盖：LLM微调 · RAG · LangGraph多Agent · FastAPI · Gradio

---

## 项目概述

**定位**：上传研报/财报PDF或输入财经问题 → 多Agent并行分析 → 输出结构化报告

**技术亮点**：
- Qwen2.5-7B + LoRA 微调（CFGPT 54万条金融数据）
- LangGraph 5Agent状态机编排
- 混合检索RAG（BM25 + 语义向量）
- FastAPI 异步接口 + Gradio 前端

---

## 技术选型

| 模块 | 技术 |
|------|------|
| 基座模型 | Qwen2.5-7B |
| 微调方法 | LoRA (r=16, alpha=32) |
| 微调框架 | LLaMA-Factory |
| 训练数据 | CFGPT 54万条（AutoDL A100） |
| Agent框架 | LangGraph |
| 向量库 | ChromaDB |
| Embedding | BGE-base-zh |
| 后端 | FastAPI |
| 前端 | Gradio |

---

## 整体架构

```
用户输入（PDF 或 文本问题）
         ↓
    FastAPI 接口层
         ↓
   Router Agent（意图分类）
    ↙              ↘
文档分析流              问答流
    ↓                   ↓
4个并行Agent         RAG检索（ChromaDB）
  ├─ 事件检测Agent         ↓
  ├─ 情感分析Agent     Answer Agent
  ├─ 摘要生成Agent
  └─ 主题分解Agent
         ↓
   Synthesis Agent（汇总）
         ↓
    Gradio 前端展示
```

---

## 代码结构

```
finsight/
├── data/
│   ├── download_cfgpt.py       # 下载CFGPT数据
│   ├── preprocess.py           # 统一转为Alpaca格式
│   └── sample_540k.py          # 按比例采样54万
├── training/
│   ├── train_config.yaml       # LLaMA-Factory配置
│   ├── train.sh                # 一键启动训练
│   └── evaluate.py             # ROUGE + 人工评估
├── rag/
│   ├── indexer.py              # PDF解析+向量化
│   ├── retriever.py            # BM25+语义混合检索
│   └── knowledge_base/         # 存放研报PDF
├── agents/
│   ├── router.py               # 意图路由
│   ├── event_agent.py          # 事件检测
│   ├── sentiment_agent.py      # 情感分析
│   ├── summary_agent.py        # 摘要生成
│   ├── topic_agent.py          # 主题分解
│   └── qa_agent.py             # RAG问答
├── graph/
│   └── workflow.py             # LangGraph状态机编排
├── api/
│   └── main.py                 # FastAPI接口
├── frontend/
│   └── app.py                  # Gradio界面
└── notebooks/
    ├── 01_data_exploration.ipynb
    ├── 02_colab_training.ipynb
    └── 03_evaluation.ipynb
```

---

## 开发计划

### Week 1 — 数据处理 + 训练启动
> 目标：把训练任务挂上AutoDL，边跑边开发其他模块

- [ ] **1.1** 申请AutoDL账号，租A100 40GB实例
- [ ] **1.2** 下载CFGPT数据集（HuggingFace / GitHub）
- [ ] **1.3** 数据探索：查看各任务类型样本格式和分布
- [ ] **1.4** 编写预处理脚本：统一转为Alpaca三字段格式（instruction/input/output）
- [ ] **1.5** 按比例采样54万条：事件150k / 摘要150k / 主题100k / 情感100k / 股价40k
- [ ] **1.6** 安装LLaMA-Factory，配置train_config.yaml
- [ ] **1.7** 启动训练任务（挂机，预计36-48小时）
- [ ] **1.8** 提交data/目录代码到GitHub

### Week 2 — RAG模块 + 单Agent实现
> 目标：RAG链路跑通，各Agent可独立测试

- [ ] **2.1** 实现 `rag/indexer.py`：PDF解析 → 分块 → BGE向量化 → ChromaDB存储
- [ ] **2.2** 实现 `rag/retriever.py`：BM25 + 语义混合检索
- [ ] **2.3** 收集10-20份公开研报PDF放入knowledge_base/
- [ ] **2.4** 实现 `agents/router.py`：意图分类（文档分析 vs 问答）
- [ ] **2.5** 实现 `agents/event_agent.py`：事件检测
- [ ] **2.6** 实现 `agents/sentiment_agent.py`：情感分析
- [ ] **2.7** 实现 `agents/summary_agent.py`：摘要生成
- [ ] **2.8** 实现 `agents/topic_agent.py`：主题分解
- [ ] **2.9** 实现 `agents/qa_agent.py`：RAG问答
- [ ] **2.10** 各Agent单元测试

### Week 3 — LangGraph编排 + FastAPI接口
> 目标：完整流程端到端跑通

- [ ] **3.1** 设计LangGraph State结构（输入/中间结果/最终输出）
- [ ] **3.2** 实现 `graph/workflow.py`：状态机编排，4Agent并行
- [ ] **3.3** 集成微调后的模型权重（训练完成后）
- [ ] **3.4** 实现 `api/main.py`：
  - `POST /analyze`（上传PDF分析）
  - `POST /chat`（多轮问答）
  - `POST /upload`（上传研报到知识库）
- [ ] **3.5** 接口异步处理 + 流式输出
- [ ] **3.6** 端到端集成测试

### Week 4 — 前端 + 评估 + 收尾
> 目标：可展示的完整Demo，GitHub可直接运行

- [ ] **4.1** 实现 `frontend/app.py`（Gradio界面）
- [ ] **4.2** 实现 `training/evaluate.py`：ROUGE评估 + 对比基座模型
- [ ] **4.3** 整理 `notebooks/03_evaluation.ipynb`：可视化评估结果
- [ ] **4.4** 编写 GitHub README（含架构图、快速启动、Demo截图）
- [ ] **4.5** 部署到 Hugging Face Spaces（免费）
- [ ] **4.6** 整理简历项目描述（突出LangGraph/RAG/微调关键词）

---

## 训练配置参考

```yaml
# train_config.yaml
model_name_or_path: Qwen/Qwen2.5-7B-Instruct
method: lora
lora_rank: 16
lora_alpha: 32
lora_target: q_proj,v_proj,k_proj,o_proj
dataset: cfgpt_540k
num_train_epochs: 3
per_device_train_batch_size: 4
gradient_accumulation_steps: 4
learning_rate: 5e-5
output_dir: ./output/fin-qwen25-7b-lora
```

---

## 数据采样策略

| 任务类型 | CFGPT原始量 | 采样量 | 采样比例 |
|---------|------------|--------|---------|
| 事件检测 | 490k | 150k | 31% |
| 研报摘要 | 369k | 150k | 28% |
| 主题分解 | 369k | 100k | 19% |
| 情感分析 | 120k | 100k | 19% |
| 股价预测 | 212k | 40k | 7% |
| **合计** | **1,560k** | **540k** | — |

---

## 面试考点对照

| JD考点 | 项目体现 | 能讲的技术细节 |
|--------|---------|--------------|
| LangGraph多Agent | 5Agent + 状态机编排 | State设计、并行节点、条件路由 |
| RAG全链路 | 混合检索 | BM25+语义融合、分块策略、召回优化 |
| LLM微调 | LoRA + 54万金融数据 | 参数选择、训练曲线、ROUGE评估 |
| FastAPI | 3个异步接口 | 流式输出、异步处理 |
| Memory | LangGraph State持久化 | 多轮对话历史管理 |
| LangChain Chain | Agent内部Chain编排 | 工具调用、提示词模板 |

---

## 进度日志

### 2026-06-10
- [x] 完成需求调研（医疗/法律/金融方向对比）
- [x] 确定技术选型（Qwen2.5-7B + CFGPT + LangGraph）
- [x] 完成项目架构设计
- [ ] 下一步：开始Week 1数据处理

---

## 参考资源

- CFGPT数据集：https://github.com/TongjiFinLab/CFGPT
- LLaMA-Factory：https://github.com/hiyouga/LLaMA-Factory
- Qwen2.5：https://huggingface.co/Qwen/Qwen2.5-7B-Instruct
- BGE Embedding：https://huggingface.co/BAAI/bge-base-zh-v1.5
- LangGraph文档：https://langchain-ai.github.io/langgraph/
