#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TrendRadar自定义分析工作流
将投资分析集成到推送流程中
"""

import os
import sys
import json
import subprocess
from pathlib import Path


def run_investment_analysis():
    """运行投资分析并生成报告"""

    # 检查数据文件
    data_file = Path("output/latest_news.json")
    if not data_file.exists():
        print("未找到新闻数据文件，跳过投资分析")
        return None

    # 导入自定义分析器
    sys.path.append(str(Path.cwd()))
    from custom_investment_analyzer import InvestmentAnalyzer

    # 读取新闻数据
    with open(data_file, 'r', encoding='utf-8') as f:
        news_data = json.load(f)

    # 运行分析
    analyzer = InvestmentAnalyzer()
    result = analyzer.analyze_news(news_data)

    # 保存分析结果
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    # 保存JSON格式
    with open(output_dir / "investment_analysis.json", 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # 生成钉钉消息
    dingtalk_message = analyzer.format_for_dingtalk(result)
    with open(output_dir / "dingtalk_investment.md", 'w', encoding='utf-8') as f:
        f.write(dingtalk_message)

    # 生成HTML报告
    html_report = generate_html_report(result)
    with open(output_dir / "investment_report.html", 'w', encoding='utf-8') as f:
        f.write(html_report)

    return dingtalk_message


def generate_html_report(analysis_result):
    """生成HTML格式的报告"""

    advice = analysis_result["investment_advice"]

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>投资热点分析报告 - {analysis_result['analysis_time']}</title>
    <style>
        body {{ font-family: 'Microsoft YaHei', sans-serif; margin: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }}
        .section {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }}
        .stock-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        .stock-table th, .stock-table td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        .stock-table th {{ background-color: #f5f5f5; }}
        .positive {{ color: #52c41a; }}
        .negative {{ color: #f5222d; }}
        .neutral {{ color: #faad14; }}
        .tag {{ display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; margin: 2px; }}
        .tag-tech {{ background: #e6f7ff; color: #1890ff; }}
        .tag-consumer {{ background: #f6ffed; color: #52c41a; }}
        .tag-finance {{ background: #fff7e6; color: #fa8c16; }}
        .tag-medical {{ background: #f9f0ff; color: #722ed1; }}
        .risk-warning {{ background: #fff2e8; border-left: 4px solid #fa8c16; padding: 15px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📈 投资热点分析报告</h1>
            <p>分析时间: {analysis_result['analysis_time']} | 监测新闻数: {analysis_result['news_count']}条</p>
        </div>

        <div class="section">
            <h2>🎯 热点主题</h2>
            <p>{advice['热点主题']}</p>
        </div>

        <div class="section">
            <h2>📊 影响分析</h2>
            <p><strong>行业影响:</strong> {advice['影响分析']['行业影响']}</p>
            <p><strong>市场情绪:</strong> <span class="{advice['影响分析']['市场情绪']}">{advice['影响分析']['市场情绪']}</span></p>
            <p><strong>持续时间:</strong> {advice['影响分析']['持续时间']}</p>
            <p><strong>建议关注度:</strong> {advice['影响分析']['建议关注度']}</p>
        </div>

        <div class="section">
            <h2>💰 推荐关注股票</h2>
            <table class="stock-table">
                <thead>
                    <tr>
                        <th>市场</th>
                        <th>代码</th>
                        <th>名称</th>
                        <th>行业</th>
                        <th>投资逻辑</th>
                    </tr>
                </thead>
                <tbody>"""

    for stock in advice['股票推荐'][:8]:
        html += f"""
                    <tr>
                        <td>A股</td>
                        <td>{stock['code']}</td>
                        <td><strong>{stock['name']}</strong></td>
                        <td><span class="tag tag-{stock['industry']}">{stock['industry']}</span></td>
                        <td>{stock['reason']}</td>
                    </tr>"""

    html += """
                </tbody>
            </table>
        </div>

        <div class="section">
            <h2>📊 推荐关注ETF</h2>
            <table class="stock-table">
                <thead>
                    <tr>
                        <th>代码</th>
                        <th>名称</th>
                        <th>跟踪指数</th>
                        <th>行业</th>
                    </tr>
                </thead>
                <tbody>"""

    for etf in advice['ETF推荐'][:5]:
        html += f"""
                    <tr>
                        <td>{etf['code']}</td>
                        <td><strong>{etf['name']}</strong></td>
                        <td>{etf['index']}</td>
                        <td><span class="tag tag-{etf['industry']}">{etf['industry']}</span></td>
                    </tr>"""

    html += f"""
                </tbody>
            </table>
        </div>

        <div class="risk-warning">
            <h2>⚠️ 风险提示</h2>
            <p>{advice['风险提示'].replace('• ', '<br>• ')}</p>
        </div>

        <div class="section">
            <h3>📋 免责声明</h3>
            <p>本分析基于公开热点新闻自动生成，仅供参考，不构成投资建议。投资有风险，入市需谨慎。</p>
            <p>数据来源: TrendRadar热点监控系统 | 生成时间: {analysis_result['analysis_time']}</p>
        </div>
    </div>
</body>
</html>"""

    return html


def main():
    """主函数"""
    print("开始投资热点分析...")

    # 运行投资分析
    message = run_investment_analysis()

    if message:
        print("投资分析完成！")
        print("\n" + "=" * 50)
        print("生成的钉钉消息预览：")
        print("=" * 50)
        print(message[:500] + "..." if len(message) > 500 else message)

        # 将消息发送到钉钉
        send_to_dingtalk(message)
    else:
        print("未生成投资分析报告")


def send_to_dingtalk(message):
    """发送消息到钉钉"""
    import requests
    import os

    # 从环境变量获取钉钉Webhook
    webhook_url = os.getenv("DINGTALK_WEBHOOK_URL")
    if not webhook_url:
        print("未配置钉钉Webhook URL")
        return

    # 钉钉消息格式
    payload = {
        "msgtype": "markdown",
        "markdown": {
            "title": "📈 投资热点分析报告",
            "text": message
        },
        "at": {
            "isAtAll": False  # 不@所有人
        }
    }

    try:
        response = requests.post(webhook_url, json=payload)
        if response.status_code == 200:
            print("✓ 投资分析报告已发送到钉钉")
        else:
            print(f"✗ 发送失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ 发送出错: {str(e)}")


if __name__ == "__main__":
    main()