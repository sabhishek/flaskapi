from datetime import datetime
from app.models.job import Job
from app import db, celery_app


@celery_app.task(name="process_job")
def process_job(job_id: str, resource: str, action: str, payload: dict, tenant_id: str):
    # TODO: Integrate git writer, template engine, argo sync
    job = Job.query.filter_by(job_id=job_id).first()
    job.status = "running"
    db.session.commit()

    # Simulate work
    import time
    time.sleep(2)

    job.status = "completed"
    job.result = {"message": f"{action} {resource} completed"}
    job.updated_at = datetime.utcnow()
    db.session.commit()


def enqueue_job(job_id: str, resource: str, action: str, payload: dict, tenant_id: str):
    # Persist job
    job = Job(job_id=job_id, status="queued", created_at=datetime.utcnow(), resource=resource, tenant_id=tenant_id)
    db.session.add(job)
    db.session.commit()

    # Send async
    process_job.delay(job_id, resource, action, payload, tenant_id)
