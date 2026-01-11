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
        
        # Biomarker match scoring guidance: exact match = 70
        if study.has_biomarker_match:
            score += 70
            justifications.append("strong match (70)")
        
        # Unexpected non-serious AE scoring guidance: presence = 30
        if study.has_unexpected_ae:
            score += 30
            justifications.append("unexpected AE signal (30)")
            
        # Penalize if specifically missing key data (Biomarker OR AE data explicitly missing)
        # Default 15 points penalty
        if study.missing_data_penalty:
             score -= 15
             justifications.append("missing critical data (-15)")
             
        # Clamp score 0-100
        study.relevance_score = max(0, min(100, score))
        
        # 1-line human-readable justification
        # e.g., "strong biomarker match (70) + unexpected AE signal (30)"
        study.score_justification = " + ".join(justifications) if justifications else "baseline relevance (0)"
