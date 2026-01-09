from data_sources.clinical_trials import ClinicalTrialsAPI
import json

def test_search():
    api = ClinicalTrialsAPI()
    
    # 1. Natural Language Query (User's input)
    nl_query = "Do you have any trials in the last 3 years connecting GLP1 agonists and depression"
    print(f"Testing NL Query: '{nl_query}'")
    results_nl = api.search(nl_query)
    print(f"Results found: {len(results_nl)}")
    
    print("-" * 20)
    
    # 2. Keyword Query (Expected working input)
    kw_query = "GLP1 agonists depression"
    print(f"Testing Keyword Query: '{kw_query}'")
    results_kw = api.search(kw_query)
    print(f"Results found: {len(results_kw)}")
    if results_kw:
        print(f"First result: {results_kw[0]['title']}")

if __name__ == "__main__":
    test_search()
