#!/usr/bin/env python3
"""
从Hacker News获取AI相关新闻
"""

import requests
import time
from datetime import datetime


# AI相关关键词
AI_KEYWORDS = [
    'ai', 'artificial intelligence', 'machine learning', 'ml',
    'deep learning', 'neural network', 'gpt', 'llm', 'chatgpt',
    'openai', 'anthropic', 'claude', 'gemini', 'transformer',
    'nlp', 'computer vision', 'diffusion', 'stable diffusion',
    'midjourney', 'autonomous', 'robot', 'robotics',
    'pytorch', 'tensorflow', 'hugging face', 'langchain',
    'generative', 'generative ai', 'foundation model',
    'large language model', 'reinforcement learning',
    'data science', 'analytics', 'model', 'training'
]


def is_ai_related(title, url=""):
    """判断文章是否与AI相关"""
    text = (title + " " + url).lower()
    return any(keyword in text for keyword in AI_KEYWORDS)


def get_hacker_news_stories(story_type="top", limit=100):
    """
    获取Hacker News故事列表

    Args:
        story_type: 故事类型 (top, new, best, ask, show)
        limit: 获取数量

    Returns:
        list: 故事ID列表
    """
    url = f"https://hacker-news.firebaseio.com/v0/{story_type}stories.json"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        story_ids = response.json()
        return story_ids[:limit]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {story_type} stories: {e}")
        return []


def get_story_details(story_id):
    """获取单个故事的详细信息"""
    url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching story {story_id}: {e}")
        return None


def get_ai_news(limit=15):
    """
    获取AI相关新闻

    Args:
        limit: 返回的新闻数量

    Returns:
        list: AI新闻列表
    """
    print("Fetching top stories from Hacker News...")

    # 获取热门故事（包含最近的和高分的）
    story_ids = get_hacker_news_stories("top", 200)

    # 也获取一些新故事
    new_story_ids = get_hacker_news_stories("new", 100)

    # 合并去重
    all_ids = list(dict.fromkeys(story_ids + new_story_ids))

    ai_news = []
    processed = 0

    print(f"Checking {len(all_ids)} stories for AI content...")

    for story_id in all_ids:
        if len(ai_news) >= limit:
            break

        story = get_story_details(story_id)
        processed += 1

        if processed % 50 == 0:
            print(f"Processed {processed} stories, found {len(ai_news)} AI news...")

        if not story or story.get("type") != "story":
            continue

        title = story.get("title", "")
        url = story.get("url", "")

        # 跳过没有链接的故事（如Ask HN）
        if not url:
            continue

        # 检查是否与AI相关
        if is_ai_related(title, url):
            news_item = {
                "title": title,
                "url": url,
                "score": story.get("score", 0),
                "comments": story.get("descendants", 0),
                "author": story.get("by", ""),
                "time": story.get("time", 0),
                "hn_url": f"https://news.ycombinator.com/item?id={story_id}"
            }
            ai_news.append(news_item)

        # 小延迟避免请求过快
        time.sleep(0.1)

    print(f"Found {len(ai_news)} AI news items")

    # 按分数排序
    ai_news.sort(key=lambda x: x.get("score", 0), reverse=True)

    return ai_news[:limit]


def format_time_ago(timestamp):
    """将时间戳转换为"X小时前"的格式"""
    if not timestamp:
        return ""

    now = time.time()
    diff = now - timestamp

    if diff < 3600:
        return f"{int(diff / 60)}分钟前"
    elif diff < 86400:
        return f"{int(diff / 3600)}小时前"
    else:
        return f"{int(diff / 86400)}天前"


if __name__ == "__main__":
    # 测试使用
    news = get_ai_news(limit=10)
    print(f"\nTop {len(news)} AI News:")
    for i, item in enumerate(news, 1):
        print(f"{i}. {item['title']}")
        print(f"   Score: {item['score']} | Comments: {item['comments']}")
        print(f"   URL: {item['url'][:60]}...")
        print()
