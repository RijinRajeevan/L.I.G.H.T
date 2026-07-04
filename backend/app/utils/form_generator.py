from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import os
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# ── Color themes per form type ──────────────────────────────────────────────
THEMES = {
    "aadhaar": {
        "header":      colors.HexColor("#003366"),  # UIDAI navy
        "accent":      colors.HexColor("#C9A84C"),  # gold
        "row_bg":      colors.HexColor("#E8F0F7"),
        "border":      colors.HexColor("#B0C4DE"),
    },
    "dl": {
        "header":      colors.HexColor("#1A472A"),  # MVD deep green
        "accent":      colors.HexColor("#D4A017"),  # amber
        "row_bg":      colors.HexColor("#EAF4EA"),
        "border":      colors.HexColor("#A3C4A3"),
    },
    "default": {
        "header":      colors.HexColor("#4A4A4A"),
        "accent":      colors.HexColor("#888888"),
        "row_bg":      colors.HexColor("#F5F5F5"),
        "border":      colors.HexColor("#CCCCCC"),
    },
}

# A4 usable width = 21cm - 2cm (left) - 2cm (right) = 17cm
PAGE_W = 17 * cm
LABEL_W = 5.5 * cm
VALUE_W = PAGE_W - LABEL_W  # 11.5cm

class FormGenerator:
    """
    Generates high-fidelity pre-filled government application forms as PDFs using ReportLab.
    Designed to look professional and official for the hackathon presentation.
    """
    def __init__(self):
        self.output_dir = "backend/app/temp_forms"
        os.makedirs(self.output_dir, exist_ok=True)

    def generate(self, service_type, user_data):
        """
        Generates a polished, professional PDF using ReportLab's Platypus layout engine.
        """
        filename = f"{service_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(self.output_dir, filename)

        # Load field metadata
        meta_path = f"backend/app/data/forms/{service_type}.json"
        template_meta = None
        if os.path.exists(meta_path):
            with open(meta_path, "r") as f:
                template_meta = json.load(f)

        # Pick color theme by form type keyword
        theme_key = "default"
        stype_lower = service_type.lower()
        if "aadhaar" in stype_lower or "aadhar" in stype_lower:
            theme_key = "aadhaar"
        elif "dl" in stype_lower or "driving" in stype_lower or "licence" in stype_lower:
            theme_key = "dl"
        T = THEMES[theme_key]
        HDR_COLOR = T["header"]
        ACCENT    = T["accent"]
        ROW_BG    = T["row_bg"]
        BORDER    = T["border"]

        fields = []
        if template_meta:
            for field in template_meta.get("fields", []):
                fields.append({
                    "label": field["label"],
                    "value": str(user_data.get(field["id"], " "))
                })
        else:
            for key, val in user_data.items():
                fields.append({
                    "label": key.replace("_", " ").title(),
                    "value": str(val)
                })

        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            leftMargin=2*cm,
            rightMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        styles = getSampleStyleSheet()
        story = []

        # ── Header ──────────────────────────────────────────────────────────────
        header_style = ParagraphStyle(
            "Header",
            fontName="Helvetica-Bold",
            fontSize=15,
            textColor=HDR_COLOR,
            alignment=TA_CENTER,
            spaceAfter=3
        )
        sub_header_style = ParagraphStyle(
            "SubHeader",
            fontName="Helvetica-Bold",
            fontSize=10,
            textColor=HDR_COLOR,
            alignment=TA_CENTER,
            spaceAfter=2
        )
        dept_name = template_meta.get("department", "Government of India") if template_meta else "Government of India"
        act_ref   = template_meta.get("act_reference", "") if template_meta else ""

        story.append(Paragraph(dept_name, header_style))
        if act_ref:
            story.append(Paragraph(f"[{act_ref}]", sub_header_style))
        story.append(HRFlowable(width="100%", thickness=2, color=HDR_COLOR, spaceAfter=6))

        # ── Form Title Banner ───────────────────────────────────────────────────
        form_title = template_meta.get("form_name", service_type.replace("_", " ").title()) if template_meta else service_type.replace("_", " ").title()
        title_table = Table(
            [[Paragraph(f"<b>{form_title.upper()}</b>", ParagraphStyle("T", fontName="Helvetica-Bold", fontSize=13, textColor=colors.white, alignment=TA_CENTER))]],
            colWidths=[PAGE_W]
        )
        title_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), HDR_COLOR),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ]))
        story.append(title_table)
        story.append(Spacer(1, 0.5*cm))

        # ── Field rows ──────────────────────────────────────────────────────────
        label_style = ParagraphStyle("Label", fontName="Helvetica-Bold", fontSize=10, textColor=HDR_COLOR)
        value_style = ParagraphStyle("Value", fontName="Helvetica", fontSize=11, textColor=colors.black)

        table_data = []
        for field in fields:
            label = Paragraph(field["label"].upper(), label_style)
            value = Paragraph(field["value"] if field["value"].strip() else "________________", value_style)
            table_data.append([label, value])

        if table_data:
            field_table = Table(table_data, colWidths=[LABEL_W, VALUE_W])
            field_table.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("BACKGROUND", (0, 0), (0, -1), ROW_BG),
                ("LINEBELOW", (0, 0), (-1, -2), 0.5, BORDER),
                ("BOX", (0, 0), (-1, -1), 1, BORDER),
            ]))
            story.append(field_table)
            story.append(Spacer(1, 1*cm))

        # ── Declaration ─────────────────────────────────────────────────────────
        decl_text = template_meta.get("declaration", "I hereby declare that all the information provided above is true to the best of my knowledge and belief. Providing false information is a punishable offence under the Aadhaar Act, 2016.") if template_meta else "I hereby declare that all the information provided above is true."
        decl_style = ParagraphStyle("Decl", fontName="Helvetica-Oblique", fontSize=9, textColor=colors.grey, spaceAfter=6)
        story.append(Paragraph(f"<b>Declaration:</b> {decl_text}", decl_style))
        story.append(Spacer(1, 1.5*cm))

        # ── Signature & Date row ─────────────────────────────────────────────────
        sig_data = [[
            Paragraph(f"Date: <b>{datetime.now().strftime('%d/%m/%Y')}</b>",
                      ParagraphStyle("Date", fontName="Helvetica", fontSize=10)),
            Paragraph("_______________________<br/>Signature of Applicant",
                      ParagraphStyle("Sig", fontName="Helvetica", fontSize=10, alignment=TA_CENTER))
        ]]
        sig_table = Table(sig_data, colWidths=["50%", "50%"])
        sig_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "BOTTOM"), ("TOPPADDING", (0, 0), (-1, -1), 5)]))
        story.append(sig_table)
        story.append(Spacer(1, 1.5*cm))

        # ── Footer ──────────────────────────────────────────────────────────────
        story.append(HRFlowable(width="100%", thickness=1, color=ACCENT))
        footer_style = ParagraphStyle("Footer", fontName="Helvetica", fontSize=8, textColor=colors.grey, alignment=TA_CENTER, spaceBefore=4)
        story.append(Paragraph("Generated by NYAANA-VAAS AI KIOSK &bull; Akshaya Digital Support Centre &bull; Govt of Kerala", footer_style))

        doc.build(story)
        logger.info(f"Professional PDF generated via ReportLab: {filepath}")
        return filepath, filename

