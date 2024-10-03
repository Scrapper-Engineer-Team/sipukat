from bs4 import BeautifulSoup
import requests

class Soup:
    def __init__(self, url):
        self.url = url
        self.soup = self.load_html()

    def load_html(self):        
        try:
            res = requests.get(self.url)
            res.raise_for_status()  # Akan menimbulkan HTTPError jika status bukan 200
            return BeautifulSoup(res.text, 'html.parser')
        except requests.RequestException as e:
            print(f"Error while fetching the URL: {e}")
            return None

    def select(self, selector):
        if self.soup:
            return self.soup.select(selector)
        else:
            print("Soup is not loaded. Please check the URL.")
            return []
