# StrategyZR MCP Server (Alternative Implementation)

A structured data approach to Business Model Canvas (BMC) and Value Proposition Canvas (VPC) using the Model Context Protocol (MCP).

## Overview

This MCP server implements Osterwalder's strategic canvas frameworks with:

- **Pydantic validation** for all inputs
- **Computed quality scores** based on proven frameworks
- **Fit analysis** between VPC and BMC
- **Competitive positioning** analysis

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/stratmcp2.git
cd stratmcp2

# Install dependencies
pip install -e .

# Or with development dependencies
pip install -e ".[dev]"
```

## Running the Server

```bash
# Using the installed command
strategyzr-mcp

# Or directly
python -m strategyzr_mcp.server
```

## Tools

### 1. `strategyzr_create_vpc`

Create a Value Proposition Canvas with structured validation and scoring.

**Returns:**
- Complete VPC with customer profile and value map
- Fit score (problem-solution fit, pain/gain coverage)
- Quality score based on 10 Characteristics of Great Value Propositions
- Recommendations for improvement

### 2. `strategyzr_create_bmc`

Create a Business Model Canvas with all 9 building blocks.

**Returns:**
- Complete BMC structure
- Business Model Attractiveness score (7 dimensions)
- VPC alignment check (optional)
- Strategic recommendations

### 3. `strategyzr_validate_canvas`

Validate and score an existing canvas.

**Returns:**
- Validation results (errors, warnings, suggestions)
- Quality score breakdown
- Gap analysis
- Prioritized recommendations

### 4. `strategyzr_analyze_fit`

Analyze fit within VPC and between VPC/BMC.

**Returns:**
- Problem-Solution Fit score
- Product-Market Fit indicators
- VPC-BMC alignment (if BMC provided)
- Human-readable interpretation

### 5. `strategyzr_compare_competitors`

Compare your value proposition against competitors.

**Returns:**
- Your strengths and weaknesses
- Differentiation opportunities
- "Difficult to copy" assessment
- Positioning recommendations

### 6. `strategyzr_get_template`

Get empty canvas templates with field descriptions.

**Returns:**
- Empty template structure
- Field constraints and descriptions
- Optional examples
- Filling guidance

## Resources

- `strategyzr://methodology` - Osterwalder methodology overview
- `strategyzr://quality-criteria` - 10 Characteristics & Attractiveness criteria

## Prompts

- `vpc_workshop` - Interactive VPC creation guide
- `bmc_workshop` - Interactive BMC creation guide
- `strategy_review` - Canvas review and improvement workflow

## Quality Frameworks

### 10 Characteristics of Great Value Propositions (VPC)

Each scored 1-5, max 50 points:

1. Embedded in great business models
2. Focus on most important jobs, pains, gains
3. Focus on unsatisfied jobs, pains, gains
4. Converge on few things done well
5. Address functional, emotional, and social jobs
6. Align with customer success metrics
7. Focus on high-impact jobs, pains, gains
8. Differentiate from competition
9. Outperform competition substantially
10. Difficult to copy

### Business Model Attractiveness (BMC)

7 dimensions, max 35 points:

1. **Switching Costs** - Customer lock-in
2. **Recurring Revenues** - Predictable income
3. **Earning vs Spending** - Cash flow timing
4. **Cost Structure** - Efficiency
5. **Others Do Work** - Leverage
6. **Scalability** - Growth potential
7. **Protection** - Competitive barriers

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=strategyzr_mcp

# Run specific test file
pytest tests/test_models.py
```

## Project Structure

```
stratmcp2/
├── strategyzr_mcp/
│   ├── __init__.py
│   ├── server.py              # Main FastMCP server
│   ├── models/
│   │   ├── common.py          # Shared enums and base models
│   │   ├── vpc.py             # VPC Pydantic models
│   │   └── bmc.py             # BMC Pydantic models
│   ├── tools/
│   │   ├── vpc_tools.py       # VPC creation/template tools
│   │   ├── bmc_tools.py       # BMC creation/template tools
│   │   └── analysis_tools.py  # Validation, fit, competitors
│   ├── validators/
│   │   ├── quality_scorer.py  # 10 Characteristics & Attractiveness
│   │   └── fit_analyzer.py    # VPC-BMC fit analysis
│   └── templates/
│       ├── vpc_template.json  # JSON schema for VPC
│       └── bmc_template.json  # JSON schema for BMC
├── tests/
│   ├── test_models.py
│   ├── test_validators.py
│   └── test_server.py
├── pyproject.toml
├── requirements.txt
├── README.md
└── DESIGN_RATIONALE.md
```

## Configuration for Claude Desktop

Add to your Claude Desktop MCP settings:

```json
{
  "mcpServers": {
    "strategyzr": {
      "command": "strategyzr-mcp"
    }
  }
}
```

Or with explicit Python path:

```json
{
  "mcpServers": {
    "strategyzr": {
      "command": "python",
      "args": ["-m", "strategyzr_mcp.server"],
      "cwd": "/path/to/stratmcp2"
    }
  }
}
```

## License

MIT License
