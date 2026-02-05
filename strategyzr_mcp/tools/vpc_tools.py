"""
VPC (Value Proposition Canvas) tools.
"""

import json
from pathlib import Path
from typing import Any

from ..models.common import ResponseFormat
from ..models.vpc import (
    VPCInput,
    VPCOutput,
    CustomerProfile,
    ValueMap,
)
from ..validators.quality_scorer import VPCQualityScorer
from ..validators.fit_analyzer import FitAnalyzer


def create_vpc(vpc_input: VPCInput) -> VPCOutput:
    """
    Create a Value Proposition Canvas with structured validation and scoring.

    Takes structured input about customer profile and value map,
    validates the data, computes fit and quality scores,
    and returns a complete VPC with recommendations.
    """
    # Build the customer profile
    customer_profile = CustomerProfile(
        jobs=vpc_input.customer_jobs,
        pains=vpc_input.customer_pains,
        gains=vpc_input.customer_gains,
    )

    # Build the value map
    value_map = ValueMap(
        products_services=vpc_input.products_services,
        pain_relievers=vpc_input.pain_relievers,
        gain_creators=vpc_input.gain_creators,
    )

    # Score and validate
    scorer = VPCQualityScorer()
    fit_analyzer = FitAnalyzer()

    quality_score = scorer.score(vpc_input)
    validation = scorer.validate(vpc_input)
    fit_score = fit_analyzer.analyze_vpc_fit(vpc_input)
    recommendations = scorer.generate_recommendations(vpc_input, quality_score)

    # Add fit-based recommendations
    fit_recommendations = fit_analyzer.generate_fit_recommendations(
        vpc_input, None, fit_score, None
    )
    recommendations.extend(fit_recommendations)

    # Generate markdown output if requested
    markdown_output = None
    if vpc_input.response_format == ResponseFormat.MARKDOWN:
        markdown_output = _generate_vpc_markdown(
            vpc_input, customer_profile, value_map,
            fit_score, quality_score, validation, recommendations
        )

    return VPCOutput(
        company_name=vpc_input.company_name,
        target_segment=vpc_input.target_segment,
        customer_profile=customer_profile,
        value_map=value_map,
        fit_score=fit_score,
        quality_score=quality_score,
        validation=validation,
        recommendations=recommendations,
        markdown_output=markdown_output,
    )


def _generate_vpc_markdown(
    vpc_input: VPCInput,
    customer_profile: CustomerProfile,
    value_map: ValueMap,
    fit_score: Any,
    quality_score: Any,
    validation: Any,
    recommendations: list,
) -> str:
    """Generate markdown representation of the VPC."""
    lines = [
        f"# Value Proposition Canvas: {vpc_input.company_name}",
        f"**Target Segment:** {vpc_input.target_segment}",
        "",
        "---",
        "",
        "## Customer Profile",
        "",
        "### Customer Jobs",
    ]

    for job in customer_profile.jobs:
        lines.append(f"- **{job.job_type.value.title()}** (Importance: {job.importance}/5): {job.description}")

    lines.extend(["", "### Customer Pains"])
    for pain in customer_profile.pains:
        lines.append(f"- (Intensity: {pain.intensity}/5, {pain.frequency}): {pain.description}")

    lines.extend(["", "### Customer Gains"])
    for gain in customer_profile.gains:
        lines.append(f"- **{gain.gain_type.value.title()}** (Relevance: {gain.relevance}/5): {gain.description}")

    lines.extend([
        "",
        "---",
        "",
        "## Value Map",
        "",
        "### Products & Services",
    ])

    for product in value_map.products_services:
        tags = []
        if product.is_digital:
            tags.append("digital")
        if not product.is_tangible:
            tags.append("intangible")
        tag_str = f" [{', '.join(tags)}]" if tags else ""
        lines.append(f"- **{product.name}** (Importance: {product.importance}/5){tag_str}: {product.description}")

    lines.extend(["", "### Pain Relievers"])
    for reliever in value_map.pain_relievers:
        lines.append(f"- (Effectiveness: {reliever.effectiveness}/5) {reliever.description}")
        lines.append(f"  - *Addresses:* {reliever.addresses_pain}")

    lines.extend(["", "### Gain Creators"])
    for creator in value_map.gain_creators:
        lines.append(f"- (Effectiveness: {creator.effectiveness}/5) {creator.description}")
        lines.append(f"  - *Creates:* {creator.creates_gain}")

    # Fit Score
    lines.extend([
        "",
        "---",
        "",
        "## Fit Assessment",
        "",
        f"| Metric | Score |",
        f"|--------|-------|",
        f"| Problem-Solution Fit | {fit_score.problem_solution_fit:.1f}% |",
        f"| Product-Market Fit Indicators | {fit_score.product_market_fit_indicators:.1f}% |",
        f"| Pain Coverage | {fit_score.pain_coverage:.1f}% |",
        f"| Gain Coverage | {fit_score.gain_coverage:.1f}% |",
        f"| **Overall Fit** | **{fit_score.overall_fit:.1f}%** |",
    ])

    # Quality Score
    lines.extend([
        "",
        "## Quality Assessment (10 Characteristics)",
        "",
        f"**Total Score: {quality_score.total_score:.1f} / {quality_score.max_score:.1f} ({quality_score.percentage:.1f}%)**",
        "",
    ])

    for criterion, score in quality_score.breakdown.items():
        criterion_display = criterion.replace("_", " ").title()
        bar = "█" * int(score) + "░" * (5 - int(score))
        lines.append(f"- {criterion_display}: {bar} {score:.1f}/5")

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


