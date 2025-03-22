import spacy
from typing import List, Dict, Any
import re
from textblob import TextBlob
from collections import Counter
import textstat

class NLPPipeline:
    """Natural Language Processing pipeline for legal document analysis."""
    
    def __init__(self):
        """Initialize NLP models and resources."""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")
        
        # Legal-specific patterns
        self.legal_patterns = {
            "obligation": r"(?i)shall|must|will|required to|obligated to",
            "prohibition": r"(?i)shall not|must not|will not|prohibited|forbidden",
            "permission": r"(?i)may|permitted to|allowed to",
            "definition": r"(?i)means|refers to|is defined as|shall mean",
            "condition": r"(?i)if|provided that|subject to|conditional upon",
            "exception": r"(?i)except|unless|excluding|other than",
            "temporal": r"(?i)within|after|before|during|upon|following",
            "termination": r"(?i)terminate|termination|cancel|cancellation|end|expire",
            "amendment": r"(?i)amend|modify|change|alter|revise",
            "indemnification": r"(?i)indemnify|indemnification|hold harmless|reimburse",
            "warranty": r"(?i)warrant|represent|guarantee|assure",
            "confidentiality": r"(?i)confidential|proprietary|trade secret|non-disclosure",
            "governing_law": r"(?i)govern|jurisdiction|applicable law|venue",
            "severability": r"(?i)sever|invalid|unenforceable|void",
            "force_majeure": r"(?i)force majeure|act of god|beyond.*control",
            "assignment": r"(?i)assign|transfer|delegate",
            "notice": r"(?i)notice|notify|notification|inform",
            "payment": r"(?i)pay|payment|compensation|fee|amount",
            "intellectual_property": r"(?i)intellectual property|patent|copyright|trademark",
            "dispute_resolution": r"(?i)dispute|arbitration|mediation|litigation"
        }
    
    def analyze_document(self, text: str) -> Dict[str, Any]:
        """
        Perform comprehensive NLP analysis on the document.
        Returns various analysis results including entities, key phrases, etc.
        """
        doc = self.nlp(text)
        
        return {
            "key_phrases": self._extract_key_phrases(doc),
            "legal_entities": self._extract_legal_entities(doc),
            "clause_analysis": self._analyze_clauses(text),
            "sentiment_analysis": self._analyze_sentiment(text),
            "readability_metrics": self._calculate_readability(text),
            "key_terms": self._extract_key_terms(doc),
            "legal_patterns": self._identify_legal_patterns(text),
            "section_hierarchy": self._extract_section_hierarchy(text),
            "cross_references": self._find_cross_references(text),
            "defined_terms": self._extract_defined_terms(text)
        }
    
    def _extract_key_phrases(self, doc) -> List[Dict[str, Any]]:
        """Extract important phrases and their context."""
        key_phrases = []
        
        for sent in doc.sents:
            # Look for noun phrases that might be important
            for chunk in sent.noun_chunks:
                if len(chunk.text.split()) >= 2:  # Only phrases with 2+ words
                    key_phrases.append({
                        "text": chunk.text,
                        "type": "NOUN_PHRASE",
                        "context": sent.text
                    })
        
        return key_phrases
    
    def _extract_legal_entities(self, doc) -> Dict[str, List[str]]:
        """Extract and categorize legal entities."""
        entities = {
            "PERSON": [],
            "ORG": [],
            "DATE": [],
            "MONEY": [],
            "GPE": [],  # Geo-political entities
            "LAW": []   # Legal references
        }
        
        for ent in doc.ents:
            if ent.label_ in entities:
                if ent.text not in entities[ent.label_]:
                    entities[ent.label_].append(ent.text)
        
        return entities
    
    def _analyze_clauses(self, text: str) -> List[Dict[str, Any]]:
        """Analyze individual clauses and their characteristics."""
        clauses = []
        
        # Split into paragraphs/sections
        paragraphs = text.split('\n\n')
        
        for para in paragraphs:
            if len(para.strip()) > 0:
                # Analyze the clause
                clause_type = self._determine_clause_type(para)
                sentiment = TextBlob(para).sentiment
                
                clauses.append({
                    "text": para.strip(),
                    "type": clause_type,
                    "sentiment": {
                        "polarity": sentiment.polarity,
                        "subjectivity": sentiment.subjectivity
                    },
                    "patterns": self._identify_legal_patterns(para)
                })
        
        return clauses
    
    def _determine_clause_type(self, text: str) -> str:
        """Determine the type of a legal clause."""
        text_lower = text.lower()
        
        # Check for various clause types
        if any(pattern in text_lower for pattern in ["shall", "must", "will"]):
            return "OBLIGATION"
        elif any(pattern in text_lower for pattern in ["shall not", "must not", "prohibited"]):
            return "PROHIBITION"
        elif any(pattern in text_lower for pattern in ["may", "permitted", "allowed"]):
            return "PERMISSION"
        elif any(pattern in text_lower for pattern in ["means", "shall mean", "defined as"]):
            return "DEFINITION"
        elif "notwithstanding" in text_lower or "provided that" in text_lower:
            return "CONDITION"
        elif "terminate" in text_lower or "termination" in text_lower:
            return "TERMINATION"
        else:
            return "STATEMENT"
    
    def _analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment and tone of the document."""
        blob = TextBlob(text)
        
        return {
            "overall_polarity": blob.sentiment.polarity,
            "overall_subjectivity": blob.sentiment.subjectivity,
            "sentence_sentiments": [
                {"text": str(sent), "polarity": sent.sentiment.polarity}
                for sent in blob.sentences
            ]
        }
    
    def _calculate_readability(self, text: str) -> Dict[str, float]:
        """Calculate various readability metrics."""
        return {
            "flesch_reading_ease": textstat.flesch_reading_ease(text),
            "flesch_kincaid_grade": textstat.flesch_kincaid_grade(text),
            "gunning_fog": textstat.gunning_fog(text),
            "smog_index": textstat.smog_index(text),
            "automated_readability_index": textstat.automated_readability_index(text),
            "coleman_liau_index": textstat.coleman_liau_index(text),
            "linsear_write_formula": textstat.linsear_write_formula(text),
            "dale_chall_readability_score": textstat.dale_chall_readability_score(text)
        }
    
    def _extract_key_terms(self, doc) -> List[Dict[str, Any]]:
        """Extract and rank key terms from the document."""
        # Count term frequencies
        term_freq = Counter()
        
        for token in doc:
            if (not token.is_stop and not token.is_punct and 
                not token.is_space and len(token.text) > 1):
                term_freq[token.text.lower()] += 1
        
        # Get most common terms
        key_terms = []
        for term, freq in term_freq.most_common(20):
            key_terms.append({
                "term": term,
                "frequency": freq,
                "pos_tag": next((token.pos_ for token in doc if token.text.lower() == term), None)
            })
        
        return key_terms
    
    def _identify_legal_patterns(self, text: str) -> Dict[str, List[str]]:
        """Identify common legal patterns and phrases."""
        patterns_found = {}
        
        for pattern_name, pattern in self.legal_patterns.items():
            matches = re.finditer(pattern, text)
            if matches:
                patterns_found[pattern_name] = [
                    text[max(0, match.start() - 50):min(len(text), match.end() + 50)]
                    for match in matches
                ]
        
        return patterns_found
    
    def _extract_section_hierarchy(self, text: str) -> List[Dict[str, Any]]:
        """Extract document section hierarchy."""
        sections = []
        
        # Match different section numbering patterns
        patterns = [
            (r'(?m)^\s*(\d+\.)\s+([^\n]+)', 'NUMERIC'),
            (r'(?m)^\s*([A-Z]\.)\s+([^\n]+)', 'ALPHABETIC'),
            (r'(?m)^\s*([IVX]+\.)\s+([^\n]+)', 'ROMAN'),
            (r'(?m)^\s*(\d+\.\d+)\s+([^\n]+)', 'SUBSECTION')
        ]
        
        for pattern, section_type in patterns:
            for match in re.finditer(pattern, text):
                sections.append({
                    "number": match.group(1),
                    "title": match.group(2),
                    "type": section_type,
                    "level": len(match.group(1).split('.'))
                })
        
        return sorted(sections, key=lambda x: x["number"])
    
    def _find_cross_references(self, text: str) -> List[Dict[str, str]]:
        """Find cross-references between sections."""
        references = []
        
        # Pattern for matching section references
        ref_pattern = r'(?i)(section|clause|paragraph)\s+(\d+(\.\d+)?)'
        
        for match in re.finditer(ref_pattern, text):
            context = text[max(0, match.start() - 50):min(len(text), match.end() + 50)]
            references.append({
                "type": match.group(1),
                "reference": match.group(2),
                "context": context.strip()
            })
        
        return references
    
    def _extract_defined_terms(self, text: str) -> List[Dict[str, Any]]:
        """Extract defined terms and their definitions."""
        defined_terms = []
        
        # Pattern for matching defined terms
        term_pattern = r'"([^"]+)"\s+(?:means|shall mean|refers to|is defined as)\s+([^.]+)'
        
        for match in re.finditer(term_pattern, text):
            defined_terms.append({
                "term": match.group(1),
                "definition": match.group(2).strip(),
                "context": text[max(0, match.start() - 30):min(len(text), match.end() + 30)]
            })
        
        return defined_terms 