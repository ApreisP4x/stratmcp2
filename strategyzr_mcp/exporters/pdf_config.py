"""
PDF layout configuration for Business Model Canvas template.

The BMC PDF template is landscape A4 (~842 x 595 points).
Coordinates are from bottom-left origin.
"""

from dataclasses import dataclass
from typing import NamedTuple


class TextBox(NamedTuple):
    """Defines a text insertion area in the PDF."""
    x: float  # X coordinate (from left)
    y: float  # Y coordinate (from bottom)
    width: float  # Maximum width for text wrapping
    height: float  # Maximum height before truncation
    font_size: float = 9.0  # Default font size
    min_font_size: float = 6.0  # Minimum before truncation


@dataclass
class FontConfig:
    """Font configuration for PDF text."""
    font_name: str = "helv"  # Helvetica (built-in PDF font)
    color: tuple[float, float, float] = (0.2, 0.2, 0.2)  # Dark gray RGB
    line_height: float = 1.3  # Line height multiplier


@dataclass
class BMCPDFLayout:
    """
    Layout coordinates for the 9 BMC building blocks plus metadata fields.

    The PDF template has the standard Strategyzer BMC layout:
    - Top row: Key Partners | Key Activities + Key Resources | Value Props | Customer Rels + Channels | Customer Segments
    - Bottom row: Cost Structure | Revenue Streams

    Coordinates are calibrated for the Strategyzer Business-model-canvas.pdf template.
    These may need adjustment based on the exact PDF version.
    """

    # Building block text boxes (x, y, width, height, font_size, min_font_size)
    # Coordinates calibrated for landscape A4 (~842 x 595 points)

    # Left column
    key_partnerships: TextBox = TextBox(
        x=38, y=390, width=130, height=170, font_size=8, min_font_size=6
    )

    # Second column (split vertically)
    key_activities: TextBox = TextBox(
        x=178, y=480, width=115, height=80, font_size=8, min_font_size=6
    )
    key_resources: TextBox = TextBox(
        x=178, y=390, width=115, height=80, font_size=8, min_font_size=6
    )

    # Center column
    value_propositions: TextBox = TextBox(
        x=305, y=390, width=135, height=170, font_size=8, min_font_size=6
    )

    # Fourth column (split vertically)
    customer_relationships: TextBox = TextBox(
        x=452, y=480, width=115, height=80, font_size=8, min_font_size=6
    )
    channels: TextBox = TextBox(
        x=452, y=390, width=115, height=80, font_size=8, min_font_size=6
    )

    # Right column
    customer_segments: TextBox = TextBox(
        x=578, y=390, width=130, height=170, font_size=8, min_font_size=6
    )

    # Bottom row (spans full width, split horizontally)
    cost_structure: TextBox = TextBox(
        x=38, y=280, width=370, height=95, font_size=8, min_font_size=6
    )
    revenue_streams: TextBox = TextBox(
        x=428, y=280, width=280, height=95, font_size=8, min_font_size=6
    )

    # Metadata fields (top of canvas)
    designed_for: TextBox = TextBox(
        x=135, y=555, width=200, height=15, font_size=9, min_font_size=7
    )
    designed_by: TextBox = TextBox(
        x=405, y=555, width=150, height=15, font_size=9, min_font_size=7
    )
    date: TextBox = TextBox(
        x=600, y=555, width=80, height=15, font_size=9, min_font_size=7
    )
    version: TextBox = TextBox(
        x=735, y=555, width=60, height=15, font_size=9, min_font_size=7
    )


# Default layout instance
DEFAULT_BMC_LAYOUT = BMCPDFLayout()
DEFAULT_FONT_CONFIG = FontConfig()
