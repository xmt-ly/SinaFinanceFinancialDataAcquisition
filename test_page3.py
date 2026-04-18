import requests

url = "https://finance.sina.com.cn/roll/?pageid=384&lid=2519&k=&num=50&page=1"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    # 自动检测编码
    response.encoding = response.apparent_encoding
    
    # 保存页面内容到文件
    with open('page_content.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    
    print("Page content saved to page_content.html")
    
    # 搜索新闻模式
    content = response.text
    
    # 查找包含时间的新闻项
    import re
    # 查找类似 "2026-04-12 16:25" 这样的时间格式
    time_patterns = re.findall(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}', content)
    print(f"\nFound {len(time_patterns)} time patterns")
    print("First 10 time patterns:")
    for time_pat in time_patterns[:10]:
        print(time_pat)
        
    # 查找包含链接和时间的模式
    print("\nLooking for news links with time...")
    # 查找包含时间的链接
    links_with_time = re.findall(r'<a href="([^"]+)".*?>(.*?)\d{4}-\d{2}-\d{2} \d{2}:\d{2}', content, re.DOTALL)
    print(f"Found {len(links_with_time)} links with time")
    for i, (url, title) in enumerate(links_with_time[:5]):
        print(f"{i+1}: {title.strip()} - {url}")
        
except Exception as e:
    print(f"Error: {e}")
