from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import os

pdf_path = r"e:\D DRIVE\5TH SEM\IBM\U-1\bob-ai-hackathon-Eat-Code-Sleep\presentation\slides.pdf"

doc = SimpleDocTemplate(
    pdf_path,
    pagesize=landscape(letter),
    rightMargin=40,
    leftMargin=40,
    topMargin=40,
    bottomMargin=40
)

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    'SlideTitle',
    parent=styles['Heading1'],
    fontSize=26,
    leading=32,
    textColor=colors.HexColor('#0F62FE'),
    spaceAfter=15
)

subtitle_style = ParagraphStyle(
    'SlideSubtitle',
    parent=styles['Heading2'],
    fontSize=16,
    leading=22,
    textColor=colors.HexColor('#161616'),
    spaceAfter=20
)

body_style = ParagraphStyle(
    'SlideBody',
    parent=styles['Normal'],
    fontSize=13,
    leading=18,
    textColor=colors.HexColor('#393939'),
    spaceAfter=10
)

bullet_style = ParagraphStyle(
    'SlideBullet',
    parent=styles['Normal'],
    fontSize=12,
    leading=17,
    textColor=colors.HexColor('#262626'),
    spaceAfter=8
)

slides = []

# --- Slide 1: Title ---
slides.append(Spacer(1, 40))
slides.append(Paragraph("<b>GridPulse AI</b>", title_style))
slides.append(Paragraph("<b>Power Outage Prediction & Grid Equipment Failure Advisor</b>", subtitle_style))
slides.append(Paragraph("<b>Track:</b> AI &nbsp;|&nbsp; <b>Team:</b> Eat-Code-Sleep", body_style))
slides.append(Paragraph("<b>Lead:</b> Darshan Thummar (darshantce.059@gmail.com)", body_style))
slides.append(Paragraph("<b>Members:</b> Shreeja Upadhyay, Kishan Vadsola, Vishv Undavia", body_style))
slides.append(Paragraph("<i>Powered by IBM Bob & watsonx.ai</i>", body_style))
slides.append(PageBreak())

# --- Slide 2: Problem ---
slides.append(Paragraph("<b>The Problem: Unplanned Blackouts & Siloed Data</b>", title_style))
slides.append(Paragraph("• <b>Costly Catastrophes:</b> High-voltage transformer failures trigger grid blackouts costing utilities upwards of <b>$1M/hour</b> and impacting millions of citizens.", bullet_style))
slides.append(Paragraph("• <b>Blind Calendar Maintenance:</b> Maintenance relies on static calendar intervals regardless of actual physical condition or degrading insulation.", bullet_style))
slides.append(Paragraph("• <b>Siloed Sensor Telemetry:</b> Substation sensor data (oil temp, vibration, partial discharge, DGA) is isolated from live meteorological storm forecasts.", bullet_style))
slides.append(Paragraph("• <b>Reactive Emergency Dispatch:</b> Field repair crews are deployed only after blackouts occur, causing prolonged Mean Time to Recovery (MTTR).", bullet_style))
slides.append(PageBreak())

# --- Slide 3: Solution Overview ---
slides.append(Paragraph("<b>The Solution: GridPulse AI</b>", title_style))
slides.append(Paragraph("A proactive, multi-factor intelligence platform bridging physical telemetry with weather threat vectors:", subtitle_style))
slides.append(Paragraph("• <b>Continuous Ingestion:</b> Captures thermal, vibration, partial discharge, and IEEE C57 Dissolved Gas Analysis (DGA).", bullet_style))
slides.append(Paragraph("• <b>Compound Stress Correlation:</b> Fuses live wind speed, extreme heat, lightning strikes, and rain to compute failure likelihood.", bullet_style))
slides.append(Paragraph("• <b>Severity Ranking:</b> Calculates customer impact and grid contagion to establish clear operational priority.", bullet_style))
slides.append(Paragraph("• <b>Tactical Pre-Positioning:</b> Generates automated 24-72h crew staging plans prior to storm landfall.", bullet_style))
slides.append(PageBreak())

# --- Slide 4: System Architecture ---
slides.append(Paragraph("<b>System Architecture & Data Flow</b>", title_style))
slides.append(Paragraph("<b>1. Telemetry Ingestion Layer:</b> Substation IoT streams & Weather Forecast APIs.", bullet_style))
slides.append(Paragraph("<b>2. Analytics Core (FastAPI Engine):</b> IEEE C57 DGA calculations, Health Indexing, Weather Stress scoring, Risk Priority Index (RPI).", bullet_style))
slides.append(Paragraph("<b>3. AI Advisory Layer (IBM Bob & watsonx.ai):</b> Automated root-cause analysis and operational runbooks.", bullet_style))
slides.append(Paragraph("<b>4. Operator Command Center:</b> Glassmorphic dashboard with live maps, telemetry charts, and mobile crew dispatch routing.", bullet_style))
slides.append(PageBreak())

# --- Slide 5: IBM Technologies Integration ---
slides.append(Paragraph("<b>Load-Bearing IBM Technology Integration</b>", title_style))
slides.append(Paragraph("• <b>IBM Bob:</b> AI SDLC partner utilized to plan, scaffold, review, and construct the multi-factor risk engine and API architectures.", bullet_style))
slides.append(Paragraph("• <b>watsonx.ai (Granite 3.0):</b> Ingests multi-sensor diagnostic anomalies to generate explainable Bottom Line Up Front (BLUF) summaries for grid operators.", bullet_style))
slides.append(Paragraph("• <b>Automated Runbook Synthesis:</b> Instantly translates chemical and thermal fault alerts into standardized CAPA remediation work orders.", bullet_style))
slides.append(PageBreak())

# --- Slide 6: Results, Impact & Vision ---
slides.append(Paragraph("<b>Measurable Impact & Future Roadmap</b>", title_style))
slides.append(Paragraph("• <b>Reduced MTTR:</b> Pre-staging crews cuts emergency restoration times by up to <b>45%</b>.", bullet_style))
slides.append(Paragraph("• <b>Avoided Losses:</b> Early anomaly detection averts multi-million-dollar transformer burnouts and severe grid fines.", bullet_style))
slides.append(Paragraph("• <b>Human-in-the-loop Trust:</b> Provides explainable recommendations rather than opaque black-box alerts.", bullet_style))
slides.append(Paragraph("• <b>Future Scope:</b> Direct integration with utility SCADA switches and drone-based visual inspection fleets.", bullet_style))
slides.append(PageBreak())

doc.build(slides)
print(f"Presentation successfully created at: {pdf_path}")
