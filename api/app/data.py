from app.models import (
    ActivityRecord,
    ClientRecord,
    DashboardOverview,
    MetricCard,
    MonthlyTouchRecord,
    PromptTemplateRecord,
    UserProfile,
)


def build_dashboard_overview() -> DashboardOverview:
    current_user = UserProfile(
        id="user_1",
        full_name="Ariana Cole",
        role="admin",
        email="ariana@northstargrowth.com",
    )

    metrics = [
        MetricCard(id="briefs", label="Briefs Ready", value="18", detail="4 due in 24h", trend="up"),
        MetricCard(id="risk", label="Retention Risks", value="6", detail="2 escalated this week", trend="down"),
        MetricCard(id="approvals", label="Pending Approvals", value="14", detail="Tasks and recap emails", trend="stable"),
        MetricCard(id="qa", label="QA Coverage", value="92%", detail="Last 30 day audit rate", trend="up"),
    ]

    clients = [
        ClientRecord(
            id="client_1",
            name="BluePeak Dental",
            owner="Ariana Cole",
            health_score=84,
            risk_level="Low",
            next_touch_at="Jun 18 · 11:00 AM",
            top_opportunity="GBP optimization",
        ),
        ClientRecord(
            id="client_2",
            name="Northwind Legal",
            owner="Mila Grant",
            health_score=67,
            risk_level="Medium",
            next_touch_at="Jun 19 · 2:30 PM",
            top_opportunity="Lead qualification automation",
        ),
        ClientRecord(
            id="client_3",
            name="Harbor Ortho",
            owner="Ariana Cole",
            health_score=51,
            risk_level="High",
            next_touch_at="Jun 20 · 9:00 AM",
            top_opportunity="Retention rescue plan",
        ),
    ]

    monthly_touches = [
        MonthlyTouchRecord(
            id="touch_1",
            client_name="BluePeak Dental",
            scheduled_at="Jun 18 · 11:00 AM",
            stage="Pre-Meeting Intelligence",
            owner="Ariana Cole",
        ),
        MonthlyTouchRecord(
            id="touch_2",
            client_name="Northwind Legal",
            scheduled_at="Jun 19 · 2:30 PM",
            stage="Task Approval",
            owner="Mila Grant",
        ),
        MonthlyTouchRecord(
            id="touch_3",
            client_name="Harbor Ortho",
            scheduled_at="Jun 20 · 9:00 AM",
            stage="QA Audit",
            owner="Ariana Cole",
        ),
    ]

    prompt_templates = [
        PromptTemplateRecord(
            id="prompt_1",
            name="Monthly Touch Brief Structure",
            category="Monthly Touch",
            version="v12",
            status="Active",
            provider="Claude",
        ),
        PromptTemplateRecord(
            id="prompt_2",
            name="Ticket Extraction Rules",
            category="Follow-Up",
            version="v6",
            status="Active",
            provider="Gemini",
        ),
        PromptTemplateRecord(
            id="prompt_3",
            name="Retention Analysis",
            category="Retention",
            version="v4",
            status="Draft",
            provider="Mixed",
        ),
    ]

    activity = [
        ActivityRecord(
            id="activity_1",
            title="Brief generated for BluePeak Dental",
            description="30 day unified context compiled from Search Console, GBP, Ads, and ClickUp.",
            at="2m ago",
            kind="brief",
        ),
        ActivityRecord(
            id="activity_2",
            title="Ownership sync completed",
            description="ClickUp Client Health Tracker matched 112 of 115 account manager assignments.",
            at="16m ago",
            kind="sync",
        ),
        ActivityRecord(
            id="activity_3",
            title="Revenue leakage flagged",
            description="Northwind Legal has unresolved lead follow-up gaps and ad spend inefficiency.",
            at="24m ago",
            kind="risk",
        ),
        ActivityRecord(
            id="activity_4",
            title="QA score posted",
            description="Harbor Ortho scored 88 with coaching notes on discovery depth and action framing.",
            at="48m ago",
            kind="qa",
        ),
    ]

    return DashboardOverview(
        tenant_name="Northstar Growth",
        current_user=current_user,
        metrics=metrics,
        clients=clients,
        monthly_touches=monthly_touches,
        prompt_templates=prompt_templates,
        activity=activity,
    )
