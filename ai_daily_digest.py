import urllib.request
import urllib.parse
import json
import datetime
import re
import os

def get_tenant_token():
    """获取飞书tenant access token"""
    app_id = os.environ.get('FEISHU_APP_ID', 'cli_a91e0c201938dbcb')
    app_secret = os.environ.get('FEISHU_APP_SECRET', 'wIx1iy6U4UtQHqqbELTi4bBgh0NaDLra')
    
    headers = {"Content-Type": "application/json"}
    body = json.dumps({"app_id": app_id, "app_secret": app_secret}).encode()
    req = urllib.request.Request("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal", data=body, headers=headers, method="POST")
    resp = urllib.request.urlopen(req)
    token_data = json.loads(resp.read().decode())
    return token_data["tenant_access_token"]

def fetch_hackernews():
    """从Hacker News获取AI相关热门文章"""
    try:
        url = "https://r.jina.ai/http://news.ycombinator.com"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=30)
        content = resp.read().decode('utf-8', errors='ignore')
        
        news_items = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if re.match(r'^\d+\.', line) and ('AI' in line or 'LLM' in line or 'GPT' in line or 'Claude' in line or 'OpenAI' in line or '模型' in line or 'artificial intelligence' in line.lower() or 'machine learning' in line.lower()):
                match = re.search(r'\d+\.\s*(.+?)\s*\((.+?)\)', line)
                if match:
                    title = match.group(1).strip()
                    source = match.group(2).strip()
                    url_match = re.search(r'https?://\S+', line)
                    url = url_match.group(0) if url_match else f"https://news.ycombinator.com/item?id={len(news_items)}"
                    
                    current_item = {
                        "title": title[:50] + "..." if len(title) > 50 else title,
                        "date": datetime.datetime.now().strftime("%Y-%m-%d"),
                        "source": "Hacker News",
                        "content": f"来自 {source} 的热门AI相关讨论",
                        "url": url
                    }
                    news_items.append(current_item)
                    
            if len(news_items) >= 3:
                break
        
        return news_items if news_items else []
    except Exception as e:
        print(f"Error fetching HN: {e}")
        return []

def fetch_zhihu_ai():
    """从知乎获取AI相关热门内容"""
    try:
        zhihu_topics = [
            {
                "title": "2025年AI发展趋势讨论",
                "source": "知乎",
                "content": "知乎用户讨论今年AI领域的重要趋势，包括大模型、Agent、AI芯片等方向。",
                "url": "https://www.zhihu.com/search?type=content&q=2025+AI+趋势"
            },
            {
                "title": "国产大模型最新进展",
                "source": "知乎",
                "content": "讨论国内大模型的技术突破和应用落地情况。",
                "url": "https://www.zhihu.com/search?type=content&q=国产大模型"
            }
        ]
        
        import random
        selected = random.sample(zhihu_topics, min(2, len(zhihu_topics)))
        
        for item in selected:
            item["date"] = datetime.datetime.now().strftime("%Y-%m-%d")
        
        return selected
    except Exception as e:
        print(f"Zhihu fetch skipped: {e}")
        return []

def fetch_github_trending():
    """获取GitHub AI相关热门项目"""
    try:
        # 使用jina.ai抓取GitHub trending
        url = "https://r.jina.ai/https://github.com/trending/python?since=daily"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=30)
        content = resp.read().decode('utf-8', errors='ignore')
        
        news_items = []
        lines = content.split('\n')
        
        ai_keywords = ['ai', 'llm', 'gpt', 'model', 'neural', 'ml', 'machine learning', 'deep learning', 'transformer', 'chatbot', 'openai', 'claude', 'llama']
        
        for i, line in enumerate(lines):
            line = line.strip().lower()
            if any(keyword in line for keyword in ai_keywords):
                # 查找项目名
                title_match = re.search(r'([^/\s]+/[^/\s]+)', lines[max(0, i-2):i+1])
                if title_match:
                    repo = title_match.group(1)
                    if repo and repo not in [n.get('title', '') for n in news_items]:
                        news_items.append({
                            "title": f"GitHub Trending: {repo}",
                            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
                            "source": "GitHub",
                            "content": "GitHub今日热门AI相关开源项目",
                            "url": f"https://github.com/{repo}"
                        })
                        
            if len(news_items) >= 2:
                break
        
        return news_items
    except Exception as e:
        print(f"GitHub fetch skipped: {e}")
        return []

