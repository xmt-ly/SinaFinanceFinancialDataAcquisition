import requests
from bs4 import BeautifulSoup
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

stock_code = 'sh600519'
url = f"https://finance.sina.com.cn/realstock/company/{stock_code}/nc.shtml"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

response = requests.get(url, headers=headers, timeout=10)
response.encoding = 'gb2312'
html_content = response.content.decode('gb2312', errors='ignore')
soup = BeautifulSoup(html_content, 'html.parser')

details_div = soup.find('div', class_='hq_details')
print(f"Found: {details_div is not None}")

if details_div:
    # 保存到文件
    with open('stock_details.html', 'w', encoding='utf-8') as f:
        f.write(str(details_div))
    
    # 提取所有数据
    data = {}
    
    # 从表格中提取
    table = details_div.find('table')
    if table:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 2:
                key = cells[0].get_text(strip=True)
                value = cells[1].get_text(strip=True)
                if key:
                    data[key] = value
    
    # 从span中提取
    spans = details_div.find_all('span')
    for span in spans:
        text = span.get_text(strip=True)
        if ':' in text:
            parts = text.split(':', 1)
            if len(parts) == 2:
                data[parts[0].strip()] = parts[1].strip()
    
    print("\n=== Extracted Data ===")
    for k, v in data.items():
        print(f"{k}: {v}")
