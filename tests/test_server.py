"""
Integration tests for the StrategyZR MCP server.
"""

import json
import pytest

from strategyzr_mcp.tools.vpc_tools import create_vpc, get_vpc_template
from strategyzr_mcp.tools.bmc_tools import create_bmc, get_bmc_template
from strategyzr_mcp.tools.analysis_tools import validate_canvas, analyze_fit, compare_competitors
from strategyzr_mcp.models.common import JobType, GainType, ResponseFormat, BusinessStage, ChannelPhase, RelationshipType, RevenueType, PricingMechanism, ResourceType, ActivityType, CostType
from strategyzr_mcp.models.vpc import (
    VPCInput,
    CustomerJob,
    CustomerPain,
    CustomerGain,
    ProductService,
    PainReliever,
    GainCreator,
)
from strategyzr_mcp.models.bmc import (
    BMCInput,
    CustomerSegment,
    ValueProposition,
    Channel,
    CustomerRelationship,
    RevenueStream,
    KeyResource,
    KeyActivity,
    KeyPartnership,
    CostItem,
)


class TestVPCTools:
    """Tests for VPC tools."""

    def create_vpc_input(self) -> VPCInput:
        """Create a sample VPC input."""
        return VPCInput(
            company_name="CloudTask Pro",
            target_segment="Remote team managers at startups",
            customer_jobs=[
                CustomerJob(
                    description="Coordinate team tasks across time zones",
                    job_type=JobType.FUNCTIONAL,
                    importance=5
                ),
                CustomerJob(
                    description="Be seen as an effective leader",
                    job_type=JobType.SOCIAL,
                    importance=4
                ),
            ],
            customer_pains=[
                CustomerPain(
                    description="Tasks fall through the cracks",
                    intensity=5,
                    frequency="often"
                ),
                CustomerPain(
                    description="Hard to coordinate across timezones",
                    intensity=4,
                    frequency="always"
                ),
            ],
            customer_gains=[
                CustomerGain(
                    description="Clear visibility into team workload",
                    gain_type=GainType.REQUIRED,
                    relevance=5
                ),
                CustomerGain(
                    description="Save time on status updates",
                    gain_type=GainType.EXPECTED,
                    relevance=4
                ),
            ],
            products_services=[
                ProductService(
                    name="TaskSync Platform",
                    description="AI-powered task coordination",
                    importance=5,
                    is_digital=True
                ),
            ],
            pain_relievers=[
                PainReliever(
                    description="AI monitors and flags at-risk tasks automatically",
                    addresses_pain="Tasks fall through the cracks",
                    effectiveness=5
                ),
                PainReliever(
                    description="Smart scheduling considers all timezones",
                    addresses_pain="Hard to coordinate across timezones",
                    effectiveness=4
                ),
            ],
            gain_creators=[
                GainCreator(
                    description="Real-time dashboard shows team workload",
                    creates_gain="Clear visibility into team workload",
                    effectiveness=5
                ),
                GainCreator(
                    description="Auto-generated status reports",
                    creates_gain="Save time on status updates",
                    effectiveness=4
                ),
            ],
            competitors=["Asana", "Monday.com"],
            response_format=ResponseFormat.MARKDOWN
        )

    def test_create_vpc_markdown(self):
        """Test creating VPC with markdown output."""
        vpc_input = self.create_vpc_input()
        result = create_vpc(vpc_input)

        assert result.company_name == "CloudTask Pro"
        assert result.target_segment == "Remote team managers at startups"
        assert result.markdown_output is not None
        assert "# Value Proposition Canvas" in result.markdown_output
        assert "CloudTask Pro" in result.markdown_output

    def test_create_vpc_json(self):
        """Test creating VPC with JSON output."""
        vpc_input = self.create_vpc_input()
        vpc_input.response_format = ResponseFormat.JSON
        result = create_vpc(vpc_input)

        assert result.markdown_output is None

    def test_create_vpc_fit_scores(self):
        """Test that VPC creation produces fit scores."""
        vpc_input = self.create_vpc_input()
        result = create_vpc(vpc_input)

        assert result.fit_score.problem_solution_fit >= 0
        assert result.fit_score.pain_coverage >= 0
        assert result.fit_score.gain_coverage >= 0

    def test_create_vpc_quality_scores(self):
        """Test that VPC creation produces quality scores."""
        vpc_input = self.create_vpc_input()
        result = create_vpc(vpc_input)

        assert result.quality_score.total_score >= 0
        assert result.quality_score.max_score == 50.0
        assert len(result.quality_score.breakdown) == 10

    def test_create_vpc_validation(self):
        """Test that VPC creation produces validation results."""
        vpc_input = self.create_vpc_input()
        result = create_vpc(vpc_input)

        assert result.validation.is_valid is True

    def test_get_vpc_template(self):
        """Test getting VPC template."""
        template = get_vpc_template()

        assert "company_name" in template
        assert "customer_jobs" in template
        assert "pain_relievers" in template
        assert "_guidance" in template

    def test_get_vpc_template_with_examples(self):
        """Test getting VPC template with examples."""
        template = get_vpc_template(include_examples=True)

        assert "_example" in template
        assert "company_name" in template["_example"]


