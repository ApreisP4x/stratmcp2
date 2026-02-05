"""
PDF exporter for Business Model Canvas.

Uses PyMuPDF (fitz) to overlay text on the Strategyzer BMC template.
"""

import base64
from datetime import date
from pathlib import Path
from typing import Any

import fitz  # PyMuPDF

from .pdf_config import (
    BMCPDFLayout,
    FontConfig,
    TextBox,
    DEFAULT_BMC_LAYOUT,
    DEFAULT_FONT_CONFIG,
)


class BMCPDFExporter:
    """
    Exports Business Model Canvas data to a filled PDF template.

    Uses the official Strategyzer BMC template and overlays text
    at predefined coordinates for each of the 9 building blocks.
    """

    def __init__(
        self,
        template_path: str | Path | None = None,
        layout: BMCPDFLayout | None = None,
        font_config: FontConfig | None = None,
    ):
        """
        Initialize the PDF exporter.

        Args:
            template_path: Path to PDF template. Defaults to bundled template.
            layout: PDF layout configuration. Defaults to standard BMC layout.
            font_config: Font configuration. Defaults to standard config.
        """
        if template_path is None:
            # Use bundled template
            template_path = Path(__file__).parent.parent / "templates" / "bmc_template.pdf"
        self.template_path = Path(template_path)

        if not self.template_path.exists():
            raise FileNotFoundError(f"PDF template not found: {self.template_path}")

        self.layout = layout or DEFAULT_BMC_LAYOUT
        self.font_config = font_config or DEFAULT_FONT_CONFIG
        self._warnings: list[str] = []
        self._truncations: list[dict[str, Any]] = []
        self._font_reductions: list[dict[str, Any]] = []

    def export(
        self,
        bmc_data: dict[str, Any],
        designed_for: str | None = None,
        designed_by: str | None = None,
        version: str | None = None,
        export_date: date | None = None,
    ) -> tuple[bytes, dict[str, Any]]:
        """
        Export BMC data to a filled PDF.

        Args:
            bmc_data: BMC data dictionary with building block content.
            designed_for: "Designed for" field (company/project name).
            designed_by: "Designed by" field (author name).
            version: Version string.
            export_date: Date for the canvas. Defaults to today.

        Returns:
            Tuple of (PDF bytes, warnings/metadata dict).
        """
        self._warnings = []
        self._truncations = []
        self._font_reductions = []

        # Open template
        doc = fitz.open(self.template_path)
        page = doc[0]  # BMC is single page

        # Fill metadata
        if designed_for:
            self._insert_text(page, self.layout.designed_for, designed_for, "designed_for")
        if designed_by:
            self._insert_text(page, self.layout.designed_by, designed_by, "designed_by")
        if version:
            self._insert_text(page, self.layout.version, version, "version")

        date_str = (export_date or date.today()).strftime("%Y-%m-%d")
        self._insert_text(page, self.layout.date, date_str, "date")

        # Fill the 9 building blocks
        self._fill_key_partnerships(page, bmc_data)
        self._fill_key_activities(page, bmc_data)
        self._fill_key_resources(page, bmc_data)
        self._fill_value_propositions(page, bmc_data)
        self._fill_customer_relationships(page, bmc_data)
        self._fill_channels(page, bmc_data)
        self._fill_customer_segments(page, bmc_data)
        self._fill_cost_structure(page, bmc_data)
        self._fill_revenue_streams(page, bmc_data)

        # Get PDF bytes
        pdf_bytes = doc.tobytes()
        doc.close()

        metadata = {
            "warnings": self._warnings,
            "truncations": self._truncations,
            "font_reductions": self._font_reductions,
        }

        return pdf_bytes, metadata

    def export_base64(
        self,
        bmc_data: dict[str, Any],
        designed_for: str | None = None,
        designed_by: str | None = None,
        version: str | None = None,
        export_date: date | None = None,
    ) -> tuple[str, dict[str, Any]]:
        """
        Export BMC data to a base64-encoded PDF string.

        Args:
            Same as export().

        Returns:
            Tuple of (base64-encoded PDF string, warnings/metadata dict).
        """
        pdf_bytes, metadata = self.export(
            bmc_data, designed_for, designed_by, version, export_date
        )
        return base64.b64encode(pdf_bytes).decode("utf-8"), metadata

    def _insert_text(
        self,
        page: fitz.Page,
        box: TextBox,
        text: str,
        field_name: str,
    ) -> None:
        """
        Insert text into a text box, handling overflow.

        Reduces font size if needed, then truncates with "..." if still too long.
        """
        if not text or not text.strip():
            return

        text = text.strip()

        # Create text rect
        rect = fitz.Rect(box.x, box.y, box.x + box.width, box.y + box.height)

        # Try with default font size
        font_size = box.font_size
        fontname = self.font_config.font_name
        color = self.font_config.color

        # Get font for text measurement
        font = fitz.Font(fontname)

        # Calculate how many lines we can fit
        line_height = font_size * self.font_config.line_height

        # Wrap text to fit width
        wrapped_lines = self._wrap_text(text, font, font_size, box.width)
        total_height = len(wrapped_lines) * line_height

        # Reduce font size if needed
        while total_height > box.height and font_size > box.min_font_size:
            font_size -= 0.5
            line_height = font_size * self.font_config.line_height
            wrapped_lines = self._wrap_text(text, font, font_size, box.width)
            total_height = len(wrapped_lines) * line_height

        if font_size < box.font_size:
            self._font_reductions.append({
                "field": field_name,
                "original_size": box.font_size,
                "reduced_size": font_size,
            })

        # Truncate if still too long
        max_lines = int(box.height / line_height)
        if len(wrapped_lines) > max_lines:
            wrapped_lines = wrapped_lines[:max_lines]
            if wrapped_lines:
                wrapped_lines[-1] = self._truncate_line(wrapped_lines[-1], font, font_size, box.width)
            self._truncations.append({
                "field": field_name,
                "original_length": len(text),
            })
            self._warnings.append(f"Content truncated in {field_name}")

        # Insert each line
        y_pos = box.y
        for line in wrapped_lines:
            text_point = fitz.Point(box.x, y_pos + font_size)  # baseline position
            page.insert_text(
                text_point,
                line,
                fontname=fontname,
                fontsize=font_size,
                color=color,
            )
            y_pos += line_height

    def _wrap_text(
        self,
        text: str,
        font: fitz.Font,
        font_size: float,
        max_width: float,
    ) -> list[str]:
        """Wrap text to fit within max_width."""
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = " ".join(current_line + [word])
            text_width = font.text_length(test_line, fontsize=font_size)

            if text_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]

                # Handle very long words
                word_width = font.text_length(word, fontsize=font_size)
                if word_width > max_width:
                    # Force break the word
                    lines[-1] = self._truncate_line(word, font, font_size, max_width)
                    current_line = []

        if current_line:
            lines.append(" ".join(current_line))

        return lines

    def _truncate_line(
        self,
        line: str,
        font: fitz.Font,
        font_size: float,
        max_width: float,
    ) -> str:
        """Truncate a line to fit, adding '...' at the end."""
        ellipsis = "..."
        ellipsis_width = font.text_length(ellipsis, fontsize=font_size)
        available_width = max_width - ellipsis_width

        while line and font.text_length(line, fontsize=font_size) > available_width:
            line = line[:-1]

        return line.rstrip() + ellipsis if line else ellipsis

    def _format_list_items(self, items: list[Any], format_func: callable) -> str:
        """Format a list of items as bullet points."""
        if not items:
            return ""

        lines = []
        for item in items:
            formatted = format_func(item)
            if formatted:
                lines.append(f"• {formatted}")

        return "\n".join(lines)

    # =========================================================================
    # Building Block Fillers
    # =========================================================================

    def _fill_key_partnerships(self, page: fitz.Page, bmc_data: dict) -> None:
        """Fill Key Partnerships section."""
        partnerships = bmc_data.get("key_partnerships", [])

        def format_partnership(p: dict) -> str:
            name = p.get("partner_name", "")
            ptype = p.get("partnership_type", "").replace("_", " ")
            return f"{name} ({ptype})" if ptype else name

        text = self._format_list_items(partnerships, format_partnership)
        self._insert_text(page, self.layout.key_partnerships, text, "key_partnerships")

    def _fill_key_activities(self, page: fitz.Page, bmc_data: dict) -> None:
        """Fill Key Activities section."""
        activities = bmc_data.get("key_activities", [])

        def format_activity(a: dict) -> str:
            name = a.get("name", "")
            atype = a.get("activity_type", "")
            if isinstance(atype, str):
                atype = atype.replace("_", " ")
            else:
                atype = getattr(atype, "value", str(atype)).replace("_", " ")
            return f"{name} ({atype})" if atype else name

        text = self._format_list_items(activities, format_activity)
        self._insert_text(page, self.layout.key_activities, text, "key_activities")

    def _fill_key_resources(self, page: fitz.Page, bmc_data: dict) -> None:
        """Fill Key Resources section."""
        resources = bmc_data.get("key_resources", [])

        def format_resource(r: dict) -> str:
            name = r.get("name", "")
            rtype = r.get("resource_type", "")
            if isinstance(rtype, str):
                rtype = rtype.replace("_", " ")
            else:
                rtype = getattr(rtype, "value", str(rtype)).replace("_", " ")
            return f"{name} ({rtype})" if rtype else name

        text = self._format_list_items(resources, format_resource)
        self._insert_text(page, self.layout.key_resources, text, "key_resources")

    def _fill_value_propositions(self, page: fitz.Page, bmc_data: dict) -> None:
        """Fill Value Propositions section."""
        props = bmc_data.get("value_propositions", [])

        def format_prop(p: dict) -> str:
            desc = p.get("description", "")
            target = p.get("target_segment", "")
            if target:
                return f"{desc} (for {target})"
            return desc

        text = self._format_list_items(props, format_prop)
        self._insert_text(page, self.layout.value_propositions, text, "value_propositions")

    def _fill_customer_relationships(self, page: fitz.Page, bmc_data: dict) -> None:
        """Fill Customer Relationships section."""
        relationships = bmc_data.get("customer_relationships", [])

        def format_rel(r: dict) -> str:
            segment = r.get("segment", "")
            rtype = r.get("relationship_type", "")
            if isinstance(rtype, str):
                rtype = rtype.replace("_", " ")
            else:
                rtype = getattr(rtype, "value", str(rtype)).replace("_", " ")
            return f"{segment}: {rtype}" if segment else rtype

        text = self._format_list_items(relationships, format_rel)
        self._insert_text(page, self.layout.customer_relationships, text, "customer_relationships")

    def _fill_channels(self, page: fitz.Page, bmc_data: dict) -> None:
        """Fill Channels section."""
        channels = bmc_data.get("channels", [])

        def format_channel(c: dict) -> str:
            name = c.get("name", "")
            ctype = c.get("channel_type", "").replace("_", " ")
            return f"{name} ({ctype})" if ctype else name

        text = self._format_list_items(channels, format_channel)
        self._insert_text(page, self.layout.channels, text, "channels")

    def _fill_customer_segments(self, page: fitz.Page, bmc_data: dict) -> None:
        """Fill Customer Segments section."""
        segments = bmc_data.get("customer_segments", [])

        def format_segment(s: dict) -> str:
            name = s.get("name", "")
            stype = s.get("segment_type", "").replace("_", " ")
            primary = " [PRIMARY]" if s.get("is_primary") else ""
            return f"{name}{primary} ({stype})" if stype else f"{name}{primary}"

        text = self._format_list_items(segments, format_segment)
        self._insert_text(page, self.layout.customer_segments, text, "customer_segments")

    def _fill_cost_structure(self, page: fitz.Page, bmc_data: dict) -> None:
        """Fill Cost Structure section."""
        costs = bmc_data.get("cost_structure", [])

        def format_cost(c: dict) -> str:
            name = c.get("name", "")
            ctype = c.get("cost_type", "")
            if isinstance(ctype, str):
                ctype = ctype.replace("_", " ")
            else:
                ctype = getattr(ctype, "value", str(ctype)).replace("_", " ")
            key = " [KEY]" if c.get("is_key_cost") else ""
            return f"{name}{key} ({ctype})" if ctype else f"{name}{key}"

        text = self._format_list_items(costs, format_cost)
        self._insert_text(page, self.layout.cost_structure, text, "cost_structure")

    def _fill_revenue_streams(self, page: fitz.Page, bmc_data: dict) -> None:
        """Fill Revenue Streams section."""
        streams = bmc_data.get("revenue_streams", [])

        def format_stream(s: dict) -> str:
            name = s.get("name", "")
            rtype = s.get("revenue_type", "")
            if isinstance(rtype, str):
                rtype = rtype.replace("_", " ")
            else:
                rtype = getattr(rtype, "value", str(rtype)).replace("_", " ")
            recurring = " [RECURRING]" if s.get("is_recurring") else ""
            return f"{name}{recurring} ({rtype})" if rtype else f"{name}{recurring}"

        text = self._format_list_items(streams, format_stream)
        self._insert_text(page, self.layout.revenue_streams, text, "revenue_streams")
