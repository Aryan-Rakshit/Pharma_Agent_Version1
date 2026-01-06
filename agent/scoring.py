from .models import Study

class RelevanceScorer:
    def score(self, study: Study) -> None:
        """
        Apply scoring logic:
        - Biomarker match: +70
        - Unexpected non-serious AE signal: +30
        - Missing biomarker or AE data: -15
        """
        score = 0
        justifications = []
        
        if study.has_biomarker_match:
            score += 70
            justifications.append("Biomarker match (+70)")
        
        if study.has_unexpected_ae:
            score += 30
            justifications.append("Unexpected non-serious AE signal (+30)")
            
        # Penalize if specifically missing key data (Biomarker OR AE data explicitly missing)
        # Note: "Not reported" is the default, so we check if it stays that way or if analysis confirms missing
        if study.missing_data_penalty:
             score -= 15
             justifications.append("Missing key biomarker/AE data (-15)")
             
        # Clamp score 0-100
        study.relevance_score = max(0, min(100, score))
        study.score_justification = ", ".join(justifications) if justifications else "Baseline relevance"