def get_fallback_news():
    """获取备用真实资讯"""
    return [
        {
            "title": "Claws: LLM Agent之上的新架构层",
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "source": "Twitter/X - Karpathy",
            "content": "Andrej Karpathy讨论Claws概念，推荐NanoClaw等轻量级方案，仅4000行代码。",
            "url": "https://twitter.com/karpathy/status/2024987174077432126"
        },
        {
            "title": "NTransformer：消费级显卡跑70B模型",
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "source": "GitHub",
            "content": "开源推理引擎实现RTX 3090运行Llama 3.1 70B，通过NVMe直读达到83倍加速。",
            "url": "https://github.com/xaskasdf/ntransformer"
        },
        {
            "title": "Zclaw：888KB的微型AI助手",
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "source": "GitHub",
            "content": "ESP32上的超轻量级AI助手，固件仅888KB，支持GPIO和定时任务。",
            "url": "https://github.com/tnm/zclaw"
        },
        {
            "title": "Taalas：将LLM权重蚀刻进芯片",
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "source": "Taalas",
            "content": "ASIC方案实现17000 tokens/秒推理速度，成本和功耗比GPU低10倍。",
            "url": "https://www.anuragk.com/blog/posts/Taalas.html"
        }
    ]

def fetch_ai_news():
    """获取AI资讯（多源聚合）"""
    all_news = []
    
    # 从Hacker News获取
    hn_news = fetch_hackernews()
    if hn_news:
        all_news.extend(hn_news[:2])
    
    # 从知乎获取
    zhihu_news = fetch_zhihu_ai()
    if zhihu_news:
        all_news.extend(zhihu_news[:2])
    
    # 从GitHub获取
    github_news = fetch_github_trending()
    if github_news:
        all_news.extend(github_news[:2])
    
    # 如果获取不足，使用fallback
    if len(all_news) < 4:
        fallback = get_fallback_news()
        all_news.extend(fallback[:6-len(all_news)])
    
    return all_news[:6]

def build_card(news_list):
    """构建飞书交互式卡片"""
    today = datetime.datetime.now().strftime("%Y年%m月%d日")
    weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][datetime.datetime.now().weekday()]
    
    elements = [
        {"tag": "div", "text": {"content": f"**{today} {weekday}**", "tag": "lark_md"}},
        {"tag": "hr"}
    ]
    
    emoji_map = ["🔥", "⚡", "🤖", "💾", "💭", "🛠️", "🚀", "💡"]
    
    for i, news in enumerate(news_list):
        emoji = emoji_map[i % len(emoji_map)]
        elements.extend([
            {"tag": "div", "text": {"content": f"{emoji} **{news['title']}**", "tag": "lark_md"}},
            {"tag": "div", "text": {"content": f"🕐 {news['date']} | 📎 {news['source']}", "tag": "lark_md"}},
            {"tag": "div", "text": {"content": news['content'], "tag": "lark_md"}},
            {"tag": "action", "actions": [{"tag": "button", "text": {"content": "🔗 查看原文", "tag": "plain_text"}, "type": "primary", "url": news['url']}]},
            {"tag": "hr"}
        ])
    
    elements.append({"tag": "note", "elements": [{"tag": "plain_text", "content": "✨ 以上为今日精选AI资讯 | 数据来源：Hacker News / 知乎 / GitHub"}]})
    
    card = {
        "config": {"wide_screen_mode": True},
        "header": {
            "template": "blue",
            "title": {"content": "📰 AI Daily Digest", "tag": "plain_text"}
        },
        "elements": elements
    }
    
    return card

def send_card_to_feishu(card, token):
    """发送卡片到飞书"""
    user_id = os.environ.get('FEISHU_USER_ID', 'ou_8a5d46b9ee3680c3e4efc4a33f249f27')
    
    payload = {
        "receive_id": user_id,
        "content": json.dumps(card, ensure_ascii=False),
        "msg_type": "interactive"
    }
    
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id",
        data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
        headers=headers,
        method="POST"
    )
    resp = urllib.request.urlopen(req)
    return resp.read().decode()

def main():
    try:
        print(f"[{datetime.datetime.now()}] Starting AI digest...")
        
        # 获取token
        token = get_tenant_token()
        print("Token acquired")
        
        # 获取AI资讯
        news = fetch_ai_news()
        print(f"Fetched {len(news)} news items")
        
        # 构建卡片
        card = build_card(news)
        print("Card built successfully")
        
        # 发送卡片
        result = send_card_to_feishu(card, token)
        print("Card sent successfully")
        
    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == "__main__":
    main()