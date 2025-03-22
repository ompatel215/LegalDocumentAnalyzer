from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from motor.motor_asyncio import AsyncIOMotorClient
from ..core.database import get_db
from ..core.security import oauth2_scheme, get_current_user_id
from ..models.document import Document
from ..services.document_analyzer import DocumentAnalyzer
from datetime import datetime
from bson import ObjectId
import io

router = APIRouter()
document_analyzer = DocumentAnalyzer()

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
    """Upload and analyze a document."""
    user_id = ObjectId(get_current_user_id(token))
    
    # Read document content
    content = await read_document_content(file)
    
    # Create document record
    document = {
        "title": file.filename,
        "content": content,
        "file_path": f"/documents/{file.filename}",  # You'll need to actually save the file
        "document_type": "unknown",  # This should be determined based on content analysis
        "upload_date": datetime.utcnow(),
        "user_id": user_id,
        "analysis_status": "pending"
    }
    
    # Insert document
    result = await db.documents.insert_one(document)
    document_id = result.inserted_id
    
    # Start analysis in background
    analysis_result = await document_analyzer.analyze(content)
    
    # Update document with analysis results
    await db.documents.update_one(
        {"_id": document_id},
        {
            "$set": {
                "analysis_status": "completed",
                "document_type": analysis_result.get("document_type", "unknown"),
                "summary": analysis_result.get("summary"),
                "key_clauses": analysis_result.get("key_clauses", []),
                "risk_factors": analysis_result.get("risk_factors", []),
                "entities": analysis_result.get("entities", []),
                "metadata": analysis_result.get("metadata", {})
            }
        }
    )
    
    # Update user's document count
    await db.users.update_one(
        {"_id": user_id},
        {"$inc": {"document_count": 1}}
    )
    
    return {
        "id": str(document_id),
        "message": "Document uploaded and analysis started"
    }

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

@router.get("/{document_id}")
async def get_document(
    document_id: str,
    db: AsyncIOMotorClient = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """Get a specific document."""
    user_id = ObjectId(get_current_user_id(token))
    document = await db.documents.find_one({
        "_id": ObjectId(document_id),
        "user_id": user_id
    })
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    document["_id"] = str(document["_id"])
    document["user_id"] = str(document["user_id"])
    return document

@router.get("/{document_id}/analysis")
async def get_document_analysis(
    document_id: str,
    db: AsyncIOMotorClient = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """Get analysis results for a document."""
    user_id = ObjectId(get_current_user_id(token))
    document = await db.documents.find_one({
        "_id": ObjectId(document_id),
        "user_id": user_id
    })
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return {
        "id": str(document["_id"]),
        "title": document["title"],
        "document_type": document["document_type"],
        "analysis_status": document["analysis_status"],
        "summary": document.get("summary"),
        "key_clauses": document.get("key_clauses", []),
        "risk_factors": document.get("risk_factors", []),
        "entities": document.get("entities", []),
        "metadata": document.get("metadata", {})
    }

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