from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseDataSource(ABC):
    @abstractmethod
    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search the data source for the query.
        Returns a list of raw study/article dictionaries.
        """
        pass
