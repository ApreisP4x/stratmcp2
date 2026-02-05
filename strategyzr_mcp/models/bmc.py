"""
Business Model Canvas (BMC) Pydantic models.

Based on Osterwalder's Business Model Generation methodology.
The BMC has 9 building blocks:
1. Customer Segments
2. Value Propositions
3. Channels
4. Customer Relationships
5. Revenue Streams
6. Key Resources
7. Key Activities
8. Key Partnerships
9. Cost Structure
"""

from typing import Optional
from pydantic import BaseModel, Field

from .common import (
    ResponseFormat,
    BusinessStage,
    ChannelPhase,
    RelationshipType,
    ResourceType,
    ActivityType,
    RevenueType,
    PricingMechanism,
    CostType,
    QualityScore,
    Recommendation,
    ValidationResult,
)


# =============================================================================
# BMC Building Blocks
# =============================================================================

class CustomerSegment(BaseModel):
    """A customer segment the business serves."""
    name: str = Field(..., min_length=2, description="Segment name")
    description: str = Field(..., min_length=5, description="Segment description")
    segment_type: str = Field(..., description="Type: mass_market, niche, segmented, diversified, multi_sided")
    size_estimate: Optional[str] = Field(None, description="Estimated market size")
    is_primary: bool = Field(False, description="Whether this is the primary segment")

    @property
    def valid_segment_types(self) -> list[str]:
        return ["mass_market", "niche", "segmented", "diversified", "multi_sided"]


class ValueProposition(BaseModel):
    """A value proposition for a customer segment."""
    description: str = Field(..., min_length=5, description="The value proposition statement")
    target_segment: str = Field(..., description="Which customer segment this serves")
    value_type: str = Field(..., description="Type: newness, performance, customization, design, brand, price, cost_reduction, risk_reduction, accessibility, convenience")
    differentiation: Optional[str] = Field(None, description="How this differs from competitors")
    vpc_reference: Optional[str] = Field(None, description="Reference to detailed VPC if available")


class Channel(BaseModel):
    """A channel to reach customers."""
    name: str = Field(..., min_length=2, description="Channel name")
    channel_type: str = Field(..., description="Type: direct, indirect, owned, partner")
    phases: list[ChannelPhase] = Field(..., min_length=1, description="Which customer journey phases it covers")
    is_primary: bool = Field(False, description="Whether this is a primary channel")
    description: Optional[str] = Field(None, description="Additional details")


class CustomerRelationship(BaseModel):
    """A type of relationship with customers."""
    segment: str = Field(..., description="Which customer segment")
    relationship_type: RelationshipType = Field(..., description="Type of relationship")
    motivation: str = Field(..., description="Motivation: acquisition, retention, upselling")
    description: Optional[str] = Field(None, description="How this relationship works")


class RevenueStream(BaseModel):
    """A source of revenue."""
    name: str = Field(..., min_length=2, description="Revenue stream name")
    source_segment: str = Field(..., description="Which customer segment pays")
    revenue_type: RevenueType = Field(..., description="Type of revenue")
    pricing_mechanism: PricingMechanism = Field(..., description="How pricing works")
    percentage_of_revenue: Optional[float] = Field(None, ge=0, le=100, description="Estimated percentage of total revenue")
    is_recurring: bool = Field(False, description="Whether this is recurring revenue")


class KeyResource(BaseModel):
    """A key resource required for the business model."""
    name: str = Field(..., min_length=2, description="Resource name")
    resource_type: ResourceType = Field(..., description="Type: physical, intellectual, human, financial")
    description: str = Field(..., min_length=5, description="Resource description")
    is_owned: bool = Field(True, description="Whether the resource is owned vs. accessed")
    criticality: int = Field(..., ge=1, le=5, description="How critical (1=helpful, 5=essential)")


class KeyActivity(BaseModel):
    """A key activity required for the business model."""
    name: str = Field(..., min_length=2, description="Activity name")
    activity_type: ActivityType = Field(..., description="Type: production, problem_solving, platform")
    description: str = Field(..., min_length=5, description="What this activity involves")
    frequency: str = Field(..., description="How often: daily, weekly, monthly, ongoing, as_needed")