class TestBMCTools:
    """Tests for BMC tools."""

    def create_bmc_input(self) -> BMCInput:
        """Create a sample BMC input."""
        return BMCInput(
            company_name="CloudTask Pro",
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
                    value_type="convenience"
                ),
            ],
            channels=[
                Channel(
                    name="Website",
                    channel_type="owned",
                    phases=[ChannelPhase.AWARENESS, ChannelPhase.EVALUATION, ChannelPhase.PURCHASE],
                    is_primary=True
                ),
            ],
            customer_relationships=[
                CustomerRelationship(
                    segment="Remote Team Managers",
                    relationship_type=RelationshipType.SELF_SERVICE,
                    motivation="acquisition"
                ),
            ],
            revenue_streams=[
                RevenueStream(
                    name="SaaS Subscription",
                    source_segment="Remote Team Managers",
                    revenue_type=RevenueType.SUBSCRIPTION,
                    pricing_mechanism=PricingMechanism.FIXED,
                    is_recurring=True
                ),
            ],
            key_resources=[
                KeyResource(
                    name="AI Model",
                    resource_type=ResourceType.INTELLECTUAL,
                    description="Proprietary task AI",
                    criticality=5
                ),
            ],
            key_activities=[
                KeyActivity(
                    name="Platform Development",
                    activity_type=ActivityType.PLATFORM,
                    description="Building and maintaining",
                    frequency="ongoing"
                ),
            ],
            key_partnerships=[
                KeyPartnership(
                    partner_name="Cloud Provider",
                    partnership_type="buyer_supplier",
                    motivation="optimization"
                ),
            ],
            cost_structure=[
                CostItem(
                    name="Cloud Infrastructure",
                    cost_type=CostType.VARIABLE,
                    description="Hosting costs"
                ),
            ],
            response_format=ResponseFormat.MARKDOWN
        )

    def test_create_bmc_markdown(self):
        """Test creating BMC with markdown output."""
        bmc_input = self.create_bmc_input()
        result = create_bmc(bmc_input)

        assert result.company_name == "CloudTask Pro"
        assert result.markdown_output is not None
        assert "# Business Model Canvas" in result.markdown_output

    def test_create_bmc_attractiveness_score(self):
        """Test that BMC creation produces attractiveness scores."""
        bmc_input = self.create_bmc_input()
        result = create_bmc(bmc_input)

        assert result.attractiveness_score.total_score >= 0
        assert result.attractiveness_score.recurring_revenues >= 1

    def test_get_bmc_template(self):
        """Test getting BMC template."""
        template = get_bmc_template()

        assert "company_name" in template
        assert "customer_segments" in template
        assert "revenue_streams" in template
        assert "_guidance" in template


