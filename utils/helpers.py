from bs4 import BeautifulSoup
from urllib.parse import quote_plus

def clean_html(html):
    return BeautifulSoup(html, "html.parser").get_text("\n", strip=True)

def quote_plus_safe(v):
    return quote_plus(v) if v else ""
