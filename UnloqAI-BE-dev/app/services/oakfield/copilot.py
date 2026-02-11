"""
OakfieldCopilotService — AI strategist for the Oakfield homebuilder platform.

Operates exclusively on oakfield_* tables via OakfieldTools.
No dependency on Meridian models, services, or schema.
"""
import json
from typing import Generator

from sqlalchemy.orm import Session

from app.services.llm_service import llm_service
from app.services.oakfield.tools import OakfieldTools


# Intent keywords mapped to tool methods — used for dynamic dispatch
_INTENT_MAP = {
    "margin": "margin",
    "margin summary": "margin",
    "bundle": "bundle",
    "upsell": "bundle",
    "missed": "bundle",
    "opportunity": "bundle",
    "development": "development",
    "site": "development",
    "region": "development",
    "eligib": "eligibility",
    "eligible": "eligibility",
    "stage": "eligibility",
    "option": "options",
    "catalogue": "options",
    "house type": "house_types",
    "house": "house_types",
    "beds": "house_types",
}


class CopilotService:
    def __init__(self, db: Session):
        self.db = db
        self.tools = OakfieldTools(db)

    # ------------------------------------------------------------------
    # Intent detection
    # ------------------------------------------------------------------

    def _detect_intent(self, query: str) -> str:
        """
        Lightweight keyword scan to decide which tool to call.
        Returns one of: margin | bundle | development | eligibility | options |
                        house_types | general
        """
        lower = query.lower()
        for keyword, intent in _INTENT_MAP.items():
            if keyword in lower:
                return intent
        return "general"

    # ------------------------------------------------------------------
    # Context assembly
    # ------------------------------------------------------------------

    def _build_context(self, query: str) -> dict:
        """
        Selects and fetches only the data relevant to the detected intent.
        Returns a dict that will be JSON-serialised into the system prompt.
        """
        intent = self._detect_intent(query)

        if intent == "margin":
            return {
                "intent": "margin_analysis",
                "data": self.tools.get_margin_summary(),
            }

        if intent == "bundle":
            return {
                "intent": "bundle_opportunity_analysis",
                "data": self.tools.get_missed_bundle_opportunities(),
                "bundles": self.tools.get_all_bundles(),
            }

        if intent == "development":
            return {
                "intent": "development_overview",
                "data": self.tools.get_all_developments(),
            }

        if intent == "options":
            return {
                "intent": "options_catalogue",
                "data": self.tools.get_options_by_category(),
            }

        if intent == "house_types":
            return {
                "intent": "house_type_overview",
                "data": self.tools.get_house_types(),
            }

        # General fallback — provide a lightweight overview
        return {
            "intent": "general",
            "margin_summary": self.tools.get_margin_summary(),
            "missed_bundles": self.tools.get_missed_bundle_opportunities(),
            "development_count": len(self.tools.get_all_developments()),
        }

    # ------------------------------------------------------------------
    # Main streaming entry point
    # ------------------------------------------------------------------

    def chat_completion(self, user_query: str) -> Generator[str, None, None]:
        """
        Streams a structured JSON response from the LLM, with Oakfield data
        injected as context. The response schema matches the frontend
        BlockRenderer expectations.
        """
        # 1. Fetch context from DB (oakfield_* tables only)
        context = self._build_context(user_query)

        # 2. Build prompt
        system_prompt = f"""
ROLE:
You are the 'Oakfield Strategist', an AI analyst for a UK homebuilder.
Your job is to analyse option basket performance, margin health, and bundle upsell opportunities
across Oakfield's residential developments.

OAKFIELD CONTEXT (from live database):
{json.dumps(context, default=str, indent=2)}

USER QUERY:
"{user_query}"

STRICT RULES:
1. OUTPUT: You must output ONLY valid JSON. No markdown. No preamble.
2. GROUNDING: Use only the numbers from OAKFIELD CONTEXT above. Do not invent data.
3. If OAKFIELD CONTEXT contains no relevant data, say so clearly in a summary block.
4. VISUALISATION:
   - Use 'bar' charts for comparing developments or categories.
   - Use 'pie' charts for share/distribution breakdowns.
   - Use 'area' charts for trends over time (only if time-series data is present).
   - Use 'table' blocks for itemised lists (e.g. missed bundle opportunities).
5. FOCUS: You analyse margin performance and bundle upsell opportunities — NOT KPIs,
   market signals, or strategic objectives (those belong to other products).

RESPONSE SCHEMA (JSON):
{{
    "type": "analysis_response",
    "title": "Short, specific headline",
    "blocks": [
        {{
            "type": "summary",
            "text": "Concise analysis using bullet points (\\n- Point 1\\n- Point 2)"
        }},
        {{
            "type": "metrics",
            "items": [
                {{ "label": "Avg Margin %", "value": "32%", "change": "+2%" }}
            ]
        }},
        {{
            "type": "chart",
            "title": "Margin by Development",
            "chartType": "bar",
            "data": [ {{ "name": "Oakfield Meadows", "value": 34.2 }} ],
            "color": "emerald"
        }},
        {{
            "type": "table",
            "title": "Missed Bundle Opportunities",
            "columns": ["Plot", "Development", "Triggered Bundles", "Missed Revenue"],
            "rows": [
                ["P-001", "Oakfield Meadows", "Premium Kitchen Pack", "£1,200"]
            ]
        }},
        {{
            "type": "recommendation",
            "title": "Action Required",
            "text": "Specific recommendation...",
            "actions": [
                {{ "label": "View Baskets", "route": "/oakfield/baskets", "type": "navigation" }}
            ]
        }}
    ]
}}
"""

        messages = [
            {"role": "system", "content": "You are a JSON-only Oakfield homebuilder analyst."},
            {"role": "user", "content": system_prompt},
        ]

        # 3. Stream from LLM
        full_response = ""
        try:
            for chunk in llm_service.stream_chat(messages):
                full_response += chunk
                yield chunk
        except Exception as e:
            error_payload = json.dumps({
                "type": "analysis_response",
                "title": "System Error",
                "blocks": [
                    {
                        "type": "summary",
                        "text": f"The Oakfield Strategist encountered an error: {str(e)}"
                    }
                ],
            })
            yield error_payload