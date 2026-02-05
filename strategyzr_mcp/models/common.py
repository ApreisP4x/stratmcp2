"""
Common enums and base models shared across VPC and BMC.
"""

from enum import Enum
from pydantic import BaseModel, Field


class ResponseFormat(str, Enum):
    """Output format for canvas results."""
    MARKDOWN = "markdown"
    JSON = "json"


class BusinessStage(str, Enum):
    """Stage of business development."""
    IDEA = "idea"
    STARTUP = "startup"
    GROWTH = "growth"
    MATURE = "mature"


class JobType(str, Enum):
    """Types of customer jobs (from VPC methodology)."""
    FUNCTIONAL = "functional"  # Tasks customers want to accomplish
    SOCIAL = "social"  # How customers want to be perceived
    EMOTIONAL = "emotional"  # Feelings customers seek


class GainType(str, Enum):
    """Types of customer gains (from VPC methodology)."""
    REQUIRED = "required"  # Must-have gains
    EXPECTED = "expected"  # Basic expectations
    DESIRED = "desired"  # Nice-to-have gains
    UNEXPECTED = "unexpected"  # Delightful surprises


class ChannelPhase(str, Enum):
    """Channel phases in customer journey."""
    AWARENESS = "awareness"
    EVALUATION = "evaluation"
    PURCHASE = "purchase"
    DELIVERY = "delivery"
    AFTER_SALES = "after_sales"


class RelationshipType(str, Enum):
    """Types of customer relationships."""
    PERSONAL_ASSISTANCE = "personal_assistance"
    DEDICATED_ASSISTANCE = "dedicated_assistance"
    SELF_SERVICE = "self_service"
    AUTOMATED = "automated"
    COMMUNITIES = "communities"
    CO_CREATION = "co_creation"


class ResourceType(str, Enum):
    """Types of key resources."""
    PHYSICAL = "physical"
    INTELLECTUAL = "intellectual"
    HUMAN = "human"
    FINANCIAL = "financial"


class ActivityType(str, Enum):
    """Types of key activities."""
    PRODUCTION = "production"
    PROBLEM_SOLVING = "problem_solving"
    PLATFORM = "platform"


class RevenueType(str, Enum):
    """Types of revenue streams."""
    ASSET_SALE = "asset_sale"
    USAGE_FEE = "usage_fee"
    SUBSCRIPTION = "subscription"
    LENDING = "lending"
    LICENSING = "licensing"
    BROKERAGE = "brokerage"
    ADVERTISING = "advertising"


class PricingMechanism(str, Enum):
    """Pricing mechanisms for revenue streams."""
    FIXED = "fixed"
    DYNAMIC = "dynamic"
    AUCTION = "auction"
    MARKET_DEPENDENT = "market_dependent"
    VOLUME_DEPENDENT = "volume_dependent"
    NEGOTIATION = "negotiation"


class CostType(str, Enum):
    """Types of costs in cost structure."""
    FIXED = "fixed"
    VARIABLE = "variable"


class QualityScore(BaseModel):
    """Quality score with breakdown."""
    total_score: float = Field(..., ge=0, description="Total quality score")
    max_score: float = Field(..., gt=0, description="Maximum possible score")
    percentage: float = Field(..., ge=0, le=100, description="Score as percentage")
    breakdown: dict[str, float] = Field(default_factory=dict, description="Score breakdown by criterion")

    @classmethod
    def create(cls, breakdown: dict[str, float], max_per_criterion: float = 5.0) -> "QualityScore":
        """Create a quality score from criterion breakdown."""
        total = sum(breakdown.values())
        max_score = len(breakdown) * max_per_criterion
        return cls(
            total_score=total,
            max_score=max_score,
            percentage=round((total / max_score) * 100, 1) if max_score > 0 else 0,
            breakdown=breakdown
        )


class Recommendation(BaseModel):
    """A strategic recommendation."""
    priority: int = Field(..., ge=1, le=3, description="Priority level (1=high, 2=medium, 3=low)")
    category: str = Field(..., description="Category of recommendation")
    description: str = Field(..., description="Detailed recommendation")
    rationale: str = Field(..., description="Why this is recommended")


class ValidationResult(BaseModel):
    """Result of canvas validation."""
    is_valid: bool = Field(..., description="Whether the canvas passes validation")
    errors: list[str] = Field(default_factory=list, description="Critical errors that must be fixed")
    warnings: list[str] = Field(default_factory=list, description="Non-critical issues to consider")
    suggestions: list[str] = Field(default_factory=list, description="Improvement suggestions")
