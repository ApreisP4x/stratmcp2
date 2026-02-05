"""
StrategyZR MCP Server

A structured data approach to Business Model Canvas and Value Proposition Canvas
using Pydantic models for validation and computed quality scores.

This server provides 5 tools:
1. create_vpc - Create a Value Proposition Canvas
2. create_bmc - Create a Business Model Canvas
3. validate - Validate and score an existing canvas
4. analyze_fit - Analyze fit between VPC and BMC
5. compare - Competitive analysis
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
    instructions="""StrategyZR builds and scores Osterwalder strategy canvases (Value Proposition Canvas and Business Model Canvas). All inputs are Pydantic-validated; all outputs include computed quality scores and actionable recommendations.

## Recommended workflow
1. Read template resources (`strategyzr://template/vpc`, `strategyzr://template/bmc`) to understand required fields.
2. `create_vpc` — build the Value Proposition Canvas for a customer segment.
3. `create_bmc` — build the Business Model Canvas (pass vpc_data to check alignment).
4. `validate` — score either canvas against Osterwalder best practices.
5. `analyze_fit` — measure Problem-Solution Fit and Product-Market Fit indicators.
6. `compare` — map competitor value propositions for differentiation analysis.

## Tool guide
- **create_vpc**: Use when designing or documenting a value proposition for a specific customer segment.
- **create_bmc**: Use when describing how a business creates, delivers, and captures value.
- **validate**: Use when the user has canvas data and wants quality feedback or gap analysis.
- **analyze_fit**: Use when you need to measure alignment between customer needs and the value proposition (and optionally the business model).
- **compare**: Use when the user wants to understand competitive positioning or differentiation opportunities.

## Scoring thresholds
- VPC Quality: max 50 pts (10 characteristics x 5). Above 35 = strong.
- BMC Attractiveness: max 35 pts (7 dimensions x 5). Above 25 = strong.
- Fit scores: >70% = strong alignment, 40-70% = moderate, <40% = weak.

