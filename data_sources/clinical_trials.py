import requests
import logging
from typing import List, Dict, Any
from .base import BaseDataSource

class ClinicalTrialsAPI(BaseDataSource):
    BASE_URL = "https://clinicaltrials.gov/api/v2/studies"
    
    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search ClinicalTrials.gov API v2.
        """
        params = {
            "query.term": query,
            "pageSize": limit,
            "fields": "NCTId,BriefTitle,OfficialTitle,Phase,Condition,InterventionName,StudyType,LeadSponsorName,BriefSummary,EnrollmentCount,EligibilityCriteria,OutcomeMeasure,EventGroup,ReferencesModule"
        }
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            studies = data.get('studies', [])
            results = []
            
            for study in studies:
                protocol = study.get('protocolSection', {})
                derived = study.get('derivedSection', {})
                
                # Flatten crucial fields for easier processing later
                ident = protocol.get('identificationModule', {})
                status = protocol.get('statusModule', {})
                design = protocol.get('designModule', {})
                eligibility = protocol.get('eligibilityModule', {})
                outcomes = protocol.get('outcomesModule', {})
                references = protocol.get('referencesModule', {})
                
                # Extract PMIDs from references
                pmids = []
                for ref in references.get('references', []):
                    if ref.get('pmid'):
                        pmids.append(str(ref['pmid']))
                    elif ref.get('citation') and 'PMID' in ref['citation']:
                        # Simple heuristic if PMID not in structure but in text
                        pass 

                # Safe extraction
                result = {
                    "source": "ClinicalTrials.gov",
                    "id": ident.get('nctId'),
                    "url": f"https://clinicaltrials.gov/study/{ident.get('nctId')}",
                    "title": ident.get('officialTitle') or ident.get('briefTitle'),
                    "status": status.get('overallStatus'),
                    "phases": design.get('phases', []),
                    "study_type": design.get('studyType'),
                    "enrollment": design.get('enrollmentInfo', {}).get('count'),
                    "conditions": [c for c in protocol.get('conditionsModule', {}).get('conditions', [])],
                    "interventions": [i.get('name') for i in protocol.get('armsInterventionsModule', {}).get('interventions', [])],
                    "summary": protocol.get('descriptionModule', {}).get('briefSummary'),
                    "eligibility_criteria": eligibility.get('eligibilityCriteria'),
                    "primary_outcomes": [o.get('measure') for o in outcomes.get('primaryOutcomes', [])],
                    "publications": pmids,
                    # Adverse events are in a separate module often not populated in simple view, 
                    # but we request 'EventGroup' if available. 
                    # Note: API v2 structure for AEs is complex; we catch what we can.
                    "raw_data": study # Keep raw for deep parsing if needed
                }

                results.append(result)
                
            return results
            
        except Exception as e:
            logging.error(f"Error searching ClinicalTrials.gov: {e}")
            return []
