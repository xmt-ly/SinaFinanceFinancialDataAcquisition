import requests
from bs4 import BeautifulSoup

url = "https://finance.sina.com.cn/roll/?pageid=384&lid=2519&k=&num=50&page=1"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    # 自动检测编码
    response.encoding = response.apparent_encoding
    
    # 打印前5000个字符
    print("Page content preview:")
    print(response.text[:5000])
    
    # 解析页面
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 查找所有的li标签
    li_tags = soup.find_all('li')
    print(f"\nFound {len(li_tags)} li tags")
    
    # 打印前10个li标签的内容
    print("\nFirst 10 li tags:")
    for i, li in enumerate(li_tags[:10]):
        print(f"{i+1}: {li.get_text(strip=True)}")
        
    # 查找可能的新闻列表容器
    print("\nLooking for news list containers...")
    possible_containers = soup.find_all(['div', 'ul'], class_=True)
    for container in possible_containers[:5]:
        print(f"Container: {container.name}, class: {container.get('class')}")
        
except Exception as e:
    print(f"Error: {e}")
