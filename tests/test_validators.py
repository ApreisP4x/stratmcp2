"""
Tests for validators and scorers.
"""

import pytest

from strategyzr_mcp.models.common import JobType, GainType, ResourceType, ActivityType, RelationshipType, RevenueType, PricingMechanism, CostType, ChannelPhase, BusinessStage
from strategyzr_mcp.models.vpc import (
    CustomerJob,
    CustomerPain,
    CustomerGain,
    ProductService,
    PainReliever,
    GainCreator,
    VPCInput,
)
from strategyzr_mcp.models.bmc import (
    CustomerSegment,
    ValueProposition,
    Channel,
    CustomerRelationship,
    RevenueStream,
    KeyResource,
    KeyActivity,
    KeyPartnership,
    CostItem,
    BMCInput,
)
from strategyzr_mcp.validators.quality_scorer import VPCQualityScorer, BMCAttractivenessScorer
from strategyzr_mcp.validators.fit_analyzer import FitAnalyzer


def create_sample_vpc() -> VPCInput:
    """Create a sample VPC for testing."""
    return VPCInput(
        company_name="TestCo",
        target_segment="Remote team managers",
        customer_jobs=[
            CustomerJob(
                description="Coordinate team tasks",
                job_type=JobType.FUNCTIONAL,
                importance=5
            ),
            CustomerJob(
                description="Be seen as effective leader",
                job_type=JobType.SOCIAL,
                importance=4
            ),
            CustomerJob(
                description="Feel in control of projects",
                job_type=JobType.EMOTIONAL,
                importance=3
            ),
        ],
        customer_pains=[
            CustomerPain(
                description="Tasks fall through cracks",
                intensity=5,
                frequency="often"
            ),
            CustomerPain(
                description="Timezone coordination is hard",
                intensity=4,
                frequency="always"
            ),
            CustomerPain(
                description="Status updates take too long",
                intensity=3,
                frequency="often"
            ),
        ],
        customer_gains=[
            CustomerGain(
                description="Clear visibility into workload",
                gain_type=GainType.REQUIRED,
                relevance=5
            ),
            CustomerGain(
                description="Automated progress tracking",
                gain_type=GainType.EXPECTED,
                relevance=4
            ),
            CustomerGain(
                description="Real-time collaboration",
                gain_type=GainType.DESIRED,
                relevance=3
            ),
        ],
        products_services=[
            ProductService(
                name="TaskSync",
                description="AI-powered task coordination",
                importance=5,
                is_digital=True
            ),
            ProductService(
                name="TimeZone Scheduler",
                description="Smart meeting scheduler",
                importance=4,
                is_digital=True
            ),
        ],
        pain_relievers=[
            PainReliever(
                description="AI monitors and flags at-risk tasks",
                addresses_pain="Tasks fall through cracks",
                effectiveness=5
            ),
            PainReliever(
                description="Automatic timezone-aware scheduling",
                addresses_pain="Timezone coordination is hard",
                effectiveness=4
            ),
            PainReliever(
                description="Auto-generated status reports",
                addresses_pain="Status updates take too long",
                effectiveness=4
            ),
        ],
        gain_creators=[
            GainCreator(
                description="Real-time dashboard with workload view",
                creates_gain="Clear visibility into workload",
                effectiveness=5
            ),
            GainCreator(
                description="Automatic progress tracking",
                creates_gain="Automated progress tracking",
                effectiveness=4
            ),
            GainCreator(
                description="Integrated collaboration tools",
                creates_gain="Real-time collaboration",
                effectiveness=3
            ),
        ],
        competitors=["Asana", "Monday.com", "ClickUp"]
    )


