# -*- coding: utf-8 -*-
"""
FinSight 数据预处理：清洗 + 统一Alpaca格式

输入: data/raw/ 下载的原始数据（先跑 download_datasets.py）
输出: data/processed/finsight_train.jsonl / finsight_eval.jsonl
      统一字段: instruction / input / output / task / agent

清洗规则（对应数据探索发现的噪声）:
1. 网页杂质: 广告语（【立即开户，领取福利】）、"原标题："、乱码问号串、多余空白
2. 情感标签归一: FINFE输出表述不统一（"中性。"/"所属情感是中性。"）→ 统一为"积极/消极/中性"
3. BAAI数据: 只保留中文、deita质量分>=7、取首轮对话转Alpaca格式
4. 通用过滤: 输出为空、总长超4000字符的样本剔除；按(instruction+input)去重
"""
import hashlib
import json
import os
import re
from collections import Counter

RAW = os.path.join(os.path.dirname(__file__), "raw")
OUT = os.path.join(os.path.dirname(__file__), "processed")
os.makedirs(OUT, exist_ok=True)

# FinCUGE任务 → FinSight Agent 的映射
TASK2AGENT = {
    "FINQA": "event",     # 事件抽取
    "FINCQA": "event",    # 因果事件抽取
    "FINESE": "event",    # 事件主体抽取
    "FINFE": "sentiment", # 论坛情绪
    "FINNSP": "sentiment",# 负面消息及主体
    "FINNA": "summary",   # 新闻摘要
    "FINNL": "topic",     # 新闻分类
    "FINRE": "topic",     # 关系抽取
}

# 含这些关键词的整句删除（券商广告变体太多，按关键词整句清除比枚举文案可靠）
AD_KEYWORDS = ["立即开户", "你还在等什么", "领取福利", "极速响应", "点击查看",
               "股市震荡，需要注意什么", "跨年行情，应该如何布局"]
# 句子 = 到上一个句末标点/换行 为止、到下一个句末标点/换行 为止
AD_SENT_RE = re.compile(
    r"[^。！？!?\n]*(?:" + "|".join(map(re.escape, AD_KEYWORDS)) + r")[^。！？!?\n]*[。！？!?]?"
)
AD_RE = re.compile(r"原标题[：:]\s*|\?{3,}|？{3,}")
WS_RE = re.compile(r"[ \t　]+")

SENT_LABELS = ["积极", "消极", "中性"]


def clean_text(t):
    t = AD_SENT_RE.sub("", t)
    t = AD_RE.sub("", t)
    t = WS_RE.sub(" ", t)
    return t.strip()


def normalize_sentiment(out):
    """'所属情感是中性。' / '以上文本情感极性属于消极。' → '中性' / '消极'"""
    hits = [lb for lb in SENT_LABELS if lb in out]
    return hits[0] if len(hits) == 1 else None  # 多标签/无标签视为噪声


def iter_fincuge(path):
    with open(path, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            task = r["task"]
            ins = clean_text(r["instruction"])
            inp = clean_text(r.get("input", ""))
            out = clean_text(r["output"])
            if task == "FINFE":
                label = normalize_sentiment(out)
                if label is None:
                    continue
                out = label
            yield {"instruction": ins, "input": inp, "output": out,
                   "task": task, "agent": TASK2AGENT[task]}


def iter_baai(path, min_score=7.0):
    with open(path, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if r.get("lang") != "zh" or r.get("deita_score", 0) < min_score:
                continue
            conv = r.get("conversations", [])
            if len(conv) < 2 or conv[0]["from"] != "human":
                continue
            ins = clean_text(conv[0]["value"])
            out = clean_text(conv[1]["value"])
            yield {"instruction": ins, "input": "", "output": out,
                   "task": "BAAI_QA", "agent": "qa"}


def dedup_and_filter(rows):
    seen, kept = set(), []
    stats = Counter()
    for r in rows:
        if not r["output"] or not r["instruction"]:
            stats["空字段剔除"] += 1
            continue
        if len(r["instruction"]) + len(r["input"]) + len(r["output"]) > 4000:
            stats["超长剔除"] += 1
            continue
        key = hashlib.md5((r["instruction"] + r["input"]).encode()).hexdigest()
        if key in seen:
            stats["重复剔除"] += 1
            continue
        seen.add(key)
        kept.append(r)
    return kept, stats


def save(rows, name):
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"  {name}: {len(rows):,} 条")
    print(f"  agent分布: {dict(Counter(r['agent'] for r in rows))}")


if __name__ == "__main__":
    print("[1/2] 处理训练集 ...")
    train = list(iter_fincuge(os.path.join(RAW, "fincuge_train.jsonl")))
    n_fincuge = len(train)
    train += list(iter_baai(os.path.join(RAW, "baai_finance_all.jsonl")))
    print(f"  原始: FinCUGE {n_fincuge:,} + BAAI筛后 {len(train)-n_fincuge:,}")
    train, stats = dedup_and_filter(train)
    print(f"  清洗统计: {dict(stats)}")
    save(train, "finsight_train.jsonl")

    print("[2/2] 处理评估集 ...")
    ev = list(iter_fincuge(os.path.join(RAW, "fincuge_eval.jsonl")))
    ev, stats = dedup_and_filter(ev)
    print(f"  清洗统计: {dict(stats)}")
    save(ev, "finsight_eval.jsonl")