class TestAnalysisTools:
    """Tests for analysis tools."""

    def get_vpc_data(self) -> dict:
        """Get sample VPC data as dict."""
        return {
            "company_name": "TestCo",
            "target_segment": "Test segment",
            "customer_jobs": [
                {"description": "Test job", "job_type": "functional", "importance": 4}
            ],
            "customer_pains": [
                {"description": "Test pain", "intensity": 4, "frequency": "often"}
            ],
            "customer_gains": [
                {"description": "Test gain", "gain_type": "required", "relevance": 4}
            ],
            "products_services": [
                {"name": "Test Product", "description": "Test desc", "importance": 4}
            ],
            "pain_relievers": [
                {"description": "Relieves test pain", "addresses_pain": "Test pain", "effectiveness": 4}
            ],
            "gain_creators": [
                {"description": "Creates test gain", "creates_gain": "Test gain", "effectiveness": 4}
            ]
        }

    def get_bmc_data(self) -> dict:
        """Get sample BMC data as dict."""
        return {
            "company_name": "TestCo",
            "industry": "Tech",
            "business_stage": "startup",
            "customer_segments": [
                {"name": "Test segment", "description": "Test desc", "segment_type": "niche"}
            ],
            "value_propositions": [
                {"description": "Test VP", "target_segment": "Test segment", "value_type": "convenience"}
            ],
            "channels": [
                {"name": "Website", "channel_type": "owned", "phases": ["awareness"]}
            ],
            "customer_relationships": [
                {"segment": "Test segment", "relationship_type": "self_service", "motivation": "acquisition"}
            ],
            "revenue_streams": [
                {"name": "Sales", "source_segment": "Test segment", "revenue_type": "subscription", "pricing_mechanism": "fixed", "is_recurring": True}
            ],
            "key_resources": [
                {"name": "Team", "resource_type": "human", "description": "Dev team", "criticality": 4}
            ],
            "key_activities": [
                {"name": "Dev", "activity_type": "platform", "description": "Development", "frequency": "ongoing"}
            ],
            "key_partnerships": [
                {"partner_name": "AWS", "partnership_type": "buyer_supplier", "motivation": "optimization"}
            ],
            "cost_structure": [
                {"name": "Hosting", "cost_type": "variable", "description": "Cloud hosting"}
            ]
        }

    def test_validate_vpc(self):
        """Test validating a VPC."""
        vpc_data = self.get_vpc_data()
        result = validate_canvas("vpc", vpc_data)

        assert result["canvas_type"] == "vpc"
        assert "validation" in result
        assert "quality_score" in result

    def test_validate_bmc(self):
        """Test validating a BMC."""
        bmc_data = self.get_bmc_data()
        result = validate_canvas("bmc", bmc_data)

        assert result["canvas_type"] == "bmc"
        assert "validation" in result
        assert "quality_score" in result

    def test_validate_invalid_data(self):
        """Test validating invalid canvas data."""
        result = validate_canvas("vpc", {"invalid": "data"})

        assert result["validation"].is_valid is False
        assert len(result["validation"].errors) > 0

    def test_analyze_fit_vpc_only(self):
        """Test fit analysis with VPC only."""
        vpc_data = self.get_vpc_data()
        result = analyze_fit(vpc_data)

        assert "vpc_fit" in result
        assert result["vpc_fit"]["problem_solution_fit"] >= 0

    def test_analyze_fit_with_bmc(self):
        """Test fit analysis with VPC and BMC."""
        vpc_data = self.get_vpc_data()
        bmc_data = self.get_bmc_data()
        result = analyze_fit(vpc_data, bmc_data)

        assert "vpc_fit" in result
        assert "vpc_bmc_alignment" in result

    def test_compare_competitors(self):
        """Test competitor comparison."""
        vpc_data = self.get_vpc_data()
        competitors = [
            {
                "name": "Competitor A",
                "pain_relievers": ["Different pain relief"],
                "gain_creators": ["Different gain"]
            },
            {
                "name": "Competitor B",
                "pain_relievers": ["Test pain"],  # Overlaps
                "gain_creators": ["Other gain"]
            },
        ]

        result = compare_competitors("TestCo", vpc_data, competitors)

        assert result["company_name"] == "TestCo"
        assert result["competitors_analyzed"] == 2
        assert "your_strengths" in result
        assert "differentiation_opportunities" in result


