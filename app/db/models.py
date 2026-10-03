import uuid

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import UUID

from app.db.database import Base


class Document(Base):
    __tablename__ = "document"

    document_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    document_name = Column(
        String(255),
        nullable=False
    )

    document_type = Column(
        String(50),
        nullable=False
    )

    document_group_id = Column(
        String(100),
        nullable=False
    )

    version = Column(
        Integer,
        nullable=False
    )

    status = Column(
        String(20),
        nullable=False
    )

    blob_path = Column(
        String(500),
        nullable=False
    )

    uploaded_by = Column(
        String(100)
    )

    uploaded_at = Column(
        DateTime(timezone=True),
        nullable=False
    )

    activated_at = Column(
        DateTime(timezone=True)
    )

    deactivated_at = Column(
        DateTime(timezone=True)
    )