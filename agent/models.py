from pydantic import BaseModel
from typing import List, Optional

class Study(BaseModel):
    id: str
    source: str # ClinicalTrials.gov, PubMed, NEJM
    title: str
    url: str
    phase: Optional[str] = None
    study_type: Optional[str] = None
    status: Optional[str] = None
    enrollment: Optional[str] = None # String to handle "100 participants" or just numbers
    demographics: Optional[str] = "Not reported"
    exposure: Optional[str] = "Not reported" # Duration/Dose
    endpoints: Optional[str] = "Not reported"
    biomarkers: Optional[str] = "Not reported" # Extracted or raw
    protein_data: Optional[str] = "Not reported"
    biology_note: Optional[str] = None # Generated 1-2 lines
    adverse_events: Optional[str] = "Not reported"
    unexpected_aes: Optional[str] = "None identified"
    publications: List[str] = [] # PMIDs
    summary: str # Brief 1-2 sentences
    raw_data: Optional[dict] = None
    
    # Metadata for scoring
    has_biomarker_match: bool = False
    has_unexpected_ae: bool = False
    missing_data_penalty: bool = False
    
    relevance_score: int = 0
    score_justification: str = ""
    next_steps: str = ""
