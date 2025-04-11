from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Any, List, Optional
import uuid

from app.db.database import get_db
from app.models import User, Project
from app.schemas import ProjectCreate, ProjectOut, ProjectUpdate
from app.utils.security import get_current_user

router = APIRouter()

@router.post("/", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    project_in: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Create a new project.
    """
    # Set initial status
    status_value = "planning"
    
    # Create project
    project = Project(
        **project_in.dict(),
        status=status_value,
        manager_id=current_user.user_id
    )
    
    # Add to database
    db.add(project)
    db.commit()
    db.refresh(project)
    
    return project

@router.get("/", response_model=List[ProjectOut])
def read_projects(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Retrieve all projects managed by the current user.
    """
    query = db.query(Project).filter(Project.manager_id == current_user.user_id)
    
    if status:
        query = query.filter(Project.status == status)
    
    projects = query.offset(skip).limit(limit).all()
    return projects

@router.get("/{project_id}", response_model=ProjectOut)
def read_project(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get project by ID.
    """
    project = db.query(Project).filter(
        Project.project_id == project_id,
        Project.manager_id == current_user.user_id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return project

@router.put("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: uuid.UUID,
    project_in: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update a project.
    """
    project = db.query(Project).filter(
        Project.project_id == project_id,
        Project.manager_id == current_user.user_id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Update project attributes
    for field, value in project_in.dict(exclude_unset=True).items():
        setattr(project, field, value)
    
    db.commit()
    db.refresh(project)
    
    return project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Delete a project.
    """
    project = db.query(Project).filter(
        Project.project_id == project_id,
        Project.manager_id == current_user.user_id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    db.delete(project)
    db.commit()