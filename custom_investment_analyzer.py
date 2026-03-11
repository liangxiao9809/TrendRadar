#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TrendRadar自定义投资分析模块
根据热点新闻生成股票/ETF投资建议
"""

import json
import re
from typing import Dict, List, Any
import yaml


class InvestmentAnalyzer:
    """投资分析器"""

    # 行业-股票映射数据库
    INDUSTRY_STOCKS = {
        "人工智能": {
            "A股": [
                {"code": "002230", "name": "科大讯飞", "reason": "AI语音龙头"},
                {"code": "300496", "name": "中科创达", "reason": "智能汽车AI"},
                {"code": "688111", "name": "金山办公", "reason": "办公AI应用"},
            ],
            "ETF": [
                {"code": "515070", "name": "人工智能ETF", "index": "中证人工智能主题指数"},
                {"code": "512720", "name": "计算机ETF", "index": "中证计算机主题指数"},
            ]
        },
        "半导体": {
            "A股": [
                {"code": "603501", "name": "韦尔股份", "reason": "CIS芯片龙头"},
                {"code": "688981", "name": "中芯国际", "reason": "晶圆代工龙头"},
                {"code": "002049", "name": "紫光国微", "reason": "安全芯片"},
            ],
            "ETF": [
                {"code": "512480", "name": "半导体ETF", "index": "中证全指半导体指数"},
                {"code": "159995", "name": "芯片ETF", "index": "国证半导体芯片指数"},
            ]
        },
        "新能源": {
            "A股": [
                {"code": "300750", "name": "宁德时代", "reason": "动力电池龙头"},
                {"code": "002594", "name": "比亚迪", "reason": "新能源汽车全产业链"},
                {"code": "601012", "name": "隆基绿能", "reason": "光伏组件龙头"},
            ],
            "ETF": [
                {"code": "515030", "name": "新能源车ETF", "index": "中证新能源汽车指数"},
                {"code": "515790", "name": "光伏ETF", "index": "中证光伏产业指数"},
            ]
        },
        "医药": {
            "A股": [
                {"code": "600276", "name": "恒瑞医药", "reason": "创新药龙头"},
                {"code": "300760", "name": "迈瑞医疗", "reason": "医疗器械龙头"},
                {"code": "000538", "name": "云南白药", "reason": "中药龙头"},
            ],
            "ETF": [
                {"code": "512290", "name": "生物医药ETF", "index": "中证生物医药指数"},
                {"code": "512170", "name": "医疗ETF", "index": "中证医疗指数"},
            ]
        },
        "消费": {
            "A股": [
                {"code": "000858", "name": "五粮液", "reason": "高端白酒"},
                {"code": "600519", "name": "贵州茅台", "reason": "白酒龙头"},
                {"code": "002304", "name": "洋河股份", "reason": "区域白酒龙头"},
            ],
            "ETF": [
                {"code": "159928", "name": "消费ETF", "index": "中证主要消费指数"},
                {"code": "512690", "name": "酒ETF", "index": "中证酒指数"},
            ]
        },
        "金融": {
            "A股": [
                {"code": "601318", "name": "中国平安", "reason": "保险龙头"},
                {"code": "600036", "name": "招商银行", "reason": "零售银行龙头"},
                {"code": "600030", "name": "中信证券", "reason": "券商龙头"},
            ],
            "ETF": [
                {"code": "512880", "name": "证券ETF", "index": "中证全指证券公司指数"},
                {"code": "512800", "name": "银行ETF", "index": "中证银行指数"},
            ]
        }
    }

    # 关键词-行业映射
    KEYWORD_INDUSTRY_MAP = {
        "人工智能": ["AI", "人工智能", "大模型", "机器学习", "深度学习", "ChatGPT", "GPT"],
        "半导体": ["芯片", "半导体", "集成电路", "光刻机", "EDA", "晶圆"],
        "新能源": ["新能源", "光伏", "风电", "储能", "锂电池", "新能源汽车", "特斯拉"],
        "医药": ["医药", "生物", "创新药", "医疗器械", "疫苗", "医保", "集采"],
        "消费": ["消费", "白酒", "食品饮料", "零售", "旅游", "酒店", "免税"],
        "金融": ["银行", "保险", "证券", "券商", "房地产", "基建", "货币政策"],
    }

    def __init__(self, config_path="config/config.yaml"):
        """初始化分析器"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

    def analyze_news(self, news_data: List[Dict]) -> Dict[str, Any]:
        """分析新闻数据，生成投资建议"""

        # 提取所有新闻文本
        all_text = " ".join([news.get('title', '') + " " + news.get('content', '')
                             for news in news_data])

        # 识别涉及的行业
        industries = self._identify_industries(all_text)

        # 生成投资建议
        investment_advice = self._generate_investment_advice(industries, news_data)

        return {
            "industries": industries,
            "investment_advice": investment_advice,
            "news_count": len(news_data),
            "analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def _identify_industries(self, text: str) -> List[str]:
        """识别文本中涉及的行业"""
        industries_found = []

        for industry, keywords in self.KEYWORD_INDUSTRY_MAP.items():
            for keyword in keywords:
                if keyword.lower() in text.lower():
                    if industry not in industries_found:
                        industries_found.append(industry)
                    break

        return industries_found

    def _generate_investment_advice(self, industries: List[str], news_data: List[Dict]) -> Dict:
        """生成投资建议"""

        if not industries:
            return {"message": "未识别到明确的投资主题"}

        advice = {
            "热点主题": ", ".join(industries),
            "影响分析": self._analyze_impact(industries, news_data),
            "股票推荐": [],
            "ETF推荐": [],
            "风险提示": self._generate_risk_warning(industries)
        }

        # 为每个识别到的行业推荐股票和ETF
        for industry in industries[:3]:  # 最多分析前3个行业
            if industry in self.INDUSTRY_STOCKS:
                advice["股票推荐"].extend([
                    {**stock, "industry": industry}
                    for stock in self.INDUSTRY_STOCKS[industry]["A股"][:2]
                ])
                advice["ETF推荐"].extend([
                    {**etf, "industry": industry}
                    for etf in self.INDUSTRY_STOCKS[industry]["ETF"][:2]
                ])

        return advice

    def _analyze_impact(self, industries: List[str], news_data: List[Dict]) -> Dict:
        """分析影响"""
        sentiment = self._analyze_sentiment(news_data)

        return {
            "行业影响": f"本次热点涉及{len(industries)}个主要行业：{', '.join(industries)}",
            "市场情绪": sentiment,
            "持续时间": self._estimate_duration(news_data),
            "建议关注度": "高" if len(industries) > 0 else "低"
        }

    def _analyze_sentiment(self, news_data: List[Dict]) -> str:
        """简单情感分析"""
        positive_keywords = ["利好", "上涨", "增长", "突破", "创新", "政策支持", "业绩超预期"]
        negative_keywords = ["利空", "下跌", "下滑", "风险", "监管", "处罚", "业绩不及预期"]

        text = " ".join([news.get('title', '') for news in news_data])

        pos_count = sum(1 for word in positive_keywords if word in text)
        neg_count = sum(1 for word in negative_keywords if word in text)

        if pos_count > neg_count * 2:
            return "积极"
        elif neg_count > pos_count * 2:
            return "谨慎"
        else:
            return "中性"

    def _estimate_duration(self, news_data: List[Dict]) -> str:
        """估计热点持续时间"""
        platforms = set(news.get('platform', '') for news in news_data)

        if len(platforms) >= 5:
            return "中期（1-2周）"
        elif len(platforms) >= 3:
            return "短期（3-7天）"
        else:
            return "短暂（1-3天）"

    def _generate_risk_warning(self, industries: List[str]) -> str:
        """生成风险提示"""
        warnings = [
            "热点投资需注意市场情绪变化，避免追高",
            "建议结合基本面分析，不宜仅凭热点决策",
            "注意仓位控制，单行业配置不宜超过总仓位的20%",
            "关注政策风险和市场流动性变化"
        ]

        if "半导体" in industries:
            warnings.append("半导体行业受技术迭代和地缘政治影响较大")
        if "医药" in industries:
            warnings.append("医药行业受政策影响显著，关注集采政策变化")
        if "新能源" in industries:
            warnings.append("新能源行业技术路线存在不确定性")

        return "\n".join(f"• {w}" for w in warnings)

    def format_for_dingtalk(self, analysis_result: Dict) -> str:
        """格式化为钉钉消息"""
        advice = analysis_result["investment_advice"]

        message = f"""## 📈 投资热点分析报告
**分析时间**: {analysis_result['analysis_time']}
**监测到新闻数**: {analysis_result['news_count']}条

### 🎯 热点主题
{advice['热点主题']}

### 📊 影响分析
**行业影响**: {advice['影响分析']['行业影响']}
**市场情绪**: {advice['影响分析']['市场情绪']}
**持续时间**: {advice['影响分析']['持续时间']}
**建议关注度**: {advice['影响分析']['建议关注度']}

### 💰 推荐关注股票
"""

        for stock in advice['股票推荐'][:5]:  # 最多显示5只
            message += f"**{stock['name']} ({stock['code']})** - {stock['industry']}\n"
            message += f"逻辑: {stock['reason']}\n\n"

        message += "### 📊 推荐关注ETF\n"
        for etf in advice['ETF推荐'][:3]:  # 最多显示3只
            message += f"**{etf['name']} ({etf['code']})** - 跟踪{etf['index']}\n"

        message += f"\n### ⚠️ 风险提示\n{advice['风险提示']}"

        return message


# 集成到TrendRadar的主函数
def main():
    """主函数，集成到TrendRadar的AI分析流程"""
    import sys
    import os

    # 从标准输入或文件读取新闻数据
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            news_data = json.load(f)
    else:
        # 从TrendRadar的数据文件读取
        data_file = "output/latest_news.json"
        if os.path.exists(data_file):
            with open(data_file, 'r', encoding='utf-8') as f:
                news_data = json.load(f)
        else:
            print("未找到新闻数据文件")
            return

    # 初始化分析器
    analyzer = InvestmentAnalyzer()

    # 分析新闻
    result = analyzer.analyze_news(news_data)

    # 输出结果
    output_file = "output/investment_analysis.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # 生成钉钉消息
    dingtalk_message = analyzer.format_for_dingtalk(result)

    # 保存钉钉消息
    with open("output/dingtalk_message.md", 'w', encoding='utf-8') as f:
        f.write(dingtalk_message)

    print("投资分析完成！")


if __name__ == "__main__":
    from datetime import datetime

    main()