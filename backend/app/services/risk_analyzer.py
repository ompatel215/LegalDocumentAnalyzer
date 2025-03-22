from typing import List, Dict, Any
import re
from collections import defaultdict
from textblob import TextBlob

class RiskAnalyzer:
    """Analyzes legal risks in documents."""
    
    def __init__(self):
        """Initialize risk analyzer with risk patterns and weights."""
        # Risk patterns with their weights
        self.risk_patterns = {
            "high_risk": {
                "non_compete": (
                    r"(?i)non-compete|compete|competition|competitive|"
                    r"restricted\s+from|prohibited\s+from\s+competing"
                ),
                "confidentiality": (
                    r"(?i)confidential|proprietary|trade\s+secret|"
                    r"non-disclosure|confidentiality"
                ),
                "termination": (
                    r"(?i)terminate|termination|immediate\s+termination|"
                    r"right\s+to\s+terminate|grounds\s+for\s+termination"
                ),
                "liability": (
                    r"(?i)liable|liability|indemnify|indemnification|"
                    r"hold\s+harmless|damages|claims"
                ),
                "intellectual_property": (
                    r"(?i)intellectual\s+property|patent|copyright|trademark|"
                    r"trade\s+secret|proprietary\s+rights"
                ),
            },
            "medium_risk": {
                "payment": (
                    r"(?i)payment|compensation|fee|amount|salary|"
                    r"remuneration|consideration"
                ),
                "notice": (
                    r"(?i)notice\s+period|notification|written\s+notice|"
                    r"advance\s+notice"
                ),
                "modification": (
                    r"(?i)modify|modification|amend|amendment|change|alter|"
                    r"revision|update"
                ),
                "assignment": (
                    r"(?i)assign|assignment|transfer|delegate|delegation"
                ),
                "governing_law": (
                    r"(?i)governing\s+law|jurisdiction|venue|applicable\s+law|"
                    r"dispute\s+resolution"
                ),
            },
            "low_risk": {
                "definitions": r"(?i)means|defined|definition|refers\s+to",
                "interpretation": r"(?i)interpret|construction|meaning",
                "notices": r"(?i)notice|notify|notification|inform",
                "severability": r"(?i)sever|severability|invalid|unenforceable",
                "force_majeure": r"(?i)force\s+majeure|act\s+of\s+god|beyond\s+control",
            }
        }
        
        # Risk weights for scoring
        self.risk_weights = {
            "high_risk": 1.0,
            "medium_risk": 0.6,
            "low_risk": 0.3
        }
        
        # Compliance requirements patterns
        self.compliance_patterns = {
            "data_privacy": r"(?i)personal\s+data|privacy|gdpr|ccpa|data\s+protection",
            "employment": r"(?i)employee|employment|worker|staff|personnel",
            "financial": r"(?i)financial|monetary|payment|tax|revenue",
            "environmental": r"(?i)environmental|sustainability|pollution|waste",
            "health_safety": r"(?i)health|safety|security|hazard|risk",
            "regulatory": r"(?i)regulation|compliance|authority|regulatory|law"
        }
    
    def analyze_risks(self, text: str, clause_analysis: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Perform comprehensive risk analysis on the document.
        Returns risk assessment results including scores and recommendations.
        """
        # Initialize risk analysis results
        results = {
            "overall_risk_score": 0.0,
            "risk_categories": self._analyze_risk_categories(text),
            "critical_clauses": self._identify_critical_clauses(clause_analysis),
            "compliance_requirements": self._identify_compliance_requirements(text),
            "recommendations": [],
            "risk_factors": self._analyze_risk_factors(text),
            "sentiment_analysis": self._analyze_risk_sentiment(text)
        }
        
        # Calculate overall risk score
        risk_scores = []
        for category, risks in results["risk_categories"].items():
            weight = self.risk_weights.get(category, 0.5)
            if risks:  # If any risks found in this category
                risk_scores.append(len(risks) * weight)
        
        if risk_scores:
            results["overall_risk_score"] = min(1.0, sum(risk_scores) / (len(risk_scores) * 2))
        
        # Generate recommendations based on findings
        results["recommendations"] = self._generate_recommendations(results)
        
        return results
    
    def _analyze_risk_categories(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """Analyze text for different categories of risks."""
        risk_categories = {
            "high_risk": [],
            "medium_risk": [],
            "low_risk": []
        }
        
        # Analyze each risk category
        for category, patterns in self.risk_patterns.items():
            for risk_type, pattern in patterns.items():
                matches = list(re.finditer(pattern, text, re.IGNORECASE))
                if matches:
                    for match in matches:
                        # Get context around the match
                        start = max(0, match.start() - 100)
                        end = min(len(text), match.end() + 100)
                        context = text[start:end]
                        
                        risk_categories[category].append({
                            "type": risk_type,
                            "context": context.strip(),
                            "matched_text": match.group(),
                            "position": match.start()
                        })
        
        return risk_categories
    
    def _identify_critical_clauses(self, clause_analysis: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify critical clauses that require attention."""
        critical_clauses = []
        
        for clause in clause_analysis:
            risk_level = self._assess_clause_risk(clause)
            if risk_level > 0.6:  # High risk threshold
                critical_clauses.append({
                    "text": clause["text"],
                    "risk_level": risk_level,
                    "type": clause["type"],
                    "concerns": self._identify_clause_concerns(clause)
                })
        
        return sorted(critical_clauses, key=lambda x: x["risk_level"], reverse=True)
    
    def _assess_clause_risk(self, clause: Dict[str, Any]) -> float:
        """Assess the risk level of a specific clause."""
        risk_score = 0.0
        text = clause["text"].lower()
        
        # Check for high-risk patterns
        for pattern in self.risk_patterns["high_risk"].values():
            if re.search(pattern, text, re.IGNORECASE):
                risk_score += 0.4
        
        # Check for medium-risk patterns
        for pattern in self.risk_patterns["medium_risk"].values():
            if re.search(pattern, text, re.IGNORECASE):
                risk_score += 0.2
        
        # Consider clause type
        if clause["type"] in ["OBLIGATION", "PROHIBITION"]:
            risk_score += 0.2
        
        # Consider sentiment
        if "sentiment" in clause:
            if clause["sentiment"]["polarity"] < -0.2:  # Negative sentiment
                risk_score += 0.1
        
        return min(1.0, risk_score)
    
    def _identify_clause_concerns(self, clause: Dict[str, Any]) -> List[str]:
        """Identify specific concerns in a clause."""
        concerns = []
        text = clause["text"].lower()
        
        # Check for specific concerning patterns
        if re.search(r"(?i)unlimited|unrestricted", text):
            concerns.append("Overly broad or unlimited scope")
        
        if re.search(r"(?i)perpetual|forever|indefinite", text):
            concerns.append("Indefinite or excessive duration")
        
        if re.search(r"(?i)all.*damages|any.*liability", text):
            concerns.append("Extensive liability or damages")
        
        if re.search(r"(?i)sole.*discretion|absolute.*right", text):
            concerns.append("Unilateral or absolute rights")
        
        if re.search(r"(?i)warrant|represent|guarantee", text):
            concerns.append("Strong warranties or representations")
        
        return concerns
    
    def _identify_compliance_requirements(self, text: str) -> List[Dict[str, Any]]:
        """Identify compliance requirements and regulations."""
        requirements = []
        
        for category, pattern in self.compliance_patterns.items():
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                requirements.append({
                    "category": category,
                    "instances": [
                        {
                            "text": match.group(),
                            "context": text[
                                max(0, match.start() - 50):
                                min(len(text), match.end() + 50)
                            ].strip()
                        }
                        for match in matches
                    ]
                })
        
        return requirements
    
    def _analyze_risk_factors(self, text: str) -> Dict[str, Any]:
        """Analyze various risk factors in the document."""
        return {
            "complexity": self._assess_complexity(text),
            "ambiguity": self._assess_ambiguity(text),
            "enforceability": self._assess_enforceability(text),
            "balance": self._assess_balance(text)
        }
    
    def _assess_complexity(self, text: str) -> Dict[str, Any]:
        """Assess the complexity of the document."""
        sentences = text.split('.')
        return {
            "score": min(1.0, len(text) / 5000),  # Normalize by typical document length
            "factors": {
                "length": len(text),
                "avg_sentence_length": sum(len(s.split()) for s in sentences) / len(sentences),
                "long_sentences": sum(1 for s in sentences if len(s.split()) > 30)
            }
        }
    
    def _assess_ambiguity(self, text: str) -> Dict[str, Any]:
        """Assess ambiguity in the document."""
        ambiguous_terms = [
            r"reasonable",
            r"substantial",
            r"material",
            r"appropriate",
            r"satisfactory",
            r"good faith",
            r"fair"
        ]
        
        findings = []
        for term in ambiguous_terms:
            matches = list(re.finditer(r"\b" + term + r"\b", text, re.IGNORECASE))
            if matches:
                findings.append({
                    "term": term,
                    "count": len(matches),
                    "contexts": [
                        text[max(0, m.start() - 30):min(len(text), m.end() + 30)].strip()
                        for m in matches
                    ]
                })
        
        return {
            "score": min(1.0, len(findings) / 10),  # Normalize by typical number of findings
            "findings": findings
        }
    
    def _assess_enforceability(self, text: str) -> Dict[str, Any]:
        """Assess potential enforceability issues."""
        enforceability_patterns = {
            "jurisdiction": r"(?i)jurisdiction|venue|governing\s+law",
            "severability": r"(?i)sever|severability|invalid|unenforceable",
            "consideration": r"(?i)consideration|exchange|value",
            "capacity": r"(?i)capacity|authority|power|right",
            "consent": r"(?i)consent|agree|accept|approve"
        }
        
        issues = []
        for category, pattern in enforceability_patterns.items():
            if not re.search(pattern, text, re.IGNORECASE):
                issues.append(f"Missing {category} clause")
        
        return {
            "score": max(0, 1 - len(issues) / len(enforceability_patterns)),
            "issues": issues
        }
    
    def _assess_balance(self, text: str) -> Dict[str, Any]:
        """Assess the balance of rights and obligations."""
        party_patterns = {
            "first_party": r"(?i)company|employer|lessor|licensor",
            "second_party": r"(?i)employee|contractor|lessee|licensee"
        }
        
        balance = {
            "first_party": {"obligations": 0, "rights": 0},
            "second_party": {"obligations": 0, "rights": 0}
        }
        
        for party, pattern in party_patterns.items():
            party_mentions = len(re.findall(pattern, text, re.IGNORECASE))
            obligations = len(re.findall(
                r"(?i)shall|must|required|obligation|duty", text[party_mentions:]))
            rights = len(re.findall(
                r"(?i)may|entitled|right|option|discretion", text[party_mentions:]))
            
            if party == "first_party":
                balance["first_party"]["obligations"] = obligations
                balance["first_party"]["rights"] = rights
            else:
                balance["second_party"]["obligations"] = obligations
                balance["second_party"]["rights"] = rights
        
        return {
            "score": min(1.0, abs(
                (balance["first_party"]["rights"] / max(1, balance["first_party"]["obligations"])) -
                (balance["second_party"]["rights"] / max(1, balance["second_party"]["obligations"]))
            )),
            "details": balance
        }
    
    def _analyze_risk_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment in risk-related contexts."""
        blob = TextBlob(text)
        
        # Analyze sentiment specifically around risk-related terms
        risk_contexts = []
        for category in self.risk_patterns.values():
            for pattern in category.values():
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    start = max(0, match.start() - 50)
                    end = min(len(text), match.end() + 50)
                    context = text[start:end]
                    risk_contexts.append(TextBlob(context).sentiment.polarity)
        
        return {
            "overall_sentiment": blob.sentiment.polarity,
            "risk_context_sentiment": sum(risk_contexts) / len(risk_contexts) if risk_contexts else 0,
            "subjectivity": blob.sentiment.subjectivity
        }
    
    def _generate_recommendations(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on risk analysis results."""
        recommendations = []
        
        # High-risk categories
        if analysis_results["risk_categories"]["high_risk"]:
            for risk in analysis_results["risk_categories"]["high_risk"]:
                recommendations.append(
                    f"Review {risk['type']} clause carefully - "
                    f"contains high-risk elements"
                )
        
        # Critical clauses
        for clause in analysis_results["critical_clauses"]:
            if clause["concerns"]:
                recommendations.append(
                    f"Address concerns in {clause['type']} clause: "
                    f"{', '.join(clause['concerns'])}"
                )
        
        # Compliance requirements
        for req in analysis_results["compliance_requirements"]:
            recommendations.append(
                f"Ensure compliance with {req['category']} requirements"
            )
        
        # Risk factors
        if analysis_results["risk_factors"]["complexity"]["score"] > 0.7:
            recommendations.append(
                "Consider simplifying document language and structure"
            )
        
        if analysis_results["risk_factors"]["ambiguity"]["score"] > 0.5:
            recommendations.append(
                "Clarify ambiguous terms and provide specific definitions"
            )
        
        if analysis_results["risk_factors"]["enforceability"]["score"] < 0.7:
            recommendations.append(
                "Add missing essential clauses to improve enforceability"
            )
        
        if analysis_results["risk_factors"]["balance"]["score"] > 0.3:
            recommendations.append(
                "Review rights and obligations to ensure fair balance between parties"
            )
        
        return recommendations 