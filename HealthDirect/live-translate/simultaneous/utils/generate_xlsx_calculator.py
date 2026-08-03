import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def create_styled_calculator():
    wb = openpyxl.Workbook()
    
    # ---- PALETTE & STYLES (Shared across sheets) ----
    # Colors
    NAVY_BLUE = "1E3A8A"       # Primary Title/Headers
    ICE_BLUE = "E0F2FE"        # Section Header backgrounds
    LIGHT_GRAY = "F8FAFC"      # Subtle backgrounds
    BORDER_COLOR = "D1D5DB"    # Clean borders
    
    # Fonts
    font_title = Font(name="Segoe UI", size=15, bold=True, color=NAVY_BLUE)
    font_section = Font(name="Segoe UI", size=11, bold=True, color="1E293B")
    font_header = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
    font_bold = Font(name="Segoe UI", size=10, bold=True)
    font_regular = Font(name="Segoe UI", size=10)
    font_italic = Font(name="Segoe UI", size=9, italic=True, color="64748B")

    # Fills
    fill_header = PatternFill(start_color=NAVY_BLUE, end_color=NAVY_BLUE, fill_type="solid")
    fill_section = PatternFill(start_color=ICE_BLUE, end_color=ICE_BLUE, fill_type="solid")
    fill_total = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")

    # Alignments
    align_left = Alignment(horizontal="left", vertical="center")
    align_right = Alignment(horizontal="right", vertical="center")
    align_center = Alignment(horizontal="center", vertical="center")

    # Borders
    thin_border_side = Side(border_style="thin", color=BORDER_COLOR)
    double_border_side = Side(border_style="double", color="475569")
    
    border_all = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
    border_total = Border(top=thin_border_side, bottom=double_border_side)

    # ==========================================
    # ---- TAB 1: MODEL EXPLAINER ----
    # ==========================================
    ws_explainer = wb.active
    ws_explainer.title = "Model Explainer"
    ws_explainer.views.sheetView[0].showGridLines = True

    # Title
    ws_explainer["A1"] = "HealthDirect Simultaneous Interpreter: Model Architecture & Roles"
    ws_explainer["A1"].font = font_title
    ws_explainer.row_dimensions[1].height = 35

    # Section 1 Overview
    ws_explainer["A3"] = "SECTION 1: OVERVIEW & STRATEGIC HIGHLIGHTS"
    ws_explainer["A3"].font = font_section
    ws_explainer.row_dimensions[3].height = 24
    for col in ["A", "B", "C", "D"]:
        ws_explainer[f"{col}3"].fill = fill_section

    desc_text = (
        "This workbook provides a rigorous, data-driven cost and performance model comparing three alternative "
        "deployment approaches for real-time translation on HealthDirect Video Call, as well as the new post-call clinical summary workflow.\n\n"
        "Model projections are based on official scale parameters (1.8 Million annual consultations, rounded 30-minute average, and 5% to 10% translation target)."
    )
    ws_explainer["A4"] = desc_text
    ws_explainer["A4"].font = font_italic
    ws_explainer["A4"].alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
    ws_explainer.row_dimensions[4].height = 50
    ws_explainer.merge_cells("A4:D4")

    # Section 2 Matrix Header
    ws_explainer["A6"] = "SECTION 2: MODEL ARCHITECTURE MATRIX"
    ws_explainer["A6"].font = font_section
    ws_explainer.row_dimensions[6].height = 24
    for col in ["A", "B", "C", "D"]:
        ws_explainer[f"{col}6"].fill = fill_section

    headers_explainer = ["Model / Approach", "Primary Role in System", "Pacing & Audio Streaming Profile", "Financial & Operational Implications"]
    for idx, h in enumerate(headers_explainer):
        cell = ws_explainer.cell(row=7, column=idx+1, value=h)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = align_left
    ws_explainer.row_dimensions[7].height = 22

    # Explainer Data
    data_explainer = [
        ("Approach A:\nNative Translation Baseline\n(gemini-3.5-live-translate-preview)", 
         "Handles real-time Patient-to-Nurse and Nurse-to-Patient simultaneous translation natively using Google's dedicated live-translate preview API config.",
         "Hardware-accelerated native translation pacing. No custom prompt guidelines needed. Continuous bidirectional streaming.",
         "RECOMMENDED BASELINE.\nSaves 7.5% to 8.5% on total session costs compared to Approach B/C by avoiding any prompt-driven audio duration expansion (saves ~$120,000 to ~$240,000 AUD annually across HealthDirect's scale)."),
         
        ("Approach B:\nPrompt-Driven Flash 3.1\n(gemini-3.1-flash)",
         "Alternative translation approach where translation and pacing are guided using developer system instructions on standard Gemini Live streams.",
         "Requires custom pacing guidelines and manual turn timeouts. Adds a ~12.5% duration overhead to streaming audio output to prevent over-talk.",
         "High reasoning capability but moderately more expensive due to prompt instruction overhead and pacing audio duration expansion."),
         
        ("Approach C:\nPrompt-Driven Flash 2.5\n(gemini-2.5-flash)",
         "Legacy translation approach using previous-generation Gemini Live streams with developer system instruction prompts for pacing.",
         "Requires identical custom pacing guidelines as Approach B, adding a +12.5% pacing duration overhead to spoken outputs.",
         "Lowest unit text-token rate, but this minor saving is completely offset by the high audio streaming rates and pacing duration overhead."),
         
        ("Clinical Summary Feature:\nPost-Call Summarization\n(gemini-3.5-flash)",
         "Compiles the completed session transcript and generates a structured clinical SOAP note / summary immediately after the call is finished.",
         "Standard non-streaming unary text-to-text call triggered once upon call completion. No real-time audio streaming involved.",
         "VIRTUALLY FREE.\nCosts less than 1/10th of a single cent ($0.00096 USD) per call, adding a negligible 0.14% cost overhead to the live stream.")
    ]

    for r_idx, row_data in enumerate(data_explainer, start=8):
        for c_idx, val in enumerate(row_data):
            cell = ws_explainer.cell(row=r_idx, column=c_idx+1, value=val)
            cell.font = font_bold if c_idx == 0 else font_regular
            cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
            cell.border = border_all
        ws_explainer.row_dimensions[r_idx].height = 85

    # Explainer Column Widths
    ws_explainer.column_dimensions["A"].width = 38
    ws_explainer.column_dimensions["B"].width = 45
    ws_explainer.column_dimensions["C"].width = 45
    ws_explainer.column_dimensions["D"].width = 50

    # ==========================================
    # ---- TAB 2: COST CALCULATOR ----
    # ==========================================
    ws = wb.create_sheet(title="Cost Calculator")
    ws.views.sheetView[0].showGridLines = True

    # Title
    ws["A1"] = "HealthDirect Simultaneous Translation Cost Calculator"
    ws["A1"].font = font_title
    ws.row_dimensions[1].height = 35

    # Section 1 Header
    ws["A3"] = "SECTION 1: GLOBAL PARAMETERS"
    ws["A3"].font = font_section
    ws.row_dimensions[3].height = 24
    for col in ["A", "B", "C", "D", "E"]:
        ws[f"{col}3"].fill = fill_section

    # Parameter Table Header
    headers_s1 = ["Parameter", "Value", "Description", "", ""]
    for idx, h in enumerate(headers_s1):
        cell = ws.cell(row=4, column=idx+1, value=h)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = align_left
    ws.row_dimensions[4].height = 22

    # S1 Data rows
    data_s1 = [
        ("AUD_USD_Exchange_Rate", 1.515, "Indicative exchange rate (1 USD = 1.515 AUD)"),
        ("Average_Session_Duration_Minutes", 30, "Adjustable production clinical session length in minutes (rounded to 30 mins)"),
        ("Weekly_Session_Volume", 1730, "Adjustable volume parameter (5% low target is 1,730/week; 10% high target is 3,460/week)")
    ]
    for r_idx, row_data in enumerate(data_s1, start=5):
        ws.cell(row=r_idx, column=1, value=row_data[0]).font = font_bold
        val_cell = ws.cell(row=r_idx, column=2, value=row_data[1])
        val_cell.font = font_bold
        val_cell.alignment = align_right
        ws.cell(row=r_idx, column=3, value=row_data[2]).font = font_regular
        
        # Apply formatting
        if row_data[0] == "AUD_USD_Exchange_Rate":
            val_cell.number_format = "0.000"
        elif row_data[0] == "Average_Session_Duration_Minutes":
            val_cell.number_format = "#,##0"
        else:
            val_cell.number_format = "#,##0"
            
        for col_idx in range(1, 4):
            ws.cell(row=r_idx, column=col_idx).border = border_all
        ws.row_dimensions[r_idx].height = 20

    # Section 2 Header
    ws["A9"] = "SECTION 2: MODEL UNIT RATES (USD)"
    ws["A9"].font = font_section
    ws.row_dimensions[9].height = 24
    for col in ["A", "B", "C", "D", "E"]:
        ws[f"{col}9"].fill = fill_section

    # Section 2 Headers
    headers_s2 = ["Service/Item", "gemini-3.5-live-translate-preview", "gemini-3.1-flash", "gemini-2.5-flash", "Unit"]
    for idx, h in enumerate(headers_s2):
        cell = ws.cell(row=10, column=idx+1, value=h)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = align_left if idx == 0 or idx == 4 else align_right
    ws.row_dimensions[10].height = 22

    # S2 Data rows
    data_s2 = [
        ("Audio Input", 0.00000300, 0.00000300, 0.00000300, "per token ($3.00 per 1M)"),
        ("Audio Output", 0.00001200, 0.00001200, 0.00001200, "per token ($12.00 per 1M)"),
        ("Text Input", 0.00000075, 0.00000075, 0.000000075, "per token ($0.75/$0.075 per 1M)"),
        ("Text Output", 0.00000450, 0.00000450, 0.000000300, "per token ($4.50/$0.30 per 1M)"),
        ("Cached Read", 0.00000015, 0.00000015, 0.000000015, "per token ($0.15/$0.015 per 1M)"),
        ("Cache Storage", 0.00000100, 0.00000100, 0.000000100, "per token ($1.00/$0.10 per 1M)")
    ]
    for r_idx, row_data in enumerate(data_s2, start=11):
        ws.cell(row=r_idx, column=1, value=row_data[0]).font = font_bold
        for c in range(1, 4):
            val_cell = ws.cell(row=r_idx, column=c+1, value=row_data[c])
            val_cell.font = font_regular
            val_cell.alignment = align_right
            val_cell.number_format = "$0.00000000"
        ws.cell(row=r_idx, column=5, value=row_data[4]).font = font_regular
        for col_idx in range(1, 6):
            ws.cell(row=r_idx, column=col_idx).border = border_all
        ws.row_dimensions[r_idx].height = 20

    # Section 3 Header
    ws["A18"] = "SECTION 3: EMPIRICAL BASES & FORMULAS (PER SESSION)"
    ws["A18"].font = font_section
    ws.row_dimensions[18].height = 24
    for col in ["A", "B", "C", "D", "E"]:
        ws[f"{col}18"].fill = fill_section

    # Section 3 Headers
    headers_s3 = ["Metric/Calculation", "Approach A: Native 3.5", "Approach B: 3.1 Flash Prompt-driven", "Approach C: 2.5 Flash Prompt-driven", "Formula Description"]
    for idx, h in enumerate(headers_s3):
        cell = ws.cell(row=19, column=idx+1, value=h)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = align_left if idx == 0 or idx == 4 else align_right
    ws.row_dimensions[19].height = 22

    # S3 Formulas & Data
    data_s3 = [
        # Row 20
        ("Prompt Cache Read Size (Tokens)", 1000, 3000, 3000, "Static instructions + glossary context", "#,##0"),
        # Row 21
        ("Prompt Cache Read Cost (USD)", "=B20*B15", "=C20*C15", "=D20*D15", "Tokens * Cache Read Rate", "$#,##0.00000"),
        # Row 22
        ("Audio Input Tokens per Session", "=2*$B$6*60*250", "=2*$B$6*60*250", "=2*$B$6*60*250", "2 connections * Duration in seconds * 250 tokens/sec", "#,##0"),
        # Row 23
        ("Audio Input Cost (USD)", "=B22*B11", "=C22*C11", "=D22*D11", "Tokens * Audio Input Rate", "$#,##0.00"),
        # Row 24
        ("Spoken Dialogue Word Count (Est.)", "=$B$6*200", "=$B$6*200", "=$B$6*200", "Estimated transcript words (200 words/min average)", "#,##0"),
        # Row 25
        ("Audio Output Pacing Duration (Sec)", "=(B24/2.5)", "=(C24/2.5)*1.125", "=(D24/2.5)*1.125", "150 words/min spoken rate + pacing overhead", "#,##0"),
        # Row 26
        ("Audio Output Tokens per Session", "=B25*250", "=C25*250", "=D25*250", "Spoken seconds * 250 tokens/sec", "#,##0"),
        # Row 27
        ("Audio Output Cost (USD)", "=B26*B12", "=C26*C12", "=D26*D12", "Tokens * Audio Output Rate", "$#,##0.00"),
        # Row 28
        ("Transcription Text Output (Tokens)", "=(B24*2.2)*1.33", "=(C24*2.2)*1.33", "=(D24*2.2)*1.33", "(Spoken + Translated words) * 1.33 tokens/word", "#,##0"),
        # Row 29
        ("Transcription Text Cost (USD)", "=B28*B14", "=C28*C14", "=D28*D14", "Tokens * Text Output Rate", "$#,##0.0000"),
        
        # New Post-Call Summary Rows
        # Row 30
        ("Post-Call Summary Input (Tokens)", "=B28", "=C28", "=D28", "Input size of the compiled transcript text (matched to Row 28)", "#,##0"),
        # Row 31
        ("Post-Call Summary Output (Tokens)", 1200, 1200, 1200, "Output size of the generated structured clinical SOAP note", "#,##0"),
        # Row 32
        ("Post-Call Summary Cost (USD)", "=B30*B13+B31*B14", "=C30*C13+C31*C14", "=D30*D13+D31*D14", "Summary Input & Output * Model Text Rates (Row 13 & 14)", "$#,##0.00000"),
        
        # Shifted Totals Rows (Row 33 & 34)
        ("Total Session Cost (USD)", "=B21+B23+B27+B29+B32", "=C21+C23+C27+C29+C32", "=D21+D23+D27+D29+D32", "Sum of all live streaming & summary costs", "$#,##0.00"),
        ("Total Session Cost (AUD)", "=B33*$B$5", "=C33*$B$5", "=D33*$B$5", "USD Cost * Exchange Rate", "$#,##0.00")
    ]

    for r_idx, row_data in enumerate(data_s3, start=20):
        # Calculation name
        is_total_row = (row_data[0] in ["Total Session Cost (USD)", "Total Session Cost (AUD)"])
        ws.cell(row=r_idx, column=1, value=row_data[0]).font = font_bold if is_total_row else font_regular
        
        # Columns B, C, D
        for c in range(1, 4):
            val_cell = ws.cell(row=r_idx, column=c+1, value=row_data[c])
            val_cell.font = font_bold if is_total_row else font_regular
            val_cell.alignment = align_right
            val_cell.number_format = row_data[5]
            if is_total_row:
                val_cell.fill = fill_total
                
        # Description
        ws.cell(row=r_idx, column=5, value=row_data[4]).font = font_regular if not is_total_row else font_bold
        
        for col_idx in range(1, 6):
            cell = ws.cell(row=r_idx, column=col_idx)
            cell.border = border_total if is_total_row else border_all
            if is_total_row:
                cell.fill = fill_total
        ws.row_dimensions[r_idx].height = 22 if is_total_row else 20

    # Section 4 Header (Shifted to Row 36)
    ws["A36"] = "SECTION 4: VOLUME PROJECTION CALCULATOR"
    ws["A36"].font = font_section
    ws.row_dimensions[36].height = 24
    for col in ["A", "B", "C", "D", "E"]:
        ws[f"{col}36"].fill = fill_section

    # Row 37: Section 4 Headers
    headers_s4 = ["Volume / Projections", "Approach A: Native 3.5", "Approach B: 3.1 Flash Prompt-driven", "Approach C: 2.5 Flash Prompt-driven", "Notes"]
    for idx, h in enumerate(headers_s4):
        cell = ws.cell(row=37, column=idx+1, value=h)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = align_left if idx == 0 or idx == 4 else align_right
    ws.row_dimensions[37].height = 22

    # S4 Projections (Shifted to Row 38 onwards)
    data_s4 = [
        ("Weekly Cost (USD)", "=B33*$B$7", "=C33*$B$7", "=D33*$B$7", "Sessions/Week * Session Cost (Row 33)", "$#,##0.00"),
        ("Weekly Cost (AUD)", "=B38*$B$5", "=C38*$B$5", "=D38*$B$5", "Weekly USD * Exchange Rate", "$#,##0.00"),
        ("Monthly Cost (USD)", "=B38*4.33", "=C38*4.33", "=D38*4.33", "Weekly Cost * 4.33 weeks/month", "$#,##0.00"),
        ("Monthly Cost (AUD)", "=B40*$B$5", "=C40*$B$5", "=D40*$B$5", "Monthly USD * Exchange Rate", "$#,##0.00"),
        ("Annual Cost (USD)", "=B38*52", "=C38*52", "=D38*52", "Weekly Cost * 52 weeks", "$#,##0.00"),
        ("Annual Cost (AUD)", "=B42*$B$5", "=C42*$B$5", "=D42*$B$5", "Annual USD * Exchange Rate", "$#,##0.00")
    ]

    for r_idx, row_data in enumerate(data_s4, start=38):
        is_annual_aud = (row_data[0] == "Annual Cost (AUD)")
        ws.cell(row=r_idx, column=1, value=row_data[0]).font = font_bold if is_annual_aud else font_regular
        for c in range(1, 4):
            val_cell = ws.cell(row=r_idx, column=c+1, value=row_data[c])
            val_cell.font = font_bold if is_annual_aud else font_regular
            val_cell.alignment = align_right
            val_cell.number_format = row_data[5]
            if is_annual_aud:
                val_cell.fill = fill_total
                
        ws.cell(row=r_idx, column=5, value=row_data[4]).font = font_regular if not is_annual_aud else font_bold
        for col_idx in range(1, 6):
            cell = ws.cell(row=r_idx, column=col_idx)
            cell.border = border_total if is_annual_aud else border_all
            if is_annual_aud:
                cell.fill = fill_total
        ws.row_dimensions[r_idx].height = 22 if is_annual_aud else 20

    # ---- AUTO-FIT CALCULATOR COLUMN WIDTHS ----
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        
        # Determine maximum contents length
        for cell in col:
            val_str = str(cell.value or '')
            if val_str.startswith('='):
                # Don't size based on formulas, use average length
                max_len = max(max_len, 14)
            else:
                max_len = max(max_len, len(val_str))
                
        # Padding adjustments for specific columns
        if col_letter == "A":
            ws.column_dimensions[col_letter].width = 38
        elif col_letter in ["B", "C", "D"]:
            ws.column_dimensions[col_letter].width = 32
        elif col_letter == "E":
            ws.column_dimensions[col_letter].width = 48
        else:
            ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

    # Save to disk
    output_path = "/home/brendanhills/dev/uk-bh-experiments/HealthDirect/live-translate/simultaneous/utils/cost_calculator_sheet.xlsx"
    wb.save(output_path)
    print(f"Workbook successfully saved to: {output_path}")

if __name__ == "__main__":
    create_styled_calculator()
