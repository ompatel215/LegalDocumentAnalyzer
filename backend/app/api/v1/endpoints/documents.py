from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import List, Dict, Any
from ....services.document_processor import document_processor
from ....core.auth import get_current_user
from ....models.user import User
from ....models.document import DocumentCreate, DocumentResponse
from ....db.mongodb import get_database
import os
from datetime import datetime

router = APIRouter()

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Upload and analyze a document"""
    # Validate file type
    allowed_extensions = {"pdf", "docx", "doc", "txt", "png", "jpg", "jpeg"}
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="File type not supported")

    # Save file
    file_path = os.path.join(UPLOAD_DIR, f"{datetime.now().timestamp()}_{file.filename}")
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    try:
        # Extract text and analyze document
        text = document_processor.extract_text(file_path, file_extension)
        analysis_result = document_processor.analyze_document(text)

        # Create document record
        document = DocumentCreate(
            filename=file.filename,
            file_path=file_path,
            user_id=current_user.id,
            content=text,
            analysis=analysis_result,
            upload_date=datetime.now()
        )

        # Save to database
        document_id = await db.documents.insert_one(document.dict())

        return DocumentResponse(
            id=str(document_id.inserted_id),
            filename=file.filename,
            analysis=analysis_result,
            upload_date=document.upload_date
        )

    except Exception as e:
        # Clean up file if analysis fails
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analysis/{document_id}", response_model=DocumentResponse)
async def get_document_analysis(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get analysis results for a specific document"""
    from bson import ObjectId
    
    document = await db.documents.find_one({"_id": ObjectId(document_id)})
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this document")
    
    return DocumentResponse(
        id=str(document["_id"]),
        filename=document["filename"],
        analysis=document["analysis"],
        upload_date=document["upload_date"]
    )

@router.get("/recent", response_model=List[DocumentResponse])
async def get_recent_documents(
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get recent documents for the current user"""
    cursor = db.documents.find({"user_id": current_user.id}).sort("upload_date", -1).limit(5)
    documents = []
    async for doc in cursor:
        documents.append(DocumentResponse(
            id=str(doc["_id"]),
            filename=doc["filename"],
            analysis=doc["analysis"],
            upload_date=doc["upload_date"]
        ))
    return documents 