class TestEndToEndWorkflow:
    """End-to-end workflow tests."""

    def test_vpc_then_bmc_workflow(self):
        """Test creating VPC, then BMC with alignment check."""
        # 1. Create VPC
        vpc_input = VPCInput(
            company_name="E2E Test Co",
            target_segment="Enterprise developers",
            customer_jobs=[
                CustomerJob(
                    description="Deploy code faster",
                    job_type=JobType.FUNCTIONAL,
                    importance=5
                ),
            ],
            customer_pains=[
                CustomerPain(
                    description="Deployments are slow",
                    intensity=5,
                    frequency="always"
                ),
            ],
            customer_gains=[
                CustomerGain(
                    description="Faster time to market",
                    gain_type=GainType.REQUIRED,
                    relevance=5
                ),
            ],
            products_services=[
                ProductService(
                    name="DeployFast",
                    description="One-click deployments",
                    importance=5,
                    is_digital=True
                ),
            ],
            pain_relievers=[
                PainReliever(
                    description="Parallel builds cut time 10x",
                    addresses_pain="Deployments are slow",
                    effectiveness=5
                ),
            ],
            gain_creators=[
                GainCreator(
                    description="Ship features in minutes",
                    creates_gain="Faster time to market",
                    effectiveness=5
                ),
            ]
        )
        vpc_result = create_vpc(vpc_input)
        assert vpc_result.fit_score.overall_fit > 0

        # 2. Create BMC with VPC data
        bmc_input = BMCInput(
            company_name="E2E Test Co",
            industry="DevOps",
            business_stage=BusinessStage.STARTUP,
            customer_segments=[
                CustomerSegment(
                    name="Enterprise developers",
                    description="Dev teams at large companies",
                    segment_type="niche",
                    is_primary=True
                ),
            ],
            value_propositions=[
                ValueProposition(
                    description="10x faster deployments",
                    target_segment="Enterprise developers",
                    value_type="performance"
                ),
            ],
            channels=[
                Channel(
                    name="Website",
                    channel_type="owned",
                    phases=[ChannelPhase.AWARENESS, ChannelPhase.EVALUATION],
                    is_primary=True
                ),
            ],
            customer_relationships=[
                CustomerRelationship(
                    segment="Enterprise developers",
                    relationship_type=RelationshipType.SELF_SERVICE,
                    motivation="acquisition"
                ),
            ],
            revenue_streams=[
                RevenueStream(
                    name="Subscription",
                    source_segment="Enterprise developers",
                    revenue_type=RevenueType.SUBSCRIPTION,
                    pricing_mechanism=PricingMechanism.FIXED,
                    is_recurring=True
                ),
            ],
            key_resources=[
                KeyResource(
                    name="Platform",
                    resource_type=ResourceType.INTELLECTUAL,
                    description="Deployment platform",
                    criticality=5
                ),
            ],
            key_activities=[
                KeyActivity(
                    name="Platform Dev",
                    activity_type=ActivityType.PLATFORM,
                    description="Building platform",
                    frequency="ongoing"
                ),
            ],
            key_partnerships=[
                KeyPartnership(
                    partner_name="Cloud Providers",
                    partnership_type="strategic_alliance",
                    motivation="resource_acquisition"
                ),
            ],
            cost_structure=[
                CostItem(
                    name="Infrastructure",
                    cost_type=CostType.VARIABLE,
                    description="Cloud costs"
                ),
            ]
        )
        bmc_result = create_bmc(bmc_input, vpc_input)

        assert bmc_result.attractiveness_score.total_score > 0

        # 3. Analyze fit
        fit_result = analyze_fit(
            vpc_input.model_dump(),
            bmc_input.model_dump(),
            "detailed"
        )
        assert "vpc_fit" in fit_result
        assert "vpc_bmc_alignment" in fit_result
        assert "interpretation" in fit_result
