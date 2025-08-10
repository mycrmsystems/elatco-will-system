from io import BytesIO
from html import escape
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import mm

# Spacing helpers and styles
LINE = Spacer(1, 4 * mm)

TITLE = ParagraphStyle(
    name="Title",
    parent=getSampleStyleSheet()["Heading1"],
    alignment=TA_CENTER,
    spaceAfter=8,
)
SUBTITLE = ParagraphStyle(
    name="Subtitle",
    parent=getSampleStyleSheet()["Heading3"],
    spaceBefore=6,
    spaceAfter=6,
)
BODY = getSampleStyleSheet()["BodyText"]
BODY.spaceAfter = 4

LEGAL_NOTE = ParagraphStyle(
    name="Legal",
    parent=BODY,
    fontSize=8,
    leading=10,
    spaceBefore=8,
)

def build_will_pdf(will) -> bytes:
    """
    Build a professional PDF from a Will ORM object.
    Returns raw PDF bytes.
    """
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
    )

    story = []

    # Header
    story.append(Paragraph("Last Will and Testament", TITLE))
    story.append(Paragraph(f"of {escape(will.client_name or '')}", SUBTITLE))

    # Personal details
    story.append(Paragraph("1. Personal Details", SUBTITLE))
    if getattr(will, "dob", None):
        story.append(Paragraph(f"Date of Birth: {escape(will.dob)}", BODY))
    if getattr(will, "address", None):
        story.append(Paragraph(f"Address: {escape(will.address)}", BODY))

    # Executors / Guardians
    if getattr(will, "executors", None):
        story.append(Paragraph("2. Appointment of Executors", SUBTITLE))
        story.append(Paragraph(escape(will.executors), BODY))
    if getattr(will, "guardians", None):
        story.append(Paragraph("3. Appointment of Guardians", SUBTITLE))
        story.append(Paragraph(escape(will.guardians), BODY))

    # Gifts
    if getattr(will, "gifts", None):
        story.append(Paragraph("4. Specific Gifts & Legacies", SUBTITLE))
        story.append(Paragraph(escape(will.gifts), BODY))

    # Residuary
    if getattr(will, "residuary", None):
        story.append(Paragraph("5. Residuary Estate", SUBTITLE))
        story.append(Paragraph(escape(will.residuary), BODY))

    # Trust provisions
    if getattr(will, "trust_type", None) and will.trust_type != "None" and getattr(will, "trust_text", None):
        story.append(Paragraph("6. Trust Provisions", SUBTITLE))
        for para in (will.trust_text or "").split("\n\n"):
            para = para.strip()
            if para:
                story.append(Paragraph(escape(para), BODY))

    # Execution block
    story.append(Paragraph("\n\nExecuted as a Will on the date of signature below.", BODY))
    story.append(Spacer(1, 14 * mm))
    story.append(Paragraph("Signed by the Testator in the presence of:", BODY))
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph("______________________________    ______________________________", BODY))
    story.append(Paragraph("Testator Signature                      Date", BODY))
    story.append(Spacer(1, 12 * mm))
    story.append(Paragraph("Witness 1: Name/Address/Signature", BODY))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph("Witness 2: Name/Address/Signature", BODY))

    # Disclaimer
    story.append(Spacer(1, 10 * mm))
    story.append(Paragraph(
        "This document is generated from template wording and is provided for review. "
        "You are responsible for ensuring legal suitability and witnessing in accordance with applicable law.",
        LEGAL_NOTE
    ))

    doc.build(story)
    pdf = buf.getvalue()
    buf.close()
    return pdf
