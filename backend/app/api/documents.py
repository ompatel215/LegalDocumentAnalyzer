from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from motor.motor_asyncio import AsyncIOMotorClient
from ..core.database import get_db
from ..core.security import oauth2_scheme, get_current_user_id
from ..models.document import Document
from ..services.document_analyzer import DocumentAnalyzer
from ..services.document_processor import DocumentProcessor
from ..services.nlp_pipeline import NLPPipeline
from ..services.risk_analyzer import RiskAnalyzer
from ..services.document_classifier import DocumentClassifier
from ..services.document_summarizer import DocumentSummarizer
from datetime import datetime, timedelta
from bson import ObjectId
import io
from typing import List

router = APIRouter()
document_analyzer = DocumentAnalyzer()
document_processor = DocumentProcessor()
nlp_pipeline = NLPPipeline()
risk_analyzer = RiskAnalyzer()
document_classifier = DocumentClassifier()
document_summarizer = DocumentSummarizer()

async def read_document_content(file: UploadFile) -> str:
    """Extract text content from uploaded document."""
    content = await file.read()
    file_ext = file.filename.lower().split('.')[-1]
    
    if file_ext == 'txt':
        return content.decode('utf-8')
    elif file_ext == 'pdf':
        # Use PyPDF2 or similar to extract text
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PDF parsing not implemented yet"
        )
    elif file_ext in ['doc', 'docx']:
        # Use python-docx to extract text
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Word document parsing not implemented yet"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format"
        )

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncIOMotorClient = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Upload and process a legal document.
    """
    try:
        # Get user ID
        user_id = ObjectId(get_current_user_id(token))
        
        # Validate file type
        allowed_extensions = ['.pdf', '.docx', '.txt', '.png', '.jpg', '.jpeg']
        file_ext = '.' + file.filename.lower().split('.')[-1]
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format. Allowed formats: {', '.join(allowed_extensions)}"
            )
        
        # Process the document
        processed_text, metadata = await document_processor.process_document(file)
        
        # Perform initial analysis
        nlp_results = nlp_pipeline.analyze_document(processed_text)
        risk_results = risk_analyzer.analyze_risks(processed_text, nlp_results["clause_analysis"])
        classification_results = document_classifier.classify_document(processed_text)
        summary_results = document_summarizer.generate_summary(processed_text)
        
        # Create document record
        document = {
            "user_id": user_id,
            "filename": file.filename,
            "content": processed_text,
            "metadata": metadata,
            "upload_date": datetime.utcnow(),
            "last_analyzed": datetime.utcnow(),
            "file_type": file.content_type,
            "analysis_status": "completed",
            "nlp_analysis": nlp_results,
            "risk_analysis": risk_results,
            "classification": classification_results,
            "summary": summary_results
        }
        
        # Save to database
        result = await db.documents.insert_one(document)
        
        # Update user's document count
        await db.users.update_one(
            {"_id": user_id},
            {"$inc": {"document_count": 1}}
        )
        
        # Return document info
        return {
            "id": str(result.inserted_id),
            "filename": file.filename,
            "metadata": metadata,
            "analysis": {
                "document_type": classification_results["primary_type"],
                "risk_score": risk_results["overall_risk_score"],
                "summary_length": len(summary_results["executive_summary"]),
                "entities_found": len(nlp_results["legal_entities"])
            },
            "message": "Document processed successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing document: {str(e)}"
        )

@router.get("/list")
async def list_documents(db: AsyncIOMotorClient = Depends(get_db)):
    """
    List all uploaded documents.
    """
    try:
        cursor = db.documents.find({})
        documents = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
            documents.append(doc)
        return documents
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving documents: {str(e)}"
        )

@router.get("/{document_id}")
async def get_document(
    document_id: str,
    db: AsyncIOMotorClient = Depends(get_db)
):
    """
    Get a specific document by ID.
    """
    try:
        document = await db.documents.find_one({"_id": ObjectId(document_id)})
        if document:
            document["_id"] = str(document["_id"])
            return document
        raise HTTPException(status_code=404, detail="Document not found")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving document: {str(e)}"
        )

@router.get("/recent")
async def get_recent_documents(
    db: AsyncIOMotorClient = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """Get user's recent documents."""
    user_id = ObjectId(get_current_user_id(token))
    
    documents = await db.documents.find(
        {"user_id": user_id}
    ).sort("upload_date", -1).limit(10).to_list(None)
    
    return [{
        "id": str(doc["_id"]),
        "title": doc["title"],
        "upload_date": doc["upload_date"],
        "analysis_status": doc["analysis_status"]
    } for doc in documents]

