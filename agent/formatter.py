from typing import List
from .models import Study

class ResulFormatter:
    @staticmethod
    def format_study(study: Study) -> str:
        """
        Format a single study according to strict requirements.
        """
        # Determine Source Citation Tag
        if "ClinicalTrials.gov" in study.source:
             citation = f"[ClinicalTrials.gov:{study.id}]"
        elif "PubMed" in study.source:
             citation = f"[PubMed:{study.id}]"
        else: # NEJM or other
             citation = f"[{study.source}:{study.id}]"
             
        # Build structured fields
        output = f"""
### Title: {study.title}
{study.summary} {citation}

- **Identifier**: {study.id} ([Link]({study.url})) {citation}
- **Type**: {study.study_type or 'Not specified'} {study.phase or ''}
- **Enrollment**: {study.enrollment or 'Not reported'}
- **Demographics**: {study.demographics}
- **Exposure**: {study.exposure}
- **Endpoints**: {study.endpoints}
- **Biomarkers**: {study.biomarkers} / {study.protein_data}
- **Biology Note**: {study.biology_note or 'Not reported'}
- **Adverse Events**: {study.adverse_events}
  - *Unexpected Non-Serious*: {study.unexpected_aes}
- **Publications**: {", ".join(study.publications) if study.publications else "None listed"}

*Relevance Score*: {study.relevance_score}/100 ({study.score_justification})
*Next Steps*: {study.next_steps}
"""
        return output.strip()

    @staticmethod
    def format_no_results() -> str:
        return "No relevant records found in ClinicalTrials.gov / AACT / PubMed / NEJM within the specified timeframe."
