"""
Analysis tools for canvas validation, fit analysis, and competitor comparison.
"""

from typing import Any, Literal

from ..models.common import ValidationResult, Recommendation
from ..models.vpc import VPCInput, FitScore
from ..models.bmc import BMCInput
from ..validators.quality_scorer import VPCQualityScorer, BMCAttractivenessScorer
from ..validators.fit_analyzer import FitAnalyzer, CompetitorAnalyzer


def validate_canvas(
    canvas_type: Literal["vpc", "bmc"],
    canvas_data: dict[str, Any],
    check_vpc_alignment: bool = False,
    vpc_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Validate and score an existing canvas against best practices.

    Args:
        canvas_type: Type of canvas ("vpc" or "bmc")
        canvas_data: The canvas data to validate
        check_vpc_alignment: For BMC, whether to check VPC alignment
        vpc_data: VPC data for alignment check (required if check_vpc_alignment is True)

    Returns:
        Validation results including errors, warnings, quality score, and recommendations
    """
    result = {
        "canvas_type": canvas_type,
        "validation": None,
        "quality_score": None,
        "gap_analysis": [],
        "recommendations": [],
        "vpc_alignment": None,
    }

    if canvas_type == "vpc":
        # Parse and validate VPC
        try:
            vpc_input = VPCInput(**canvas_data)
        except Exception as e:
            result["validation"] = ValidationResult(
                is_valid=False,
                errors=[f"Invalid VPC data: {str(e)}"],
                warnings=[],
                suggestions=[]
            )
            return result

        scorer = VPCQualityScorer()
        result["validation"] = scorer.validate(vpc_input)
        quality_score = scorer.score(vpc_input)
        result["quality_score"] = {
            "total": quality_score.total_score,
            "max": quality_score.max_score,
            "percentage": quality_score.percentage,
            "breakdown": quality_score.breakdown,
        }
        result["recommendations"] = [
            r.model_dump() for r in scorer.generate_recommendations(vpc_input, quality_score)
        ]

        # Gap analysis
        result["gap_analysis"] = _analyze_vpc_gaps(vpc_input)

    elif canvas_type == "bmc":
        # Parse and validate BMC
        try:
            bmc_input = BMCInput(**canvas_data)
        except Exception as e:
            result["validation"] = ValidationResult(
                is_valid=False,
                errors=[f"Invalid BMC data: {str(e)}"],
                warnings=[],
                suggestions=[]
            )
            return result

        scorer = BMCAttractivenessScorer()
        result["validation"] = scorer.validate(bmc_input)
        attractiveness = scorer.score(bmc_input)
        result["quality_score"] = {
            "switching_costs": attractiveness.switching_costs,
            "recurring_revenues": attractiveness.recurring_revenues,
            "earning_vs_spending": attractiveness.earning_vs_spending,
            "cost_structure": attractiveness.cost_structure,
            "others_do_work": attractiveness.others_do_work,
            "scalability": attractiveness.scalability,
            "protection": attractiveness.protection,
            "total": attractiveness.total_score,
            "max": 35,
            "percentage": (attractiveness.total_score / 35) * 100,
        }
        result["recommendations"] = [
            r.model_dump() for r in scorer.generate_recommendations(bmc_input, attractiveness)
        ]

        # Gap analysis
        result["gap_analysis"] = _analyze_bmc_gaps(bmc_input)

        # VPC alignment check
        if check_vpc_alignment and vpc_data:
            try:
                vpc_input = VPCInput(**vpc_data)
                fit_analyzer = FitAnalyzer()
                result["vpc_alignment"] = fit_analyzer.analyze_vpc_bmc_fit(vpc_input, bmc_input)
            except Exception as e:
                result["vpc_alignment"] = {"error": f"Could not analyze VPC alignment: {str(e)}"}

    return result


def _analyze_vpc_gaps(vpc: VPCInput) -> list[str]:
    """Identify gaps in a VPC."""
    gaps = []

    # Check for unaddressed pains
    pain_texts = {p.description.lower() for p in vpc.customer_pains}
    addressed = set()
    for reliever in vpc.pain_relievers:
        for pain in pain_texts:
            if pain in reliever.addresses_pain.lower() or reliever.addresses_pain.lower() in pain:
                addressed.add(pain)

    unaddressed_pains = pain_texts - addressed
    if unaddressed_pains:
        gaps.append(f"Unaddressed pains: {len(unaddressed_pains)} of {len(pain_texts)}")

    # Check for uncreated gains
    gain_texts = {g.description.lower() for g in vpc.customer_gains}
    created = set()
    for creator in vpc.gain_creators:
        for gain in gain_texts:
            if gain in creator.creates_gain.lower() or creator.creates_gain.lower() in gain:
                created.add(gain)

    uncreated_gains = gain_texts - created
    if uncreated_gains:
        gaps.append(f"Uncreated gains: {len(uncreated_gains)} of {len(gain_texts)}")

    # Check job type coverage
    job_types = {j.job_type.value for j in vpc.customer_jobs}
    missing_types = {"functional", "social", "emotional"} - job_types
    if missing_types:
        gaps.append(f"Missing job types: {', '.join(missing_types)}")

    # Check for low-effectiveness items
    low_relievers = [r for r in vpc.pain_relievers if r.effectiveness <= 2]
    if low_relievers:
        gaps.append(f"Low-effectiveness pain relievers: {len(low_relievers)}")

    low_creators = [c for c in vpc.gain_creators if c.effectiveness <= 2]
    if low_creators:
        gaps.append(f"Low-effectiveness gain creators: {len(low_creators)}")

    return gaps


def _analyze_bmc_gaps(bmc: BMCInput) -> list[str]:
    """Identify gaps in a BMC."""
    gaps = []

    # Check for segments without value propositions
    segment_names = {s.name.lower() for s in bmc.customer_segments}
    vp_targets = {vp.target_segment.lower() for vp in bmc.value_propositions}
    orphan_segments = segment_names - vp_targets
    if orphan_segments:
        gaps.append(f"Segments without value propositions: {len(orphan_segments)}")

    # Check channel phase coverage
    covered_phases = set()
    for channel in bmc.channels:
        covered_phases.update(p.value for p in channel.phases)

    all_phases = {"awareness", "evaluation", "purchase", "delivery", "after_sales"}
    missing_phases = all_phases - covered_phases
    if missing_phases:
        gaps.append(f"Missing channel phases: {', '.join(missing_phases)}")

    # Check for no recurring revenue
    recurring = [r for r in bmc.revenue_streams if r.is_recurring]
    if not recurring:
        gaps.append("No recurring revenue streams identified")

    # Check for low-criticality resources
    critical_resources = [r for r in bmc.key_resources if r.criticality >= 4]
    if not critical_resources:
        gaps.append("No highly critical resources identified")

    # Check partnership coverage
    if len(bmc.key_partnerships) < 2:
        gaps.append("Limited partnership network (fewer than 2 partners)")

    return gaps


def analyze_fit(
    vpc_data: dict[str, Any],
    bmc_data: dict[str, Any] | None = None,
    analysis_depth: Literal["quick", "detailed"] = "detailed",
) -> dict[str, Any]:
    """
    Analyze fit within VPC and between VPC and BMC.

    Args:
        vpc_data: VPC data to analyze
        bmc_data: Optional BMC data for cross-canvas analysis
        analysis_depth: "quick" for basic scores, "detailed" for full analysis

    Returns:
        Fit analysis results
    """
    result = {
        "vpc_fit": None,
        "bmc_fit": None,
        "vpc_bmc_alignment": None,
        "recommendations": [],
    }

    # Parse VPC
    try:
        vpc_input = VPCInput(**vpc_data)
    except Exception as e:
        return {"error": f"Invalid VPC data: {str(e)}"}

    fit_analyzer = FitAnalyzer()

    # VPC internal fit
    vpc_fit = fit_analyzer.analyze_vpc_fit(vpc_input)
    result["vpc_fit"] = {
        "problem_solution_fit": vpc_fit.problem_solution_fit,
        "product_market_fit_indicators": vpc_fit.product_market_fit_indicators,
        "pain_coverage": vpc_fit.pain_coverage,
        "gain_coverage": vpc_fit.gain_coverage,
        "overall_fit": vpc_fit.overall_fit,
    }

    bmc_input = None
    bmc_alignment = None

    # BMC analysis if provided
    if bmc_data:
        try:
            bmc_input = BMCInput(**bmc_data)

            # VPC-BMC alignment
            bmc_alignment = fit_analyzer.analyze_vpc_bmc_fit(vpc_input, bmc_input)
            result["vpc_bmc_alignment"] = bmc_alignment

        except Exception as e:
            result["bmc_error"] = f"Invalid BMC data: {str(e)}"

    # Generate recommendations
    if analysis_depth == "detailed":
        recommendations = fit_analyzer.generate_fit_recommendations(
            vpc_input, bmc_input, vpc_fit, bmc_alignment
        )
        result["recommendations"] = [r.model_dump() for r in recommendations]

        # Add interpretation
        result["interpretation"] = _interpret_fit_scores(vpc_fit, bmc_alignment)

    return result


def _interpret_fit_scores(vpc_fit: FitScore, bmc_alignment: dict | None) -> dict[str, str]:
    """Provide human-readable interpretation of fit scores."""
    interpretation = {}

    # Problem-Solution Fit interpretation
    psf = vpc_fit.problem_solution_fit
    if psf >= 80:
        interpretation["problem_solution_fit"] = "Strong - Your solution clearly addresses customer problems"
    elif psf >= 60:
        interpretation["problem_solution_fit"] = "Good - Solution addresses most problems, some gaps remain"
    elif psf >= 40:
        interpretation["problem_solution_fit"] = "Moderate - Significant alignment work needed"
    else:
        interpretation["problem_solution_fit"] = "Weak - Reconsider problem-solution alignment"

    # PMF indicators interpretation
    pmf = vpc_fit.product_market_fit_indicators
    if pmf >= 70:
        interpretation["product_market_indicators"] = "Promising - Strong theoretical indicators for market fit"
    elif pmf >= 50:
        interpretation["product_market_indicators"] = "Encouraging - Good foundation, validate with customers"
    else:
        interpretation["product_market_indicators"] = "Early stage - More customer discovery needed"

    # Coverage interpretation
    if vpc_fit.pain_coverage >= 80 and vpc_fit.gain_coverage >= 80:
        interpretation["coverage"] = "Comprehensive - Most customer needs are addressed"
    elif vpc_fit.pain_coverage >= 60 or vpc_fit.gain_coverage >= 60:
        interpretation["coverage"] = "Partial - Some important needs may be unaddressed"
    else:
        interpretation["coverage"] = "Limited - Many customer needs not yet addressed"

    # BMC alignment interpretation
    if bmc_alignment:
        score = bmc_alignment.get("fit_score", 0)
        if score >= 80:
            interpretation["business_model_fit"] = "Strong - Business model well-aligned with value proposition"
        elif score >= 60:
            interpretation["business_model_fit"] = "Good - Minor alignment adjustments needed"
        elif score >= 40:
            interpretation["business_model_fit"] = "Moderate - Business model needs refinement"
        else:
            interpretation["business_model_fit"] = "Weak - Significant business model work needed"

    return interpretation


def compare_competitors(
    company_name: str,
    your_vpc: dict[str, Any],
    competitors: list[dict[str, Any]],
    market_context: str | None = None,
) -> dict[str, Any]:
    """
    Compare your value proposition against competitors.

    Args:
        company_name: Your company name
        your_vpc: Your VPC data
        competitors: List of competitor VPCs (simplified format with name, pain_relievers, gain_creators)
        market_context: Optional market context description

    Returns:
        Competitive analysis with positioning recommendations
    """
    # Parse your VPC
    try:
        vpc_input = VPCInput(**your_vpc)
    except Exception as e:
        return {"error": f"Invalid VPC data: {str(e)}"}

    analyzer = CompetitorAnalyzer()

    # Run analysis
    analysis = analyzer.analyze_competitors(
        vpc_input,
        competitors,
        market_context
    )

    # Add summary
    analysis["company_name"] = company_name
    analysis["competitors_analyzed"] = len(competitors)
    analysis["market_context"] = market_context

    # Generate positioning statement
    if analysis["your_strengths"]:
        analysis["positioning_statement"] = _generate_positioning_statement(
            company_name,
            analysis["your_strengths"],
            analysis.get("copy_difficulty", "Medium")
        )

    return analysis


def _generate_positioning_statement(
    company_name: str,
    strengths: list[str],
    copy_difficulty: str
) -> str:
    """Generate a positioning statement based on analysis."""
    if not strengths:
        return f"{company_name} should identify unique differentiators to establish clear market positioning."

    strength_summary = strengths[0] if len(strengths) == 1 else f"{strengths[0]} and {strengths[1]}"

    defensibility = {
        "High": "with strong barriers to imitation",
        "Medium": "with moderate defensibility",
        "Low": "but should work on building defensible advantages"
    }.get(copy_difficulty, "")

    return f"{company_name} can position around {strength_summary.lower()}, {defensibility}."