@router.get("/{document_id}/analysis")
async def get_document_analysis(
    document_id: str,
    db: AsyncIOMotorClient = Depends(get_db)
):
    """Get detailed analysis results for a document."""
    try:
        # Retrieve document
        document = await db.documents.find_one({"_id": ObjectId(document_id)})
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        # Perform NLP analysis
        nlp_results = nlp_pipeline.analyze_document(document["content"])
        
        # Perform risk analysis
        risk_results = risk_analyzer.analyze_risks(
            document["content"],
            nlp_results["clause_analysis"]
        )
        
        # Perform document classification
        classification_results = document_classifier.classify_document(
            document["content"]
        )
        
        # Generate document summary
        summary_results = document_summarizer.generate_summary(
            document["content"]
        )
        
        # Combine all analysis results
        response = {
            "id": str(document["_id"]),
            "filename": document["filename"],
            "upload_date": document["upload_date"],
            "file_type": document["file_type"],
            "basic_metadata": document["metadata"],
            "classification": {
                "document_type": classification_results["primary_type"],
                "confidence_score": classification_results["confidence_score"],
                "alternative_types": classification_results["alternative_types"],
                "document_structure": classification_results["document_structure"]
            },
            "summary": {
                "executive_summary": summary_results["executive_summary"],
                "key_points": summary_results["key_points"],
                "section_summaries": summary_results["section_summaries"],
                "important_clauses": summary_results["important_clauses"]
            },
            "analysis": {
                "key_phrases": nlp_results["key_phrases"],
                "legal_entities": nlp_results["legal_entities"],
                "clauses": nlp_results["clause_analysis"],
                "sentiment": nlp_results["sentiment_analysis"],
                "readability": nlp_results["readability_metrics"],
                "key_terms": nlp_results["key_terms"]
            },
            "risk_analysis": {
                "overall_risk_score": risk_results["overall_risk_score"],
                "risk_categories": risk_results["risk_categories"],
                "critical_clauses": risk_results["critical_clauses"],
                "compliance_requirements": risk_results["compliance_requirements"],
                "deadlines": risk_results["deadlines"],
                "risk_summary": risk_results["risk_summary"],
                "recommendations": risk_results["recommendations"]
            }
        }
        
        # Update document with analysis results
        await db.documents.update_one(
            {"_id": ObjectId(document_id)},
            {
                "$set": {
                    "nlp_analysis": nlp_results,
                    "risk_analysis": risk_results,
                    "classification": classification_results,
                    "summary": summary_results,
                    "last_analyzed": datetime.utcnow()
                }
            }
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing document: {str(e)}"
        )

@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    db: AsyncIOMotorClient = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """Delete a document."""
    user_id = ObjectId(get_current_user_id(token))
    result = await db.documents.delete_one({
        "_id": ObjectId(document_id),
        "user_id": user_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Update user's document count
    await db.users.update_one(
        {"_id": user_id},
        {"$inc": {"document_count": -1}}
    )
    
    return {"message": "Document deleted"}

@router.get("/stats")
async def get_document_stats(db: AsyncIOMotorClient = Depends(get_db)):
    """Get document statistics and analytics."""
    try:
        # Get total documents
        total_documents = await db.documents.count_documents({})
        
        # Get documents analyzed today
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        analyzed_today = await db.documents.count_documents({
            "last_analyzed": {"$gte": today_start}
        })
        
        # Get high risk documents (risk score >= 0.7)
        high_risk_docs = await db.documents.count_documents({
            "risk_analysis.overall_risk_score": {"$gte": 0.7}
        })
        
        # Calculate average risk score
        risk_scores = []
        async for doc in db.documents.find(
            {"risk_analysis.overall_risk_score": {"$exists": True}},
            {"risk_analysis.overall_risk_score": 1}
        ):
            risk_scores.append(doc["risk_analysis"]["overall_risk_score"])
        
        avg_risk_score = sum(risk_scores) / len(risk_scores) if risk_scores else 0
        
        # Get document type distribution
        doc_types = {}
        async for doc in db.documents.find(
            {"classification.document_type": {"$exists": True}},
            {"classification.document_type": 1}
        ):
            doc_type = doc["classification"]["document_type"]
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
        
        document_types = [
            {"name": k, "value": v}
            for k, v in doc_types.items()
        ]
        
        # Get risk distribution
        risk_dist = {
            "Low Risk": 0,
            "Medium Risk": 0,
            "High Risk": 0
        }
        
        async for doc in db.documents.find(
            {"risk_analysis.overall_risk_score": {"$exists": True}},
            {"risk_analysis.overall_risk_score": 1}
        ):
            score = doc["risk_analysis"]["overall_risk_score"]
            if score >= 0.7:
                risk_dist["High Risk"] += 1
            elif score >= 0.4:
                risk_dist["Medium Risk"] += 1
            else:
                risk_dist["Low Risk"] += 1
        
        risk_distribution = [
            {"name": k, "value": v}
            for k, v in risk_dist.items()
        ]
        
        return {
            "total_documents": total_documents,
            "analyzed_today": analyzed_today,
            "high_risk_documents": high_risk_docs,
            "average_risk_score": avg_risk_score,
            "document_types": document_types,
            "risk_distribution": risk_distribution
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving document statistics: {str(e)}"
        ) 