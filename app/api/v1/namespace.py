from flask import request, jsonify
from flask_restful import Resource
from uuid import uuid4

from ...services.job_manager import enqueue_job


class NamespaceResource(Resource):
    """Handle namespace CRUD via async jobs.

    Endpoint pattern: /api/v1/ns/<action>
    Accepted actions: create, delete, status
    """

    def post(self, action: str):
        data = request.get_json(force=True, silent=True) or {}
        tenant_id = request.headers.get("X-Tenant-ID") or data.get("tenant_id")
        if not tenant_id:
            return {"error": "tenant_id missing in headers or body"}, 400

        job_id = str(uuid4())
        enqueue_job(job_id, resource="namespace", action=action, payload=data, tenant_id=tenant_id)
        return {"job_id": job_id, "status": "queued"}, 202

    def get(self, action: str):
        # For read/status-type actions we may implement later
        return {"message": f"GET not implemented for action {action}"}, 405
