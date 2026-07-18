import pytest
from pathlib import Path
from reportlab.lib import colors
from reportlab.platypus import Paragraph, Spacer
from scripts.base_generator import StyleManager, BaseDocumentTemplate

def test_style_manager_init():
    sm = StyleManager(provider_name="TestProvider", primary_color="#123456")
    assert sm.provider_name == "TestProvider"
    assert sm.primary_color == colors.HexColor("#123456")
    
    # Test color string normalization without hash prefix
    sm_no_hash = StyleManager(provider_name="TestProvider", primary_color="123456")
    assert sm_no_hash.primary_color == colors.HexColor("#123456")

    # Test passing a reportlab Color object directly
    red_color = colors.HexColor("#FF0000")
    sm_color_obj = StyleManager(provider_name="TestProvider", primary_color=red_color)
    assert sm_color_obj.primary_color == red_color

    # Verify we can get styles
    styles = sm.styles
    assert 'LegalText' in styles
    assert 'SectionHeader' in styles
    assert 'TDA_Title' in styles
    assert styles['TDA_Title'].alignment == 1  # Centered

def test_base_document_template_flowable(tmp_path):
    output_path = tmp_path / "flowable_test.pdf"
    sm = StyleManager(provider_name="AWS", primary_color="#FF9900")
    
    # Flowable doc
    doc = BaseDocumentTemplate(output_path, sm, "Service Agreement")
    story = [
        Paragraph("Test Title", sm.styles['TDA_Title']),
        Spacer(1, 10),
        Paragraph("This is some legal text.", sm.styles['LegalText'])
    ]
    doc.build_flowable(story)
    
    assert output_path.exists()
    assert output_path.stat().st_size > 0

def test_base_document_template_canvas(tmp_path):
    output_path = tmp_path / "canvas_test.pdf"
    sm = StyleManager(provider_name="Azure", primary_color="#008AD7")
    
    # Canvas-based doc
    doc = BaseDocumentTemplate(output_path, sm, "Invoice")
    
    def draw_callback(c):
        c.drawString(100, 100, "Hello World from Canvas Callback")
        
    doc.build_canvas(draw_callback)
    
    assert output_path.exists()
    assert output_path.stat().st_size > 0
