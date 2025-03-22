from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Optional
from datetime import datetime
import os
import shutil
from bson import ObjectId

from ..models.document import Document, DocumentResponse, DocumentAnalysis
from ..services.document_processor import document_processor
from ..database import get_database
from ..auth.dependencies import get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

async def process_document(
    document_id: str,
    file_path: str,
    content_type: str,
    db: get_database
):
    try:
        # Read the file
        with open(file_path, "rb") as f:
            file_content = f.read()

        # Extract text from the document
        text = document_processor.extract_text(file_content, content_type)

        # Analyze the document
        analysis_results = document_processor.analyze_document(text)

        # Update the document in the database
        await db.documents.update_one(
            {"_id": ObjectId(document_id)},
            {
                "$set": {
                    "status": "completed",
                    "analysis": analysis_results,
                    "last_modified": datetime.utcnow()
                }
            }
        )
    except Exception as e:
        # Update document status to failed
        await db.documents.update_one(
            {"_id": ObjectId(document_id)},
            {
                "$set": {
                    "status": "failed",
                    "last_modified": datetime.utcnow()
                }
            }
        )
        raise e

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: get_database = Depends(get_database)
):
    # Validate file type
    allowed_types = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
        "image/jpeg",
        "image/png"
    ]
    
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file.content_type} not supported. Supported types: PDF, DOCX, TXT, JPG, PNG"
        )

    # Create unique filename
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Create document record
    document = Document(
        title=file.filename,
        file_type=file.filename.split(".")[-1].lower(),
        content_type=file.content_type,
        size=os.path.getsize(file_path),
        user_id=current_user.id,
        file_path=file_path,
        status="processing"
    )

    # Insert document into database
    result = await db.documents.insert_one(document.dict(by_alias=True))
    document.id = result.inserted_id

    # Start background processing
    background_tasks.add_task(
        process_document,
        str(result.inserted_id),
        file_path,
        file.content_type,
        db
    )

    return DocumentResponse(
        id=str(document.id),
        title=document.title,
        file_type=document.file_type,
        size=document.size,
        upload_date=document.upload_date,
        last_modified=document.last_modified,
        status=document.status,
        tags=document.tags
    )

@router.get("/list", response_model=List[DocumentResponse])
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: get_database = Depends(get_database)
):
    cursor = db.documents.find({"user_id": current_user.id, "is_deleted": False})
    documents = await cursor.to_list(length=None)
    return [DocumentResponse(**doc) for doc in documents]

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: get_database = Depends(get_database)
):
    document = await db.documents.find_one({
        "_id": ObjectId(document_id),
        "user_id": current_user.id,
        "is_deleted": False
    })
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return DocumentResponse(**document)

@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: get_database = Depends(get_database)
):
    result = await db.documents.update_one(
        {
            "_id": ObjectId(document_id),
            "user_id": current_user.id
        },
        {"$set": {"is_deleted": True}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return JSONResponse(content={"message": "Document deleted successfully"})

@router.get("/analysis/{document_id}", response_model=DocumentAnalysis)
async def get_document_analysis(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: get_database = Depends(get_database)
):
    document = await db.documents.find_one({
        "_id": ObjectId(document_id),
        "user_id": current_user.id,
        "is_deleted": False
    })
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document["status"] == "pending" or document["status"] == "processing":
        raise HTTPException(status_code=202, detail="Analysis in progress")
    
    if document["status"] == "failed":
        raise HTTPException(status_code=500, detail="Document analysis failed")
    
    if not document.get("analysis"):
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return DocumentAnalysis(**document["analysis"]) 