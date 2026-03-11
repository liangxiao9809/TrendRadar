#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试投资分析功能
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from custom_scripts.custom_investment_analyzer import InvestmentAnalyzer

# 测试数据
test_news = [
    {
        "title": "人工智能大会召开，多家公司发布大模型新品",
        "content": "2024世界人工智能大会在上海开幕，多家科技公司发布最新大模型产品",
        "platform": "财联社",
        "time": "2024-07-10 09:30:00"
    },
    {
        "title": "半导体产业迎政策利好，国产芯片加速替代",
        "content": "国家发布半导体产业扶持政策，推动国产芯片研发和应用",
        "platform": "华尔街见闻",
        "time": "2024-07-10 10:15:00"
    },
    {
        "title": "新能源车销量创新高，锂电池需求持续增长",
        "content": "6月新能源车销量同比增长40%，动力电池需求旺盛",
        "platform": "东方财富",
        "time": "2024-07-10 11:00:00"
    }
]


def test_analysis():
    """测试分析功能"""
    print("开始测试投资分析功能...")

    analyzer = InvestmentAnalyzer()
    result = analyzer.analyze_news(test_news)

    print("\n" + "=" * 50)
    print("分析结果：")
    print("=" * 50)
    print(f"识别到的行业: {result['industries']}")
    print(f"分析时间: {result['analysis_time']}")
    print(f"新闻数量: {result['news_count']}")

    print("\n投资建议摘要：")
    advice = result['investment_advice']
    print(f"热点主题: {advice['热点主题']}")
    print(f"市场情绪: {advice['影响分析']['市场情绪']}")

    print("\n推荐的股票：")
    for stock in advice['股票推荐'][:3]:
        print(f"  {stock['code']} {stock['name']} - {stock['reason']}")

    print("\n推荐的ETF：")
    for etf in advice['ETF推荐'][:2]:
        print(f"  {etf['code']} {etf['name']} - {etf['index']}")

    print("\n风险提示：")
    print(advice['风险提示'])

    # 生成钉钉消息
    dingtalk_msg = analyzer.format_for_dingtalk(result)
    print("\n" + "=" * 50)
    print("钉钉消息预览（前200字符）：")
    print("=" * 50)
    print(dingtalk_msg[:200] + "...")

    # 保存测试结果
    import json
    with open("test_output.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("\n✓ 测试完成！结果已保存到 test_output.json")


if __name__ == "__main__":
    test_analysis()
