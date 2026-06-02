from pathlib import Path
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate
from scripts.pdf_utils import (
    draw_header, draw_footer, draw_header_canvas, draw_footer_canvas, get_styles
)

class StyleManager:
    def __init__(self, provider_name: str, primary_color: str):
        self.provider_name = provider_name
        if isinstance(primary_color, str):
            if not primary_color.startswith('#'):
                primary_color = '#' + primary_color
            self.primary_color = colors.HexColor(primary_color)
        else:
            self.primary_color = primary_color
        self.styles = get_styles()

class BaseDocumentTemplate:
    def __init__(self, output_path, style_manager: StyleManager, doc_type: str):
        self.output_path = Path(output_path)
        self.style_manager = style_manager
        self.doc_type = doc_type

    def build_flowable(self, story):
        doc = SimpleDocTemplate(str(self.output_path), pagesize=LETTER)
        
        def on_page(canvas, doc):
            draw_header_canvas(
                canvas, doc, 
                self.style_manager.provider_name, 
                self.style_manager.primary_color, 
                self.doc_type
            )
            draw_footer_canvas(canvas, doc, self.style_manager.provider_name)
            
        doc.build(story, onFirstPage=on_page, onLaterPages=on_page)

    def build_canvas(self, draw_callback):
        c = canvas.Canvas(str(self.output_path), pagesize=LETTER)
        draw_header(c, self.style_manager.provider_name, self.style_manager.primary_color, self.doc_type)
        draw_callback(c)
        draw_footer(c, self.style_manager.provider_name)
        c.showPage()
        c.save()
