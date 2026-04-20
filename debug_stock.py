import requests
from bs4 import BeautifulSoup
import re

stock_code = 'sh600519'
url = f"https://finance.sina.com.cn/realstock/company/{stock_code}/nc.shtml"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
}

response = requests.get(url, headers=headers, timeout=10)
response.encoding = 'gb2312'
html_content = response.content.decode('gb2312', errors='ignore')
soup = BeautifulSoup(html_content, 'html.parser')

# 查找所有script
scripts = soup.find_all('script')
print(f"Found {len(scripts)} script tags")

for i, script in enumerate(scripts):
    if script.string:
        if 'hq' in script.string.lower() or 'stock' in script.string.lower():
            print(f"\n=== Script {i} ===")
            print(script.string[:500])
