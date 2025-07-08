from app import db


class TenantResourceMapping(db.Model):
    __tablename__ = "tenant_resources"

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.String, nullable=False, index=True)
    resource_type = db.Column(db.String, nullable=False)
    resource_name = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"<TenantResource {self.tenant_id} {self.resource_type}/{self.resource_name}>"
