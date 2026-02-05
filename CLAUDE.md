# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

StrategyZR MCP Server implements Osterwalder's strategic canvas frameworks (Business Model Canvas and Value Proposition Canvas) using the Model Context Protocol. It takes a **structured data approach** with Pydantic validation rather than prompt-based workflows, enabling reproducible, testable, and composable outputs.

## Commands

```bash
# Install
pip install -e .              # Install from source
pip install -e ".[dev]"       # With dev dependencies (pytest)

# Run server
strategyzr-mcp                # Using installed entry point
python -m strategyzr_mcp.server  # Direct module execution

# Tests
pytest                        # All tests
pytest --cov=strategyzr_mcp   # With coverage
pytest tests/test_models.py   # Single test file
pytest tests/test_validators.py -k "test_vpc"  # Specific test by name
```

## Architecture

```
models/       → Data structures (Pydantic schemas, enums)
validators/   → Business logic (scoring algorithms, fit analysis)
tools/        → User-facing MCP tools (create, validate, analyze)
server.py     → MCP server hub (registers tools, resources, prompts)
```

**Data flow:** Input dict → Pydantic validation → Validators (scoring) → Output models → Markdown/JSON rendering

### Key Components

- **server.py**: FastMCP server with 6 tools, 2 resources, 3 prompts, and `/health` endpoint
- **models/common.py**: 11 enums (JobType, GainType, RelationshipType, etc.) and base models
- **models/vpc.py**: Customer profile and value map models (CustomerJob, CustomerPain, PainReliever, etc.)
- **models/bmc.py**: 9 building blocks of BMC (CustomerSegment, ValueProposition, RevenueStream, etc.)
- **validators/quality_scorer.py**: VPC 10 Characteristics scoring (max 50 pts) + BMC Attractiveness scoring (max 35 pts)
- **validators/fit_analyzer.py**: Problem-Solution Fit, Product-Market Fit indicators, VPC-BMC alignment

### MCP Tool Design

All tools use annotations:
```python
@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True})
```

Tools: `strategyzr_create_vpc`, `strategyzr_create_bmc`, `strategyzr_validate_canvas`, `strategyzr_analyze_fit`, `strategyzr_compare_competitors`, `strategyzr_get_template`

## Quality Scoring Frameworks

**VPC - 10 Characteristics** (Osterwalder): Each 1-5 points, computed by dedicated `_score_*` functions in quality_scorer.py

**BMC - Attractiveness**: 7 dimensions (switching costs, recurring revenues, scalability, protection, etc.)

**Fit Analysis**: Three-stage progression from Problem-Solution Fit → Product-Market Fit indicators → Business Model Fit

## Coding Patterns

- Heavy Pydantic usage: `Field()` with constraints, `field_validator` decorators, enum validation
- Type hints throughout: `def create_vpc(vpc_input: VPCInput) -> VPCOutput:`
- Private functions: `_score_completeness()`, `_generate_vpc_markdown()`
- Tests: class-based organization (`TestVPCModels`, `TestVPCTools`)

## Transport Modes

- **stdio**: Local use with Claude Desktop (default)
- **HTTP**: Remote deployment (set `MCP_TRANSPORT=http`, uses port 8000)
