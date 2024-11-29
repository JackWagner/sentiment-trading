import requests
from bs4 import BeautifulSoup

class WebScraper:
    def __init__(self, url, headers):
        self.url = url
        self.headers = headers

    def get_html(self):
        response = requests.get(self.url, self.headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.content

    def parse_html(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        return soup

    def extract_data(self, soup):
        # Implement your data extraction logic here
        # Example: Extract all links
        links = [link.get('href') for link in soup.find_all('a', href=True)]
        return links

# Example usage
"""
url = 'https://www.example.com'
scraper = WebScraper(url)

html = scraper.get_html()
soup = scraper.parse_html(html)
data = scraper.extract_data(soup)
"""