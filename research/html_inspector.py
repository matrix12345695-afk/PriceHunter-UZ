from pathlib import Path

from bs4 import BeautifulSoup


html = Path(
    "research/samples/search.html"
).read_text(
    encoding="utf-8"
)

soup = BeautifulSoup(
    html,
    "lxml",
)

print()

print("=" * 60)

print("TITLE")

print(soup.title.text if soup.title else "None")

print()

print("=" * 60)

print("FIRST 100 LINKS")

for link in soup.find_all("a")[:100]:

    href = link.get("href")

    text = link.get_text(strip=True)

    print(href, text)
