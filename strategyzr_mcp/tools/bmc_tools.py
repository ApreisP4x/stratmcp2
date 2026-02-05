"""
BMC (Business Model Canvas) tools.
"""

from typing import Any

from ..models.common import ResponseFormat, BusinessStage
from ..models.bmc import BMCInput, BMCOutput
from ..models.vpc import VPCInput
from ..validators.quality_scorer import BMCAttractivenessScorer
from ..validators.fit_analyzer import FitAnalyzer


def create_bmc(bmc_input: BMCInput, vpc_data: VPCInput | None = None) -> BMCOutput:
    """
    Create a Business Model Canvas with structured validation and scoring.

    Takes structured input for all 9 BMC building blocks,
    validates the data, computes attractiveness score,
    and returns a complete BMC with recommendations.

    Args:
        bmc_input: The BMC input data
        vpc_data: Optional VPC for alignment checking
    """
    # Score and validate
    scorer = BMCAttractivenessScorer()
    attractiveness_score = scorer.score(bmc_input)
    validation = scorer.validate(bmc_input)
    recommendations = scorer.generate_recommendations(bmc_input, attractiveness_score)

    # VPC alignment check if provided
    vpc_alignment = None
    if vpc_data:
        fit_analyzer = FitAnalyzer()
        vpc_alignment = fit_analyzer.analyze_vpc_bmc_fit(vpc_data, bmc_input)

        # Add alignment-based recommendations
        if vpc_alignment["fit_score"] < 60:
            from ..models.common import Recommendation
            recommendations.append(Recommendation(
                priority=1,
                category="VPC-BMC Alignment",
                description="Strengthen alignment between value proposition and business model",
                rationale=f"Current alignment score: {vpc_alignment['fit_score']:.1f}%"
            ))

    # Generate markdown output if requested
    markdown_output = None
    if bmc_input.response_format == ResponseFormat.MARKDOWN:
        markdown_output = _generate_bmc_markdown(
            bmc_input, attractiveness_score, validation, recommendations, vpc_alignment
        )

    return BMCOutput(
        company_name=bmc_input.company_name,
        industry=bmc_input.industry,
        business_stage=bmc_input.business_stage,
        customer_segments=bmc_input.customer_segments,
        value_propositions=bmc_input.value_propositions,
        channels=bmc_input.channels,
        customer_relationships=bmc_input.customer_relationships,
        revenue_streams=bmc_input.revenue_streams,
        key_resources=bmc_input.key_resources,
        key_activities=bmc_input.key_activities,
        key_partnerships=bmc_input.key_partnerships,
        cost_structure=bmc_input.cost_structure,
        attractiveness_score=attractiveness_score,
        validation=validation,
        recommendations=recommendations,
        vpc_alignment=vpc_alignment,
        markdown_output=markdown_output,
    )


