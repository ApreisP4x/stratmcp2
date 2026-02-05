"""
StrategyZR MCP Server - Alternative Implementation

A structured data approach to Business Model Canvas and Value Proposition Canvas
using Pydantic models for validation and computed quality scores.

This server provides 6 tools:
1. strategyzr_create_vpc - Create a Value Proposition Canvas
2. strategyzr_create_bmc - Create a Business Model Canvas
3. strategyzr_validate_canvas - Validate and score an existing canvas
4. strategyzr_analyze_fit - Analyze fit between VPC and BMC
5. strategyzr_compare_competitors - Competitive analysis
6. strategyzr_get_template - Get empty canvas templates
"""

import json
import os
from typing import Any, Literal, Annotated

from fastmcp import FastMCP
from pydantic import Field

from .models.vpc import VPCInput
from .models.bmc import BMCInput
from .tools.vpc_tools import create_vpc, get_vpc_template
from .tools.bmc_tools import create_bmc, get_bmc_template
from .tools.analysis_tools import validate_canvas, analyze_fit, compare_competitors

# Initialize FastMCP server
mcp = FastMCP(
    name="strategyzr_mcp",
    instructions="""
StrategyZR MCP Server - Strategic Canvas Tools

This server provides structured tools for creating and analyzing business strategy canvases
based on Osterwalder's frameworks:

- Value Proposition Canvas (VPC): Customer Profile + Value Map
- Business Model Canvas (BMC): 9 building blocks of a business model

Key features:
- Pydantic validation for all inputs
- Computed quality scores (10 Characteristics, Attractiveness)
- Fit analysis between VPC and BMC
- Competitive positioning analysis

Use strategyzr_get_template to get empty templates with guidance before creating canvases.
""",
)


# =============================================================================
# Tool 1: Create VPC
# =============================================================================

@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
    }
)
def strategyzr_create_vpc(
    company_name: Annotated[str, Field(description="Company or product name")],
    target_segment: Annotated[str, Field(description="Target customer segment")],
    customer_jobs: Annotated[list[dict], Field(description="Customer jobs (3-5 recommended). Each: {description, job_type: functional|social|emotional, importance: 1-5, context?}")],
    customer_pains: Annotated[list[dict], Field(description="Customer pains (3-5 recommended). Each: {description, intensity: 1-5, frequency: rarely|sometimes|often|always, related_job?}")],
    customer_gains: Annotated[list[dict], Field(description="Customer gains (3-5 recommended). Each: {description, gain_type: required|expected|desired|unexpected, relevance: 1-5, related_job?}")],
    products_services: Annotated[list[dict], Field(description="Products/services. Each: {name, description, importance: 1-5, is_digital?, is_tangible?}")],
    pain_relievers: Annotated[list[dict], Field(description="Pain relievers. Each: {description, addresses_pain, effectiveness: 1-5, product_service?}")],
    gain_creators: Annotated[list[dict], Field(description="Gain creators. Each: {description, creates_gain, effectiveness: 1-5, product_service?}")],
    competitors: Annotated[list[str] | None, Field(description="Optional list of competitor names")] = None,
    response_format: Annotated[Literal["markdown", "json"], Field(description="Output format")] = "markdown",
) -> str:
    """
    Create a Value Proposition Canvas with structured validation and quality scoring.

    Returns a complete VPC with:
    - Organized customer profile (jobs, pains, gains)
    - Value map (products/services, pain relievers, gain creators)
    - Fit score (problem-solution fit, pain/gain coverage)
    - Quality score based on 10 Characteristics of Great Value Propositions
    - Validation results and improvement recommendations
    """
    vpc_input = VPCInput(
        company_name=company_name,
        target_segment=target_segment,
        customer_jobs=customer_jobs,
        customer_pains=customer_pains,
        customer_gains=customer_gains,
        products_services=products_services,
        pain_relievers=pain_relievers,
        gain_creators=gain_creators,
        competitors=competitors,
        response_format=response_format,
    )

    result = create_vpc(vpc_input)

    if response_format == "markdown":
        return result.markdown_output or ""
    else:
        return json.dumps(result.model_dump(), indent=2, default=str)


# =============================================================================
# Tool 2: Create BMC
# =============================================================================

