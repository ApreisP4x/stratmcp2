"""
Quality scoring based on Osterwalder's frameworks.

VPC Quality: 10 Characteristics of Great Value Propositions (max 50 points)
BMC Attractiveness: 6 Dimensions of Business Model Attractiveness (max 30 points)
"""

from typing import Any

from ..models.common import (
    QualityScore,
    ValidationResult,
    Recommendation,
    RelationshipType,
    ResourceType,
    ActivityType,
    RevenueType,
    CostType,
    ChannelPhase,
)
from ..models.vpc import VPCInput, CustomerProfile, ValueMap, FitScore
from ..models.bmc import BMCInput, AttractivenessScore


class VPCQualityScorer:
    """
    Scores a Value Proposition Canvas against the 10 Characteristics
    of Great Value Propositions (Osterwalder).

    Each characteristic is scored 1-5, for a maximum of 50 points.
    """

    CHARACTERISTICS = [
        "embedded_in_great_business_model",
        "focus_on_most_important_jobs_pains_gains",
        "focus_on_unsatisfied_jobs_pains_gains",
        "converge_on_few_things_done_well",
        "address_functional_emotional_social_jobs",
        "align_with_customer_success_metrics",
        "focus_on_high_impact_jobs_pains_gains",
        "differentiate_from_competition",
        "outperform_competition_substantially",
        "difficult_to_copy",
    ]

    def score(self, vpc_input: VPCInput) -> QualityScore:
        """Score the VPC against the 10 characteristics."""
        breakdown = {}

        # 1. Embedded in great business model (check completeness)
        breakdown["embedded_in_great_business_model"] = self._score_completeness(vpc_input)

        # 2. Focus on most important jobs, pains, gains
        breakdown["focus_on_most_important"] = self._score_importance_focus(vpc_input)

        # 3. Focus on unsatisfied jobs, pains, gains
        breakdown["focus_on_unsatisfied"] = self._score_unsatisfied_focus(vpc_input)

        # 4. Converge on few things done well
        breakdown["converge_on_few_things"] = self._score_convergence(vpc_input)

        # 5. Address functional, emotional, and social jobs
        breakdown["address_all_job_types"] = self._score_job_type_coverage(vpc_input)

        # 6. Align with customer success metrics
        breakdown["align_with_success_metrics"] = self._score_alignment(vpc_input)

        # 7. Focus on high-impact jobs, pains, gains
        breakdown["focus_on_high_impact"] = self._score_high_impact(vpc_input)

        # 8. Differentiate from competition
        breakdown["differentiate_from_competition"] = self._score_differentiation(vpc_input)

        # 9. Outperform competition substantially
        breakdown["outperform_competition"] = self._score_outperformance(vpc_input)

        # 10. Difficult to copy
        breakdown["difficult_to_copy"] = self._score_copyability(vpc_input)

        return QualityScore.create(breakdown, max_per_criterion=5.0)

    def _score_completeness(self, vpc: VPCInput) -> float:
        """Score based on canvas completeness."""
        score = 1.0  # Base score

        # Check balance between customer profile and value map
        jobs_count = len(vpc.customer_jobs)
        pains_count = len(vpc.customer_pains)
        gains_count = len(vpc.customer_gains)

        relievers_count = len(vpc.pain_relievers)
        creators_count = len(vpc.gain_creators)
        products_count = len(vpc.products_services)

        # Good balance: 3-5 items per category
        if 3 <= jobs_count <= 5:
            score += 1.0
        if 3 <= pains_count <= 5 and 3 <= gains_count <= 5:
            score += 1.0
        if relievers_count >= pains_count * 0.6:  # Cover at least 60% of pains
            score += 1.0
        if creators_count >= gains_count * 0.6:  # Cover at least 60% of gains
            score += 1.0

        return min(score, 5.0)

    def _score_importance_focus(self, vpc: VPCInput) -> float:
        """Score based on focus on important items."""
        total_importance = sum(j.importance for j in vpc.customer_jobs)
        avg_importance = total_importance / len(vpc.customer_jobs) if vpc.customer_jobs else 0

        # Higher average importance = better focus
        return min(avg_importance, 5.0)

    def _score_unsatisfied_focus(self, vpc: VPCInput) -> float:
        """Score based on addressing unsatisfied needs."""
        # Check pain intensity and reliever effectiveness
        high_intensity_pains = [p for p in vpc.customer_pains if p.intensity >= 4]
        high_effectiveness_relievers = [r for r in vpc.pain_relievers if r.effectiveness >= 4]

        if not high_intensity_pains:
            return 3.0  # No extreme pains identified

        coverage = len(high_effectiveness_relievers) / len(high_intensity_pains)
        return min(1.0 + coverage * 4.0, 5.0)

    def _score_convergence(self, vpc: VPCInput) -> float:
        """Score based on focusing on few things done well."""
        # Fewer products/services with higher importance = better
        core_products = [p for p in vpc.products_services if p.importance >= 4]

        if len(core_products) <= 3 and len(vpc.products_services) <= 5:
            return 5.0
        elif len(core_products) <= 5:
            return 4.0
        elif len(vpc.products_services) <= 7:
            return 3.0
        else:
            return 2.0

    def _score_job_type_coverage(self, vpc: VPCInput) -> float:
        """Score based on covering functional, social, and emotional jobs."""
        job_types = set(j.job_type.value for j in vpc.customer_jobs)

        if len(job_types) == 3:
            return 5.0
        elif len(job_types) == 2:
            return 3.5
        else:
            return 2.0

    def _score_alignment(self, vpc: VPCInput) -> float:
        """Score based on alignment between pains/gains and relievers/creators."""
        # Check if pain relievers reference actual pains
        pain_descriptions = {p.description.lower() for p in vpc.customer_pains}
        relievers_aligned = sum(
            1 for r in vpc.pain_relievers
            if any(pain in r.addresses_pain.lower() for pain in pain_descriptions)
            or r.addresses_pain.lower() in pain_descriptions
        )

        alignment_ratio = relievers_aligned / len(vpc.pain_relievers) if vpc.pain_relievers else 0
        return 1.0 + alignment_ratio * 4.0

    def _score_high_impact(self, vpc: VPCInput) -> float:
        """Score based on focusing on high-impact items."""
        # High impact = high importance jobs + high intensity pains + high relevance gains
        high_impact_jobs = [j for j in vpc.customer_jobs if j.importance >= 4]
        high_impact_pains = [p for p in vpc.customer_pains if p.intensity >= 4]
        high_impact_gains = [g for g in vpc.customer_gains if g.relevance >= 4]

        total_high_impact = len(high_impact_jobs) + len(high_impact_pains) + len(high_impact_gains)
        total_items = len(vpc.customer_jobs) + len(vpc.customer_pains) + len(vpc.customer_gains)

        ratio = total_high_impact / total_items if total_items > 0 else 0
        return 1.0 + ratio * 4.0

    def _score_differentiation(self, vpc: VPCInput) -> float:
        """Score based on differentiation potential."""
        # If competitors listed, better differentiation analysis possible
        if vpc.competitors and len(vpc.competitors) > 0:
            return 4.0  # Can analyze differentiation

        # Check for unique value elements
        unique_products = [p for p in vpc.products_services if p.importance >= 4]
        return min(2.0 + len(unique_products), 5.0)

    def _score_outperformance(self, vpc: VPCInput) -> float:
        """Score based on outperformance indicators."""
        # High effectiveness in relievers and creators indicates outperformance
        avg_reliever_effectiveness = (
            sum(r.effectiveness for r in vpc.pain_relievers) / len(vpc.pain_relievers)
            if vpc.pain_relievers else 0
        )
        avg_creator_effectiveness = (
            sum(c.effectiveness for c in vpc.gain_creators) / len(vpc.gain_creators)
            if vpc.gain_creators else 0
        )

        avg_effectiveness = (avg_reliever_effectiveness + avg_creator_effectiveness) / 2
        return min(avg_effectiveness, 5.0)

    def _score_copyability(self, vpc: VPCInput) -> float:
        """Score based on how difficult it is to copy."""
        # Intellectual products and complex solutions are harder to copy
        digital_products = [p for p in vpc.products_services if p.is_digital]
        intangible_products = [p for p in vpc.products_services if not p.is_tangible]

        base_score = 2.0
        if digital_products:
            base_score += 1.0
        if intangible_products:
            base_score += 1.0
        if len(vpc.products_services) >= 3:
            base_score += 0.5

        return min(base_score, 5.0)

    def validate(self, vpc_input: VPCInput) -> ValidationResult:
        """Validate the VPC for completeness and consistency."""
        errors = []
        warnings = []
        suggestions = []

        # Check minimum requirements
        if len(vpc_input.customer_jobs) < 3:
            warnings.append("Consider adding more customer jobs (3-5 recommended)")

        if len(vpc_input.customer_pains) < 3:
            warnings.append("Consider adding more customer pains (3-5 recommended)")

        if len(vpc_input.customer_gains) < 3:
            warnings.append("Consider adding more customer gains (3-5 recommended)")

        # Check job type diversity
        job_types = set(j.job_type.value for j in vpc_input.customer_jobs)
        if len(job_types) < 2:
            suggestions.append("Consider adding jobs of different types (functional, social, emotional)")

        # Check pain-reliever coverage
        pains_addressed = set()
        for reliever in vpc_input.pain_relievers:
            pains_addressed.add(reliever.addresses_pain.lower())

        pain_descriptions = [p.description.lower() for p in vpc_input.customer_pains]
        unaddressed = [p for p in pain_descriptions if p not in pains_addressed]
        if unaddressed:
            suggestions.append(f"Consider adding pain relievers for: {', '.join(unaddressed[:2])}")

        # Check gain-creator coverage
        gains_created = set()
        for creator in vpc_input.gain_creators:
            gains_created.add(creator.creates_gain.lower())

        gain_descriptions = [g.description.lower() for g in vpc_input.customer_gains]
        uncreated = [g for g in gain_descriptions if g not in gains_created]
        if uncreated:
            suggestions.append(f"Consider adding gain creators for: {', '.join(uncreated[:2])}")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions
        )

    def generate_recommendations(self, vpc_input: VPCInput, score: QualityScore) -> list[Recommendation]:
        """Generate improvement recommendations based on scoring."""
        recommendations = []

        # Find lowest-scoring characteristics
        sorted_scores = sorted(score.breakdown.items(), key=lambda x: x[1])

        for criterion, criterion_score in sorted_scores[:3]:  # Top 3 areas to improve
            if criterion_score < 4.0:
                rec = self._get_recommendation_for_criterion(criterion, criterion_score)
                if rec:
                    recommendations.append(rec)

        return recommendations

    def _get_recommendation_for_criterion(self, criterion: str, score: float) -> Recommendation | None:
        """Get specific recommendation for a criterion."""
        recommendations_map = {
            "embedded_in_great_business_model": Recommendation(
                priority=1,
                category="Business Model",
                description="Ensure your VPC is connected to a comprehensive business model",
                rationale="A great value proposition needs a great business model to deliver it"
            ),
            "focus_on_most_important": Recommendation(
                priority=1,
                category="Customer Focus",
                description="Prioritize the most important customer jobs",
                rationale="Focus resources on what matters most to customers"
            ),
            "address_all_job_types": Recommendation(
                priority=2,
                category="Job Coverage",
                description="Address functional, social, and emotional jobs",
                rationale="Customers have multiple types of jobs beyond just functional tasks"
            ),
            "differentiate_from_competition": Recommendation(
                priority=1,
                category="Differentiation",
                description="Analyze competitors and identify unique positioning",
                rationale="Clear differentiation is essential for market success"
            ),
            "difficult_to_copy": Recommendation(
                priority=2,
                category="Defensibility",
                description="Build in elements that are difficult for competitors to copy",
                rationale="Sustainable advantage requires defensibility"
            ),
        }

        return recommendations_map.get(criterion)


