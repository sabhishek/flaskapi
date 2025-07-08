from flask_restful import Resource
from app.models.job import Job
from app import db


class JobStatusResource(Resource):
    def get(self, job_id: str):
        job = Job.query.filter_by(job_id=job_id).first()
        if not job:
            return {"error": "job not found"}, 404
        return {
            "job_id": job.job_id,
            "status": job.status,
            "resource": job.resource,
            "tenant_id": job.tenant_id,
            "result": job.result,
            "created_at": job.created_at.isoformat(),
            "updated_at": job.updated_at.isoformat() if job.updated_at else None,
        }