@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
    }
)
def strategyzr_create_bmc(
    company_name: Annotated[str, Field(description="Company name")],
    industry: Annotated[str, Field(description="Industry/sector")],
    business_stage: Annotated[Literal["idea", "startup", "growth", "mature"], Field(description="Business stage")],
    customer_segments: Annotated[list[dict], Field(description="Customer segments. Each: {name, description, segment_type: mass_market|niche|segmented|diversified|multi_sided, size_estimate?, is_primary?}")],
    value_propositions: Annotated[list[dict], Field(description="Value propositions. Each: {description, target_segment, value_type, differentiation?, vpc_reference?}")],
    channels: Annotated[list[dict], Field(description="Channels. Each: {name, channel_type: direct|indirect|owned|partner, phases: [awareness|evaluation|purchase|delivery|after_sales], is_primary?, description?}")],
    customer_relationships: Annotated[list[dict], Field(description="Customer relationships. Each: {segment, relationship_type: personal_assistance|dedicated_assistance|self_service|automated|communities|co_creation, motivation, description?}")],
    revenue_streams: Annotated[list[dict], Field(description="Revenue streams. Each: {name, source_segment, revenue_type, pricing_mechanism, percentage_of_revenue?, is_recurring?}")],
    key_resources: Annotated[list[dict], Field(description="Key resources. Each: {name, resource_type: physical|intellectual|human|financial, description, is_owned?, criticality: 1-5}")],
    key_activities: Annotated[list[dict], Field(description="Key activities. Each: {name, activity_type: production|problem_solving|platform, description, frequency}")],
    key_partnerships: Annotated[list[dict], Field(description="Key partnerships. Each: {partner_name, partnership_type, motivation, key_activities?, key_resources?}")],
    cost_structure: Annotated[list[dict], Field(description="Cost structure. Each: {name, cost_type: fixed|variable, description, is_key_cost?, percentage_of_costs?}")],
    vpc_data: Annotated[dict | None, Field(description="Optional VPC data for alignment check")] = None,
    response_format: Annotated[Literal["markdown", "json"], Field(description="Output format")] = "markdown",
) -> str:
    """
    Create a Business Model Canvas with structured validation and attractiveness scoring.

    Returns a complete BMC with:
    - All 9 building blocks organized
    - Business Model Attractiveness score (7 dimensions)
    - VPC alignment check (if vpc_data provided)
    - Validation results and improvement recommendations
    """
    bmc_input = BMCInput(
        company_name=company_name,
        industry=industry,
        business_stage=business_stage,
        customer_segments=customer_segments,
        value_propositions=value_propositions,
        channels=channels,
        customer_relationships=customer_relationships,
        revenue_streams=revenue_streams,
        key_resources=key_resources,
        key_activities=key_activities,
        key_partnerships=key_partnerships,
        cost_structure=cost_structure,
        response_format=response_format,
    )

    vpc_input = None
    if vpc_data:
        vpc_input = VPCInput(**vpc_data)

    result = create_bmc(bmc_input, vpc_input)

    if response_format == "markdown":
        return result.markdown_output or ""
    else:
        return json.dumps(result.model_dump(), indent=2, default=str)


# =============================================================================
# Tool 3: Validate Canvas
# =============================================================================

@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
    }
)
def strategyzr_validate_canvas(
    canvas_type: Annotated[Literal["vpc", "bmc"], Field(description="Type of canvas to validate")],
    canvas_data: Annotated[dict, Field(description="The canvas data to validate")],
    check_vpc_alignment: Annotated[bool, Field(description="For BMC, whether to check VPC alignment")] = False,
    vpc_data: Annotated[dict | None, Field(description="VPC data for alignment check (required if check_vpc_alignment is True)")] = None,
) -> str:
    """
    Validate and score an existing canvas against best practices.

    Returns:
    - Validation results (errors, warnings, suggestions)
    - Quality score with breakdown
    - Gap analysis
    - Prioritized improvement recommendations
    - VPC alignment check (for BMC with vpc_data)
    """
    result = validate_canvas(canvas_type, canvas_data, check_vpc_alignment, vpc_data)
    return json.dumps(result, indent=2, default=str)


# =============================================================================
# Tool 4: Analyze Fit
# =============================================================================

@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
    }
)
def strategyzr_analyze_fit(
    vpc_data: Annotated[dict, Field(description="VPC data to analyze")],
    bmc_data: Annotated[dict | None, Field(description="Optional BMC data for cross-canvas analysis")] = None,
    analysis_depth: Annotated[Literal["quick", "detailed"], Field(description="Analysis depth")] = "detailed",
) -> str:
    """
    Analyze the fit between VPC and BMC.

    Returns:
    - Problem-Solution Fit score
    - Product-Market Fit indicators
    - VPC-BMC alignment assessment (if bmc_data provided)
    - Recommendations for improving fit
    - Interpretation of scores
    """
    result = analyze_fit(vpc_data, bmc_data, analysis_depth)
    return json.dumps(result, indent=2, default=str)


# =============================================================================
# Tool 5: Compare Competitors
# =============================================================================

