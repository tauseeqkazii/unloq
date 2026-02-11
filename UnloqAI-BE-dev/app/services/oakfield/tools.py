from sqlalchemy.orm import Session
from app.models.shared import Decision, ImpactLedger, Company


class OakfieldTools:
    def __init__(self, db: Session):
        self.db = db

    def get_decision(self, decision_id):
        return self.db.query(Decision).filter(Decision.id == decision_id).first()

    def get_company(self, company_id):
        return self.db.query(Company).filter(Company.id == company_id).first()

    def get_impact_ledger(self, decision_id):
        return (
            self.db.query(ImpactLedger)
            .filter(ImpactLedger.decision_id == decision_id)
            .first()
        )
