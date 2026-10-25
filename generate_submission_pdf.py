"""Submission Document Generator for MailCheck.

Generates a neat, one-page academic submission PDF containing project title,
description, live application URL, and GitHub repository URL using ReportLab.

Usage:
    python generate_submission_pdf.py --live-url <URL> --repo-url <URL> [--student-name <NAME>] [--output <FILE>]
"""

import argparse
import os
import sys
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch


def generate_submission_pdf(
    live_url: str,
    repo_url: str,
    student_name: str = "Student Developer",
    course_name: str = "Software Development Project Assignment",
    output_filename: str = "MailCheck_Project_Submission.pdf",
):
    """Generate a clean, professional, single-page submission PDF."""
    if not live_url or not repo_url:
        raise ValueError("Both --live-url and --repo-url must be provided with real URLs.")

    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    primary_color = colors.HexColor("#1e40af")   # Deep navy blue
    accent_blue = colors.HexColor("#2563eb")     # Brand blue
    text_dark = colors.HexColor("#0f172a")       # Slate 900
    text_muted = colors.HexColor("#475569")      # Slate 600
    card_bg = colors.HexColor("#f8fafc")         # Slate 50
    border_color = colors.HexColor("#cbd5e1")    # Slate 300
    green_accent = colors.HexColor("#16a34a")

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=primary_color,
        alignment=0,
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=accent_blue,
        alignment=0,
    )

    body_style = ParagraphStyle(
        "DocBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=text_dark,
    )

    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=primary_color,
        spaceAfter=4,
    )

    link_label_style = ParagraphStyle(
        "LinkLabel",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=14,
        textColor=text_dark,
    )

    link_url_style = ParagraphStyle(
        "LinkUrl",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=13,
        textColor=accent_blue,
    )

    disclaimer_style = ParagraphStyle(
        "DisclaimerText",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#7c2d12"),
    )

    elements = []

    # 1. Header & Title Block
    elements.append(Paragraph(course_name.upper(), subtitle_style))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph("MailCheck – Bulk Email Verification Tool", title_style))
    elements.append(Spacer(1, 4))
    elements.append(
        Paragraph(
            "Final Software Development Project Submission Document",
            ParagraphStyle("SubDesc", parent=body_style, textColor=text_muted, fontSize=10),
        )
    )
    elements.append(Spacer(1, 8))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceAfter=10))

    # 2. Metadata Information Table
    meta_data = [
        [
            Paragraph("<b>Author / Student:</b>", body_style),
            Paragraph(student_name, body_style),
            Paragraph("<b>Submission Date:</b>", body_style),
            Paragraph(datetime.now().strftime("%B %d, %Y"), body_style),
        ],
        [
            Paragraph("<b>Architecture:</b>", body_style),
            Paragraph("Full-Stack (Vite/React + Flask API)", body_style),
            Paragraph("<b>Test Suite:</b>", body_style),
            Paragraph("27 Pytest Backend Tests (Passing)", body_style),
        ],
    ]
    meta_table = Table(meta_data, colWidths=[105, 175, 105, 145])
    meta_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), card_bg),
            ("BOX", (0, 0), (-1, -1), 0.5, border_color),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ])
    )
    elements.append(meta_table)
    elements.append(Spacer(1, 12))

    # 3. Project Submission Links Box (Crucial Assignment Requirement)
    elements.append(Paragraph("PROJECT SUBMISSION &amp; ACCESS LINKS", section_heading))
    elements.append(Spacer(1, 4))

    links_table_data = [
        [
            Paragraph("<b>Live Application URL:</b>", link_label_style),
            Paragraph(f'<link href="{live_url}"><font color="#2563eb"><u>{live_url}</u></font></link>', link_url_style),
        ],
        [
            Paragraph("<b>GitHub Repository URL:</b>", link_label_style),
            Paragraph(f'<link href="{repo_url}"><font color="#2563eb"><u>{repo_url}</u></font></link>', link_url_style),
        ],
    ]
    links_table = Table(links_table_data, colWidths=[150, 380])
    links_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#eff6ff")),
            ("BOX", (0, 0), (-1, -1), 1.2, accent_blue),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bfdbfe")),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ])
    )
    elements.append(links_table)
    elements.append(Spacer(1, 12))

    # 4. Project Overview & Scope
    elements.append(Paragraph("PROJECT OVERVIEW &amp; CORE CAPABILITIES", section_heading))
    elements.append(Spacer(1, 4))
    overview_text = (
        "<b>MailCheck</b> is a robust, full-stack email verification application designed to evaluate "
        "batches of up to 100 email addresses. It performs genuine, multi-stage verification including "
        "strict syntax parsing and live DNS/MX mail route resolution, classifying each address into three "
        "deterministic categories: <i>Likely to Be Delivered</i>, <i>Likely to Bounce</i>, or <i>Unknown</i>."
    )
    elements.append(Paragraph(overview_text, body_style))
    elements.append(Spacer(1, 8))

    # Features Bullets
    features = [
        "<b>Batch Input &amp; Consolidation:</b> Multi-line input area with instant duplicate deduplication and batch size limit checks.",
        "<b>RFC Standards Validation:</b> Comprehensive syntax checking (RFC 5321/5322) and length boundary validation (64-char local, 254-char total).",
        "<b>DNS &amp; MX Resolution:</b> Real DNS lookups via dnspython with RFC 7505 Null MX detection and RFC 5321 Section 5.1 A/AAAA implicit mail fallback routing.",
        "<b>Interactive Dashboard &amp; CSV Export:</b> Summary count cards, real-time filtering, status search, and one-click structured CSV export.",
    ]
    for feat in features:
        elements.append(Paragraph(f"&bull;&nbsp;&nbsp;{feat}", body_style))
        elements.append(Spacer(1, 3))

    elements.append(Spacer(1, 8))

    # 5. Technology Stack Summary Table
    elements.append(Paragraph("TECHNOLOGY STACK", section_heading))
    elements.append(Spacer(1, 4))
    tech_data = [
        [
            Paragraph("<b>Frontend</b>", body_style),
            Paragraph("React 19, TypeScript, Vite, Lucide Icons, Custom Responsive CSS", body_style),
        ],
        [
            Paragraph("<b>Backend API</b>", body_style),
            Paragraph("Python 3.11+, Flask, dnspython, email-validator, Gunicorn", body_style),
        ],
        [
            Paragraph("<b>Testing &amp; QA</b>", body_style),
            Paragraph("Pytest suite (27 unit/integration tests with deterministic mock DNS)", body_style),
        ],
        [
            Paragraph("<b>Deployment</b>", body_style),
            Paragraph("Render Cloud Web Service (Automated build &amp; unified static hosting)", body_style),
        ],
    ]
    tech_table = Table(tech_data, colWidths=[120, 410])
    tech_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), card_bg),
            ("BOX", (0, 0), (-1, -1), 0.5, border_color),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ])
    )
    elements.append(tech_table)
    elements.append(Spacer(1, 10))

    # 6. Disclaimer Banner
    disclaimer_box = [
        [
            Paragraph(
                "<b>Notice &amp; Disclaimer:</b> MailCheck performs syntax and domain-level checks. A valid domain does not "
                "guarantee that an individual mailbox exists or will accept messages. In accordance with cloud hosting security "
                "policies, outbound TCP port 25 is restricted, and verification strictly avoids invasive SMTP probes.",
                disclaimer_style,
            )
        ]
    ]
    disc_table = Table(disclaimer_box, colWidths=[530])
    disc_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fff7ed")),
            ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#fdba74")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ])
    )
    elements.append(disc_table)

    doc.build(elements)
    print(f"Submission PDF successfully generated: {os.path.abspath(output_filename)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate MailCheck Assignment Submission PDF")
    parser.add_argument("--live-url", type=str, help="Public live application URL (e.g., https://mailcheck-app.onrender.com)")
    parser.add_argument("--repo-url", type=str, help="GitHub repository URL (e.g., https://github.com/username/mailcheck)")
    parser.add_argument("--student-name", type=str, default="Student Developer", help="Student or author name")
    parser.add_argument("--course-name", type=str, default="Software Development Project Assignment", help="Course name")
    parser.add_argument("--output", type=str, default="MailCheck_Project_Submission.pdf", help="Output PDF file path")

    args = parser.parse_args()

    # If parameters not supplied via CLI flags, prompt interactively
    live_url = args.live_url
    repo_url = args.repo_url

    if not live_url:
        live_url = input("Enter Public Live Application URL: ").strip()
    if not repo_url:
        repo_url = input("Enter GitHub Repository URL: ").strip()

    if not live_url or not repo_url:
        print("Error: Both live URL and repository URL are required.")
        sys.exit(1)

    generate_submission_pdf(
        live_url=live_url,
        repo_url=repo_url,
        student_name=args.student_name,
        course_name=args.course_name,
        output_filename=args.output,
    )
