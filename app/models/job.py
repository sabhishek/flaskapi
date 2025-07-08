from datetime import datetime
from app import db


class Job(db.Model):
    __tablename__ = "jobs"

    job_id = db.Column(db.String, primary_key=True)
    status = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime)
    resource = db.Column(db.String)
    tenant_id = db.Column(db.String, nullable=False)
    result = db.Column(db.JSON)

    def __repr__(self):
        return f"<Job {self.job_id} {self.status}>"