class KeyPartnership(BaseModel):
    """A key partnership for the business model."""
    partner_name: str = Field(..., min_length=2, description="Partner name or type")
    partnership_type: str = Field(..., description="Type: strategic_alliance, coopetition, joint_venture, buyer_supplier")
    motivation: str = Field(..., description="Why: optimization, risk_reduction, resource_acquisition")
    key_activities: list[str] = Field(default_factory=list, description="Activities this partner supports")
    key_resources: list[str] = Field(default_factory=list, description="Resources this partner provides")


class CostItem(BaseModel):
    """A cost item in the cost structure."""
    name: str = Field(..., min_length=2, description="Cost item name")
    cost_type: CostType = Field(..., description="Fixed or variable")
    description: str = Field(..., min_length=5, description="What this cost covers")
    is_key_cost: bool = Field(False, description="Whether this is one of the largest costs")
    percentage_of_costs: Optional[float] = Field(None, ge=0, le=100, description="Estimated percentage of total costs")


# =============================================================================
# BMC Input/Output Models
# =============================================================================

class BMCInput(BaseModel):
    """Input for creating a Business Model Canvas."""
    company_name: str = Field(..., min_length=1, description="Company name")
    industry: str = Field(..., min_length=2, description="Industry/sector")
    business_stage: BusinessStage = Field(..., description="Stage: idea, startup, growth, mature")

    # All 9 building blocks
    customer_segments: list[CustomerSegment] = Field(..., min_length=1, max_length=10, description="Customer segments")
    value_propositions: list[ValueProposition] = Field(..., min_length=1, max_length=10, description="Value propositions")
    channels: list[Channel] = Field(..., min_length=1, max_length=10, description="Channels")
    customer_relationships: list[CustomerRelationship] = Field(..., min_length=1, max_length=10, description="Customer relationships")
    revenue_streams: list[RevenueStream] = Field(..., min_length=1, max_length=10, description="Revenue streams")
    key_resources: list[KeyResource] = Field(..., min_length=1, max_length=10, description="Key resources")
    key_activities: list[KeyActivity] = Field(..., min_length=1, max_length=10, description="Key activities")
    key_partnerships: list[KeyPartnership] = Field(..., min_length=1, max_length=10, description="Key partnerships")
    cost_structure: list[CostItem] = Field(..., min_length=1, max_length=10, description="Cost structure")

    # Optional
    vpc_reference: Optional[str] = Field(None, description="Reference to existing VPC for alignment check")
    response_format: ResponseFormat = Field(ResponseFormat.MARKDOWN, description="Output format")


class AttractivenessScore(BaseModel):
    """Business Model Attractiveness assessment (6 dimensions, max 30 points)."""
    switching_costs: float = Field(..., ge=0, le=5, description="How hard for customers to switch")
    recurring_revenues: float = Field(..., ge=0, le=5, description="Predictability of revenue")
    earning_vs_spending: float = Field(..., ge=0, le=5, description="Earn before spending ratio")
    cost_structure: float = Field(..., ge=0, le=5, description="Cost efficiency")
    others_do_work: float = Field(..., ge=0, le=5, description="Leverage of partner/customer work")
    scalability: float = Field(..., ge=0, le=5, description="Growth potential without proportional costs")
    protection: float = Field(..., ge=0, le=5, description="Protection from competition")
    total_score: float = Field(..., ge=0, le=35, description="Total attractiveness score")


class BMCOutput(BaseModel):
    """Output from BMC creation tool."""
    company_name: str
    industry: str
    business_stage: BusinessStage

    # All building blocks
    customer_segments: list[CustomerSegment]
    value_propositions: list[ValueProposition]
    channels: list[Channel]
    customer_relationships: list[CustomerRelationship]
    revenue_streams: list[RevenueStream]
    key_resources: list[KeyResource]
    key_activities: list[KeyActivity]
    key_partnerships: list[KeyPartnership]
    cost_structure: list[CostItem]

    # Assessment
    attractiveness_score: AttractivenessScore
    validation: ValidationResult
    recommendations: list[Recommendation]
    vpc_alignment: Optional[dict] = Field(None, description="VPC alignment check if vpc_reference provided")
    markdown_output: Optional[str] = Field(None, description="Markdown formatted output if requested")
