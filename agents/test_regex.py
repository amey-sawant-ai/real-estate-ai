import requests, re
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": "https://www.numbeo.com/"
}

r = requests.get('https://www.numbeo.com/quality-of-life/in/Mumbai', headers=headers)
html_content = r.text

metrics = [
    "Quality of Life Index",
    "Safety Index",
    "Cost of Living Index",
    "Property Price to Income Ratio",
    "Purchasing Power Index",
    "Health Care Index",
    "Climate Index"
]

print("--- RAW HTML REGEX ---")
for metric in metrics:
    # Any combination of HTML tags, whitespace, or colons
    pattern = re.compile(re.escape(metric) + r'(?:<[^>]*>|\s|:)+([\d.]+)')
    match = pattern.search(html_content)
    print(f"{metric}: {match.group(1) if match else None}")
