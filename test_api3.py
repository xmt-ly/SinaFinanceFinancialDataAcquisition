import requests
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

stock_code = 'sh600519'

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://finance.sina.com.cn/",
    "Accept": "*/*",
}

# 新浪财经股票详情API
urls = [
    f"https://hq.sinajs.cn/list=gb_{stock_code}",
    f"https://hq.sinajs.cn/list=gb_{stock_code[2:]}",
]

for url in urls:
    print(f"\n=== Trying: {url} ===")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Content: {response.text[:300]}")
    except Exception as e:
        print(f"Error: {e}")

# 尝试获取基金/股票详细数据
print("\n=== Trying detailed quote ===")
url = f"https://finance.sina.com.cn/realstock/company/{stock_code}/hq.js"
try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Content: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")
