"""
Subscription endpoints for dynamic calendar links
"""
from fastapi import APIRouter, HTTPException, Depends, Response
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.core.database import get_db
from app.models.subscription import Subscription as SubscriptionModel
from app.schemas.event import (
    SubscriptionCreate,
    Subscription,
    SubscriptionListResponse
)
from app.utils.calendar_generator import CalendarGenerator
from app.utils.parser import FileParser

router = APIRouter()


@router.post("/", response_model=Subscription)
async def create_subscription(
    subscription: SubscriptionCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new dynamic calendar subscription
    """
    try:
        # Create subscription record
        db_subscription = SubscriptionModel(
            name=subscription.name,
            description=subscription.description,
            source_url=subscription.source_url,
            source_type=subscription.source_type,
            parsing_rules=subscription.parsing_rules,
            calendar_name=subscription.calendar_name,
            timezone=subscription.timezone
        )
        
        db.add(db_subscription)
        db.commit()
        db.refresh(db_subscription)
        
        return db_subscription
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating subscription: {str(e)}"
        )


@router.get("/", response_model=SubscriptionListResponse)
async def list_subscriptions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all calendar subscriptions
    """
    subscriptions = db.query(SubscriptionModel)\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    total = db.query(SubscriptionModel).count()
    
    return SubscriptionListResponse(
        subscriptions=subscriptions,
        total=total
    )


@router.get("/{subscription_id}", response_model=Subscription)
async def get_subscription(
    subscription_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific subscription by ID
    """
    subscription = db.query(SubscriptionModel)\
        .filter(SubscriptionModel.id == subscription_id)\
        .first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    return subscription


@router.get("/{subscription_id}/calendar.ics")
async def get_subscription_calendar(
    subscription_id: str,
    db: Session = Depends(get_db)
):
    """
    Fetch and generate calendar for a subscription
    This is the dynamic endpoint that fetches fresh data each time
    """
    subscription = db.query(SubscriptionModel)\
        .filter(SubscriptionModel.id == subscription_id)\
        .first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    if not subscription.is_active:
        raise HTTPException(status_code=400, detail="Subscription is inactive")
    
    try:
        # Fetch data from source
        parser = FileParser()
        
        # Parse based on source type
        if subscription.source_url:
            # TODO: Implement fetching from URL
            # For now, assume we have the data
            raise HTTPException(
                status_code=501,
                detail="URL fetching not yet implemented"
            )
        
        # Generate calendar
        generator = CalendarGenerator()
        
        # Placeholder: In production, fetch and parse real data
        events_data = []
        
        ics_content = generator.generate_ics(
            events=events_data,
            calendar_name=subscription.calendar_name,
            timezone=subscription.timezone
        )
        
        # Update last fetched timestamp
        subscription.last_fetched_at = datetime.utcnow()
        db.commit()
        
        return Response(
            content=ics_content.encode('utf-8'),
            media_type="text/calendar",
            headers={
                "Content-Disposition": f"attachment; filename={subscription.calendar_name.replace(' ', '_')}.ics"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating subscription calendar: {str(e)}"
        )


@router.put("/{subscription_id}", response_model=Subscription)
async def update_subscription(
    subscription_id: str,
    subscription_update: SubscriptionCreate,
    db: Session = Depends(get_db)
):
    """
    Update a subscription
    """
    subscription = db.query(SubscriptionModel)\
        .filter(SubscriptionModel.id == subscription_id)\
        .first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # Update fields
    subscription.name = subscription_update.name
    subscription.description = subscription_update.description
    subscription.source_url = subscription_update.source_url
    subscription.source_type = subscription_update.source_type
    subscription.parsing_rules = subscription_update.parsing_rules
    subscription.calendar_name = subscription_update.calendar_name
    subscription.timezone = subscription_update.timezone
    subscription.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(subscription)
    
    return subscription


@router.delete("/{subscription_id}")
async def delete_subscription(
    subscription_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a subscription
    """
    subscription = db.query(SubscriptionModel)\
        .filter(SubscriptionModel.id == subscription_id)\
        .first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    db.delete(subscription)
    db.commit()
    
    return {"message": "Subscription deleted successfully"}
