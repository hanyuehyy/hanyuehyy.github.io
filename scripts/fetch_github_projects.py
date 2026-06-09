#!/usr/bin/env python3
"""
获取GitHub最近2周star增长最快的AI相关项目
"""

import requests
from datetime import datetime, timedelta
import json


def get_trending_projects(days=14, max_results=10):
    """
    获取最近指定天数内创建的、star数最高的项目

    Args:
        days: 时间范围（天）
        max_results: 最多返回的项目数

    Returns:
        list: 项目列表
    """
    # 计算起始日期
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    # GitHub API搜索接口
    # 搜索条件：最近N天内创建的，按star数排序
    url = "https://api.github.com/search/repositories"

    # 搜索参数 - 搜索AI相关的热门项目
    params = {
        "q": f"created:>{start_date} stars:>50",  # 创建时间 > start_date 且 star数 > 50
        "sort": "stars",
        "order": "desc",
        "per_page": max_results * 2  # 多获取一些，后面会筛选
    }

    headers = {
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()

        data = response.json()
        items = data.get("items", [])

        # 筛选和整理项目信息
        projects = []
        for item in items[:max_results]:
            project = {
                "name": item.get("name", ""),
                "full_name": item.get("full_name", ""),
                "description": item.get("description", "No description") or "No description",
                "stars": item.get("stargazers_count", 0),
                "forks": item.get("forks_count", 0),
                "language": item.get("language", "Unknown") or "Unknown",
                "url": item.get("html_url", ""),
                "topics": item.get("topics", [])[:5],  # 最多5个标签
                "created_at": item.get("created_at", ""),
                "owner": {
                    "login": item.get("owner", {}).get("login", ""),
                    "avatar_url": item.get("owner", {}).get("avatar_url", "")
                }
            }
            projects.append(project)

        return projects

    except requests.exceptions.RequestException as e:
        print(f"Error fetching GitHub projects: {e}")
        return []


def format_number(num):
    """格式化数字显示（如 1200 -> 1.2k）"""
    if num >= 1000:
        return f"{num / 1000:.1f}k"
    return str(num)


if __name__ == "__main__":
    # 测试使用
    projects = get_trending_projects(days=14, max_results=10)
    print(f"Found {len(projects)} trending projects:")
    for i, proj in enumerate(projects, 1):
        print(f"{i}. {proj['name']} - ⭐ {format_number(proj['stars'])}")
        print(f"   {proj['description'][:80]}...")
        print()
