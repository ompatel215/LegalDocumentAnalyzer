from typing import Dict, List, Tuple
import re
from collections import defaultdict

class DocumentClassifier:
    def __init__(self):
        """Initialize document classifier with document type patterns."""
        self.document_types = {
            "EMPLOYMENT_AGREEMENT": {
                "patterns": [
                    "employment agreement", "employment contract",
                    "work agreement", "labor contract",
                    "compensation", "salary", "wages",
                    "job duties", "work schedule"
                ],
                "weight": 1.0
            },
            "NON_DISCLOSURE": {
                "patterns": [
                    "non-disclosure agreement", "confidentiality agreement",
                    "confidential information", "trade secrets",
                    "proprietary information", "confidentiality obligations"
                ],
                "weight": 1.0
            },
            "SERVICE_AGREEMENT": {
                "patterns": [
                    "service agreement", "consulting agreement",
                    "professional services", "statement of work",
                    "service provider", "scope of services"
                ],
                "weight": 1.0
            },
            "LEASE_AGREEMENT": {
                "patterns": [
                    "lease agreement", "rental agreement",
                    "landlord", "tenant", "property",
                    "rent payment", "security deposit"
                ],
                "weight": 1.0
            },
            "TERMS_AND_CONDITIONS": {
                "patterns": [
                    "terms and conditions", "terms of service",
                    "terms of use", "user agreement",
                    "acceptable use", "service terms"
                ],
                "weight": 0.8
            },
            "PRIVACY_POLICY": {
                "patterns": [
                    "privacy policy", "data protection",
                    "personal information", "data collection",
                    "privacy rights", "data processing"
                ],
                "weight": 0.8
            },
            "PURCHASE_AGREEMENT": {
                "patterns": [
                    "purchase agreement", "sales contract",
                    "bill of sale", "purchase order",
                    "buyer", "seller", "purchase price"
                ],
                "weight": 0.9
            }
        }

        # Additional patterns for specific sections
        self.section_patterns = {
            "definitions": r"(?i)(definitions|interpretation|meaning of terms)",
            "parties": r"(?i)(between|party|parties)",
            "term": r"(?i)(term|duration|period)",
            "payment": r"(?i)(payment terms|compensation|fees)",
            "termination": r"(?i)(termination|cancellation)",
            "governing_law": r"(?i)(governing law|jurisdiction|applicable law)"
        }

    def classify_document(self, text: str) -> Dict:
        """
        Classify the document type and provide confidence scores.
        Returns classification results with supporting evidence.
        """
        # Initialize scores for each document type
        scores = defaultdict(float)
        evidence = defaultdict(list)
        
        # Convert text to lowercase for pattern matching
        text_lower = text.lower()
        
        # Calculate scores based on pattern matches
        for doc_type, config in self.document_types.items():
            type_score = 0
            for pattern in config["patterns"]:
                matches = list(re.finditer(r'\b' + re.escape(pattern) + r'\b', text_lower))
                if matches:
                    # Score based on number of matches and their context
                    pattern_score = len(matches) * 0.2
                    for match in matches:
                        # Get context around match
                        start = max(0, match.start() - 50)
                        end = min(len(text), match.end() + 50)
                        context = text[start:end].strip()
                        evidence[doc_type].append({
                            "pattern": pattern,
                            "context": context
                        })
                    type_score += pattern_score
            
            # Apply weight and normalize
            scores[doc_type] = min(1.0, type_score * config["weight"])

        # Get section analysis
        section_analysis = self._analyze_sections(text)
        
        # Determine primary and secondary classifications
        classifications = sorted(
            [(t, s) for t, s in scores.items() if s > 0.1],
            key=lambda x: x[1],
            reverse=True
        )
        
        # Prepare response
        result = {
            "primary_type": classifications[0][0] if classifications else "UNKNOWN",
            "confidence_score": classifications[0][1] if classifications else 0.0,
            "alternative_types": [
                {"type": t, "score": s}
                for t, s in classifications[1:3]  # Top 2 alternatives
            ],
            "evidence": dict(evidence),
            "section_analysis": section_analysis
        }
        
        # Add document structure analysis
        result["document_structure"] = self._analyze_document_structure(text)
        
        return result

    def _analyze_sections(self, text: str) -> Dict[str, Dict]:
        """Analyze document sections and their characteristics."""
        sections = {}
        
        for section_name, pattern in self.section_patterns.items():
            matches = list(re.finditer(pattern, text))
            if matches:
                # Get the first occurrence and its context
                match = matches[0]
                start = max(0, match.start() - 100)
                end = min(len(text), match.end() + 100)
                context = text[start:end].strip()
                
                sections[section_name] = {
                    "present": True,
                    "count": len(matches),
                    "sample_context": context
                }
            else:
                sections[section_name] = {
                    "present": False,
                    "count": 0,
                    "sample_context": None
                }
        
        return sections

    def _analyze_document_structure(self, text: str) -> Dict:
        """Analyze the overall structure of the document."""
        # Split into lines and remove empty lines
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        structure = {
            "total_sections": 0,
            "has_numbering": False,
            "has_headers": False,
            "formatting_style": "UNKNOWN",
            "structure_quality": 0.0
        }
        
        # Check for numbered sections
        numbered_lines = sum(1 for line in lines if re.match(r'^\d+\.|\([a-z]\)|[A-Z]\.', line))
        if numbered_lines > len(lines) * 0.1:
            structure["has_numbering"] = True
        
        # Check for headers (capitalized lines)
        header_lines = sum(1 for line in lines if line.isupper())
        if header_lines > 0:
            structure["has_headers"] = True
        
        # Detect formatting style
        if structure["has_numbering"] and structure["has_headers"]:
            structure["formatting_style"] = "FORMAL"
        elif structure["has_numbering"]:
            structure["formatting_style"] = "SEMI_FORMAL"
        elif structure["has_headers"]:
            structure["formatting_style"] = "BASIC"
        
        # Count potential sections
        structure["total_sections"] = sum(
            1 for line in lines
            if line.isupper() or re.match(r'^\d+\.|\([a-z]\)|[A-Z]\.', line)
        )
        
        # Calculate structure quality score
        quality_score = 0.0
        if structure["has_numbering"]: quality_score += 0.4
        if structure["has_headers"]: quality_score += 0.3
        if structure["total_sections"] > 5: quality_score += 0.3
        
        structure["structure_quality"] = quality_score
        
        return structure 