@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
    }
)
def strategyzr_compare_competitors(
    company_name: Annotated[str, Field(description="Your company name")],
    your_vpc: Annotated[dict, Field(description="Your VPC data")],
    competitors: Annotated[list[dict], Field(description="List of competitor data. Each: {name, pain_relievers: [...], gain_creators: [...]}")],
    market_context: Annotated[str | None, Field(description="Optional market context description")] = None,
) -> str:
    """
    Map competitor value propositions for differentiation analysis.

    Returns:
    - Your strengths (unique pain relievers/gain creators)
    - Your weaknesses (competitor advantages)
    - Competitive threats (high-overlap competitors)
    - Differentiation opportunities
    - 'Difficult to copy' assessment
    - Positioning recommendations and statement
    """
    result = compare_competitors(company_name, your_vpc, competitors, market_context)
    return json.dumps(result, indent=2, default=str)


# =============================================================================
# Tool 6: Get Template
# =============================================================================

@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
    }
)
def strategyzr_get_template(
    template_type: Annotated[Literal["vpc", "bmc"], Field(description="Template type to retrieve")],
    include_examples: Annotated[bool, Field(description="Include example values")] = False,
    include_guidance: Annotated[bool, Field(description="Include filling guidance")] = True,
) -> str:
    """
    Get empty canvas templates with field descriptions.

    Returns:
    - Empty template structure with all required fields
    - Field descriptions and constraints
    - Optional examples showing how to fill each section
    - Guidance based on Osterwalder methodology
    """
    if template_type == "vpc":
        template = get_vpc_template(include_examples, include_guidance)
    else:
        template = get_bmc_template(include_examples, include_guidance)

    return json.dumps(template, indent=2)


# =============================================================================
# Resources
# =============================================================================

@mcp.resource("strategyzr://methodology")
def get_methodology() -> str:
    """Return Osterwalder methodology overview."""
    return """# Osterwalder Strategic Canvas Methodology

## Value Proposition Canvas (VPC)

The VPC helps you design value propositions that customers want. It has two sides:

### Customer Profile
- **Jobs**: Tasks customers are trying to accomplish (functional, social, emotional)
- **Pains**: Frustrations, obstacles, and risks they face
- **Gains**: Outcomes and benefits they desire

### Value Map
- **Products & Services**: What you offer
- **Pain Relievers**: How you alleviate customer pains
- **Gain Creators**: How you create customer gains

**Goal**: Achieve fit by ensuring your value map addresses the customer profile.

## Business Model Canvas (BMC)

The BMC describes how an organization creates, delivers, and captures value.

### 9 Building Blocks:
1. **Customer Segments**: Who you create value for
2. **Value Propositions**: Why customers choose you
3. **Channels**: How you reach customers
4. **Customer Relationships**: How you interact with customers
5. **Revenue Streams**: How you make money
6. **Key Resources**: Assets required to deliver value
7. **Key Activities**: Most important things you do
8. **Key Partnerships**: Network of suppliers and partners
9. **Cost Structure**: Costs incurred to operate

## Fit Progression

1. **Problem-Solution Fit**: Evidence that your value proposition addresses real customer problems
2. **Product-Market Fit**: Evidence that customers want your value proposition
3. **Business Model Fit**: Evidence that your business model is scalable and profitable
"""


@mcp.resource("strategyzr://quality-criteria")
def get_quality_criteria() -> str:
    """Return the 10 Characteristics and Attractiveness criteria."""
    return """# Quality Assessment Criteria

## 10 Characteristics of Great Value Propositions

Each rated 1-5, maximum 50 points:

1. **Embedded in great business models** - VP is supported by a viable business model
2. **Focus on most important jobs, pains, gains** - Prioritize what matters most
3. **Focus on unsatisfied jobs, pains, gains** - Address unmet needs
4. **Converge on few things done well** - Don't try to do everything
5. **Address functional, emotional, and social jobs** - Complete customer understanding
6. **Align with customer success metrics** - Measure what customers measure
7. **Focus on high-impact jobs, pains, gains** - Maximum value creation
8. **Differentiate from competition** - Clear positioning
9. **Outperform competition substantially** - Not just marginally better
10. **Difficult to copy** - Sustainable advantage

## Business Model Attractiveness (7 Dimensions)

Each rated 1-5, maximum 35 points:

1. **Switching Costs** - How hard for customers to leave
2. **Recurring Revenues** - Predictable, repeatable income
3. **Earning vs Spending** - Get paid before spending
4. **Cost Structure** - Efficient cost management
5. **Getting Others to Do the Work** - Leverage partners/customers
6. **Scalability** - Grow without proportional cost increase
7. **Protection from Competition** - Barriers to entry/imitation

## Fit Scores

- **Problem-Solution Fit**: >70% indicates strong alignment
- **Pain Coverage**: Aim for >70% of pains addressed
- **Gain Coverage**: Aim for >70% of gains created
- **VPC-BMC Alignment**: >60% indicates good business model fit
"""


