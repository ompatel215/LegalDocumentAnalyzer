from typing import List, Dict, Any
import re
from collections import defaultdict
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

class DocumentSummarizer:
    def __init__(self):
        """Initialize document summarizer with necessary models."""
        self.nlp = spacy.load("en_core_web_sm")
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english'
        )
        
        # Important legal phrases that should be included in summaries
        self.important_phrases = [
            "agrees to", "shall", "must", "will",
            "represents and warrants", "subject to",
            "in accordance with", "notwithstanding",
            "hereby", "pursuant to"
        ]

    def generate_summary(self, text: str, max_length: int = 1000) -> Dict[str, Any]:
        """
        Generate a hierarchical summary of the document.
        Returns executive summary and detailed section summaries.
        """
        # Process the document
        doc = self.nlp(text)
        
        # Generate different levels of summary
        result = {
            "executive_summary": self._generate_executive_summary(doc),
            "key_points": self._extract_key_points(doc),
            "section_summaries": self._generate_section_summaries(doc),
            "important_clauses": self._extract_important_clauses(doc),
            "metadata": self._extract_summary_metadata(doc)
        }
        
        return result

    def _generate_executive_summary(self, doc) -> str:
        """Generate a brief executive summary."""
        # Get the most important sentences
        sentences = list(doc.sents)
        sentence_scores = self._score_sentences(sentences)
        
        # Select top sentences for executive summary
        top_sentences = sorted(
            [(sent, score) for sent, score in sentence_scores.items()],
            key=lambda x: x[1],
            reverse=True
        )[:5]  # Take top 5 sentences
        
        # Order sentences by their original position
        ordered_sentences = sorted(
            top_sentences,
            key=lambda x: sentences.index(x[0])
        )
        
        # Combine sentences into a coherent summary
        summary = " ".join(sent.text for sent, _ in ordered_sentences)
        
        return summary

    def _extract_key_points(self, doc) -> List[Dict[str, Any]]:
        """Extract key points from the document."""
        key_points = []
        
        for sent in doc.sents:
            # Score the sentence for importance
            importance_score = self._calculate_sentence_importance(sent)
            
            if importance_score > 0.5:  # Only include important points
                key_points.append({
                    "text": sent.text,
                    "importance": importance_score,
                    "category": self._categorize_point(sent)
                })
        
        # Sort by importance and take top 10
        key_points.sort(key=lambda x: x["importance"], reverse=True)
        return key_points[:10]

    def _generate_section_summaries(self, doc) -> List[Dict[str, Any]]:
        """Generate summaries for each major section."""
        # Split into sections based on headers
        sections = self._split_into_sections(doc)
        
        section_summaries = []
        for section in sections:
            if len(section["content"]) > 0:
                summary = self._summarize_section(section["content"])
                section_summaries.append({
                    "title": section["title"],
                    "summary": summary,
                    "key_terms": self._extract_key_terms(section["content"])
                })
        
        return section_summaries

    def _extract_important_clauses(self, doc) -> List[Dict[str, Any]]:
        """Extract and summarize important clauses."""
        important_clauses = []
        
        for sent in doc.sents:
            if self._is_important_clause(sent):
                clause = {
                    "text": sent.text,
                    "type": self._determine_clause_type(sent),
                    "entities": self._extract_clause_entities(sent),
                    "importance": self._calculate_sentence_importance(sent)
                }
                important_clauses.append(clause)
        
        return sorted(
            important_clauses,
            key=lambda x: x["importance"],
            reverse=True
        )[:10]  # Return top 10 important clauses

    def _score_sentences(self, sentences) -> Dict:
        """Score sentences based on importance."""
        scores = {}
        
        # Create TF-IDF matrix
        sentence_texts = [sent.text.lower() for sent in sentences]
        tfidf_matrix = self.vectorizer.fit_transform(sentence_texts)
        
        # Calculate sentence scores
        for i, sent in enumerate(sentences):
            # Base score from TF-IDF
            score = np.mean(tfidf_matrix[i].toarray())
            
            # Adjust score based on various factors
            score += self._calculate_position_score(i, len(sentences))
            score += self._calculate_phrase_score(sent)
            score += self._calculate_entity_score(sent)
            
            scores[sent] = score
        
        return scores

    def _calculate_position_score(self, position: int, total: int) -> float:
        """Calculate score based on sentence position."""
        if position == 0:  # First sentence
            return 0.3
        elif position == total - 1:  # Last sentence
            return 0.2
        elif position < total * 0.1:  # First 10%
            return 0.1
        return 0.0

    def _calculate_phrase_score(self, sent) -> float:
        """Calculate score based on important phrases."""
        score = 0.0
        text_lower = sent.text.lower()
        
        for phrase in self.important_phrases:
            if phrase in text_lower:
                score += 0.1
        
        return min(0.5, score)  # Cap at 0.5

    def _calculate_entity_score(self, sent) -> float:
        """Calculate score based on named entities."""
        return min(0.3, len([ent for ent in sent.ents]) * 0.1)

    def _split_into_sections(self, doc) -> List[Dict[str, Any]]:
        """Split document into sections based on headers."""
        sections = []
        current_section = {"title": "Introduction", "content": []}
        
        for sent in doc.sents:
            if self._is_header(sent):
                if current_section["content"]:
                    sections.append(current_section)
                current_section = {
                    "title": sent.text.strip(),
                    "content": []
                }
            else:
                current_section["content"].append(sent)
        
        if current_section["content"]:
            sections.append(current_section)
        
        return sections

    def _is_header(self, sent) -> bool:
        """Check if sentence is a section header."""
        text = sent.text.strip()
        return (
            text.isupper() or
            re.match(r'^\d+\.\s+[A-Z]', text) or
            (len(text.split()) <= 5 and text[0].isupper())
        )

    def _summarize_section(self, sentences: List) -> str:
        """Generate summary for a section."""
        if not sentences:
            return ""
        
        # Score sentences
        scores = self._score_sentences(sentences)
        
        # Select top sentences
        num_sentences = max(1, len(sentences) // 5)  # 20% of original
        top_sentences = sorted(
            [(sent, score) for sent, score in scores.items()],
            key=lambda x: x[1],
            reverse=True
        )[:num_sentences]
        
        # Order by original position
        ordered_sentences = sorted(
            top_sentences,
            key=lambda x: sentences.index(x[0])
        )
        
        return " ".join(sent.text for sent, _ in ordered_sentences)

    def _extract_key_terms(self, sentences: List) -> List[Dict[str, str]]:
        """Extract key terms from a section."""
        text = " ".join(sent.text for sent in sentences)
        doc = self.nlp(text)
        
        terms = defaultdict(int)
        for chunk in doc.noun_chunks:
            if not chunk.root.is_stop and len(chunk.text.split()) <= 3:
                terms[chunk.text.lower()] += 1
        
        return [
            {"term": term, "frequency": freq}
            for term, freq in sorted(
                terms.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]  # Top 5 terms
        ]

    def _is_important_clause(self, sent) -> bool:
        """Determine if a sentence contains an important clause."""
        text_lower = sent.text.lower()
        
        # Check for important legal phrases
        if any(phrase in text_lower for phrase in self.important_phrases):
            return True
        
        # Check for obligations or requirements
        if any(word in text_lower for word in ["shall", "must", "will", "agrees"]):
            return True
        
        # Check for conditions or exceptions
        if any(word in text_lower for word in ["if", "unless", "except", "provided"]):
            return True
        
        return False

    def _determine_clause_type(self, sent) -> str:
        """Determine the type of clause."""
        text_lower = sent.text.lower()
        
        if "shall" in text_lower or "must" in text_lower:
            return "OBLIGATION"
        elif "may" in text_lower:
            return "PERMISSION"
        elif "will not" in text_lower or "shall not" in text_lower:
            return "PROHIBITION"
        elif "if" in text_lower:
            return "CONDITION"
        else:
            return "STATEMENT"

    def _extract_clause_entities(self, sent) -> Dict[str, List[str]]:
        """Extract named entities from a clause."""
        entities = defaultdict(list)
        
        for ent in sent.ents:
            if ent.text not in entities[ent.label_]:
                entities[ent.label_].append(ent.text)
        
        return dict(entities)

    def _calculate_sentence_importance(self, sent) -> float:
        """Calculate overall importance score for a sentence."""
        score = 0.0
        
        # Check for important phrases
        score += self._calculate_phrase_score(sent)
        
        # Check for named entities
        score += self._calculate_entity_score(sent)
        
        # Check for numerical values
        if any(token.like_num for token in sent):
            score += 0.1
        
        # Check for legal references
        if re.search(r'section|article|clause|paragraph', sent.text.lower()):
            score += 0.1
        
        return min(1.0, score)

    def _extract_summary_metadata(self, doc) -> Dict[str, Any]:
        """Extract metadata about the summary."""
        return {
            "original_length": len(doc.text),
            "summary_ratio": len(self._generate_executive_summary(doc)) / len(doc.text),
            "key_entities": self._extract_key_entities(doc),
            "document_stats": {
                "sentences": len(list(doc.sents)),
                "words": len([token for token in doc if not token.is_punct]),
                "entities": len(list(doc.ents))
            }
        }

    def _extract_key_entities(self, doc) -> Dict[str, List[str]]:
        """Extract key named entities from the document."""
        entities = defaultdict(list)
        
        for ent in doc.ents:
            if len(entities[ent.label_]) < 5:  # Limit to top 5 per category
                if ent.text not in entities[ent.label_]:
                    entities[ent.label_].append(ent.text)
        
        return dict(entities)

    def _categorize_point(self, sent) -> str:
        """Categorize the type of key point."""
        text_lower = sent.text.lower()
        
        if any(word in text_lower for word in ["shall", "must", "will", "agrees"]):
            return "OBLIGATION"
        elif any(word in text_lower for word in ["represents", "warrants", "acknowledges"]):
            return "REPRESENTATION"
        elif any(word in text_lower for word in ["terminate", "cancel", "end"]):
            return "TERMINATION"
        elif any(word in text_lower for word in ["pay", "payment", "fee", "cost"]):
            return "PAYMENT"
        else:
            return "GENERAL" 