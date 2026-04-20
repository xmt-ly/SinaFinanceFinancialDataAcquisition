import requests
import re

stock_codes = ['sh600519', 'sz000001', 'sh601318']

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "Referer": "https://finance.sina.com.cn/stock/",
    "Accept": "*/*",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

for code in stock_codes:
    url = f"https://hq.sinajs.cn/list={code}"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        text = response.text
        print(f"\n{code}: {text[:300]}")
        
        if '=' in text:
            data = text.split('=')[1].split(',')
            if len(data) > 1:
                print(f"  解析数据: {data[0:10]}")
    except Exception as e:
        print(f"{code}: Error - {e}")
