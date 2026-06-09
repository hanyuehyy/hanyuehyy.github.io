#!/usr/bin/env python3
"""
主脚本：整合所有数据并生成data.json
"""

import json
import os
from datetime import datetime

# 导入自定义模块
from fetch_github_projects import get_trending_projects, format_number
from fetch_ai_news import get_ai_news


def generate_summary(description, max_length=100):
    """生成简洁的中文描述"""
    if not description:
        return "暂无描述"

    # 如果描述已经是中文或足够短，直接返回
    if len(description) <= max_length:
        return description

    # 截断并添加省略号
    return description[:max_length-3] + "..."


def translate_to_chinese_summary(title):
    """
    为英文标题生成中文摘要
    这里使用简单的关键词映射，实际项目中可以接入翻译API
    """
    # 简单的关键词到中文的映射
    keyword_map = {
        "ai": "AI",
        "machine learning": "机器学习",
        "deep learning": "深度学习",
        "neural network": "神经网络",
        "gpt": "GPT",
        "llm": "大语言模型",
        "openai": "OpenAI",
        "anthropic": "Anthropic",
        "claude": "Claude",
        "transformer": "Transformer模型",
        "nlp": "自然语言处理",
        "computer vision": "计算机视觉",
        "diffusion": "扩散模型",
        "robot": "机器人",
        "autonomous": "自动驾驶",
        "pytorch": "PyTorch",
        "tensorflow": "TensorFlow",
        "data science": "数据科学",
        "model": "模型",
        "training": "训练",
        "inference": "推理",
        "benchmark": "基准测试",
        "release": "发布",
        "launch": "推出",
        "open source": "开源",
        "startup": "创业公司",
        "funding": "融资",
        "api": "API",
        "tool": "工具",
        "framework": "框架",
        "library": "库"
    }

    # 如果标题主要包含中文，直接返回
    chinese_chars = sum(1 for c in title if '一' <= c <= '鿿')
    if chinese_chars > len(title) * 0.3:
        return title

    # 尝试生成中文摘要
    title_lower = title.lower()
    summary_parts = []

    for en, cn in keyword_map.items():
        if en in title_lower:
            summary_parts.append(cn)

    if summary_parts:
        return f"【{', '.join(summary_parts[:3])}】{title}"

    return title


def main():
    """主函数"""
    print("=" * 60)
    print("Starting data update...")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    data = {
        "updated_at": datetime.now().isoformat(),
        "github_projects": [],
        "ai_news": []
    }

    # 获取GitHub热门项目
    print("\n📦 Fetching GitHub trending projects...")
    try:
        projects = get_trending_projects(days=14, max_results=10)
        data["github_projects"] = projects
        print(f"✅ Successfully fetched {len(projects)} projects")
    except Exception as e:
        print(f"❌ Error fetching projects: {e}")

    # 获取AI新闻
    print("\n📰 Fetching AI news...")
    try:
        news = get_ai_news(limit=15)
        # 为英文新闻添加中文摘要
        for item in news:
            if item.get("title"):
                item["title_cn"] = translate_to_chinese_summary(item["title"])
        data["ai_news"] = news
        print(f"✅ Successfully fetched {len(news)} news items")
    except Exception as e:
        print(f"❌ Error fetching news: {e}")

    # 保存到JSON文件
    output_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "data.json")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n💾 Data saved to: {output_file}")
    print("=" * 60)
    print("Update completed!")
    print(f"GitHub Projects: {len(data['github_projects'])}")
    print(f"AI News: {len(data['ai_news'])}")
    print("=" * 60)


if __name__ == "__main__":
    main()
