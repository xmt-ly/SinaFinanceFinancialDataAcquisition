import requests
from bs4 import BeautifulSoup
import re

# 尝试不同的URL格式
urls = [
    "https://finance.sina.com.cn/realstock/company/sh600519/nc.shtml",
    "https://finance.sina.com.cn/realstock/company/sz000001/nc.shtml",
    "https://quote.sina.com.cn/stock/sh600519",
    "https://hq.sinajs.cn/list=sh600519",
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
}

for url in urls:
    try:
        print(f"\n=== Testing: {url} ===")
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"URL: {response.url}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 打印页面标题
            title = soup.find('title')
            if title:
                print(f"Title: {title.get_text()}")
            
            # 打印页面中的一些内容
            print(f"Content length: {len(response.text)}")
            
    except Exception as e:
        print(f"Error: {e}")
