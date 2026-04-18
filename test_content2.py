import requests
from bs4 import BeautifulSoup

# 测试一个有效的新闻URL
url = "https://finance.sina.com.cn/meeting/2026-04-12/doc-inhufqsh5639201.shtml"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    response.encoding = 'utf-8'
    
    # 打印响应状态码和URL
    print(f"Status code: {response.status_code}")
    print(f"Final URL: {response.url}")
    
    # 解析页面
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 查找内容
    content_div = soup.find('div', id='artibody')
    if content_div:
        print("Found artibody div")
        paragraphs = content_div.find_all('p')
        print(f"Found {len(paragraphs)} paragraphs")
        content = ''.join([p.get_text(strip=True) for p in paragraphs])
        print(f"Content length: {len(content)}")
        print(f"First 500 chars: {content[:500]}...")
    else:
        print("No artibody div found")
        
        # 尝试其他可能的内容容器
        other_containers = soup.find_all(['div', 'article'], class_=True)
        print(f"Found {len(other_containers)} other containers")
        for i, container in enumerate(other_containers[:5]):
            print(f"Container {i+1}: {container.name}, class: {container.get('class')}")
            
except Exception as e:
    print(f"Error: {e}")
