from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

class TemplateBase(BaseModel):
    """Base model for template data."""
    title: str = Field(..., description="The unique title of the template")
    content: str = Field(..., description="The Markdown content of the template")
    description: str = Field("", description="A brief description of the template")
    username: str = Field("anonymous", description="The username of the creator/updater")

class TemplateCreate(TemplateBase):
    """Model for creating a new template. Inherits all fields from TemplateBase."""
    pass

class TemplateUpdate(BaseModel):
    """Model for updating an existing template. All fields are optional."""
    content: Optional[str] = Field(None, description="The updated Markdown content")
    description: Optional[str] = Field(None, description="The updated description")
    username: Optional[str] = Field(None, description="The username of the updater")

class Template(TemplateBase):
    """Model representing a template retrieved from storage, including timestamps."""
    created_at: datetime = Field(..., description="Timestamp when the template was created")
    updated_at: datetime = Field(..., description="Timestamp when the template was last updated")

    model_config = {
        "from_attributes": True  # Pydantic V2 (旧 orm_mode)
    }

