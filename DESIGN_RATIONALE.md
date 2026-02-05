# Design Rationale

This document explains the design decisions behind the StrategyZR MCP Server alternative implementation.

## Design Philosophy

This implementation takes a **structured data approach** rather than a prompt-based workflow approach:

| Aspect | Prompt-Based (Original) | Structured Data (This) |
|--------|------------------------|------------------------|
| **Input** | Free-form context | Pydantic-validated models |
| **Processing** | LLM interprets prompts | Computed algorithms |
| **Output** | Text prompts for LLM | JSON/Markdown structured data |
| **Quality** | Embedded in prompts | Computed scores returned |
| **Validation** | None (LLM interprets) | Pydantic constraints |
| **Testing** | Hard to unit test | Fully testable |

## Why This Approach?

### 1. Predictable Outputs

With structured data:
- Every field has defined constraints
- Quality scores are computed deterministically
- Results are reproducible

### 2. Composable

Canvases can be:
- Stored and retrieved
- Compared over time
- Used in other systems
- Processed programmatically

### 3. Testable

The entire scoring and analysis logic can be:
- Unit tested
- Integration tested
- Validated against known inputs

### 4. Type Safety

Pydantic models provide:
- IDE autocomplete
- Runtime validation
- Clear documentation
- Self-documenting APIs

## Architecture Decisions

### Separation of Concerns

```
models/       # Data structures (what)
validators/   # Business logic (how to assess)
tools/        # User-facing API (how to use)
server.py     # MCP integration (where to expose)
```

### Quality Scoring

Based directly on Osterwalder's published frameworks:

**VPC - 10 Characteristics** (from Value Proposition Design):
- Each characteristic maps to a scoring function
- Scores 1-5 per characteristic, max 50

**BMC - Attractiveness** (from Business Model Generation):
- 7 dimensions of business model quality
- Each maps to observable patterns in the BMC

### Fit Analysis

Implements the three-stage fit progression:

1. **Problem-Solution Fit**: Does VPC address real problems?
   - Computed from pain-reliever and gain-creator coverage

2. **Product-Market Fit Indicators**: Is there market evidence?
   - Computed from intensity, frequency, and effectiveness

3. **Business Model Fit**: Is BMC aligned with VPC?
   - Computed from segment, channel, and resource alignment

## Model Design

### VPC Models

```python
VPCInput
├── company_name: str
├── target_segment: str
├── customer_jobs: List[CustomerJob]      # 3-5 recommended
├── customer_pains: List[CustomerPain]    # 3-5 recommended
├── customer_gains: List[CustomerGain]    # 3-5 recommended
├── products_services: List[ProductService]
├── pain_relievers: List[PainReliever]    # Link to pains
└── gain_creators: List[GainCreator]      # Link to gains
```

Key decisions:
- Jobs have types (functional/social/emotional) per Osterwalder
- Pains have intensity AND frequency (both matter)
- Gains have types (required/expected/desired/unexpected)
- Relievers/creators link to specific pains/gains

### BMC Models

All 9 building blocks with typed components:
- Customer segments with segment types
- Value propositions with value types
- Channels with journey phases
- Relationships with Osterwalder's 6 types
- Revenue streams with pricing mechanisms
- Resources with resource types
- Activities with activity types
- Partnerships with partnership types
- Costs with fixed/variable classification

## Scoring Implementation

### VPC Quality Scorer

Each of the 10 characteristics maps to a scoring function:

```python
def _score_completeness(vpc)        # Characteristic 1
def _score_importance_focus(vpc)    # Characteristic 2
def _score_unsatisfied_focus(vpc)   # Characteristic 3
def _score_convergence(vpc)         # Characteristic 4
def _score_job_type_coverage(vpc)   # Characteristic 5
# ... etc
```

Each function:
1. Analyzes specific VPC aspects
2. Returns 1.0-5.0 score
3. Is independently testable

### BMC Attractiveness Scorer

Each dimension maps to observable patterns:

- **Switching costs**: Relationship depth, intellectual resources
- **Recurring revenue**: Subscription streams, recurring flags
- **Scalability**: Platform activities, automated relationships
- **Protection**: Intellectual resources, strategic partnerships

## Tool Design

### Tool Annotations

All tools include MCP annotations:

```python
@mcp.tool(
    annotations={
        "readOnlyHint": True,      # Analysis tools
        "destructiveHint": False,   # Never destructive
        "idempotentHint": True,     # Same input = same output
    }
)
```

### Response Formats

Tools support both:
- **Markdown**: Human-readable, includes visual elements
- **JSON**: Machine-readable, full data structure

## Trade-offs

### What We Gain

1. **Reproducibility**: Same input always produces same output
2. **Testability**: Full unit and integration test coverage
3. **Type safety**: Pydantic validates all inputs
4. **Transparency**: Scoring logic is explicit, not hidden in prompts
5. **Integration**: Data can flow to other systems

### What We Lose

1. **Flexibility**: Must conform to schema
2. **Natural language**: Requires structured input
3. **Adaptation**: Can't interpret ambiguous inputs

### The Right Tool for the Job

This approach is ideal when:
- You want consistent, measurable outputs
- You need to track changes over time
- You're integrating with other systems
- You want to test the scoring logic

The prompt-based approach is better when:
- Inputs are highly variable
- You want the LLM to interpret and adapt
- Free-form conversation is the interface

## Future Enhancements

### Potential Additions

1. **Persistence layer**: Store canvases with IDs
2. **Diff tool**: Compare canvas versions
3. **Export formats**: PDF, PPT generation
4. **Industry templates**: Pre-filled starting points
5. **Benchmarking**: Compare against industry averages

### API Evolution

The structured approach makes it easy to:
- Add new scoring dimensions
- Refine validation rules
- Extend models with new fields
- Version the API

## References

- Osterwalder, A. & Pigneur, Y. (2010). Business Model Generation
- Osterwalder, A. et al. (2014). Value Proposition Design
- MCP Specification: https://modelcontextprotocol.io
- FastMCP Documentation: https://gofastmcp.com
