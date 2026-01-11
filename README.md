# Pharma Discovery Research Agent

A Python-based AI agent to assist with pharma discovery research by analyzing ClinicalTrials.gov, PubMed, and NEJM data using OpenAI for reasoning.
https://pharmadiscoveryagent.streamlit.app/

## Setup

1. **Prerequisites**: Python 3.10+ installed.

2. **Installation**:
   ```bash
   pip install -r requirements.txt
   ```

3. **API Key**:
   The agent requires an OpenAI API key.
   Create a `.env` file in this directory with:
   ```env
   OPENAI_API_KEY=sk-proj-...
   ```
   (A `.env` file has been pre-configured for this environment).

## Running the Agent

### User Interface (Streamlit)
To launch the interactive UI:
```bash
streamlit run ui/app.py
```
This will open the application in your browser.

### Command Line Interface (CLI)
To run a quick search from the terminal:
```bash
python main.py "your research query"
```
Example:
```bash
python main.py "lung cancer immunotherapy biomarkers"
```

## Architecture
- `data_sources/`: Clients for ClinicalTrials.gov, PubMed, NEJM.
- `agent/`: Core reasoning, scoring (biomarker/AE logic), and formatting.
- `ui/`: Streamlit source code.
