import pytest
from ..app.services.document_processor import DocumentProcessor
from ..app.services.nlp_pipeline import NLPPipeline
from ..app.services.risk_analyzer import RiskAnalyzer
from ..app.services.document_classifier import DocumentClassifier
from ..app.services.document_summarizer import DocumentSummarizer

# Sample test document
SAMPLE_DOCUMENT = """
EMPLOYMENT AGREEMENT

This Employment Agreement (the "Agreement") is made and entered into as of January 1, 2024,
by and between Company XYZ ("Employer") and John Doe ("Employee").

1. POSITION AND DUTIES
   Employee shall be employed as Senior Software Engineer and shall perform such duties
   as are regularly and customarily performed by such position.

2. COMPENSATION
   Employer agrees to pay Employee an annual salary of $120,000, payable in accordance
   with Employer's regular payroll practices.

3. TERM AND TERMINATION
   This Agreement shall commence on January 1, 2024 and continue until terminated by
   either party with 30 days written notice.

4. CONFIDENTIALITY
   Employee agrees to maintain the confidentiality of all proprietary information
   and trade secrets of the Employer.
"""

@pytest.fixture
def document_processor():
    return DocumentProcessor()

@pytest.fixture
def nlp_pipeline():
    return NLPPipeline()

@pytest.fixture
def risk_analyzer():
    return RiskAnalyzer()

@pytest.fixture
def document_classifier():
    return DocumentClassifier()

@pytest.fixture
def document_summarizer():
    return DocumentSummarizer()

def test_document_classification(document_classifier):
    """Test document type classification."""
    result = document_classifier.classify_document(SAMPLE_DOCUMENT)
    
    assert result["primary_type"] == "EMPLOYMENT_AGREEMENT"
    assert result["confidence_score"] >= 0.7
    assert len(result["alternative_types"]) > 0
    assert "document_structure" in result

def test_document_summarization(document_summarizer):
    """Test document summarization."""
    result = document_summarizer.generate_summary(SAMPLE_DOCUMENT)
    
    assert "executive_summary" in result
    assert len(result["executive_summary"]) > 0
    assert len(result["key_points"]) > 0
    assert len(result["section_summaries"]) > 0
    assert len(result["important_clauses"]) > 0

def test_risk_analysis(risk_analyzer, nlp_pipeline):
    """Test risk analysis."""
    # First get clause analysis from NLP pipeline
    nlp_results = nlp_pipeline.analyze_document(SAMPLE_DOCUMENT)
    result = risk_analyzer.analyze_risks(SAMPLE_DOCUMENT, nlp_results["clause_analysis"])
    
    assert 0 <= result["overall_risk_score"] <= 1
    assert len(result["risk_categories"]) > 0
    assert len(result["critical_clauses"]) > 0
    assert len(result["compliance_requirements"]) > 0
    assert len(result["recommendations"]) > 0

def test_nlp_pipeline(nlp_pipeline):
    """Test NLP analysis."""
    result = nlp_pipeline.analyze_document(SAMPLE_DOCUMENT)
    
    assert "key_phrases" in result
    assert "legal_entities" in result
    assert "clause_analysis" in result
    assert "sentiment_analysis" in result
    assert "readability_metrics" in result
    assert "key_terms" in result

def test_document_processor(document_processor):
    """Test document text extraction and preprocessing."""
    # Create a mock file-like object
    class MockFile:
        async def read(self):
            return SAMPLE_DOCUMENT.encode('utf-8')
        
        @property
        def filename(self):
            return "test.txt"
    
    async def test():
        mock_file = MockFile()
        content = await document_processor.extract_text(mock_file)
        assert len(content) > 0
        assert "EMPLOYMENT AGREEMENT" in content
    
    import asyncio
    asyncio.run(test())

def test_risk_score_calculation(risk_analyzer):
    """Test risk score calculation."""
    high_risk_text = """
    CONFIDENTIALITY AND NON-COMPETE AGREEMENT
    Employee shall not disclose confidential information and shall not compete
    for a period of 5 years. Liquidated damages for breach shall be $1,000,000.
    """
    
    low_risk_text = """
    GENERAL INFORMATION
    This document provides basic information about company policies.
    Please refer to the employee handbook for more details.
    """
    
    # Test with high-risk document
    high_risk_result = risk_analyzer.analyze_risks(
        high_risk_text,
        [{"text": high_risk_text, "type": "STATEMENT"}]
    )
    
    # Test with low-risk document
    low_risk_result = risk_analyzer.analyze_risks(
        low_risk_text,
        [{"text": low_risk_text, "type": "STATEMENT"}]
    )
    
    assert high_risk_result["overall_risk_score"] > low_risk_result["overall_risk_score"]

def test_entity_extraction(nlp_pipeline):
    """Test legal entity extraction."""
    result = nlp_pipeline.analyze_document(SAMPLE_DOCUMENT)
    entities = result["legal_entities"]
    
    assert "Company XYZ" in str(entities)
    assert "John Doe" in str(entities)
    assert "$120,000" in str(entities)
    assert "January 1, 2024" in str(entities)

def test_clause_importance(document_summarizer):
    """Test clause importance assessment."""
    result = document_summarizer.generate_summary(SAMPLE_DOCUMENT)
    important_clauses = result["important_clauses"]
    
    # Confidentiality clause should be identified as important
    confidentiality_found = any(
        "confidentiality" in clause["text"].lower()
        for clause in important_clauses
    )
    assert confidentiality_found

def test_document_structure_analysis(document_classifier):
    """Test document structure analysis."""
    result = document_classifier.classify_document(SAMPLE_DOCUMENT)
    structure = result["document_structure"]
    
    assert structure["has_numbering"]
    assert structure["has_headers"]
    assert structure["total_sections"] >= 4  # Our sample has 4 numbered sections 