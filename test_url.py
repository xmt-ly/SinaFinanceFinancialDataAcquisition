import requests

url = "https://finance.sina.com.cn/stock/marketresearch/2026-04-12/doc-inhufqsa3277321.shtml?cref=cj"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Status code: {response.status_code}")
    print(f"Final URL: {response.url}")
    print(f"Response length: {len(response.text)}")
    print(f"First 500 chars: {response.text[:500]}...")
except Exception as e:
    print(f"Error: {e}")