def create_sample_bmc() -> BMCInput:
    """Create a sample BMC for testing."""
    return BMCInput(
        company_name="TestCo",
        industry="B2B SaaS",
        business_stage=BusinessStage.STARTUP,
        customer_segments=[
            CustomerSegment(
                name="Remote Team Managers",
                description="Managers of distributed teams at growing startups",
                segment_type="niche",
                is_primary=True
            ),
        ],
        value_propositions=[
            ValueProposition(
                description="AI-powered task coordination for distributed teams",
                target_segment="Remote Team Managers",
                value_type="convenience",
                differentiation="Only solution with timezone-aware AI"
            ),
        ],
        channels=[
            Channel(
                name="Website",
                channel_type="owned",
                phases=[ChannelPhase.AWARENESS, ChannelPhase.EVALUATION, ChannelPhase.PURCHASE],
                is_primary=True
            ),
            Channel(
                name="Product Hunt",
                channel_type="partner",
                phases=[ChannelPhase.AWARENESS]
            ),
        ],
        customer_relationships=[
            CustomerRelationship(
                segment="Remote Team Managers",
                relationship_type=RelationshipType.SELF_SERVICE,
                motivation="acquisition"
            ),
            CustomerRelationship(
                segment="Remote Team Managers",
                relationship_type=RelationshipType.AUTOMATED,
                motivation="retention"
            ),
        ],
        revenue_streams=[
            RevenueStream(
                name="SaaS Subscription",
                source_segment="Remote Team Managers",
                revenue_type=RevenueType.SUBSCRIPTION,
                pricing_mechanism=PricingMechanism.FIXED,
                is_recurring=True,
                percentage_of_revenue=90
            ),
        ],
        key_resources=[
            KeyResource(
                name="AI Model",
                resource_type=ResourceType.INTELLECTUAL,
                description="Proprietary task prioritization AI",
                criticality=5
            ),
            KeyResource(
                name="Engineering Team",
                resource_type=ResourceType.HUMAN,
                description="Development and ML team",
                criticality=4
            ),
        ],
        key_activities=[
            KeyActivity(
                name="Platform Development",
                activity_type=ActivityType.PLATFORM,
                description="Building and maintaining the platform",
                frequency="ongoing"
            ),
            KeyActivity(
                name="AI Model Training",
                activity_type=ActivityType.PROBLEM_SOLVING,
                description="Improving AI accuracy",
                frequency="weekly"
            ),
        ],
        key_partnerships=[
            KeyPartnership(
                partner_name="Cloud Provider",
                partnership_type="buyer_supplier",
                motivation="optimization",
                key_resources=["Infrastructure"]
            ),
            KeyPartnership(
                partner_name="Calendar APIs",
                partnership_type="strategic_alliance",
                motivation="resource_acquisition",
                key_activities=["Integration"]
            ),
        ],
        cost_structure=[
            CostItem(
                name="Cloud Infrastructure",
                cost_type=CostType.VARIABLE,
                description="AWS/GCP hosting costs",
                is_key_cost=True
            ),
            CostItem(
                name="Salaries",
                cost_type=CostType.FIXED,
                description="Team salaries",
                is_key_cost=True
            ),
        ]
    )


class TestVPCQualityScorer:
    """Tests for VPC quality scoring."""

    def test_score_complete_vpc(self):
        """Test scoring a complete VPC."""
        vpc = create_sample_vpc()
        scorer = VPCQualityScorer()
        score = scorer.score(vpc)

        assert score.total_score > 0
        assert score.max_score == 50.0  # 10 characteristics * 5 points each
        assert 0 <= score.percentage <= 100
        assert len(score.breakdown) == 10

    def test_score_all_job_types_covered(self):
        """Test that all job types coverage gives high score."""
        vpc = create_sample_vpc()
        scorer = VPCQualityScorer()
        score = scorer.score(vpc)

        # Sample VPC has all 3 job types
        assert score.breakdown["address_all_job_types"] == 5.0

    def test_validate_vpc(self):
        """Test VPC validation."""
        vpc = create_sample_vpc()
        scorer = VPCQualityScorer()
        validation = scorer.validate(vpc)

        assert validation.is_valid is True
        assert len(validation.errors) == 0

    def test_validate_vpc_missing_job_types(self):
        """Test validation warns about missing job types."""
        vpc = VPCInput(
            company_name="TestCo",
            target_segment="Test segment",
            customer_jobs=[
                CustomerJob(
                    description="Functional job only",
                    job_type=JobType.FUNCTIONAL,
                    importance=4
                ),
            ],
            customer_pains=[
                CustomerPain(
                    description="Test pain",
                    intensity=3,
                    frequency="sometimes"
                ),
            ],
            customer_gains=[
                CustomerGain(
                    description="Test gain",
                    gain_type=GainType.DESIRED,
                    relevance=3
                ),
            ],
            products_services=[
                ProductService(
                    name="Test Product",
                    description="Test description",
                    importance=4
                ),
            ],
            pain_relievers=[
                PainReliever(
                    description="Relieves test pain",
                    addresses_pain="Test pain",
                    effectiveness=3
                ),
            ],
            gain_creators=[
                GainCreator(
                    description="Creates test gain",
                    creates_gain="Test gain",
                    effectiveness=3
                ),
            ]
        )
        scorer = VPCQualityScorer()
        validation = scorer.validate(vpc)

        # Should have suggestion about job types
        assert any("job" in s.lower() for s in validation.suggestions)

    def test_generate_recommendations(self):
        """Test recommendation generation."""
        vpc = create_sample_vpc()
        scorer = VPCQualityScorer()
        score = scorer.score(vpc)
        recommendations = scorer.generate_recommendations(vpc, score)

        # Should have some recommendations
        assert isinstance(recommendations, list)
        for rec in recommendations:
            assert rec.priority in [1, 2, 3]
            assert rec.category
            assert rec.description
            assert rec.rationale


