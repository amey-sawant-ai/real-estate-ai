import requests
import re
from bs4 import BeautifulSoup

r = requests.get('https://www.numbeo.com/quality-of-life/in/Mumbai', headers={'User-Agent': 'Mozilla/5.0'})
soup = BeautifulSoup(r.text, 'html.parser')
indices = {}
for table in soup.find_all('table'):
    for row in table.find_all('tr'):
        cols = row.find_all('td')
        if len(cols) >= 2:
            key = cols[0].text.replace(':', '').strip()
            val_text = cols[1].text.strip()
            match = re.search(r'([\d.]+)', val_text)
            if match:
                indices[key] = float(match.group(1))

print(indices)
