from pydantic import BaseModel
from uuid import UUID


class APIKeyData(BaseModel):
    key_id: UUID
    tenant_id: UUID
    rate_limit_rpm: int
