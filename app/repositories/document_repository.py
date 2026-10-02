from datetime import datetime

from sqlalchemy import text

from app.db.database import SessionLocal


def insert_document(document_data: dict):

    db = SessionLocal()

    try:

        query = text("""
            INSERT INTO document (
                document_id,
                document_name,
                document_type,
                document_group_id,
                version,
                status,
                blob_path,
                uploaded_by,
                uploaded_at,
                activated_at,
                deactivated_at
            )
            VALUES (
                :document_id,
                :document_name,
                :document_type,
                :document_group_id,
                :version,
                :status,
                :blob_path,
                :uploaded_by,
                :uploaded_at,
                :activated_at,
                :deactivated_at
            )
        """)

        db.execute(query, document_data)

        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()