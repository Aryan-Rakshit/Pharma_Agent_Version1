import requests
import json

def test_ct_gov():
    print("Testing ClinicalTrials.gov API v2...")
    url = "https://clinicaltrials.gov/api/v2/studies"
    params = {
        "query.term": "asthma", # simple term
        "pageSize": 1
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"CT.gov Status: {response.status_code}")
        response.raise_for_status()
        data = response.json()
        print(f"CT.gov Root Keys: {list(data.keys())}")
        if "studies" in data and data["studies"]:
            study = data["studies"][0]
            print(f"CT.gov Study Keys: {list(study.keys())}")
            # Check protocolSection and derivedSection structure deeply if needed
            if "protocolSection" in study:
                 print("protocolSection keys:", list(study["protocolSection"].keys()))
        else:
            print("CT.gov: No studies found.")
    except Exception as e:
        print(f"CT.gov failed: {e}")
        if 'response' in locals():
            print(response.text[:200])

def test_pubmed():
    print("\nTesting PubMed E-utilities...")
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    # Broader search
    search_params = {
        "db": "pubmed",
        "term": "asthma",
        "retmode": "json",
        "retmax": 1
    }
    try:
        resp = requests.get(search_url, params=search_params, timeout=10)
        print(f"PubMed Search Status: {resp.status_code}")
        resp.raise_for_status()
        data = resp.json()
        print(f"PubMed Search Keys: {list(data.keys())}")
        
        ids = data.get("esearchresult", {}).get("idlist", [])
        if ids:
            print(f"Found IDs: {ids}")
            summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
            sum_params = {
                "db": "pubmed",
                "id": ",".join(ids),
                "retmode": "json"
            }
            sum_resp = requests.get(summary_url, params=sum_params, timeout=10)
            print(f"PubMed Summary Status: {sum_resp.status_code}")
            sum_data = sum_resp.json()
            print(f"PubMed Summary Keys: {list(sum_data.keys())}")
            if "result" in sum_data:
                uid = ids[0]
                if uid in sum_data["result"]:
                    print(f"Article Title: {sum_data['result'][uid].get('title', 'N/A')}")
        else:
            print("No PubMed results found.")
            
    except Exception as e:
        print(f"PubMed failed: {e}")

if __name__ == "__main__":
    test_ct_gov()
    test_pubmed()
