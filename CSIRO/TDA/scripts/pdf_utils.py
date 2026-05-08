from reportlab.lib.pagesizes import LETTER
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def draw_header_canvas(canvas, doc, provider_name, provider_color, doc_type):
    """Callback for PageTemplate to draw headers on every page."""
    canvas.saveState()
    width, height = LETTER
    canvas.setFillColor(provider_color)
    canvas.rect(0, height - 80, width, 80, fill=1, stroke=0)
    
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 20)
    canvas.drawString(50, height - 40, provider_name)
    
    canvas.setFont("Helvetica", 12)
    canvas.drawString(50, height - 60, doc_type.upper())
    
    # Page Number
    canvas.setFillColor(colors.black)
    canvas.setFont("Helvetica", 9)
    canvas.drawRightString(width - 50, 30, f"Page {canvas.getPageNumber()}")
    canvas.restoreState()

def draw_footer_canvas(canvas, doc, provider_name):
    """Callback for PageTemplate to draw footers on every page."""
    canvas.saveState()
    width, height = LETTER
    canvas.setFont("Helvetica-Oblique", 8)
    canvas.setFillColor(colors.black)
    canvas.drawCentredString(width / 2, 20, f"Confidential - {provider_name} - © 2026 | Generated for CSIRO TDA MVP")
    canvas.restoreState()

def get_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='LegalText', fontName='Helvetica', fontSize=10, leading=12, spaceAfter=10))
    styles.add(ParagraphStyle(name='SectionHeader', fontName='Helvetica-Bold', fontSize=14, leading=18, spaceBefore=20, spaceAfter=10, borderPadding=5, borderSide='bottom'))
    styles.add(ParagraphStyle(name='TDA_Title', fontName='Helvetica-Bold', fontSize=24, leading=30, spaceAfter=30, alignment=1))
    return styles

def draw_table(data, width, header_color=colors.lightgrey):
    """Returns a styled Table flowable."""
    t = Table(data, colWidths=[width * 0.7, width * 0.3])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), header_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white if header_color != colors.lightgrey else colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))
    return t

# Keep legacy methods for single-page canvas-based docs (Invoices)
def draw_header(canvas, provider_name, provider_color, doc_type):
    width, height = LETTER
    canvas.setFillColor(provider_color)
    canvas.rect(0, height - 120, width, 120, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 28)
    canvas.drawString(50, height - 70, provider_name)
    canvas.setFont("Helvetica", 14)
    canvas.drawString(50, height - 95, doc_type.upper())

def draw_footer(canvas, provider_name):
    width, height = LETTER
    canvas.setFont("Helvetica-Oblique", 8)
    canvas.setFillColor(colors.black)
    canvas.drawCentredString(width / 2, 30, f"Confidential - {provider_name} - © 2026")
    canvas.drawCentredString(width / 2, 20, "Generated for CSIRO Technical Design Authority MVP")

def draw_address_block(canvas, label, lines, x, y, align='left'):
    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawString(x, y, label)
    canvas.setFont("Helvetica", 10)
    curr_y = y - 15
    for line in lines:
        if align == 'left':
            canvas.drawString(x, curr_y, line)
        else:
            canvas.drawRightString(x, curr_y, line)
        curr_y -= 15
    return curr_y

def draw_trend_indicator(canvas, x, y, label, value, change_pct):
    canvas.setFont("Helvetica", 10)
    canvas.setFillColor(colors.black)
    canvas.drawString(x, y, label)
    canvas.setFont("Helvetica-Bold", 12)
    canvas.drawString(x, y - 15, value)
    if change_pct > 0:
        color = colors.red
        arrow = "▲"
    else:
        color = colors.green
        arrow = "▼"
    canvas.setFillColor(color)
    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawString(x + 80, y - 15, f"{arrow} {abs(change_pct):.1f}%")
    canvas.setFillColor(colors.black)
    return y - 40
