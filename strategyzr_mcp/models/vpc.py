"""
Value Proposition Canvas (VPC) Pydantic models.

Based on Osterwalder's Value Proposition Design methodology.
The VPC has two sides:
- Customer Profile: Jobs, Pains, Gains
- Value Map: Products/Services, Pain Relievers, Gain Creators
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator

from .common import (
    ResponseFormat,
    JobType,
    GainType,
    QualityScore,
    Recommendation,
    ValidationResult,
)


# =============================================================================
# Customer Profile Components
# =============================================================================

class CustomerJob(BaseModel):
    """A job the customer is trying to get done."""
    description: str = Field(..., min_length=5, description="What the customer is trying to accomplish")
    job_type: JobType = Field(..., description="Type of job: functional, social, or emotional")
    importance: int = Field(..., ge=1, le=5, description="Importance to customer (1=low, 5=critical)")
    context: Optional[str] = Field(None, description="Situational context for this job")

    @field_validator("description")
    @classmethod
    def description_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Job description cannot be empty")
        return v.strip()


class CustomerPain(BaseModel):
    """A pain or frustration the customer experiences."""
    description: str = Field(..., min_length=5, description="The pain or frustration")
    intensity: int = Field(..., ge=1, le=5, description="How severe is this pain (1=minor, 5=extreme)")
    frequency: str = Field(..., description="How often: rarely, sometimes, often, always")
    related_job: Optional[str] = Field(None, description="Which customer job this pain relates to")

    @field_validator("frequency")
    @classmethod
    def validate_frequency(cls, v: str) -> str:
        valid = ["rarely", "sometimes", "often", "always"]
        if v.lower() not in valid:
            raise ValueError(f"Frequency must be one of: {', '.join(valid)}")
        return v.lower()


class CustomerGain(BaseModel):
    """A gain or outcome the customer desires."""
    description: str = Field(..., min_length=5, description="The desired outcome or benefit")
    gain_type: GainType = Field(..., description="Type: required, expected, desired, or unexpected")
    relevance: int = Field(..., ge=1, le=5, description="How relevant to customer (1=nice, 5=essential)")
    related_job: Optional[str] = Field(None, description="Which customer job this gain relates to")


class CustomerProfile(BaseModel):
    """The customer profile side of the VPC."""
    jobs: list[CustomerJob] = Field(..., min_length=1, max_length=10, description="Customer jobs (3-5 recommended)")
    pains: list[CustomerPain] = Field(..., min_length=1, max_length=10, description="Customer pains (3-5 recommended)")
    gains: list[CustomerGain] = Field(..., min_length=1, max_length=10, description="Customer gains (3-5 recommended)")


# =============================================================================
# Value Map Components
# =============================================================================

class ProductService(BaseModel):
    """A product or service in the value proposition."""
    name: str = Field(..., min_length=2, description="Name of the product or service")
    description: str = Field(..., min_length=5, description="What it does")
    importance: int = Field(..., ge=1, le=5, description="How central to the value proposition (1=peripheral, 5=core)")
    is_digital: bool = Field(False, description="Whether this is a digital product/service")
    is_tangible: bool = Field(True, description="Whether this is a tangible product")


class PainReliever(BaseModel):
    """How the value proposition alleviates customer pains."""
    description: str = Field(..., min_length=5, description="How this relieves pain")
    addresses_pain: str = Field(..., description="Which customer pain this addresses")
    effectiveness: int = Field(..., ge=1, le=5, description="How effectively it relieves pain (1=slightly, 5=completely)")
    product_service: Optional[str] = Field(None, description="Which product/service delivers this")


class GainCreator(BaseModel):
    """How the value proposition creates customer gains."""
    description: str = Field(..., min_length=5, description="How this creates gain")
    creates_gain: str = Field(..., description="Which customer gain this creates")
    effectiveness: int = Field(..., ge=1, le=5, description="How effectively it creates gain (1=slightly, 5=completely)")
    product_service: Optional[str] = Field(None, description="Which product/service delivers this")


class ValueMap(BaseModel):
    """The value map side of the VPC."""
    products_services: list[ProductService] = Field(..., min_length=1, max_length=10, description="Products and services")
    pain_relievers: list[PainReliever] = Field(..., min_length=1, max_length=10, description="Pain relievers")
    gain_creators: list[GainCreator] = Field(..., min_length=1, max_length=10, description="Gain creators")


# =============================================================================
# VPC Input/Output Models
# =============================================================================

class VPCInput(BaseModel):
    """Input for creating a Value Proposition Canvas."""
    company_name: str = Field(..., min_length=1, description="Company or product name")
    target_segment: str = Field(..., min_length=3, description="Target customer segment")

    # Customer Profile
    customer_jobs: list[CustomerJob] = Field(..., min_length=1, max_length=10, description="Jobs customers are trying to do")
    customer_pains: list[CustomerPain] = Field(..., min_length=1, max_length=10, description="Customer pains and frustrations")
    customer_gains: list[CustomerGain] = Field(..., min_length=1, max_length=10, description="Desired customer gains")

    # Value Map
    products_services: list[ProductService] = Field(..., min_length=1, max_length=10, description="Products and services offered")
    pain_relievers: list[PainReliever] = Field(..., min_length=1, max_length=10, description="How you relieve pains")
    gain_creators: list[GainCreator] = Field(..., min_length=1, max_length=10, description="How you create gains")

    # Optional
    competitors: Optional[list[str]] = Field(None, description="Competitor names for context")
    response_format: ResponseFormat = Field(ResponseFormat.MARKDOWN, description="Output format")


class FitScore(BaseModel):
    """Fit assessment between customer profile and value map."""
    problem_solution_fit: float = Field(..., ge=0, le=100, description="How well you address customer problems")
    product_market_fit_indicators: float = Field(..., ge=0, le=100, description="Indicators of product-market fit")
    pain_coverage: float = Field(..., ge=0, le=100, description="Percentage of pains addressed")
    gain_coverage: float = Field(..., ge=0, le=100, description="Percentage of gains created")
    overall_fit: float = Field(..., ge=0, le=100, description="Overall fit score")


class VPCOutput(BaseModel):
    """Output from VPC creation tool."""
    company_name: str
    target_segment: str
    customer_profile: CustomerProfile
    value_map: ValueMap
    fit_score: FitScore
    quality_score: QualityScore
    validation: ValidationResult
    recommendations: list[Recommendation]
    markdown_output: Optional[str] = Field(None, description="Markdown formatted output if requested")
