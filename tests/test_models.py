"""
Tests for Pydantic models.
"""

import pytest
from pydantic import ValidationError

from strategyzr_mcp.models.common import (
    QualityScore,
    Recommendation,
    ValidationResult,
    JobType,
    GainType,
    BusinessStage,
)
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
    RevenueStream,
    KeyResource,
    BMCInput,
)


class TestCommonModels:
    """Tests for common models."""

    def test_quality_score_create(self):
        """Test QualityScore.create() method."""
        breakdown = {
            "criterion_1": 4.0,
            "criterion_2": 3.5,
            "criterion_3": 5.0,
        }
        score = QualityScore.create(breakdown, max_per_criterion=5.0)

        assert score.total_score == 12.5
        assert score.max_score == 15.0
        assert score.percentage == 83.3
        assert score.breakdown == breakdown

    def test_quality_score_empty_breakdown(self):
        """Test QualityScore with empty breakdown."""
        score = QualityScore.create({})
        assert score.total_score == 0
        assert score.percentage == 0

    def test_recommendation_validation(self):
        """Test Recommendation model validation."""
        rec = Recommendation(
            priority=1,
            category="Test",
            description="Test description",
            rationale="Test rationale"
        )
        assert rec.priority == 1

        with pytest.raises(ValidationError):
            Recommendation(
                priority=5,  # Invalid: must be 1-3
                category="Test",
                description="Test",
                rationale="Test"
            )


class TestVPCModels:
    """Tests for VPC models."""

    def test_customer_job_valid(self):
        """Test valid CustomerJob."""
        job = CustomerJob(
            description="Complete project on time",
            job_type=JobType.FUNCTIONAL,
            importance=5,
            context="Work environment"
        )
        assert job.description == "Complete project on time"
        assert job.job_type == JobType.FUNCTIONAL

    def test_customer_job_empty_description(self):
        """Test CustomerJob with empty description."""
        with pytest.raises(ValidationError):
            CustomerJob(
                description="",
                job_type=JobType.FUNCTIONAL,
                importance=3
            )

    def test_customer_pain_frequency_validation(self):
        """Test CustomerPain frequency validation."""
        pain = CustomerPain(
            description="Tasks fall through cracks",
            intensity=4,
            frequency="often"
        )
        assert pain.frequency == "often"

        with pytest.raises(ValidationError):
            CustomerPain(
                description="Tasks fall through cracks",
                intensity=4,
                frequency="invalid"
            )

    def test_customer_gain_types(self):
        """Test CustomerGain with different types."""
        for gain_type in GainType:
            gain = CustomerGain(
                description="Test gain",
                gain_type=gain_type,
                relevance=3
            )
            assert gain.gain_type == gain_type

    def test_vpc_input_minimal(self):
        """Test VPCInput with minimal valid data."""
        vpc = VPCInput(
            company_name="TestCo",
            target_segment="SMB owners",
            customer_jobs=[
                CustomerJob(
                    description="Manage team tasks",
                    job_type=JobType.FUNCTIONAL,
                    importance=4
                )
            ],
            customer_pains=[
                CustomerPain(
                    description="Tasks get lost",
                    intensity=4,
                    frequency="often"
                )
            ],
            customer_gains=[
                CustomerGain(
                    description="Clear visibility",
                    gain_type=GainType.REQUIRED,
                    relevance=5
                )
            ],
            products_services=[
                ProductService(
                    name="TaskApp",
                    description="Task management app",
                    importance=5
                )
            ],
            pain_relievers=[
                PainReliever(
                    description="Automated reminders",
                    addresses_pain="Tasks get lost",
                    effectiveness=4
                )
            ],
            gain_creators=[
                GainCreator(
                    description="Dashboard view",
                    creates_gain="Clear visibility",
                    effectiveness=5
                )
            ]
        )
        assert vpc.company_name == "TestCo"

    def test_vpc_input_empty_jobs(self):
        """Test VPCInput with no jobs."""
        with pytest.raises(ValidationError):
            VPCInput(
                company_name="TestCo",
                target_segment="SMB owners",
                customer_jobs=[],  # Empty - should fail
                customer_pains=[
                    CustomerPain(
                        description="Test pain",
                        intensity=3,
                        frequency="sometimes"
                    )
                ],
                customer_gains=[
                    CustomerGain(
                        description="Test gain",
                        gain_type=GainType.DESIRED,
                        relevance=3
                    )
                ],
                products_services=[
                    ProductService(
                        name="Test",
                        description="Test product",
                        importance=3
                    )
                ],
                pain_relievers=[
                    PainReliever(
                        description="Test reliever",
                        addresses_pain="Test pain",
                        effectiveness=3
                    )
                ],
                gain_creators=[
                    GainCreator(
                        description="Test creator",
                        creates_gain="Test gain",
                        effectiveness=3
                    )
                ]
            )


class TestBMCModels:
    """Tests for BMC models."""

    def test_customer_segment_valid(self):
        """Test valid CustomerSegment."""
        segment = CustomerSegment(
            name="Enterprise",
            description="Large enterprise customers",
            segment_type="niche",
            is_primary=True
        )
        assert segment.name == "Enterprise"
        assert segment.is_primary is True

    def test_value_proposition_valid(self):
        """Test valid ValueProposition."""
        vp = ValueProposition(
            description="AI-powered productivity",
            target_segment="Enterprise",
            value_type="performance",
            differentiation="Only AI solution in market"
        )
        assert vp.value_type == "performance"

    def test_channel_phases(self):
        """Test Channel with multiple phases."""
        from strategyzr_mcp.models.common import ChannelPhase

        channel = Channel(
            name="Website",
            channel_type="owned",
            phases=[ChannelPhase.AWARENESS, ChannelPhase.EVALUATION, ChannelPhase.PURCHASE],
            is_primary=True
        )
        assert len(channel.phases) == 3
        assert ChannelPhase.AWARENESS in channel.phases

    def test_revenue_stream_recurring(self):
        """Test RevenueStream with recurring flag."""
        from strategyzr_mcp.models.common import RevenueType, PricingMechanism

        revenue = RevenueStream(
            name="SaaS Subscription",
            source_segment="Enterprise",
            revenue_type=RevenueType.SUBSCRIPTION,
            pricing_mechanism=PricingMechanism.FIXED,
            is_recurring=True,
            percentage_of_revenue=80.0
        )
        assert revenue.is_recurring is True
        assert revenue.percentage_of_revenue == 80.0

    def test_key_resource_criticality(self):
        """Test KeyResource criticality bounds."""
        from strategyzr_mcp.models.common import ResourceType

        resource = KeyResource(
            name="AI Model",
            resource_type=ResourceType.INTELLECTUAL,
            description="Proprietary AI model",
            criticality=5
        )
        assert resource.criticality == 5

        with pytest.raises(ValidationError):
            KeyResource(
                name="Test",
                resource_type=ResourceType.PHYSICAL,
                description="Test resource",
                criticality=6  # Invalid: must be 1-5
            )

    def test_bmc_input_business_stages(self):
        """Test BMCInput with different business stages."""
        for stage in BusinessStage:
            # Just test that the enum values are valid
            assert stage.value in ["idea", "startup", "growth", "mature"]