def get_vpc_template(include_examples: bool = False, include_guidance: bool = True) -> dict[str, Any]:
    """
    Get an empty VPC template with field descriptions.

    Args:
        include_examples: Whether to include example values
        include_guidance: Whether to include filling guidance
    """
    template = {
        "company_name": "",
        "target_segment": "",
        "customer_jobs": [
            {
                "description": "",
                "job_type": "functional|social|emotional",
                "importance": "1-5",
                "context": "(optional)"
            }
        ],
        "customer_pains": [
            {
                "description": "",
                "intensity": "1-5",
                "frequency": "rarely|sometimes|often|always",
                "related_job": "(optional)"
            }
        ],
        "customer_gains": [
            {
                "description": "",
                "gain_type": "required|expected|desired|unexpected",
                "relevance": "1-5",
                "related_job": "(optional)"
            }
        ],
        "products_services": [
            {
                "name": "",
                "description": "",
                "importance": "1-5",
                "is_digital": False,
                "is_tangible": True
            }
        ],
        "pain_relievers": [
            {
                "description": "",
                "addresses_pain": "",
                "effectiveness": "1-5",
                "product_service": "(optional)"
            }
        ],
        "gain_creators": [
            {
                "description": "",
                "creates_gain": "",
                "effectiveness": "1-5",
                "product_service": "(optional)"
            }
        ],
        "competitors": [],
        "response_format": "markdown"
    }

    if include_guidance:
        template["_guidance"] = {
            "customer_jobs": "3-5 jobs the customer is trying to get done. Include functional (tasks), social (status), and emotional (feelings) jobs.",
            "customer_pains": "3-5 frustrations, obstacles, or risks the customer faces. Rate intensity (1-5) and frequency.",
            "customer_gains": "3-5 outcomes or benefits the customer wants. Categorize as required, expected, desired, or unexpected.",
            "products_services": "Your products and services. Rate importance to your value proposition (1=peripheral, 5=core).",
            "pain_relievers": "How your products relieve customer pains. Link each to a specific pain.",
            "gain_creators": "How your products create customer gains. Link each to a specific gain.",
            "fit_goal": "Aim for >70% coverage of pains and gains. Focus on high-intensity pains first."
        }

    if include_examples:
        template["_example"] = {
            "company_name": "CloudTask Pro",
            "target_segment": "Remote team managers at growing startups",
            "customer_jobs": [
                {
                    "description": "Coordinate team tasks across time zones",
                    "job_type": "functional",
                    "importance": 5,
                    "context": "Managing 5-20 person distributed teams"
                },
                {
                    "description": "Be seen as an effective leader",
                    "job_type": "social",
                    "importance": 4
                }
            ],
            "customer_pains": [
                {
                    "description": "Tasks fall through the cracks between team members",
                    "intensity": 5,
                    "frequency": "often",
                    "related_job": "Coordinate team tasks across time zones"
                }
            ],
            "customer_gains": [
                {
                    "description": "Clear visibility into team workload and progress",
                    "gain_type": "required",
                    "relevance": 5
                }
            ]
        }

    return template