# =============================================================================
# Prompts
# =============================================================================

@mcp.prompt()
def vpc_workshop(company: str, segment: str) -> str:
    """Interactive VPC creation workshop prompt."""
    return f"""# Value Proposition Canvas Workshop

**Company:** {company}
**Target Segment:** {segment}

Let's create a Value Proposition Canvas together. I'll guide you through each section.

## Step 1: Customer Profile

First, let's understand your customer.

### Customer Jobs (3-5)
What tasks is your customer trying to accomplish?
- Think about functional jobs (tasks)
- Social jobs (how they want to be perceived)
- Emotional jobs (how they want to feel)

### Customer Pains (3-5)
What frustrates your customer?
- Obstacles and risks
- Undesired outcomes
- Current solution problems

### Customer Gains (3-5)
What outcomes does your customer desire?
- Required gains (must-have)
- Expected gains (basic expectations)
- Desired gains (nice-to-have)
- Unexpected gains (delights)

## Step 2: Value Map

Now let's design your value proposition.

### Products & Services
What do you offer?

### Pain Relievers
How do you relieve each customer pain?

### Gain Creators
How do you create each customer gain?

---

Once you provide this information, use the strategyzr_create_vpc tool to generate your complete canvas with scores and recommendations.
"""


@mcp.prompt()
def bmc_workshop(company: str, industry: str) -> str:
    """Interactive BMC creation workshop prompt."""
    return f"""# Business Model Canvas Workshop

**Company:** {company}
**Industry:** {industry}

Let's build your Business Model Canvas. We'll work through all 9 building blocks.

## Right Side: Value Creation

### 1. Customer Segments
Who are your most important customers?
- Mass market, niche, segmented, diversified, or multi-sided?

### 2. Value Propositions
What value do you deliver to each segment?
- Reference your VPC if you have one

### 3. Channels
How do you reach your customers?
- Cover: awareness, evaluation, purchase, delivery, after-sales

### 4. Customer Relationships
What type of relationship does each segment expect?
- Personal, self-service, automated, communities, co-creation?

### 5. Revenue Streams
How does each segment pay you?
- One-time or recurring?

## Left Side: Value Delivery

### 6. Key Resources
What assets are essential?
- Physical, intellectual, human, financial?

### 7. Key Activities
What must you do exceptionally well?
- Production, problem-solving, or platform?

### 8. Key Partnerships
Who helps you deliver value?
- Strategic alliances, joint ventures, suppliers?

### 9. Cost Structure
What are your main costs?
- Fixed vs variable?

---

Once you provide this information, use the strategyzr_create_bmc tool to generate your complete canvas with attractiveness scores and recommendations.
"""


@mcp.prompt()
def strategy_review(canvas_type: str) -> str:
    """Canvas review and improvement prompt."""
    return f"""# {canvas_type.upper()} Strategy Review

Let's review and improve your {'Value Proposition Canvas' if canvas_type == 'vpc' else 'Business Model Canvas'}.

## Review Process

1. **Validation Check**
   - Use strategyzr_validate_canvas to check for issues
   - Address any errors and warnings

2. **Quality Assessment**
   - Review your quality scores
   - Identify lowest-scoring dimensions

3. **Fit Analysis**
   - Use strategyzr_analyze_fit to check internal consistency
   - For BMC: check VPC alignment

4. **Competitive Position**
   - Use strategyzr_compare_competitors to understand differentiation
   - Identify opportunities

## Improvement Framework

### Quick Wins (This Week)
- Address validation errors
- Fill obvious gaps

### Strategic Improvements (This Month)
- Improve lowest-scoring dimensions
- Strengthen differentiation

### Long-term Evolution (This Quarter)
- Build harder-to-copy elements
- Develop new value sources

---

Provide your canvas data and I'll help you analyze and improve it.
"""


# =============================================================================
# Health Check Endpoint
# =============================================================================

@mcp.custom_route("/health", methods=["GET"])
async def health_check():
    """Health check endpoint for deployment monitoring."""
    from starlette.responses import JSONResponse
    return JSONResponse({"status": "healthy", "server": "strategyzr_mcp"})


# =============================================================================
# Main entry point
# =============================================================================

def main():
    """Run the MCP server."""
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    if transport == "http":
        host = "0.0.0.0"
        port = int(os.environ.get("PORT", 8000))
        mcp.run(transport="http", host=host, port=port)
    else:
        mcp.run()  # Default stdio for local use


if __name__ == "__main__":
    main()
