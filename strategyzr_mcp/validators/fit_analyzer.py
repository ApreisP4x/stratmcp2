"""
Fit analysis between Value Proposition Canvas and Business Model Canvas.

Analyzes:
- Problem-Solution Fit: Does the VPC address real customer problems?
- Product-Market Fit: Is there market evidence the solution is wanted?
- Business Model Fit: Is the BMC aligned with the VPC?
"""

from typing import Any

from ..models.common import Recommendation
from ..models.vpc import VPCInput, FitScore
from ..models.bmc import BMCInput


class FitAnalyzer:
    """
    Analyzes fit between VPC and BMC, and within each canvas.

    Based on Osterwalder's fit progression:
    1. Problem-Solution Fit (VPC internal)
    2. Product-Market Fit (VPC + market evidence)
    3. Business Model Fit (VPC + BMC alignment)
    """

    def analyze_vpc_fit(self, vpc: VPCInput) -> FitScore:
        """Analyze internal fit within a VPC."""
        problem_solution = self._calculate_problem_solution_fit(vpc)
        product_market = self._calculate_product_market_indicators(vpc)
        pain_coverage = self._calculate_pain_coverage(vpc)
        gain_coverage = self._calculate_gain_coverage(vpc)

        overall = (problem_solution + product_market + pain_coverage + gain_coverage) / 4

        return FitScore(
            problem_solution_fit=problem_solution,
            product_market_fit_indicators=product_market,
            pain_coverage=pain_coverage,
            gain_coverage=gain_coverage,
            overall_fit=overall
        )

    def _calculate_problem_solution_fit(self, vpc: VPCInput) -> float:
        """
        Calculate how well the value map addresses the customer profile.

        Problem-Solution Fit = Evidence that your value proposition
        addresses jobs, pains, and gains that customers care about.
        """
        score = 0.0
        max_score = 100.0

        # Check job relevance (do we address important jobs?)
        if vpc.customer_jobs:
            important_jobs = [j for j in vpc.customer_jobs if j.importance >= 4]
            job_importance_ratio = len(important_jobs) / len(vpc.customer_jobs)
            score += job_importance_ratio * 25

        # Check pain-reliever alignment
        if vpc.customer_pains and vpc.pain_relievers:
            pain_texts = {p.description.lower() for p in vpc.customer_pains}
            addressed_pains = set()
            for reliever in vpc.pain_relievers:
                # Check if reliever addresses any known pain
                for pain in pain_texts:
                    if pain in reliever.addresses_pain.lower() or reliever.addresses_pain.lower() in pain:
                        addressed_pains.add(pain)

            # Also count high effectiveness relievers
            high_effectiveness = [r for r in vpc.pain_relievers if r.effectiveness >= 4]
            relief_quality = len(high_effectiveness) / len(vpc.pain_relievers) if vpc.pain_relievers else 0

            coverage_score = (len(addressed_pains) / len(pain_texts)) * 20 if pain_texts else 0
            quality_score = relief_quality * 15
            score += coverage_score + quality_score

        # Check gain-creator alignment
        if vpc.customer_gains and vpc.gain_creators:
            gain_texts = {g.description.lower() for g in vpc.customer_gains}
            created_gains = set()
            for creator in vpc.gain_creators:
                for gain in gain_texts:
                    if gain in creator.creates_gain.lower() or creator.creates_gain.lower() in gain:
                        created_gains.add(gain)

            high_effectiveness = [c for c in vpc.gain_creators if c.effectiveness >= 4]
            creation_quality = len(high_effectiveness) / len(vpc.gain_creators) if vpc.gain_creators else 0

            coverage_score = (len(created_gains) / len(gain_texts)) * 20 if gain_texts else 0
            quality_score = creation_quality * 10
            score += coverage_score + quality_score

        # Check product-service centrality
        if vpc.products_services:
            core_products = [p for p in vpc.products_services if p.importance >= 4]
            product_focus = len(core_products) / len(vpc.products_services) if vpc.products_services else 0
            score += product_focus * 10

        return min(score, max_score)

    def _calculate_product_market_indicators(self, vpc: VPCInput) -> float:
        """
        Calculate indicators of potential product-market fit.

        Note: True PMF requires market evidence (sales, retention).
        This calculates theoretical indicators based on the canvas.
        """
        score = 0.0

        # High-intensity pains being addressed = strong PMF indicator
        if vpc.customer_pains and vpc.pain_relievers:
            extreme_pains = [p for p in vpc.customer_pains if p.intensity >= 4]
            if extreme_pains:
                # Check if we have high-effectiveness relievers
                strong_relievers = [r for r in vpc.pain_relievers if r.effectiveness >= 4]
                ratio = len(strong_relievers) / len(extreme_pains) if extreme_pains else 0
                score += min(ratio * 40, 40)

        # Required/expected gains being created = table stakes met
        if vpc.customer_gains and vpc.gain_creators:
            required_gains = [g for g in vpc.customer_gains if g.gain_type.value in ["required", "expected"]]
            if required_gains:
                strong_creators = [c for c in vpc.gain_creators if c.effectiveness >= 4]
                ratio = len(strong_creators) / len(required_gains) if required_gains else 0
                score += min(ratio * 30, 30)

        # Frequent pains = higher market need
        if vpc.customer_pains:
            frequent_pains = [p for p in vpc.customer_pains if p.frequency in ["often", "always"]]
            frequency_ratio = len(frequent_pains) / len(vpc.customer_pains)
            score += frequency_ratio * 20

        # Differentiation indicator (competitors listed = market awareness)
        if vpc.competitors:
            score += 10

        return min(score, 100.0)

    def _calculate_pain_coverage(self, vpc: VPCInput) -> float:
        """Calculate percentage of pains addressed by pain relievers."""
        if not vpc.customer_pains or not vpc.pain_relievers:
            return 0.0

        pains_addressed = 0
        for pain in vpc.customer_pains:
            for reliever in vpc.pain_relievers:
                if (pain.description.lower() in reliever.addresses_pain.lower() or
                        reliever.addresses_pain.lower() in pain.description.lower()):
                    pains_addressed += 1
                    break

        return (pains_addressed / len(vpc.customer_pains)) * 100

    def _calculate_gain_coverage(self, vpc: VPCInput) -> float:
        """Calculate percentage of gains addressed by gain creators."""
        if not vpc.customer_gains or not vpc.gain_creators:
            return 0.0

        gains_created = 0
        for gain in vpc.customer_gains:
            for creator in vpc.gain_creators:
                if (gain.description.lower() in creator.creates_gain.lower() or
                        creator.creates_gain.lower() in gain.description.lower()):
                    gains_created += 1
                    break

        return (gains_created / len(vpc.customer_gains)) * 100

    def analyze_vpc_bmc_fit(self, vpc: VPCInput, bmc: BMCInput) -> dict[str, Any]:
        """
        Analyze alignment between VPC and BMC.

        Business Model Fit = VPC is supported by a viable, scalable business model.
        """
        alignment_issues = []
        alignment_strengths = []
        fit_score = 0.0

        # 1. Check if VPC target segment matches BMC customer segments
        vpc_segment = vpc.target_segment.lower()
        bmc_segments = [s.name.lower() for s in bmc.customer_segments]

        segment_match = any(vpc_segment in seg or seg in vpc_segment for seg in bmc_segments)
        if segment_match:
            fit_score += 20
            alignment_strengths.append("VPC target segment aligns with BMC customer segments")
        else:
            alignment_issues.append(f"VPC target segment '{vpc.target_segment}' not found in BMC segments")

        # 2. Check if VPC products/services appear in BMC value propositions
        vpc_products = {p.name.lower() for p in vpc.products_services}
        bmc_vp_descriptions = {vp.description.lower() for vp in bmc.value_propositions}

        product_alignment = sum(
            1 for product in vpc_products
            if any(product in vp for vp in bmc_vp_descriptions)
        )
        if product_alignment > 0:
            fit_score += min(product_alignment * 10, 20)
            alignment_strengths.append(f"{product_alignment} VPC products reflected in BMC value propositions")
        else:
            alignment_issues.append("VPC products/services not reflected in BMC value propositions")

        # 3. Check if channels can deliver the value proposition
        channel_coverage = len(bmc.channels) >= 2
        primary_channels = [c for c in bmc.channels if c.is_primary]
        if channel_coverage and primary_channels:
            fit_score += 15
            alignment_strengths.append("BMC has adequate channel coverage")
        elif channel_coverage:
            fit_score += 10
            alignment_issues.append("Consider identifying primary channels")
        else:
            alignment_issues.append("BMC needs more channel diversity")

        # 4. Check if key resources can support value delivery
        resource_types = {r.resource_type.value for r in bmc.key_resources}
        if len(resource_types) >= 2:
            fit_score += 15
            alignment_strengths.append("Diverse key resources support value delivery")
        else:
            alignment_issues.append("Consider diversifying key resources")

        # 5. Check if key activities align with value creation
        activity_types = {a.activity_type.value for a in bmc.key_activities}
        if activity_types:
            fit_score += 15
            alignment_strengths.append("Key activities defined for value delivery")

        # 6. Check revenue model viability
        if bmc.revenue_streams:
            recurring = [r for r in bmc.revenue_streams if r.is_recurring]
            if recurring:
                fit_score += 15
                alignment_strengths.append("Revenue model includes recurring streams")
            else:
                fit_score += 10
                alignment_issues.append("Consider adding recurring revenue streams")

        return {
            "fit_score": min(fit_score, 100.0),
            "alignment_strengths": alignment_strengths,
            "alignment_issues": alignment_issues,
            "recommendation": self._generate_fit_recommendation(fit_score, alignment_issues)
        }

    def _generate_fit_recommendation(self, fit_score: float, issues: list[str]) -> str:
        """Generate overall fit recommendation."""
        if fit_score >= 80:
            return "Strong VPC-BMC alignment. Focus on execution and validation."
        elif fit_score >= 60:
            return "Good alignment with some gaps. Address alignment issues to strengthen the business model."
        elif fit_score >= 40:
            return "Moderate alignment. Review the connection between your value proposition and business model."
        else:
            return "Weak alignment. Significant work needed to connect VPC and BMC. Consider redesigning."

    def generate_fit_recommendations(
        self,
        vpc: VPCInput,
        bmc: BMCInput | None,
        vpc_fit: FitScore,
        bmc_fit: dict[str, Any] | None
    ) -> list[Recommendation]:
        """Generate recommendations to improve fit."""
        recommendations = []

        # VPC internal fit recommendations
        if vpc_fit.problem_solution_fit < 60:
            recommendations.append(Recommendation(
                priority=1,
                category="Problem-Solution Fit",
                description="Strengthen the connection between customer pains and pain relievers",
                rationale="Low problem-solution fit indicates your solution may not address real problems"
            ))

        if vpc_fit.pain_coverage < 70:
            recommendations.append(Recommendation(
                priority=2,
                category="Pain Coverage",
                description="Add pain relievers to address uncovered customer pains",
                rationale=f"Only {vpc_fit.pain_coverage:.0f}% of pains are addressed"
            ))

        if vpc_fit.gain_coverage < 70:
            recommendations.append(Recommendation(
                priority=2,
                category="Gain Coverage",
                description="Add gain creators to address uncovered customer gains",
                rationale=f"Only {vpc_fit.gain_coverage:.0f}% of gains are created"
            ))

        # VPC-BMC fit recommendations
        if bmc_fit and bmc_fit["fit_score"] < 60:
            recommendations.append(Recommendation(
                priority=1,
                category="Business Model Fit",
                description="Align your business model with your value proposition",
                rationale="Low fit score indicates disconnect between VPC and BMC"
            ))

            # Add specific issue-based recommendations
            for issue in bmc_fit.get("alignment_issues", [])[:2]:
                recommendations.append(Recommendation(
                    priority=2,
                    category="Alignment",
                    description=f"Address: {issue}",
                    rationale="Identified misalignment between VPC and BMC"
                ))

        return recommendations