def _generate_bmc_markdown(
    bmc_input: BMCInput,
    attractiveness_score: Any,
    validation: Any,
    recommendations: list,
    vpc_alignment: dict | None,
) -> str:
    """Generate markdown representation of the BMC."""
    lines = [
        f"# Business Model Canvas: {bmc_input.company_name}",
        f"**Industry:** {bmc_input.industry} | **Stage:** {bmc_input.business_stage.value.title()}",
        "",
        "---",
        "",
    ]

    # Create the 9-block layout representation
    lines.extend([
        "## The 9 Building Blocks",
        "",
        "### Customer Segments",
        "*Who are the most important customers?*",
        "",
    ])
    for segment in bmc_input.customer_segments:
        primary = " ⭐" if segment.is_primary else ""
        lines.append(f"- **{segment.name}**{primary} ({segment.segment_type})")
        lines.append(f"  - {segment.description}")
        if segment.size_estimate:
            lines.append(f"  - Size: {segment.size_estimate}")

    lines.extend(["", "### Value Propositions", "*What value do we deliver?*", ""])
    for vp in bmc_input.value_propositions:
        lines.append(f"- **For {vp.target_segment}:** {vp.description}")
        lines.append(f"  - Type: {vp.value_type}")
        if vp.differentiation:
            lines.append(f"  - Differentiation: {vp.differentiation}")

    lines.extend(["", "### Channels", "*How do we reach customers?*", ""])
    for channel in bmc_input.channels:
        primary = " ⭐" if channel.is_primary else ""
        phases = ", ".join(p.value for p in channel.phases)
        lines.append(f"- **{channel.name}**{primary} ({channel.channel_type})")
        lines.append(f"  - Phases: {phases}")

    lines.extend(["", "### Customer Relationships", "*How do we interact with customers?*", ""])
    for rel in bmc_input.customer_relationships:
        lines.append(f"- **{rel.segment}:** {rel.relationship_type.value.replace('_', ' ').title()}")
        lines.append(f"  - Motivation: {rel.motivation}")
        if rel.description:
            lines.append(f"  - {rel.description}")

    lines.extend(["", "### Revenue Streams", "*How do we make money?*", ""])
    for rev in bmc_input.revenue_streams:
        recurring = " 🔄" if rev.is_recurring else ""
        lines.append(f"- **{rev.name}**{recurring}")
        lines.append(f"  - From: {rev.source_segment}")
        lines.append(f"  - Type: {rev.revenue_type.value.replace('_', ' ').title()}")
        lines.append(f"  - Pricing: {rev.pricing_mechanism.value.replace('_', ' ').title()}")
        if rev.percentage_of_revenue:
            lines.append(f"  - ~{rev.percentage_of_revenue:.0f}% of revenue")

    lines.extend(["", "### Key Resources", "*What assets do we need?*", ""])
    for resource in bmc_input.key_resources:
        owned = "owned" if resource.is_owned else "accessed"
        lines.append(f"- **{resource.name}** ({resource.resource_type.value}, {owned})")
        lines.append(f"  - Criticality: {'█' * resource.criticality}{'░' * (5 - resource.criticality)} {resource.criticality}/5")
        lines.append(f"  - {resource.description}")

    lines.extend(["", "### Key Activities", "*What activities are essential?*", ""])
    for activity in bmc_input.key_activities:
        lines.append(f"- **{activity.name}** ({activity.activity_type.value.replace('_', ' ').title()})")
        lines.append(f"  - Frequency: {activity.frequency}")
        lines.append(f"  - {activity.description}")

    lines.extend(["", "### Key Partnerships", "*Who are our key partners?*", ""])
    for partner in bmc_input.key_partnerships:
        lines.append(f"- **{partner.partner_name}** ({partner.partnership_type.replace('_', ' ')})")
        lines.append(f"  - Motivation: {partner.motivation}")
        if partner.key_activities:
            lines.append(f"  - Supports: {', '.join(partner.key_activities)}")
        if partner.key_resources:
            lines.append(f"  - Provides: {', '.join(partner.key_resources)}")

    lines.extend(["", "### Cost Structure", "*What are our main costs?*", ""])
    for cost in bmc_input.cost_structure:
        key = " 💰" if cost.is_key_cost else ""
        lines.append(f"- **{cost.name}**{key} ({cost.cost_type.value})")
        lines.append(f"  - {cost.description}")
        if cost.percentage_of_costs:
            lines.append(f"  - ~{cost.percentage_of_costs:.0f}% of costs")

    # Attractiveness Score
    lines.extend([
        "",
        "---",
        "",
        "## Business Model Attractiveness",
        "",
        f"**Total Score: {attractiveness_score.total_score:.1f} / 35 ({(attractiveness_score.total_score / 35 * 100):.1f}%)**",
        "",
        "| Dimension | Score |",
        "|-----------|-------|",
        f"| Switching Costs | {'█' * int(attractiveness_score.switching_costs)}{'░' * (5 - int(attractiveness_score.switching_costs))} {attractiveness_score.switching_costs:.1f}/5 |",
        f"| Recurring Revenues | {'█' * int(attractiveness_score.recurring_revenues)}{'░' * (5 - int(attractiveness_score.recurring_revenues))} {attractiveness_score.recurring_revenues:.1f}/5 |",
        f"| Earning vs Spending | {'█' * int(attractiveness_score.earning_vs_spending)}{'░' * (5 - int(attractiveness_score.earning_vs_spending))} {attractiveness_score.earning_vs_spending:.1f}/5 |",
        f"| Cost Structure | {'█' * int(attractiveness_score.cost_structure)}{'░' * (5 - int(attractiveness_score.cost_structure))} {attractiveness_score.cost_structure:.1f}/5 |",
        f"| Others Do Work | {'█' * int(attractiveness_score.others_do_work)}{'░' * (5 - int(attractiveness_score.others_do_work))} {attractiveness_score.others_do_work:.1f}/5 |",
        f"| Scalability | {'█' * int(attractiveness_score.scalability)}{'░' * (5 - int(attractiveness_score.scalability))} {attractiveness_score.scalability:.1f}/5 |",
        f"| Protection | {'█' * int(attractiveness_score.protection)}{'░' * (5 - int(attractiveness_score.protection))} {attractiveness_score.protection:.1f}/5 |",
    ])

    # VPC Alignment if provided
    if vpc_alignment:
        lines.extend([
            "",
            "## VPC-BMC Alignment",
            "",
            f"**Alignment Score: {vpc_alignment['fit_score']:.1f}%**",
            "",
            "### Strengths",
        ])
        for strength in vpc_alignment.get("alignment_strengths", []):
            lines.append(f"- ✅ {strength}")

        if vpc_alignment.get("alignment_issues"):
            lines.extend(["", "### Issues"])
            for issue in vpc_alignment["alignment_issues"]:
                lines.append(f"- ⚠️ {issue}")

        lines.extend(["", f"**Recommendation:** {vpc_alignment.get('recommendation', '')}"])

    # Validation
    if validation.warnings or validation.suggestions:
        lines.extend(["", "## Validation Results", ""])
        if validation.warnings:
            lines.append("### Warnings")
            for warning in validation.warnings:
                lines.append(f"- ⚠️ {warning}")
        if validation.suggestions:
            lines.append("### Suggestions")
            for suggestion in validation.suggestions:
                lines.append(f"- 💡 {suggestion}")

    # Recommendations
    if recommendations:
        lines.extend(["", "## Recommendations", ""])
        for rec in recommendations:
            priority_icon = ["🔴", "🟡", "🟢"][rec.priority - 1]
            lines.append(f"### {priority_icon} {rec.category}")
            lines.append(f"**{rec.description}**")
            lines.append(f"*{rec.rationale}*")
            lines.append("")

    return "\n".join(lines)


