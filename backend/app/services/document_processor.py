import io
from typing import List, Dict, Any, Tuple
import PyPDF2
from docx import Document
import pytesseract
from PIL import Image
import spacy
import re
from datetime import datetime
from transformers import AutoTokenizer, AutoModel, pipeline
import fitz  # PyMuPDF
import docx
import torch
import textstat
from textblob import TextBlob

class DocumentProcessor:
    """Handles document uploads and text extraction from various file formats."""
    
    def __init__(self):
        """Initialize the document processor with necessary models and configurations."""
        # Initialize NLP models
        self.nlp = spacy.load("en_core_web_sm")
        
        # Initialize transformers
        self.tokenizer = AutoTokenizer.from_pretrained("nlpaueb/legal-bert-base-uncased")
        self.model = AutoModel.from_pretrained("nlpaueb/legal-bert-base-uncased")
        
        # Initialize summarization pipeline
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    
    async def process_document(self, file) -> Tuple[str, Dict[str, Any]]:
        """
        Process uploaded document and extract text and metadata.
        Returns tuple of (processed_text, metadata).
        """
        # Extract text from document
        raw_text = await self.extract_text(file)
        
        # Preprocess the text
        processed_text = self.preprocess_text(raw_text)
        
        # Extract metadata
        metadata = self.extract_metadata(processed_text)
        
        return processed_text, metadata
    
    async def extract_text(self, file) -> str:
        """
        Extract text from uploaded file based on its format.
        Supports PDF, DOCX, TXT, and common image formats.
        """
        content = await file.read()
        filename = file.filename.lower()
        
        if filename.endswith('.pdf'):
            return self._extract_from_pdf(content)
        elif filename.endswith('.docx'):
            return self._extract_from_docx(content)
        elif filename.endswith('.txt'):
            return content.decode('utf-8')
        elif any(filename.endswith(ext) for ext in ['.png', '.jpg', '.jpeg']):
            return self._extract_from_image(content)
        else:
            raise ValueError(f"Unsupported file format: {filename}")
    
    def _extract_from_pdf(self, content: bytes) -> str:
        """Extract text from PDF file."""
        pdf_file = io.BytesIO(content)
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    
    def _extract_from_docx(self, content: bytes) -> str:
        """Extract text from DOCX file."""
        doc_file = io.BytesIO(content)
        doc = Document(doc_file)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])
    
    def _extract_from_image(self, content: bytes) -> str:
        """Extract text from image using OCR."""
        image = Image.open(io.BytesIO(content))
        return pytesseract.image_to_string(image)
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocess extracted text:
        - Remove extra whitespace
        - Fix common OCR errors
        - Normalize text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Fix common OCR errors
        text = text.replace('|', 'I')  # Common OCR error
        text = text.replace('0', 'O')  # Common OCR error in legal docs
        
        # Process with spaCy for better text normalization
        doc = self.nlp(text)
        return doc.text
    
    def extract_metadata(self, text: str) -> Dict[str, Any]:
        """
        Extract metadata from document text:
        - Dates
        - Organizations
        - People
        - Sections
        - Monetary values
        """
        doc = self.nlp(text)
        
        # Extract entities
        entities = {
            "dates": [],
            "organizations": [],
            "people": [],
            "monetary_values": []
        }
        
        for ent in doc.ents:
            if ent.label_ == "DATE":
                entities["dates"].append(ent.text)
            elif ent.label_ == "ORG":
                entities["organizations"].append(ent.text)
            elif ent.label_ == "PERSON":
                entities["people"].append(ent.text)
            elif ent.label_ == "MONEY":
                entities["monetary_values"].append(ent.text)
        
        # Extract sections
        sections = []
        section_pattern = re.compile(r'^(?:Section|SECTION|Article|ARTICLE)\s+\d+', re.MULTILINE)
        for match in section_pattern.finditer(text):
            sections.append(match.group())
        
        # Detect document type
        doc_type = self.detect_document_type(text)
        
        return {
            "entities": entities,
            "sections": sections,
            "document_type": doc_type,
            "processed_date": datetime.utcnow().isoformat(),
            "word_count": len(text.split()),
            "has_signatures": bool(re.search(r'signature|signed|executed', text, re.IGNORECASE))
        }
    
    def detect_document_type(self, text: str) -> str:
        """Detect the type of legal document based on content."""
        text_lower = text.lower()
        
        # Common document type patterns
        doc_types = {
            "CONTRACT": r"\bcontract\b|\bagreement\b",
            "POLICY": r"\bpolicy\b|\bguidelines\b",
            "TERMS_AND_CONDITIONS": r"terms\s+and\s+conditions|terms\s+of\s+service",
            "PRIVACY_POLICY": r"privacy\s+policy|data\s+protection",
            "EMPLOYMENT_AGREEMENT": r"employment\s+agreement|employment\s+contract",
            "NDA": r"non.?disclosure|confidentiality\s+agreement",
            "LICENSE_AGREEMENT": r"license\s+agreement|software\s+license",
            "SERVICE_AGREEMENT": r"service\s+agreement|professional\s+services",
            "LEASE_AGREEMENT": r"lease\s+agreement|rental\s+agreement"
        }
        
        # Check each pattern
        for doc_type, pattern in doc_types.items():
            if re.search(pattern, text_lower):
                return doc_type
        
        return "OTHER"
    
    def validate_document(self, text: str) -> Dict[str, Any]:
        """
        Validate document structure and content.
        Returns validation results and any issues found.
        """
        issues = []
        
        # Check for minimum content
        if len(text.split()) < 100:
            issues.append("Document appears too short")
        
        # Check for section numbering
        if not re.search(r'^(?:Section|SECTION|Article|ARTICLE)\s+\d+', text, re.MULTILINE):
            issues.append("Missing section numbering")
        
        # Check for signature blocks
        if not re.search(r'signature|signed|executed', text, re.IGNORECASE):
            issues.append("Missing signature block")
        
        # Check for dates
        if not re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', text):
            issues.append("Missing dates")
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "structure_score": 1.0 - (len(issues) * 0.2)  # Simple scoring
        }

    def analyze_document(self, text: str) -> dict:
        """Perform comprehensive document analysis."""
        # Basic text statistics
        stats = {
            'word_count': len(text.split()),
            'sentence_count': textstat.sentence_count(text),
            'reading_level': textstat.flesch_kincaid_grade(text),
            'reading_time': len(text.split()) / 200  # Average reading speed
        }

        # Generate summary
        summary = self._generate_summary(text)

        # Extract entities
        entities = self._extract_entities(text)

        # Identify key clauses
        clauses = self._identify_key_clauses(text)

        # Analyze risks
        risks = self._analyze_risks(text)

        # Sentiment analysis
        sentiment = self._analyze_sentiment(text)

        return {
            'statistics': stats,
            'summary': summary,
            'entities': entities,
            'key_clauses': clauses,
            'risks': risks,
            'sentiment': sentiment
        }

    def _generate_summary(self, text: str) -> str:
        """Generate a concise summary of the document."""
        # Split text into chunks if it's too long
        max_chunk_length = 1024
        chunks = [text[i:i + max_chunk_length] for i in range(0, len(text), max_chunk_length)]
        
        summaries = []
        for chunk in chunks:
            if len(chunk.strip()) > 100:  # Only summarize substantial chunks
                summary = self.summarizer(chunk, max_length=130, min_length=30, do_sample=False)
                summaries.append(summary[0]['summary_text'])
        
        return " ".join(summaries)

    def _extract_entities(self, text: str) -> dict:
        """Extract named entities from the document."""
        doc = self.nlp(text)
        entities = {}
        
        for ent in doc.ents:
            if ent.label_ not in entities:
                entities[ent.label_] = []
            if ent.text not in entities[ent.label_]:
                entities[ent.label_].append(ent.text)
        
        return entities

    def _identify_key_clauses(self, text: str) -> list:
        """Identify important legal clauses in the document."""
        important_keywords = [
            "shall", "must", "will", "agree", "terminate", "liability",
            "warranty", "indemnify", "confidential", "intellectual property",
            "governing law", "jurisdiction", "force majeure"
        ]
        
        doc = self.nlp(text)
        clauses = []
        
        for sent in doc.sents:
            for keyword in important_keywords:
                if keyword in sent.text.lower():
                    clauses.append({
                        'type': keyword,
                        'text': sent.text.strip()
                    })
                    break
        
        return clauses

    def _analyze_risks(self, text: str) -> list:
        """Identify potential legal risks in the document."""
        risk_patterns = [
            {
                'pattern': "terminate",
                'category': "Termination Risk",
                'severity': "high"
            },
            {
                'pattern': "liability",
                'category': "Liability Risk",
                'severity': "high"
            },
            {
                'pattern': "confidential",
                'category': "Confidentiality Risk",
                'severity': "medium"
            },
            {
                'pattern': "penalty",
                'category': "Financial Risk",
                'severity': "high"
            },
            {
                'pattern': "lawsuit",
                'category': "Legal Risk",
                'severity': "high"
            },
            {
                'pattern': "breach",
                'category': "Compliance Risk",
                'severity': "high"
            }
        ]
        
        doc = self.nlp(text.lower())
        risks = []
        
        for sent in doc.sents:
            for pattern in risk_patterns:
                if pattern['pattern'] in sent.text:
                    risks.append({
                        'category': pattern['category'],
                        'severity': pattern['severity'],
                        'context': sent.text.strip()
                    })
        
        return risks

    def _analyze_sentiment(self, text: str) -> dict:
        """Analyze the sentiment of the document."""
        blob = TextBlob(text)
        
        return {
            'polarity': blob.sentiment.polarity,
            'subjectivity': blob.sentiment.subjectivity
        }

# Initialize the document processor
document_processor = DocumentProcessor() 