## Valid enum values (quick reference)
- **job_type**: functional, social, emotional
- **gain_type**: required, expected, desired, unexpected
- **channel_phase**: awareness, evaluation, purchase, delivery, after_sales
- **relationship_type**: personal_assistance, dedicated_assistance, self_service, automated, communities, co_creation
- **resource_type**: physical, intellectual, human, financial
- **activity_type**: production, problem_solving, platform
- **revenue_type**: asset_sale, usage_fee, subscription, lending, licensing, brokerage, advertising
- **pricing_mechanism**: fixed, dynamic, auction, market_dependent, volume_dependent, negotiation
- **cost_type**: fixed, variable
- **business_stage**: idea, startup, growth, mature
- **segment_type**: mass_market, niche, segmented, diversified, multi_sided
""",
)


# =============================================================================
# Tool 1: Create VPC
# =============================================================================

@mcp.tool(
    name="create_vpc",
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
    },
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
    """Build a Value Proposition Canvas from customer jobs, pains, gains, and your value map.

    Use when designing or documenting a value proposition for a specific customer segment.
    Returns a complete VPC with fit score, quality score (10 Characteristics, max 50 pts),
    validation results, and improvement recommendations.
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
    name="create_bmc",
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
    },
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
    """Build a Business Model Canvas describing how a business creates, delivers, and captures value.

    Use when mapping the 9 building blocks of a business model. Pass vpc_data to check alignment
    with an existing Value Proposition Canvas. Returns attractiveness score (7 dimensions, max 35 pts),
    validation results, and improvement recommendations.
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
    name="validate",
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
    },
)
def strategyzr_validate_canvas(
    canvas_type: Annotated[Literal["vpc", "bmc"], Field(description="Type of canvas to validate")],
    canvas_data: Annotated[dict, Field(description="The canvas data to validate")],
    check_vpc_alignment: Annotated[bool, Field(description="For BMC, whether to check VPC alignment")] = False,
    vpc_data: Annotated[dict | None, Field(description="VPC data for alignment check (required if check_vpc_alignment is True)")] = None,
) -> str:
    """Score and validate an existing VPC or BMC against Osterwalder best practices.

    Use when the user has canvas data and wants quality feedback or gap analysis.
    Returns validation results (errors, warnings, suggestions), quality score with
    breakdown, gap analysis, and prioritized improvement recommendations.
    """
    result = validate_canvas(canvas_type, canvas_data, check_vpc_alignment, vpc_data)
    return json.dumps(result, indent=2, default=str)


# =============================================================================
# Tool 4: Analyze Fit
# =============================================================================

@mcp.tool(
    name="analyze_fit",
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
    },
)
def strategyzr_analyze_fit(
    vpc_data: Annotated[dict, Field(description="VPC data to analyze")],
    bmc_data: Annotated[dict | None, Field(description="Optional BMC data for cross-canvas analysis")] = None,
    analysis_depth: Annotated[Literal["quick", "detailed"], Field(description="Analysis depth")] = "detailed",
) -> str:
    """Measure Problem-Solution Fit, Product-Market Fit indicators, and VPC-BMC alignment.

    Use when you need to assess how well a value proposition addresses customer needs.
    Pass bmc_data to also check business model alignment. Returns fit scores (>70% = strong),
    coverage analysis, and recommendations for improving fit.
    """
    result = analyze_fit(vpc_data, bmc_data, analysis_depth)
    return json.dumps(result, indent=2, default=str)


# =============================================================================
# Tool 5: Compare Competitors
# =============================================================================

@mcp.tool(
    name="compare",
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
    },
)
def strategyzr_compare_competitors(
    company_name: Annotated[str, Field(description="Your company name")],
    your_vpc: Annotated[dict, Field(description="Your VPC data")],
    competitors: Annotated[list[dict], Field(description="List of competitor data. Each: {name, pain_relievers: [...], gain_creators: [...]}")],
    market_context: Annotated[str | None, Field(description="Optional market context description")] = None,
) -> str:
    """Map competitor value propositions against yours for differentiation analysis.

    Use when the user wants to understand competitive positioning or find differentiation
    opportunities. Returns strengths, weaknesses, competitive threats, differentiation
    opportunities, 'difficult to copy' assessment, and positioning recommendations.
    """
    result = compare_competitors(company_name, your_vpc, competitors, market_context)
    return json.dumps(result, indent=2, default=str)


# =============================================================================
# Resources
# =============================================================================

@mcp.resource("strategyzr://template/vpc")
def get_vpc_template_resource() -> str:
    """VPC template with examples and guidance for filling each section."""
    return json.dumps(get_vpc_template(include_examples=True, include_guidance=True), indent=2)


@mcp.resource("strategyzr://template/bmc")
def get_bmc_template_resource() -> str:
    """BMC template with examples and guidance for filling each section."""
    return json.dumps(get_bmc_template(include_examples=True, include_guidance=True), indent=2)

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

Once you provide this information, use the create_vpc tool to generate your complete canvas with scores and recommendations.
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

Once you provide this information, use the create_bmc tool to generate your complete canvas with attractiveness scores and recommendations.
"""


@mcp.prompt()
def strategy_review(canvas_type: str) -> str:
    """Canvas review and improvement prompt."""
    return f"""# {canvas_type.upper()} Strategy Review

Let's review and improve your {'Value Proposition Canvas' if canvas_type == 'vpc' else 'Business Model Canvas'}.

## What I need from you
- Your canvas data (JSON from a previous create_vpc or create_bmc call, or raw dict)
- Optionally: competitor data for positioning analysis

## Review Process

1. **Validation Check**
   - Use the `validate` tool to check for errors, warnings, and gaps
   - Address any critical issues first

2. **Quality Assessment**
   - Review quality scores and breakdown by dimension
   - Identify lowest-scoring dimensions for targeted improvement

3. **Fit Analysis**
   - Use `analyze_fit` to measure Problem-Solution Fit and internal consistency
   - For BMC: pass vpc_data to check VPC-BMC alignment

4. **Competitive Position**
   - Use `compare` with competitor pain_relievers and gain_creators
   - Identify differentiation opportunities and competitive threats

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

async def health_check(request):
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
        import uvicorn
        host = "0.0.0.0"
        port = int(os.environ.get("PORT", 8000))
        app = mcp.http_app()
        app.add_route("/health", health_check, methods=["GET"])
        uvicorn.run(app, host=host, port=port)
    else:
        mcp.run()  # Default stdio for local use


if __name__ == "__main__":
    main()
