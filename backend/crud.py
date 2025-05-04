from sqlalchemy.orm import Session
from backend.models import MedicalReport

def save_uploaded_file(db: Session, file_content: str, filename: str):
    """Save uploaded file content to the database."""
    new_report = MedicalReport(filename=filename, content=file_content)
    db.add(new_report)
    db.commit()  # This line fails because the table doesn't exist
    db.refresh(new_report)
    return new_report

def get_latest_report(db: Session):
    """Retrieve the most recent MedicalReport entry."""
    return db.query(MedicalReport).order_by(MedicalReport.id.desc()).first()