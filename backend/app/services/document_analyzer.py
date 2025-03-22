from typing import List, Dict, Any
import spacy
from transformers import pipeline
import os
from ..models.document import Document

class DocumentAnalyzer:
    def __init__(self):
        """Initialize the document analyzer with required models."""
        # Load SpaCy model for NER and basic NLP
        self.nlp = spacy.load("en_core_web_sm")
        
        # Initialize transformers pipelines
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        self.classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",
            device=-1  # Use CPU
        )
        
        # Legal clause categories for classification
        self.clause_categories = [
            "non_compete",
            "confidentiality",
            "termination",
            "indemnification",
            "intellectual_property",
            "payment_terms",
            "liability",
            "force_majeure"
        ]
        
        # Risk patterns and keywords
        self.risk_patterns = {
            "ambiguous_terms": ["may", "might", "possibly", "reasonable efforts"],
            "strict_deadlines": ["must", "shall", "within", "no later than"],
            "high_liability": ["unlimited liability", "full responsibility"],
            "termination_risks": ["immediate termination", "without notice"]
        }
        
        # Document type labels
        self.doc_type_labels = [
            "employment contract",
            "non-disclosure agreement",
            "service agreement",
            "lease agreement",
            "sales contract",
            "other"
        ]
        
        # Risk level labels
        self.risk_labels = ["high risk", "medium risk", "low risk"]

    async def analyze(self, content: str) -> Dict[str, Any]:
        """Analyze document content and return structured analysis."""
        # Extract entities
        doc = self.nlp(content)
        entities = []
        for ent in doc.ents:
            entities.append({
                "text": ent.text,
                "type": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char
            })
        
        # Classify document type
        doc_type_result = self.classifier(
            content[:1024],  # Use first 1024 chars for classification
            candidate_labels=self.doc_type_labels,
            multi_label=False
        )
        document_type = doc_type_result["labels"][0]
        
        # Extract key clauses (simplified version)
        sentences = [sent.text.strip() for sent in doc.sents]
        key_clauses = []
        for sent in sentences[:10]:  # Look at first 10 sentences
            # Classify if sentence contains important clause
            clause_result = self.classifier(
                sent,
                candidate_labels=["important clause", "standard text"],
                multi_label=False
            )
            if clause_result["labels"][0] == "important clause" and clause_result["scores"][0] > 0.7:
                key_clauses.append({
                    "type": "key clause",
                    "content": sent
                })
        
        # Analyze risks
        risk_factors = []
        for clause in key_clauses:
            risk_result = self.classifier(
                clause["content"],
                candidate_labels=self.risk_labels,
                multi_label=False
            )
            if risk_result["scores"][0] > 0.6:
                severity = risk_result["labels"][0].split()[0]  # "high", "medium", "low"
                risk_factors.append({
                    "type": "Legal Risk",
                    "description": clause["content"],
                    "severity": severity
                })
        
        # Generate summary (simplified version)
        summary = " ".join(sentences[:3])  # First 3 sentences as summary
        
        return {
            "document_type": document_type,
            "summary": summary,
            "entities": entities,
            "key_clauses": key_clauses,
            "risk_factors": risk_factors,
            "metadata": {
                "entity_count": len(entities),
                "clause_count": len(key_clauses),
                "risk_count": len(risk_factors)
            }
        }

    async def _generate_summary(self, text: str) -> str:
        """Generate a concise summary of the document."""
        # Split text into chunks if it's too long
        max_length = 1024
        chunks = [text[i:i + max_length] for i in range(0, len(text), max_length)]
        
        summaries = []
        for chunk in chunks:
            summary = self.summarizer(chunk, max_length=150, min_length=50, do_sample=False)
            summaries.append(summary[0]['summary_text'])
        
        return " ".join(summaries)

    async def _extract_clauses(self, doc) -> List[Dict[str, Any]]:
        """Extract and classify key clauses from the document."""
        clauses = []
        
        # Split into sentences and analyze each for clause classification
        for sent in doc.sents:
            # Classify the sentence against clause categories
            classification = self.classifier(
                sent.text,
                candidate_labels=self.clause_categories,
                multi_label=True
            )
            
            # If confidence is high enough, add as a clause
            if max(classification['scores']) > 0.7:
                clauses.append({
                    "type": classification['labels'][0],
                    "content": sent.text,
                    "confidence": classification['scores'][0]
                })
        
        return clauses

    async def _identify_risks(self, doc) -> List[Dict[str, Any]]:
        """Identify potential risks in the document."""
        risks = []
        
        # Analyze each sentence for risk patterns
        for sent in doc.sents:
            sent_text = sent.text.lower()
            
            for risk_type, patterns in self.risk_patterns.items():
                for pattern in patterns:
                    if pattern.lower() in sent_text:
                        risks.append({
                            "type": risk_type,
                            "description": sent.text,
                            "pattern_matched": pattern,
                            "severity": self._calculate_risk_severity(sent_text)
                        })
        
        return risks

    async def _extract_entities(self, doc) -> Dict[str, List[str]]:
        """Extract named entities from the document."""
        entities = {
            "organizations": [],
            "people": [],
            "dates": [],
            "money": [],
            "locations": []
        }
        
        for ent in doc.ents:
            if ent.label_ == "ORG":
                entities["organizations"].append(ent.text)
            elif ent.label_ == "PERSON":
                entities["people"].append(ent.text)
            elif ent.label_ == "DATE":
                entities["dates"].append(ent.text)
            elif ent.label_ == "MONEY":
                entities["money"].append(ent.text)
            elif ent.label_ == "GPE":
                entities["locations"].append(ent.text)
        
        # Remove duplicates and keep order
        for key in entities:
            entities[key] = list(dict.fromkeys(entities[key]))
        
        return entities

    def _calculate_risk_severity(self, text: str) -> str:
        """Calculate risk severity based on language and context."""
        # Simple severity calculation based on keyword presence
        high_severity = ["must", "shall", "immediately", "terminate", "liable"]
        medium_severity = ["may", "should", "reasonable", "efforts"]
        
        text_lower = text.lower()
        severity_score = 0
        
        for word in high_severity:
            if word in text_lower:
                severity_score += 2
                
        for word in medium_severity:
            if word in text_lower:
                severity_score += 1
        
        if severity_score >= 3:
            return "high"
        elif severity_score >= 1:
            return "medium"
        else:
            return "low" 