"""Settings Pydantic schemas for validation and serialization."""

import datetime as dt
from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

from app.schemas._nullability import reject_null


class SettingBase(BaseModel):
    """Base setting schema."""

    value: str | None = Field(None, description="Setting value")
    category: str = Field("general", description="Setting category")
    description: str | None = Field(None, description="Setting description")
    encrypted: bool = Field(
        False,
        description=(
            "Whether the value is sensitive and therefore masked as '********' in "
            "API responses. Values are NOT encrypted at rest."
        ),
    )


class SettingCreate(SettingBase):
    """Schema for creating a setting."""

    key: str = Field(..., description="Setting key", min_length=1, max_length=50)


class SettingUpdate(BaseModel):
    """Schema for updating a setting."""

    value: str | None = Field(None, description="Setting value")
    category: str | None = Field(None, description="Setting category")
    description: str | None = Field(None, description="Setting description")
    encrypted: bool | None = Field(
        None, description="Whether the value is sensitive (masked in API responses)"
    )

    # NOT NULL columns: omitted keeps the stored value, null is a 422.
    _no_null = reject_null("category", "encrypted")


class SettingResponse(SettingBase):
    """Schema for setting response."""

    key: str
    created_at: dt.datetime
    updated_at: dt.datetime

    class Config:
        from_attributes = True


class SettingsListResponse(BaseModel):
    """Schema for list of settings."""

    settings: list[SettingResponse]
    total: int


#: A setting key, as wide as the `settings.key` column (and `SettingCreate.key`).
SettingKey = Annotated[str, StringConstraints(min_length=1, max_length=50)]


class SettingsBatchUpdate(BaseModel):
    """Schema for batch updating settings."""

    settings: dict[SettingKey, str] = Field(
        ..., description="Dictionary of key-value pairs to update"
    )


class POIProviderCreate(BaseModel):
    """Adding a POI provider. The route keeps its own 400s for the name and key."""

    name: str = ""
    api_key: str = ""
    enabled: bool = True


class POIProviderUpdate(BaseModel):
    """Editing a POI provider: an omitted field keeps its stored value."""

    api_key: str | None = None
    enabled: bool | None = None

    # Both write settings rows a null has no meaning for.
    _no_null = reject_null("api_key", "enabled")


class SystemInfoResponse(BaseModel):
    """Schema for system information."""

    app_name: str
    app_version: str
    python_version: str
    database_url: str
    data_directory: str
    total_vehicles: int
    database_size_mb: float
    uptime_seconds: float


class LlmTestResponse(BaseModel):
    """What ``POST /api/settings/test/llm`` reports (#211).

    ``vision_ok`` is null when the vision check did not run, which is the case
    while document reading is off; ``valid`` is the single verdict the card's
    button colours on.
    """

    valid: bool = Field(description="True when every check that ran succeeded")
    message: str = Field(description="A sentence for the operator, the endpoint's error included")
    text_ok: bool = Field(description="The text completion with llm_model succeeded")
    vision_ok: bool | None = Field(
        default=None,
        description="The vision completion succeeded; null when document reading is off",
    )
    model: str = Field(description="The text model that was tested")
    vision_model: str = Field(description="The vision model that was (or would be) tested")