def get_bmc_template(include_examples: bool = False, include_guidance: bool = True) -> dict[str, Any]:
    """
    Get an empty BMC template with field descriptions.

    Args:
        include_examples: Whether to include example values
        include_guidance: Whether to include filling guidance
    """
    template = {
        "company_name": "",
        "industry": "",
        "business_stage": "idea|startup|growth|mature",
        "customer_segments": [
            {
                "name": "",
                "description": "",
                "segment_type": "mass_market|niche|segmented|diversified|multi_sided",
                "size_estimate": "(optional)",
                "is_primary": False
            }
        ],
        "value_propositions": [
            {
                "description": "",
                "target_segment": "",
                "value_type": "newness|performance|customization|design|brand|price|cost_reduction|risk_reduction|accessibility|convenience",
                "differentiation": "(optional)",
                "vpc_reference": "(optional)"
            }
        ],
        "channels": [
            {
                "name": "",
                "channel_type": "direct|indirect|owned|partner",
                "phases": ["awareness", "evaluation", "purchase", "delivery", "after_sales"],
                "is_primary": False,
                "description": "(optional)"
            }
        ],
        "customer_relationships": [
            {
                "segment": "",
                "relationship_type": "personal_assistance|dedicated_assistance|self_service|automated|communities|co_creation",
                "motivation": "acquisition|retention|upselling",
                "description": "(optional)"
            }
        ],
        "revenue_streams": [
            {
                "name": "",
                "source_segment": "",
                "revenue_type": "asset_sale|usage_fee|subscription|lending|licensing|brokerage|advertising",
                "pricing_mechanism": "fixed|dynamic|auction|market_dependent|volume_dependent|negotiation",
                "percentage_of_revenue": "(optional, 0-100)",
                "is_recurring": False
            }
        ],
        "key_resources": [
            {
                "name": "",
                "resource_type": "physical|intellectual|human|financial",
                "description": "",
                "is_owned": True,
                "criticality": "1-5"
            }
        ],
        "key_activities": [
            {
                "name": "",
                "activity_type": "production|problem_solving|platform",
                "description": "",
                "frequency": "daily|weekly|monthly|ongoing|as_needed"
            }
        ],
        "key_partnerships": [
            {
                "partner_name": "",
                "partnership_type": "strategic_alliance|coopetition|joint_venture|buyer_supplier",
                "motivation": "optimization|risk_reduction|resource_acquisition",
                "key_activities": [],
                "key_resources": []
            }
        ],
        "cost_structure": [
            {
                "name": "",
                "cost_type": "fixed|variable",
                "description": "",
                "is_key_cost": False,
                "percentage_of_costs": "(optional, 0-100)"
            }
        ],
        "vpc_reference": "(optional)",
        "response_format": "markdown"
    }

    if include_guidance:
        template["_guidance"] = {
            "customer_segments": "Define 1-3 distinct customer segments. Mark the primary segment. Use segment types from Osterwalder's framework.",
            "value_propositions": "Each segment needs at least one value proposition. Reference your VPC if available.",
            "channels": "Cover all 5 phases of the customer journey. Identify which channels are primary.",
            "customer_relationships": "Define relationship type for each segment. Consider acquisition vs retention goals.",
            "revenue_streams": "Identify all revenue sources. Recurring revenue increases business model attractiveness.",
            "key_resources": "List resources essential for value delivery. Rate criticality (1-5).",
            "key_activities": "Focus on activities that drive your value proposition. Categorize by type.",
            "key_partnerships": "Strategic partnerships can reduce risk and provide key resources/activities.",
            "cost_structure": "Identify major costs. Variable costs provide more flexibility.",
            "attractiveness_goal": "Aim for scores >3 in each attractiveness dimension, especially scalability and recurring revenue."
        }

    if include_examples:
        template["_example"] = {
            "company_name": "CloudTask Pro",
            "industry": "B2B SaaS",
            "business_stage": "startup",
            "customer_segments": [
                {
                    "name": "Remote Team Managers",
                    "description": "Managers of distributed teams at growing startups",
                    "segment_type": "niche",
                    "size_estimate": "500K potential users globally",
                    "is_primary": True
                }
            ],
            "value_propositions": [
                {
                    "description": "AI-powered task coordination for distributed teams",
                    "target_segment": "Remote Team Managers",
                    "value_type": "convenience",
                    "differentiation": "Only solution with timezone-aware AI scheduling"
                }
            ],
            "revenue_streams": [
                {
                    "name": "SaaS Subscription",
                    "source_segment": "Remote Team Managers",
                    "revenue_type": "subscription",
                    "pricing_mechanism": "fixed",
                    "is_recurring": True,
                    "percentage_of_revenue": 90
                }
            ]
        }

    return template
