import os
import logging
import json
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed

from openai import OpenAI
from dotenv import load_dotenv

from data_sources.clinical_trials import ClinicalTrialsAPI
from data_sources.pubmed import PubMedAPI
from data_sources.nejm import NejmAPI
from .models import Study
from .scoring import RelevanceScorer
from .formatter import ResulFormatter

load_dotenv()

class PharmaAgent:
    def __init__(self):
        self.ct_api = ClinicalTrialsAPI()
        self.pubmed_api = PubMedAPI()
        self.nejm_api = NejmAPI()
        self.scorer = RelevanceScorer()
        self.formatter = ResulFormatter()
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        self.client = OpenAI(api_key=api_key)

    def search_and_analyze(self, query: str) -> str:
        """
        Main entry point.
        """
        # 0. Smart Query Extraction
        print(f"Original Query: {query}")
        optimized_query = self._extract_keywords(query)
        print(f"Optimized Search Keywords: {optimized_query}\n")
        
        # 1. Fetch raw data in parallel using optimized query
        raw_results = []
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(self.ct_api.search, optimized_query, limit=5),
                executor.submit(self.pubmed_api.search, optimized_query, limit=3), # Keep limits low for demo speed
                executor.submit(self.nejm_api.search, optimized_query, limit=2)
            ]
            for future in as_completed(futures):
                raw_results.extend(future.result())

        if not raw_results:
            return self.formatter.format_no_results() + "\n\nTry refining your search terms (e.g., specific drug or condition)."

        # 2. Analyze with LLM
        processed_studies = []
        # Process in parallel for speed
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(self._analyze_study, res, query): res for res in raw_results}
            for future in as_completed(futures):
                study = future.result()
                if study:
                    processed_studies.append(study)
        
        # 3. Score
        for study in processed_studies:
            self.scorer.score(study)
            
        # 4. Sort by score
        processed_studies.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return processed_studies

    def answer_question(self, studies: List[Study], question: str) -> str:
        """
        Answers a user question based on the context of the provided studies.
        """
        try:
            # Build Context String
            context_parts = []
            for i, study in enumerate(studies, 1):
                context_parts.append(f"Study {i}: {study.title} ({study.source})")
                context_parts.append(f"Summary: {study.summary}")
                context_parts.append(f"Biomarkers: {study.biomarkers}")
                context_parts.append(f"Adverse Events: {study.adverse_events}")
                context_parts.append(f"Demographics: {study.demographics}")
                context_parts.append(f"Enrollment: {study.enrollment}")
                context_parts.append(f"Relevance Score: {study.relevance_score}")
                context_parts.append("---")
            
            context_str = "\n".join(context_parts)
            print("--- DEBUG CHAT CONTEXT ---\n" + context_str + "\n--------------------------")
            
            prompt = f"""
            You are a research assistant answering questions about a specific set of clinical studies found by the user.
            
            User Question: "{question}"
            
            Available Study Context:
            {context_str[:15000]} # Limit context
            
             Instructions:
            - Answer strictly based on the provided studies.
            - The context includes fields for 'Enrollment', 'Relevance Score', 'Biomarkers', etc. USE THEM.
            - If the answer isn't in the studies, say "The provided studies do not mention this."
            - Cite specific studies (e.g., "Study 1 mentions...") when applicable.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating answer: {e}"

    def _extract_keywords(self, user_query: str) -> str:
        """
        Extracts search-optimized keywords from a natural language query using LLM.
        """
        try:
            prompt = f"""
            You are a helpful research assistant. Convert the following natural language query into a simple, effective keyword string for a medical database search (ClinicalTrials.gov, PubMed).
            
            Rules:
            - Remove stop words (do you have, show me, find, etc.).
            - Focus on: Drug names, Conditions, Mechanisms, Gene targets.
            - OUTPUT ONLY THE KEYWORDS. No quotes, no explanations.
            
            User Query: "{user_query}"
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logging.warning(f"Keyword extraction failed: {e}")
            return user_query # Fallback to original



    def _ensure_string(self, value) -> str:
        """Helper to handle list/string polymorphism from LLM extraction"""
        if isinstance(value, list):
            return ", ".join(str(v) for v in value)
        return str(value) if value else "Not reported"

    def _analyze_study(self, raw_data: dict, query: str) -> Study:
        """
        Use OpenAI to extracting information and populate the Study model.
        """
        try:
            # Prepare context for LLM
            source = raw_data.get("source")
            title = raw_data.get("title")
            
            # Context window optimization
            if source == "ClinicalTrials.gov":
                text_content = json.dumps({
                    "title": title,
                    "condition": raw_data.get("conditions"),
                    "intervention": raw_data.get("interventions"),
                    "summary": raw_data.get("summary"),
                    "criteria": raw_data.get("eligibility_criteria"),
                    "ages": raw_data.get("ages"),
                    "age_range": raw_data.get("age_range"),
                    "sex": raw_data.get("sex"),
                    "outcomes": raw_data.get("primary_outcomes")
                }, indent=2)
            else: # PubMed / NEJM
                text_content = f"Title: {title}\nAbstract: {raw_data.get('abstract')}\nJournal: {raw_data.get('journal')}"

            prompt = f"""
            You are an expert Pharma Discovery Data Scientist. Analyze this study/article for the query: "{query}".
            
            Extract the following fields strictly based on the text provided. Do NOT hallucinate.
            If a value is not found, use "Not reported".
            
            Required Output JSON format:
            {{
                "summary": "1-2 sentence evidence-first summary",
                "enrollment": "Number of participants/subjects if mentioned",
                "demographics": "Age, sex, N=...",
                "exposure": "Dose, duration, etc.",
                "endpoints": "Primary endpoints, results if any",
                "biomarkers": "List biomarkers mentioned or 'Not reported'",
                "protein_data": "Protein expression data or 'Not reported'",
                "biology_note": "1-2 lines on mechanism/biology",
                "adverse_events": "List Aes or 'Not reported'",
                "unexpected_aes": "Any UNEXPECTED non-serious AEs? If none, say 'None identified'",
                "has_biomarker_match": boolean (true if relevant biomarkers found),
                "has_unexpected_ae": boolean (true if unexpected non-serious AE found),
                "missing_data_penalty": boolean (true if critical biomarker/AE data is explicitly missing vs just not in abstract),
                "next_steps": "One clear recommendation for next steps"
            }}
            
            Data to Analyze:
            {text_content[:6000]} # Truncate to avoid limit
            """

            response = self.client.chat.completions.create(
                model="gpt-4o-mini", # Cost effective and standard
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0
            )
            
            content = response.choices[0].message.content
            extracted = json.loads(content)
            
            # Map back to Study model
            study = Study(
                id=raw_data.get("id", "Unknown"),
                source=source,
                title=title,
                url=raw_data.get("url", ""),
                study_type=raw_data.get("study_type") or raw_data.get("journal") or "Study",
                phase=str(raw_data.get("phases", "")) if "phases" in raw_data else None,
                
                # Priority: raw_data > LLM extraction > None
                # CT.gov provides enrollment natively; PubMed requires extraction
                enrollment=str(raw_data.get("enrollment")) if raw_data.get("enrollment") else self._ensure_string(extracted.get("enrollment")),
                
                # LLM Extracted fields
                summary=self._ensure_string(extracted.get("summary", "No summary available")),
                demographics=self._ensure_string(extracted.get("demographics")),
                exposure=self._ensure_string(extracted.get("exposure")),
                endpoints=self._ensure_string(extracted.get("endpoints")),
                biomarkers=self._ensure_string(extracted.get("biomarkers")),
                protein_data=self._ensure_string(extracted.get("protein_data")),
                biology_note=self._ensure_string(extracted.get("biology_note")),
                adverse_events=self._ensure_string(extracted.get("adverse_events")),
                unexpected_aes=self._ensure_string(extracted.get("unexpected_aes")),
                next_steps=self._ensure_string(extracted.get("next_steps")),
                
                # Publications: Use raw PMIDs from CT.gov if available, else could check extracted
                publications=raw_data.get("publications", []),
                
                # Scoring flags
                has_biomarker_match=extracted.get("has_biomarker_match", False),
                has_unexpected_ae=extracted.get("has_unexpected_ae", False),
                missing_data_penalty=extracted.get("missing_data_penalty", False),
                
                raw_data=raw_data
            )
            return study
            
        except Exception as e:
            logging.error(f"Error analyzing study {raw_data.get('id')}: {e}")
            return None