class TestBMCAttractivenessScorer:
    """Tests for BMC attractiveness scoring."""

    def test_score_complete_bmc(self):
        """Test scoring a complete BMC."""
        bmc = create_sample_bmc()
        scorer = BMCAttractivenessScorer()
        score = scorer.score(bmc)

        assert score.total_score > 0
        assert score.total_score <= 35  # 7 dimensions * 5 points each
        assert score.switching_costs >= 1
        assert score.recurring_revenues >= 1
        assert score.scalability >= 1

    def test_recurring_revenue_boost(self):
        """Test that recurring revenue boosts score."""
        bmc = create_sample_bmc()
        scorer = BMCAttractivenessScorer()
        score = scorer.score(bmc)

        # BMC has recurring subscription
        assert score.recurring_revenues >= 3.0

    def test_scalability_with_platform(self):
        """Test that platform activities boost scalability."""
        bmc = create_sample_bmc()
        scorer = BMCAttractivenessScorer()
        score = scorer.score(bmc)

        # BMC has platform activity type
        assert score.scalability >= 2.0

    def test_validate_bmc(self):
        """Test BMC validation."""
        bmc = create_sample_bmc()
        scorer = BMCAttractivenessScorer()
        validation = scorer.validate(bmc)

        assert validation.is_valid is True

    def test_generate_recommendations(self):
        """Test recommendation generation for BMC."""
        bmc = create_sample_bmc()
        scorer = BMCAttractivenessScorer()
        score = scorer.score(bmc)
        recommendations = scorer.generate_recommendations(bmc, score)

        assert isinstance(recommendations, list)


class TestFitAnalyzer:
    """Tests for fit analysis."""

    def test_vpc_fit_analysis(self):
        """Test VPC internal fit analysis."""
        vpc = create_sample_vpc()
        analyzer = FitAnalyzer()
        fit = analyzer.analyze_vpc_fit(vpc)

        assert fit.problem_solution_fit >= 0
        assert fit.product_market_fit_indicators >= 0
        assert fit.pain_coverage >= 0
        assert fit.gain_coverage >= 0
        assert fit.overall_fit >= 0

    def test_good_pain_coverage(self):
        """Test that addressing all pains gives high coverage."""
        vpc = create_sample_vpc()
        analyzer = FitAnalyzer()
        fit = analyzer.analyze_vpc_fit(vpc)

        # Sample VPC addresses all pains
        assert fit.pain_coverage > 50

    def test_vpc_bmc_alignment(self):
        """Test VPC-BMC alignment analysis."""
        vpc = create_sample_vpc()
        bmc = create_sample_bmc()
        analyzer = FitAnalyzer()

        alignment = analyzer.analyze_vpc_bmc_fit(vpc, bmc)

        assert "fit_score" in alignment
        assert "alignment_strengths" in alignment
        assert "alignment_issues" in alignment
        assert "recommendation" in alignment
        assert alignment["fit_score"] >= 0

    def test_generate_fit_recommendations(self):
        """Test fit-based recommendations."""
        vpc = create_sample_vpc()
        bmc = create_sample_bmc()
        analyzer = FitAnalyzer()

        fit = analyzer.analyze_vpc_fit(vpc)
        alignment = analyzer.analyze_vpc_bmc_fit(vpc, bmc)

        recommendations = analyzer.generate_fit_recommendations(vpc, bmc, fit, alignment)
        assert isinstance(recommendations, list)
