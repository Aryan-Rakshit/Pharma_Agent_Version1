from agent.core import PharmaAgent
from dotenv import load_dotenv

def verify_fix():
    load_dotenv()
    agent = PharmaAgent()
    
    # User's exact natural language query
    nl_query = "Do you have any trials in the last 3 years connecting GLP1 agonists and depression"
    print(f"Testing Agent with Query: '{nl_query}'")
    print("-" * 30)
    
    # This should now work because of _extract_keywords
    results = agent.search_and_analyze(nl_query)
    
    # Check if results are just "No records found"
    if "No relevant records" in results:
        print("FAIL: Still returned 'No relevant records'.")
    else:
        print("SUCCESS: Results returned!")
        print(results[:500] + "...") # Print start of results

if __name__ == "__main__":
    verify_fix()
