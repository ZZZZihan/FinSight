# -*- coding: utf-8 -*-
"""
FinSight 训练数据下载脚本

数据来源（CFGPT全量数据未公开，改用以下可下载的开源数据集）：
1. Maciel/FinCUGE-Instruction  — 13.8万条，8类金融NLP任务（情感/摘要/事件/分类等）
2. BAAI/IndustryInstruction_Finance-Economics — 12.2万条对话式金融指令（含质量分）
3. eggbiscuit/DISC-FIN-SFT     — 复旦DISC-FinLLM开源部分（咨询/任务/检索/计算）

用法: python data/download_datasets.py
输出: data/raw/ 下各数据集的jsonl文件
"""
import json
import os

from datasets import load_dataset
from huggingface_hub import hf_hub_download

RAW_DIR = os.path.join(os.path.dirname(__file__), "raw")
os.makedirs(RAW_DIR, exist_ok=True)


def save_jsonl(rows, path):
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"  已保存 {len(rows):,} 条 -> {path}")


def download_fincuge():
    print("\n[1/3] 下载 FinCUGE-Instruction (138k, 8类任务) ...")
    ds = load_dataset("Maciel/FinCUGE-Instruction")
    for split, data in ds.items():
        save_jsonl(list(data), os.path.join(RAW_DIR, f"fincuge_{split}.jsonl"))
        # 统计任务分布
        tasks = {}
        for row in data:
            tasks[row["task"]] = tasks.get(row["task"], 0) + 1
        print(f"  {split} 任务分布: {tasks}")


def download_baai_finance():
    print("\n[2/3] 下载 BAAI IndustryInstruction Finance (122k) ...")
    ds = load_dataset("BAAI/IndustryInstruction_Finance-Economics", split="train")
    rows = list(ds)
    zh = [r for r in rows if r.get("lang") == "zh"]
    save_jsonl(rows, os.path.join(RAW_DIR, "baai_finance_all.jsonl"))
    print(f"  其中中文: {len(zh):,} / {len(rows):,}")


def download_disc_fin():
    print("\n[3/3] 下载 DISC-FIN-SFT (复旦, 开源部分) ...")
    for name in ["consulting_part", "task_part", "retrieval_part", "computing_part"]:
        path = hf_hub_download(
            repo_id="eggbiscuit/DISC-FIN-SFT",
            filename=f"data/{name}.json",
            repo_type="dataset",
        )
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        save_jsonl(data, os.path.join(RAW_DIR, f"disc_fin_{name}.jsonl"))


if __name__ == "__main__":
    download_fincuge()
    download_baai_finance()
    download_disc_fin()
    print("\n全部下载完成。文件在 data/raw/")