class CompetitorAnalyzer:
    """
    Analyzes competitive positioning based on VPC comparison.
    """

    def analyze_competitors(
        self,
        company_vpc: VPCInput,
        competitor_vpcs: list[dict[str, Any]],
        market_context: str | None = None
    ) -> dict[str, Any]:
        """
        Analyze competitive positioning.

        Args:
            company_vpc: Your company's VPC
            competitor_vpcs: List of competitor VPCs (simplified dicts)
            market_context: Optional market context

        Returns:
            Competitive analysis with positioning recommendations
        """
        analysis = {
            "your_strengths": [],
            "your_weaknesses": [],
            "differentiation_opportunities": [],
            "competitive_threats": [],
            "positioning_recommendations": []
        }

        # Identify your key pain relievers
        your_pain_focus = {r.addresses_pain.lower() for r in company_vpc.pain_relievers}
        your_gain_focus = {c.creates_gain.lower() for c in company_vpc.gain_creators}

        # Compare with each competitor
        competitor_overlaps = []
        for comp in competitor_vpcs:
            comp_name = comp.get("name", "Competitor")
            comp_pains = set(p.lower() for p in comp.get("pain_relievers", []))
            comp_gains = set(g.lower() for g in comp.get("gain_creators", []))

            pain_overlap = len(your_pain_focus & comp_pains)
            gain_overlap = len(your_gain_focus & comp_gains)

            competitor_overlaps.append({
                "name": comp_name,
                "pain_overlap": pain_overlap,
                "gain_overlap": gain_overlap,
                "total_overlap": pain_overlap + gain_overlap
            })

        # Sort by overlap (highest threat first)
        competitor_overlaps.sort(key=lambda x: x["total_overlap"], reverse=True)

        # Identify strengths (unique pain relievers)
        all_competitor_pains = set()
        for comp in competitor_vpcs:
            all_competitor_pains.update(p.lower() for p in comp.get("pain_relievers", []))

        unique_pains = your_pain_focus - all_competitor_pains
        if unique_pains:
            analysis["your_strengths"].append(
                f"Unique pain relief in: {', '.join(list(unique_pains)[:3])}"
            )
            analysis["differentiation_opportunities"].append(
                "Emphasize your unique pain relievers in marketing"
            )

        # Identify weaknesses (competitor advantages)
        competitor_only_pains = all_competitor_pains - your_pain_focus
        if competitor_only_pains:
            analysis["your_weaknesses"].append(
                f"Competitors address pains you don't: {', '.join(list(competitor_only_pains)[:3])}"
            )

        # Competitive threats
        for comp in competitor_overlaps[:2]:  # Top 2 overlapping competitors
            if comp["total_overlap"] > 3:
                analysis["competitive_threats"].append(
                    f"{comp['name']}: High overlap ({comp['total_overlap']} areas)"
                )

        # Positioning recommendations
        if unique_pains:
            analysis["positioning_recommendations"].append(
                "Position around your unique value - areas competitors don't address"
            )

        if competitor_only_pains:
            analysis["positioning_recommendations"].append(
                "Consider expanding to address gaps where competitors have advantage"
            )

        # Difficult to copy assessment
        digital_products = [p for p in company_vpc.products_services if p.is_digital]
        intangible = [p for p in company_vpc.products_services if not p.is_tangible]

        copy_difficulty = "Low"
        if len(digital_products) >= 2 or len(intangible) >= 2:
            copy_difficulty = "Medium"
        if len(digital_products) >= 2 and len(intangible) >= 2:
            copy_difficulty = "High"

        analysis["copy_difficulty"] = copy_difficulty

        return analysis
