import requests
import logging
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from .base import BaseDataSource

class PubMedAPI(BaseDataSource):
    SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    
    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search PubMed.
        """
        # 1. Search for IDs
        search_params = {
            "db": "pubmed",
            "term": query,
            "retmode": "json",
            "retmax": limit,
            "sort": "relevance"
        }
        
        try:
            resp = requests.get(self.SEARCH_URL, params=search_params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            ids = data.get("esearchresult", {}).get("idlist", [])
            
            if not ids:
                return []
                
            # 2. Fetch Details (Abstracts)
            fetch_params = {
                "db": "pubmed",
                "id": ",".join(ids),
                "retmode": "xml"
            }
            
            fetch_resp = requests.get(self.FETCH_URL, params=fetch_params, timeout=15)
            fetch_resp.raise_for_status()
            
            return self._parse_xml_response(fetch_resp.content)
            
        except Exception as e:
            logging.error(f"Error searching PubMed: {e}")
            return []

    def _parse_xml_response(self, xml_content: bytes) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(xml_content, "xml")
        articles = []
        
        for article in soup.find_all("PubmedArticle"):
            try:
                medline = article.find("MedlineCitation")
                article_data = medline.find("Article")
                
                pmid = medline.find("PMID").text
                title = article_data.find("ArticleTitle").text
                
                abstract_tag = article_data.find("Abstract")
                abstract = ""
                if abstract_tag:
                    abstract_texts = abstract_tag.find_all("AbstractText")
                    abstract = " ".join([t.text for t in abstract_texts])
                
                journal = article_data.find("Journal").find("Title").text
                
                # Extract Publication Date
                pub_date = article_data.find("PubDate")
                year = pub_date.find("Year").text if pub_date.find("Year") else "N/A"
                
                result = {
                    "source": "PubMed",
                    "id": pmid,
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    "title": title,
                    "abstract": abstract,
                    "journal": journal,
                    "year": year,
                    "raw_data": str(article)
                }
                articles.append(result)
            except Exception as e:
                logging.warning(f"Error parsing a PubMed article: {e}")
                continue
                
        return articles
