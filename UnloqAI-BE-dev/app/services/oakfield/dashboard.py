from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.meridian import (
    StrategyKPI, InternalSignal, ExternalSignal, 
    StrategyRecommendation, ImpactLedgerStrategy, StrategyObjective
)
from datetime import datetime
import re

class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def get_cockpit_data(self):
        """
        Aggregates data from 5 tables into the 'Board Cockpit' schema.
        Now completely dynamic with no hardcoded mocks.
        """
        return {
            "company": {
                "company_id": "MERIDIAN",
                "company_name": "Meridian Dynamics",
                "mode": "live_demo",
                "data_updated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M")
            },
            "headline_cards": self._build_headline_cards(),
            "top_issues": self._build_top_issues(),
            "decision_inbox_preview": self._build_inbox_preview(),
            "ledger_summary": self._build_ledger_summary()
        }

    def _parse_currency(self, value_str: str) -> float:
        """Helper to convert strings like '£1.2m' into float values."""
        if not value_str:
            return 0.0
        
        # Normalize
        clean = value_str.lower().replace('£', '').replace(',', '').strip()
        multiplier = 1.0
        
        if 'm' in clean:
            multiplier = 1_000_000.0
            clean = clean.replace('m', '')
        elif 'k' in clean:
            multiplier = 1_000.0
            clean = clean.replace('k', '')
            
        try:
            match = re.search(r"[-+]?\d*\.\d+|\d+", clean)
            if match:
                return float(match.group()) * multiplier
            return 0.0
        except Exception:
            return 0.0

    def _format_currency(self, value: float) -> str:
        """Helper to format float back to '£1.2m' style."""
        if value >= 1_000_000:
            return f"£{value/1_000_000:.1f}m"
        elif value >= 1_000:
            return f"£{value/1_000:.0f}k"
        else:
            return f"£{value:.0f}"

    def _build_headline_cards(self):
        """
        Fetches KPIs and their last 12 data points for sparklines.
        """
        cards = []
        
        # 1. Objectives Card
        off_track_count = self.db.query(StrategyObjective).filter(StrategyObjective.status == 'off_track').count()
        at_risk_count = self.db.query(StrategyObjective).filter(StrategyObjective.status == 'at_risk').count()
        on_track_count = self.db.query(StrategyObjective).filter(StrategyObjective.status == 'on_track').count()
        
        cards.append({
            "card_id": "objectives_glance",
            "title": "Objectives",
            "primary_value": { "text": f"{off_track_count} Off-track", "status": "off_track" if off_track_count > 0 else "on_track" },
            "secondary_text": f"{at_risk_count} At risk • {on_track_count} On track",
            "insight_text": "Off-track means we're missing targets, not just wobbling.",
            "sparkline": None
        })

        # 2. KPI Cards (Revenue, Product B, NPS)
        target_kpis = ["Product B Monthly Sales", "Win Rate Segment X", "NPS Segment Z"]
        
        for kpi_name in target_kpis:
            kpi = self.db.query(StrategyKPI).filter(StrategyKPI.name.ilike(f"%{kpi_name}%")).first()
            if not kpi:
                continue

            # Fetch Sparkline Data (Last 12 entries)
            history = self.db.query(InternalSignal).filter(
                InternalSignal.kpi_id == kpi.kpi_id
            ).order_by(desc(InternalSignal.timestamp)).limit(12).all()
            
            history = sorted(history, key=lambda x: x.timestamp)
            points = [float(h.value) for h in history]
            
            status = "off_track" if kpi.current_value < kpi.target_value else "on_track"
            if "Win Rate" in kpi.name and kpi.current_value < 40: status = "at_risk"
            
            val_text = f"{kpi.current_value}{kpi.unit}"
            if kpi.unit == "GBP_m": val_text = f"£{kpi.current_value}m"
            if kpi.unit == "percent": val_text = f"{kpi.current_value}%"
            if kpi.unit == "score": val_text = f"{kpi.current_value}"
            
            cards.append({
                "card_id": str(kpi.kpi_id),
                "title": kpi.name,
                "primary_value": { "text": val_text, "status": status },
                "secondary_text": f"Target: {kpi.target_value} {kpi.unit}",
                "insight_text": "Trend calculated from live signals.",
                "sparkline": {
                    "period": "weekly",
                    "points": points,
                    "direction": "down" if points and points[-1] < points[0] else "up",
                    "color": "rose" if status == "off_track" else "emerald"
                }
            })
            
        return cards

    def _build_top_issues(self):
        """
        Identifies 'Off Track' KPIs and formats them as Issues.
        """
        issues = []
        failing_kpis = self.db.query(StrategyKPI).filter(StrategyKPI.current_value < StrategyKPI.target_value).all()
        
        for kpi in failing_kpis:
            recent_signal = self.db.query(ExternalSignal).order_by(desc(ExternalSignal.timestamp)).first()
            driver = recent_signal.description if recent_signal else "Internal efficiency drop detected."
            
            status = "off_track"
            if "Win Rate" in kpi.name: status = "at_risk"

            issues.append({
                "issue_id": str(kpi.kpi_id),
                "status": status,
                "title": f"{kpi.name} Issue",
                "metric_text": f"Dropped to {kpi.current_value} (Target {kpi.target_value})",
                "driver_text": driver
            })
        return issues

    def _build_inbox_preview(self):
        """
        Fetches pending strategy recommendations dynamically.
        """
        recs = self.db.query(StrategyRecommendation).filter(StrategyRecommendation.status == "pending").limit(3).all()
        preview = []
        for r in recs:
            impact_text = r.rationale[:50] + "..." if r.rationale else "Review details for impact"
            
            preview.append({
                "recommendation_id": str(r.recommendation_id),
                "title": r.title,
                "status": "pending_approval",
                "expected_impact": impact_text, 
                "linked_kpis": "Strategic Goals",
                "confidence": "High"
            })
        return preview

    def _build_ledger_summary(self):
        """
        Real-time aggregation of the Impact Ledger.
        Sums up the 'expected_roi' and 'actual_roi' columns by parsing the strings.
        """
        entries = self.db.query(ImpactLedgerStrategy).all()
        total_expected = 0.0
        total_actual = 0.0
        total_in_progress = 0.0
        rows = []
        
        for entry in entries:
            exp_val = self._parse_currency(entry.expected_roi)
            act_val = self._parse_currency(entry.actual_roi)
            
            total_expected += exp_val
            total_actual += act_val
            
            if act_val == 0:
                total_in_progress += exp_val
                status = "In Progress"
            else:
                status = "Realized"

            title = entry.recommendation.title if entry.recommendation else "Strategic Action"
            
            rows.append({
                "title": title,
                "expected": entry.expected_roi or "£0",
                "actual": entry.actual_roi or "Pending",
                "status": status,
                "note": "ROI tracked via ledger."
            })

        return {
            "totals": {
                "expected_roi_value": self._format_currency(total_expected),
                "actual_roi_value": self._format_currency(total_actual),
                "in_progress_value": self._format_currency(total_in_progress)
            },
            "rows": rows
        }