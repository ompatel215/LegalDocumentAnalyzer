from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorClient
from ..core.database import get_db
from ..core.security import oauth2_scheme, get_current_user_id
from bson import ObjectId
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/stats")
async def get_dashboard_stats(
    db: AsyncIOMotorClient = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """Get dashboard statistics for the current user."""
    user_id = ObjectId(get_current_user_id(token))
    
    # Get total documents count
    total_documents = await db.documents.count_documents({"user_id": user_id})
    
    # Get analyzed documents count
    documents_analyzed = await db.documents.count_documents({
        "user_id": user_id,
        "analysis_status": "completed"
    })
    
    # Get pending analysis count
    pending_analysis = await db.documents.count_documents({
        "user_id": user_id,
        "analysis_status": "pending"
    })
    
    # Get risk alerts count (documents with high-risk factors)
    risk_alerts = await db.documents.count_documents({
        "user_id": user_id,
        "risk_factors": {
            "$elemMatch": {
                "severity": "high"
            }
        }
    })
    
    return {
        "total_documents": total_documents,
        "documents_analyzed": documents_analyzed,
        "pending_analysis": pending_analysis,
        "risk_alerts": risk_alerts
    }

@router.get("/analytics")
async def get_analytics(
    db: AsyncIOMotorClient = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """Get detailed analytics for the current user."""
    user_id = ObjectId(get_current_user_id(token))
    
    # Get document types distribution
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {
            "_id": "$document_type",
            "count": {"$sum": 1}
        }}
    ]
    document_types = await db.documents.aggregate(pipeline).to_list(None)
    
    # Get risk distribution
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$unwind": "$risk_factors"},
        {"$group": {
            "_id": "$risk_factors.severity",
            "count": {"$sum": 1}
        }}
    ]
    risk_distribution = await db.documents.aggregate(pipeline).to_list(None)
    
    # Get most common entities
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$project": {
            "entities": "$metadata.entities"
        }},
        {"$unwind": "$entities"},
        {"$group": {
            "_id": "$entities.type",
            "entities": {"$addToSet": "$entities.text"}
        }}
    ]
    common_entities = await db.documents.aggregate(pipeline).to_list(None)
    
    # Get upload activity over time
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    pipeline = [
        {"$match": {
            "user_id": user_id,
            "upload_date": {"$gte": thirty_days_ago}
        }},
        {"$group": {
            "_id": {
                "$dateToString": {
                    "format": "%Y-%m-%d",
                    "date": "$upload_date"
                }
            },
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]
    upload_activity = await db.documents.aggregate(pipeline).to_list(None)
    
    return {
        "document_types": document_types,
        "risk_distribution": risk_distribution,
        "common_entities": common_entities,
        "upload_activity": upload_activity
    }

@router.get("/recent-activity")
async def get_recent_activity(
    db: AsyncIOMotorClient = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """Get recent activity for the current user."""
    user_id = ObjectId(get_current_user_id(token))
    
    # Get recent document uploads
    recent_uploads = await db.documents.find(
        {"user_id": user_id}
    ).sort("upload_date", -1).limit(5).to_list(None)
    
    # Get recent high-risk documents
    high_risk_docs = await db.documents.find({
        "user_id": user_id,
        "risk_factors": {
            "$elemMatch": {
                "severity": "high"
            }
        }
    }).sort("upload_date", -1).limit(5).to_list(None)
    
    return {
        "recent_uploads": [
            {
                "id": str(doc["_id"]),
                "title": doc["title"],
                "upload_date": doc["upload_date"],
                "analysis_status": doc["analysis_status"]
            }
            for doc in recent_uploads
        ],
        "high_risk_documents": [
            {
                "id": str(doc["_id"]),
                "title": doc["title"],
                "risk_factors": [
                    risk for risk in doc["risk_factors"]
                    if risk["severity"] == "high"
                ]
            }
            for doc in high_risk_docs
        ]
    } 