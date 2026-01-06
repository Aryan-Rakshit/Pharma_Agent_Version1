import sys
import argparse
from dotenv import load_dotenv
from agent.core import PharmaAgent

def main():
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Pharma Discovery Agent CLI")
    parser.add_argument("query", help="Research query string")
    args = parser.parse_args()
    
    try:
        agent = PharmaAgent()
        print(f"Searching for: '{args.query}'...\n")
        results = agent.search_and_analyze(args.query)
        print(results)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
