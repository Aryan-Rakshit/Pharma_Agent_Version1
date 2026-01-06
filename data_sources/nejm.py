from typing import List, Dict, Any
from .pubmed import PubMedAPI

class NejmAPI(PubMedAPI):
    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search specifically in New England Journal of Medicine via PubMed.
        """
        nejm_query = f'{query} AND "New England Journal of Medicine"[Journal]'
        results = super().search(nejm_query, limit)
        for res in results:
            res["source"] = "NEJM" # Override source label
            # NEJM often has DOIs that correspond to specific URLs, but PubMed URL is fine as fallback.
            # We could try to extract DOI if needed for direct link.
        return results
