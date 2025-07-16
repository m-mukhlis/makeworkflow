from fastapi import FastAPI, Depends, Request, HTTPException
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from .database import get_db, init_db
from . import models
from datetime import datetime


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="DevOps Mirror Service", lifespan=lifespan)


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/webhook/workitem/updated")
async def handle_workitem_update(
    # TODO: Define the webhook handler
    request: Request,
    db: Session = Depends(get_db),
):
    """Handle work item state changes from Azure DevOps"""
    try:
        payload = await request.json()

        # Extract key parts of payload
        resource = payload.get("resource", {})
        devops_id = resource.get("id")
        fields = resource.get("fields", {})
        revision_fields = resource.get("revision", {}).get("fields", {})

        if not devops_id or "System.State" not in revision_fields:
            raise HTTPException(status_code=400, detail="Invalid payload")

        # Extract state change details
        old_state = revision_fields["System.State"]["oldValue"]
        new_state = revision_fields["System.State"]["newValue"]
        title = fields.get("System.Title", "Untitled")
        changed_by = (
            fields.get("System.ChangedBy", {}).get("displayName", "Unknown")
        )
        changed_at_str = fields.get("System.ChangedDate")
        if not changed_at_str:
            raise HTTPException(status_code=400, detail="Missing ChangedDate")
        changed_at = datetime.fromisoformat(
            changed_at_str.replace("Z", "+00:00")
        )

        # Insert or update WorkItem
        work_item = (
            db.query(models.WorkItem)
            .filter_by(devops_id=devops_id)
            .first()
        )
        if not work_item:
            work_item = models.WorkItem(
                devops_id=devops_id,
                title=title,
                current_state=new_state,
                last_updated=changed_at,
            )
            db.add(work_item)
            db.commit()
            db.refresh(work_item)
        else:
            # Update latest state
            work_item.title = title
            work_item.current_state = new_state
            work_item.last_updated = changed_at
            db.commit()

        # Check if this exact transition already exists
        exists = (
            db.query(models.StateTransition)
            .filter_by(
                work_item_id=work_item.id,
                from_state=old_state,
                to_state=new_state,
                changed_at=changed_at,
            )
            .first()
        )
        if exists:
            # Already recorded (duplicate webhook)
            return {"status": "duplicate_ignored", "processed": False}

        # Record state transition
        transition = models.StateTransition(
            work_item_id=work_item.id,
            from_state=old_state,
            to_state=new_state,
            changed_by=changed_by,
            changed_at=changed_at,
        )
        db.add(transition)
        db.commit()

        return {"status": "ok", "processed": True}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get("/workitems/{devops_id}")
def get_workitem(devops_id: int, db: Session = Depends(get_db)):
    """Return work item details and state transition history"""
    work_item = (
        db.query(models.WorkItem)
        .filter_by(devops_id=devops_id)
        .first()
    )
    if not work_item:
        raise HTTPException(status_code=404, detail="Not Found")

    # Build response
    history = [
        {
            "from_state": t.from_state,
            "to_state": t.to_state,
            "changed_by": t.changed_by,
            "changed_at": t.changed_at.isoformat(),
        }
        for t in sorted(work_item.transitions, key=lambda t: t.changed_at)
    ]

    return {
        "devops_id": work_item.devops_id,
        "title": work_item.title,
        "current_state": work_item.current_state,
        "last_updated": work_item.last_updated.isoformat(),
        "transitions": history,
    }


@app.get("/workitems/{devops_id}/time-in-state")
def time_in_state(devops_id: int, db: Session = Depends(get_db)):
    """Compute total time spent in each state"""
    work_item = (
        db.query(models.WorkItem)
        .filter_by(devops_id=devops_id)
        .first()
    )
    if not work_item:
        raise HTTPException(status_code=404, detail="Not Found")

    transitions = sorted(work_item.transitions, key=lambda t: t.changed_at)
    state_times = {}

    for i, t in enumerate(transitions):
        start = t.changed_at
        end = (
            transitions[i + 1].changed_at
            if i + 1 < len(transitions)
            else datetime.utcnow()
        )
        duration = (end - start).total_seconds()
        state_times.setdefault(t.to_state, 0)
        state_times[t.to_state] += duration

    return {
        "devops_id": work_item.devops_id,
        "title": work_item.title,
        "current_state": work_item.current_state,
        "state_times_seconds": state_times,
    }