import chromadb
import requests
from bs4 import BeautifulSoup

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="farming_knowledge")

# Function to scrape agricultural websites
def scrape_agriculture_data(url):
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        articles = soup.find_all("p")
        text = " ".join([p.text for p in articles if len(p.text) > 50])
        return text if text else None
    except Exception:
        return None

# List of sources
agriculture_urls = [
    "https://www.nibio.no/en",
    "https://tulimee.org/",
    "https://www.urbantlandbruk.no/pageen",
    "https://www.farmafrica.org/",
    "https://en.innovasjonnorge.no/article/agriculture"
]

def update_chromadb():
    for idx, url in enumerate(agriculture_urls):
        web_text = scrape_agriculture_data(url)
        if web_text:
            doc_id = f"web_{idx}"
            collection.upsert(ids=[doc_id], documents=[web_text])

if __name__ == "__main__":
    update_chromadb()
    print("✅ ChromaDB updated with latest farming data.")