class BMCAttractivenessScorer:
    """
    Scores a Business Model Canvas on attractiveness dimensions.

    Based on Osterwalder's Business Model Attractiveness framework:
    - Switching costs
    - Recurring revenues
    - Earning before spending
    - Cost structure
    - Getting others to do the work
    - Scalability
    - Protection from competition
    """

    def score(self, bmc_input: BMCInput) -> AttractivenessScore:
        """Score the BMC on attractiveness dimensions."""
        switching_costs = self._score_switching_costs(bmc_input)
        recurring_revenues = self._score_recurring_revenues(bmc_input)
        earning_vs_spending = self._score_earning_vs_spending(bmc_input)
        cost_structure = self._score_cost_structure(bmc_input)
        others_do_work = self._score_others_do_work(bmc_input)
        scalability = self._score_scalability(bmc_input)
        protection = self._score_protection(bmc_input)

        total = (
            switching_costs + recurring_revenues + earning_vs_spending +
            cost_structure + others_do_work + scalability + protection
        )

        return AttractivenessScore(
            switching_costs=switching_costs,
            recurring_revenues=recurring_revenues,
            earning_vs_spending=earning_vs_spending,
            cost_structure=cost_structure,
            others_do_work=others_do_work,
            scalability=scalability,
            protection=protection,
            total_score=total
        )

    def _score_switching_costs(self, bmc: BMCInput) -> float:
        """Score based on customer switching costs."""
        score = 1.0

        # Strong relationships increase switching costs
        dedicated_relationships = [
            r for r in bmc.customer_relationships
            if r.relationship_type in [RelationshipType.DEDICATED_ASSISTANCE, RelationshipType.CO_CREATION]
        ]
        if dedicated_relationships:
            score += 2.0

        # Intellectual resources create lock-in
        intellectual_resources = [
            r for r in bmc.key_resources
            if r.resource_type == ResourceType.INTELLECTUAL
        ]
        if intellectual_resources:
            score += 1.5

        # Multiple channels create habit
        if len(bmc.channels) >= 3:
            score += 0.5

        return min(score, 5.0)

    def _score_recurring_revenues(self, bmc: BMCInput) -> float:
        """Score based on recurring revenue streams."""
        recurring_streams = [r for r in bmc.revenue_streams if r.is_recurring]
        subscription_streams = [
            r for r in bmc.revenue_streams
            if r.revenue_type == RevenueType.SUBSCRIPTION
        ]

        score = 1.0
        if recurring_streams:
            score += len(recurring_streams) * 1.5
        if subscription_streams:
            score += 1.0

        return min(score, 5.0)

    def _score_earning_vs_spending(self, bmc: BMCInput) -> float:
        """Score based on earning before spending ratio."""
        # Check for prepayment models
        prepay_revenues = [
            r for r in bmc.revenue_streams
            if r.revenue_type in [RevenueType.SUBSCRIPTION, RevenueType.LICENSING]
        ]

        # Check for variable costs (better for cash flow)
        variable_costs = [c for c in bmc.cost_structure if c.cost_type == CostType.VARIABLE]

        score = 2.0  # Base score
        if prepay_revenues:
            score += 1.5
        if len(variable_costs) > len(bmc.cost_structure) / 2:
            score += 1.5

        return min(score, 5.0)

    def _score_cost_structure(self, bmc: BMCInput) -> float:
        """Score based on cost structure efficiency."""
        fixed_costs = [c for c in bmc.cost_structure if c.cost_type == CostType.FIXED]
        variable_costs = [c for c in bmc.cost_structure if c.cost_type == CostType.VARIABLE]

        # More variable costs = more flexibility
        if not bmc.cost_structure:
            return 2.0

        variable_ratio = len(variable_costs) / len(bmc.cost_structure)
        return 1.0 + variable_ratio * 4.0

    def _score_others_do_work(self, bmc: BMCInput) -> float:
        """Score based on leverage from partners and customers."""
        score = 1.0

        # Strong partnership network
        if len(bmc.key_partnerships) >= 3:
            score += 2.0

        # Community or co-creation relationships
        community_relationships = [
            r for r in bmc.customer_relationships
            if r.relationship_type in [RelationshipType.COMMUNITIES, RelationshipType.CO_CREATION]
        ]
        if community_relationships:
            score += 2.0

        return min(score, 5.0)

    def _score_scalability(self, bmc: BMCInput) -> float:
        """Score based on scalability potential."""
        score = 1.0

        # Digital/intellectual resources scale better
        scalable_resources = [
            r for r in bmc.key_resources
            if r.resource_type in [ResourceType.INTELLECTUAL, ResourceType.FINANCIAL]
        ]
        if scalable_resources:
            score += 1.5

        # Platform activities scale well
        platform_activities = [
            a for a in bmc.key_activities
            if a.activity_type == ActivityType.PLATFORM
        ]
        if platform_activities:
            score += 2.0

        # Automated relationships scale
        automated_relationships = [
            r for r in bmc.customer_relationships
            if r.relationship_type in [RelationshipType.AUTOMATED, RelationshipType.SELF_SERVICE]
        ]
        if automated_relationships:
            score += 1.0

        return min(score, 5.0)

    def _score_protection(self, bmc: BMCInput) -> float:
        """Score based on protection from competition."""
        score = 1.0

        # Intellectual resources provide protection
        intellectual_resources = [
            r for r in bmc.key_resources
            if r.resource_type == ResourceType.INTELLECTUAL and r.criticality >= 4
        ]
        if intellectual_resources:
            score += 2.0

        # Strong partnerships create barriers
        strategic_partnerships = [
            p for p in bmc.key_partnerships
            if p.partnership_type in ["strategic_alliance", "joint_venture"]
        ]
        if strategic_partnerships:
            score += 1.5

        # Niche segments are easier to protect
        niche_segments = [
            s for s in bmc.customer_segments
            if s.segment_type == "niche"
        ]
        if niche_segments:
            score += 0.5

        return min(score, 5.0)

    def validate(self, bmc_input: BMCInput) -> ValidationResult:
        """Validate the BMC for completeness and consistency."""
        errors = []
        warnings = []
        suggestions = []

        # Check for orphaned value propositions
        segment_names = {s.name.lower() for s in bmc_input.customer_segments}
        for vp in bmc_input.value_propositions:
            if vp.target_segment.lower() not in segment_names:
                warnings.append(f"Value proposition targets unknown segment: {vp.target_segment}")

        # Check for segments without value propositions
        vp_targets = {vp.target_segment.lower() for vp in bmc_input.value_propositions}
        for segment in bmc_input.customer_segments:
            if segment.name.lower() not in vp_targets:
                warnings.append(f"Segment '{segment.name}' has no value proposition")

        # Check for revenue stream coverage
        revenue_segments = {r.source_segment.lower() for r in bmc_input.revenue_streams}
        for segment in bmc_input.customer_segments:
            if segment.name.lower() not in revenue_segments:
                suggestions.append(f"Consider adding revenue stream for segment: {segment.name}")

        # Check channel phase coverage
        all_phases = set()
        for channel in bmc_input.channels:
            all_phases.update(channel.phases)

        missing_phases = set(ChannelPhase) - all_phases
        if missing_phases:
            phase_names = [p.value for p in missing_phases]
            suggestions.append(f"Consider adding channels for phases: {', '.join(phase_names)}")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions
        )

    def generate_recommendations(self, bmc_input: BMCInput, score: AttractivenessScore) -> list[Recommendation]:
        """Generate improvement recommendations based on attractiveness score."""
        recommendations = []

        # Check each dimension and recommend improvements
        if score.recurring_revenues < 3.0:
            recommendations.append(Recommendation(
                priority=1,
                category="Revenue",
                description="Add recurring revenue streams (subscriptions, memberships)",
                rationale="Recurring revenue provides predictability and higher lifetime value"
            ))

        if score.switching_costs < 3.0:
            recommendations.append(Recommendation(
                priority=2,
                category="Retention",
                description="Increase switching costs through deeper integrations or relationships",
                rationale="Higher switching costs improve customer retention"
            ))

        if score.scalability < 3.0:
            recommendations.append(Recommendation(
                priority=1,
                category="Growth",
                description="Increase scalability through automation or platform elements",
                rationale="Scalable business models can grow without proportional cost increases"
            ))

        if score.protection < 3.0:
            recommendations.append(Recommendation(
                priority=2,
                category="Defensibility",
                description="Build intellectual property or exclusive partnerships",
                rationale="Protection from competition ensures long-term viability"
            ))

        return recommendations
