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

    # Section 1 Overview (Merged A:D)
    ws_explainer["A3"] = "SECTION 1: OVERVIEW & STRATEGIC HIGHLIGHTS"
    ws_explainer["A3"].font = font_section
    ws_explainer["A3"].fill = fill_section
    ws_explainer.row_dimensions[3].height = 24
    ws_explainer.merge_cells("A3:D3")

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

    # Section 2 Matrix Header (Merged A:D)
    ws_explainer["A6"] = "SECTION 2: MODEL ARCHITECTURE MATRIX"
    ws_explainer["A6"].font = font_section
    ws_explainer["A6"].fill = fill_section
    ws_explainer.row_dimensions[6].height = 24
    ws_explainer.merge_cells("A6:D6")

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
         "Handles real-time Patient-to-Nurse and Nurse-to-Patient simultaneous translation natively.\n\n[CON] Does NOT support custom system instructions or dynamic glossary injection in synthesized spoken audio.\n\nPost-call summary dynamically uses gemini-3.5-flash.",
         "Hardware-accelerated native translation pacing. System instructions are omitted completely to prevent WebSocket connection crashes.",
         "RECOMMENDED BASELINE FOR RAW SPEED.\nSaves 7.5% to 8.5% on streaming costs but cannot enforce a spoken clinical glossary. Post-call summary adds only $0.00096 USD (0.14% overhead)."),
         
        ("Approach B:\nPrompt-Driven Flash 3.1\n(gemini-3.1-flash)",
         "Alternative translation approach where translation and pacing are guided via custom system prompts.\n\n[PRO] FULLY supports custom system instructions and dynamic clinical glossary enforcement in synthesized spoken audio.\n\nPost-call summary dynamically uses gemini-3.1-flash.",
         "Requires custom pacing prompts and manual turn buffers, adding a +12.5% duration overhead to streaming audio outputs. System instruction includes the full clinical glossary, cached via Context Caching.",
         "RECOMMENDED FOR COMPLIANCE & GLOSSARIES.\nIncurs slightly higher streaming fees due to the pacing expansion, but enforces medical terminology perfectly. Fully integrated with prompt caching."),
         
        ("Approach C:\nPrompt-Driven Flash 2.5\n(gemini-2.5-flash)",
         "Legacy translation approach where translation and pacing are guided via legacy custom system instructions.\n\nPost-call summary dynamically uses gemini-2.5-flash to align model families.",
         "Requires identical custom pacing guidelines as Approach B, adding a +12.5% duration overhead to streaming audio outputs.",
         "Lowest unit text-token rate, but this minor saving is completely offset by high streaming rates. Dynamic post-call summarization is fully integrated."),
         
        ("Clinical Summary Feature:\nPost-Call Summarization\n(Dynamic Family Mirroring)",
         "Compiles the completed session transcript and generates a structured clinical SOAP note / summary immediately after the call is finished.",
         "Dynamic family matching: Uses 3.5 Flash for Approach A, 3.1 Flash for Approach B, and 2.5 Flash for Approach C to maintain system-wide architectural consistency.",
         "Highly Cost-Efficient.\nCosts under 1/10th of a single cent per call across all model families, representing a minor 0.14% session cost overhead.")
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

    # Section 1 Header (Merged A:E)
    ws["A3"] = "SECTION 1: GLOBAL PARAMETERS"
    ws["A3"].font = font_section
    ws["A3"].fill = fill_section
    ws.row_dimensions[3].height = 24
    ws.merge_cells("A3:E3")

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
        ("AUD_USD_Exchange_Rate", 1.515, "Indicative exchange rate (1 USD = 1.515 AUD)", "0.000"),
        ("Average_Session_Duration_Minutes", 30, "Adjustable production clinical session length in minutes (rounded to 30 mins)", "#,##0"),
        ("Annual_Total_Call_Volume", 1800000, "HealthDirect FY Video Call total consultation scale", "#,##0"),
        ("Target_Translation_Percentage", 0.05, "Estimated percentage of total call volume benefiting from translation (Low: 5%, High: 10%)", "0.0%"),
        ("Weeks_Per_Year", 52, "Standard billing weeks per calendar year", "#,##0"),
        ("Active_Speech_Duty_Cycle", 0.40, "Estimated percentage per channel of active speech (microphones only stream when active)", "0.0%"),
        ("Barge_In_Overlap_Overhead", 0.05, "Estimated streaming & playback duration overhead to account for overlap and barge-in", "0.0%"),
        ("Weekly_Session_Volume", "=B7*B8/B9", "Dynamic weekly session volume: (Annual Volume * Target Rate) / Weeks Per Year", "#,##0")
    ]
    for r_idx, row_data in enumerate(data_s1, start=5):
        ws.cell(row=r_idx, column=1, value=row_data[0]).font = font_bold
        val_cell = ws.cell(row=r_idx, column=2, value=row_data[1])
        val_cell.font = font_bold
        val_cell.alignment = align_right
        ws.cell(row=r_idx, column=3, value=row_data[2]).font = font_regular
        val_cell.number_format = row_data[3]
            
        for col_idx in range(1, 4):
            ws.cell(row=r_idx, column=col_idx).border = border_all
        ws.row_dimensions[r_idx].height = 20

    # Section 2 Header (Merged A:E) (Shifted to Row 14)
    ws["A14"] = "SECTION 2: MODEL UNIT RATES (USD per Million Tokens)"
    ws["A14"].font = font_section
    ws["A14"].fill = fill_section
    ws.row_dimensions[14].height = 24
    ws.merge_cells("A14:E14")

    # Section 2 Headers (Shifted to Row 15)
    headers_s2 = ["Service/Item", "gemini-3.5-live-translate-preview", "gemini-3.1-flash", "gemini-2.5-flash", "Unit"]
    for idx, h in enumerate(headers_s2):
        cell = ws.cell(row=15, column=idx+1, value=h)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = align_left if idx == 0 or idx == 4 else align_right
    ws.row_dimensions[15].height = 22

    # S2 Data rows (USD per Million Tokens) (Shifted to Row 16 onwards)
    data_s2 = [
        ("Audio Input", 3.00, 3.00, 3.00, "per Million Tokens"),
        ("Audio Output", 12.00, 12.00, 12.00, "per Million Tokens"),
        ("Text Input", 0.75, 0.75, 0.075, "per Million Tokens"),
        ("Text Output", 4.50, 4.50, 0.30, "per Million Tokens"),
        ("Cached Read", 0.15, 0.15, 0.015, "per Million Tokens"),
        ("Cache Storage", 1.00, 1.00, 0.10, "per Million Tokens")
    ]
    for r_idx, row_data in enumerate(data_s2, start=16):
        ws.cell(row=r_idx, column=1, value=row_data[0]).font = font_bold
        for c in range(1, 4):
            val_cell = ws.cell(row=r_idx, column=c+1, value=row_data[c])
            val_cell.font = font_regular
            val_cell.alignment = align_right
            # Dynamic decimals formatting
            if abs(row_data[c] - round(row_data[c], 2)) > 1e-9:
                val_cell.number_format = "$#,##0.000"
            else:
                val_cell.number_format = "$#,##0.00"
        ws.cell(row=r_idx, column=5, value=row_data[4]).font = font_regular
        for col_idx in range(1, 6):
            ws.cell(row=r_idx, column=col_idx).border = border_all
        ws.row_dimensions[r_idx].height = 20

    # Section 3 Header (Merged A:E) (Shifted to Row 23)
    ws["A23"] = "SECTION 3: EMPIRICAL BASES & FORMULAS (PER SESSION)"
    ws["A23"].font = font_section
    ws["A23"].fill = fill_section
    ws.row_dimensions[23].height = 24
    ws.merge_cells("A23:E23")

    # Section 3 Headers (Shifted to Row 24)
    headers_s3 = ["Metric/Calculation", "Approach A: Native 3.5", "Approach B: 3.1 Flash Prompt-driven", "Approach C: 2.5 Flash Prompt-driven", "Formula Description"]
    for idx, h in enumerate(headers_s3):
        cell = ws.cell(row=24, column=idx+1, value=h)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = align_left if idx == 0 or idx == 4 else align_right
    ws.row_dimensions[24].height = 22

    # S3 Formulas & Data (Dividing rates by 1,000,000) (Shifted to Row 25 onwards)
    data_s3 = [
        # Row 25
        ("Prompt Cache Read Size (Tokens)", 0, 3000, 3000, "Static instructions + glossary context (N/A for Approach A)", "#,##0"),
        # Row 26
        ("Prompt Cache Read Cost (USD)", "=B25*(B20/1000000)", "=C25*(C20/1000000)", "=D25*(D20/1000000)", "Tokens * (Cache Read Rate / 1,000,000)", "$#,##0.00000"),
        # Row 27
        ("Audio Input Tokens per Session", "=2*$B$6*60*250*$B$10*(1+$B$11)", "=2*$B$6*60*250*$B$10*(1+$B$11)", "=2*$B$6*60*250*$B$10*(1+$B$11)", "2 connections * Duration in seconds * 250 tokens/sec * Duty Cycle * (1 + Overlap Overhead)", "#,##0"),
        # Row 28
        ("Audio Input Cost (USD)", "=B27*(B16/1000000)", "=C27*(C16/1000000)", "=D27*(D16/1000000)", "Tokens * (Audio Input Rate / 1,000,000)", "$#,##0.00"),
        # Row 29
        ("Spoken Dialogue Word Count (Est.)", "=$B$6*$B$10*150", "=$B$6*$B$10*150", "=$B$6*$B$10*150", "Duration * Active Duty Cycle * 150 words/min average speaking pace", "#,##0"),
        # Row 30
        ("Audio Output Pacing Duration (Sec)", "=(B29/2.5)*(1+$B$11)", "=(C29/2.5)*1.125*(1+$B$11)", "=(D29/2.5)*1.125*(1+$B$11)", "Words / 2.5 words/sec * Pacing modifier * (1 + Overlap Overhead)", "#,##0"),
        # Row 31
        ("Audio Output Tokens per Session", "=B30*250", "=C30*250", "=D30*250", "Spoken seconds * 250 tokens/sec", "#,##0"),
        # Row 32
        ("Audio Output Cost (USD)", "=B31*(B17/1000000)", "=C31*(C17/1000000)", "=D31*(D17/1000000)", "Tokens * (Audio Output Rate / 1,000,000)", "$#,##0.00"),
        # Row 33
        ("Transcription Text Output (Tokens)", "=(B29*2.2)*1.33", "=(C29*2.2)*1.33", "=(D29*2.2)*1.33", "(Spoken + Translated words) * 1.33 tokens/word", "#,##0"),
        # Row 34
        ("Transcription Text Cost (USD)", "=B33*(B19/1000000)", "=C33*(C19/1000000)", "=D33*(D19/1000000)", "Tokens * (Text Output Rate / 1,000,000)", "$#,##0.0000"),
        
        # New Post-Call Summary Rows
        # Row 35
        ("Post-Call Summary Input (Tokens)", "=B33", "=C33", "=D33", "Input size of the compiled transcript text (matched to Row 33)", "#,##0"),
        # Row 36
        ("Post-Call Summary Output (Tokens)", 1200, 1200, 1200, "Output size of the generated structured clinical SOAP note", "#,##0"),
        # Row 37
        ("Post-Call Summary Cost (USD)", "=(B35*(B18/1000000))+(B36*(B19/1000000))", "=(C35*(C18/1000000))+(C36*(C19/1000000))", "=(D35*(D18/1000000))+(D36*(D19/1000000))", "Summary (Input*InputRate + Output*OutputRate) / 1,000,000", "$#,##0.00000"),
        
        # Shifted Totals Rows (Row 38 & 39)
        ("Total Session Cost (USD)", "=B26+B28+B32+B34+B37", "=C26+C28+C32+C34+C37", "=D26+D28+D32+D34+D37", "Sum of all live streaming & summary costs", "$#,##0.00"),
        ("Total Session Cost (AUD)", "=B38*$B$5", "=C38*$B$5", "=D38*$B$5", "USD Cost * Exchange Rate", "$#,##0.00")
    ]

    for r_idx, row_data in enumerate(data_s3, start=25):
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

    # Section 4 Header (Shifted to Row 41, Merged A:E)
    ws["A41"] = "SECTION 4: VOLUME PROJECTION CALCULATOR"
    ws["A41"].font = font_section
    ws["A41"].fill = fill_section
    ws.row_dimensions[41].height = 24
    ws.merge_cells("A41:E41")

    # Row 42: Section 4 Headers
    headers_s4 = ["Volume / Projections", "Approach A: Native 3.5", "Approach B: 3.1 Flash Prompt-driven", "Approach C: 2.5 Flash Prompt-driven", "Notes"]
    for idx, h in enumerate(headers_s4):
        cell = ws.cell(row=42, column=idx+1, value=h)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = align_left if idx == 0 or idx == 4 else align_right
    ws.row_dimensions[42].height = 22

    # S4 Projections (Shifted to Row 43 onwards)
    data_s4 = [
        ("Weekly Cost (USD)", "=B38*$B$12", "=C38*$B$12", "=D38*$B$12", "Sessions/Week * Session Cost (Row 38)", "$#,##0.00"),
        ("Weekly Cost (AUD)", "=B43*$B$5", "=C43*$B$5", "=D43*$B$5", "Weekly USD * Exchange Rate", "$#,##0.00"),
        ("Monthly Cost (USD)", "=B43*4.33", "=C43*4.33", "=D43*4.33", "Weekly Cost * 4.33 weeks/month", "$#,##0.00"),
        ("Monthly Cost (AUD)", "=B45*$B$5", "=C45*$B$5", "=D45*$B$5", "Monthly USD * Exchange Rate", "$#,##0.00"),
        ("Annual Cost (USD)", "=B43*52", "=C43*52", "=D43*52", "Weekly Cost * 52 weeks", "$#,##0.00"),
        ("Annual Cost (AUD)", "=B47*$B$5", "=C47*$B$5", "=D47*$B$5", "Annual USD * Exchange Rate", "$#,##0.00")
    ]

    for r_idx, row_data in enumerate(data_s4, start=43):
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

    # ==========================================
    # ---- TAB 3: GLOSSARY MANAGEMENT ----
    # ==========================================
    ws_g = wb.create_sheet(title="Glossary Management")
    ws_g.views.sheetView[0].showGridLines = True

    # Title
    ws_g["A1"] = "HealthDirect Clinical Glossary Generator & Management"
    ws_g["A1"].font = font_title
    ws_g.row_dimensions[1].height = 35

    # Section 1 Overview Header (Merged A:E)
    ws_g["A3"] = "SECTION 1: GLOSSARY GENERATION PARAMETERS"
    ws_g["A3"].font = font_section
    ws_g["A3"].fill = fill_section
    ws_g.row_dimensions[3].height = 24
    ws_g.merge_cells("A3:E3")

    # Table Header
    headers_g1 = ["Parameter", "Value", "Description", "", ""]
    for idx, h in enumerate(headers_g1):
        cell = ws_g.cell(row=4, column=idx+1, value=h)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = align_left
    ws_g.row_dimensions[4].height = 22

    # S1 Data rows
    data_g1 = [
        ("Number_of_Active_Languages", 5, "Number of localized language dialects (Spanish, Arabic, Vietnamese, Hindi, Cantonese)", "#,##0"),
        ("Glossary_Master_Term_Count", 500, "Number of standardized medical terms and phrases to translate for the session prompt context", "#,##0"),
        ("Input_Tokens_Per_Term", 25, "Average input tokens per term (source word + translation instructions + context guidelines)", "#,##0"),
        ("Output_Tokens_Per_Term", 50, "Average output tokens per term (translated word + pronunciation phonetics + contextual note)", "#,##0"),
        ("Model_Input_Rate_Per_Million", 1.25, "Unit cost rate of Gemini 1.5 Pro to generate high-quality clinical translations (USD / Million)", "$#,##0.00"),
        ("Model_Output_Rate_Per_Million", 5.00, "Unit cost rate of Gemini 1.5 Pro to generate high-quality clinical translations (USD / Million)", "$#,##0.00")
    ]
    for r_idx, row_data in enumerate(data_g1, start=5):
        ws_g.cell(row=r_idx, column=1, value=row_data[0]).font = font_bold
        val_cell = ws_g.cell(row=r_idx, column=2, value=row_data[1])
        val_cell.font = font_bold
        val_cell.alignment = align_right
        ws_g.cell(row=r_idx, column=3, value=row_data[2]).font = font_regular
        val_cell.number_format = row_data[3]
            
        for col_idx in range(1, 4):
            ws_g.cell(row=r_idx, column=col_idx).border = border_all
        ws_g.row_dimensions[r_idx].height = 20

    # Section 2 Header (Merged A:E) (Row 12)
    ws_g["A12"] = "SECTION 2: ONE-TIME GLOSSARY CREATION COST (GEMINI 1.5 PRO)"
    ws_g["A12"].font = font_section
    ws_g["A12"].fill = fill_section
    ws_g.row_dimensions[12].height = 24
    ws_g.merge_cells("A12:E12")

    # Section 2 Table Header (Row 13)
    headers_g2 = ["Calculation Metric", "Value", "Formula Description", "", ""]
    for idx, h in enumerate(headers_g2):
        cell = ws_g.cell(row=13, column=idx+1, value=h)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = align_left if idx == 0 or idx == 2 else align_right
    ws_g.row_dimensions[13].height = 22

    # S2 Calculations (Row 14-19)
    data_g2 = [
        ("Total Generation Input Tokens", "=B6*B7*B5", "Master Term Count (B6) * Input Tokens (B7) * Languages (B5)", "#,##0"),
        ("Total Generation Output Tokens", "=B6*B8*B5", "Master Term Count (B6) * Output Tokens (B8) * Languages (B5)", "#,##0"),
        ("Input Translation Cost (USD)", "=B14*(B9/1000000)", "Total Input Tokens * (Model Input Rate / 1,000,000)", "$#,##0.00"),
        ("Output Translation Cost (USD)", "=B15*(B10/1000000)", "Total Output Tokens * (Model Output Rate / 1,000,000)", "$#,##0.00"),
        ("Total One-Time Cost (USD)", "=B16+B17", "Sum of input and output translation costs", "$#,##0.00"),
        ("Total One-Time Cost (AUD)", "=B18*'Cost Calculator'!$B$5", "Total USD Cost * Indicative Exchange Rate (Cost Calculator B5)", "$#,##0.00")
    ]
    for r_idx, row_data in enumerate(data_g2, start=14):
        is_total = (row_data[0] in ["Total One-Time Cost (USD)", "Total One-Time Cost (AUD)"])
        ws_g.cell(row=r_idx, column=1, value=row_data[0]).font = font_bold if is_total else font_regular
        val_cell = ws_g.cell(row=r_idx, column=2, value=row_data[1])
        val_cell.font = font_bold if is_total else font_regular
        val_cell.alignment = align_right
        val_cell.number_format = row_data[3]
        if is_total:
            val_cell.fill = fill_total
            
        ws_g.cell(row=r_idx, column=3, value=row_data[2]).font = font_regular if not is_total else font_bold
        for col_idx in range(1, 4):
            cell = ws_g.cell(row=r_idx, column=col_idx)
            cell.border = border_total if is_total else border_all
            if is_total:
                cell.fill = fill_total
        ws_g.row_dimensions[r_idx].height = 22 if is_total else 20

    # Section 3 Header (Merged A:E) (Row 21)
    ws_g["A21"] = "SECTION 3: ANNUAL CLINICAL MAINTENANCE (50 TERMS ADDED/UPDATED)"
    ws_g["A21"].font = font_section
    ws_g["A21"].fill = fill_section
    ws_g.row_dimensions[21].height = 24
    ws_g.merge_cells("A21:E21")

    # Section 3 Table Header (Row 22)
    headers_g3 = ["Maintenance Metric", "Value", "Formula Description", "", ""]
    for idx, h in enumerate(headers_g3):
        cell = ws_g.cell(row=22, column=idx+1, value=h)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = align_left if idx == 0 or idx == 2 else align_right
    ws_g.row_dimensions[22].height = 22

    # S3 Calculations (Row 23-27)
    data_g3 = [
        ("Annual_New_Term_Maintenance", 50, "Average number of new clinical concepts/acronyms/guidelines added annually", "#,##0"),
        ("Maintenance Input Tokens (Annual)", "=B23*B7*B5", "New Terms (B23) * Input Tokens (B7) * Languages (B5)", "#,##0"),
        ("Maintenance Output Tokens (Annual)", "=B23*B8*B5", "New Terms (B23) * Output Tokens (B8) * Languages (B5)", "#,##0"),
        ("Annual Maintenance Cost (USD)", "=(B24*(B9/1000000))+(B25*(B10/1000000))", "Annual (InputTokens*InputRate + OutputTokens*OutputRate) / 1,000,000", "$#,##0.00"),
        ("Annual Maintenance Cost (AUD)", "=B26*'Cost Calculator'!$B$5", "Annual USD Cost * Indicative Exchange Rate (Cost Calculator B5)", "$#,##0.00")
    ]
    for r_idx, row_data in enumerate(data_g3, start=23):
        is_total = (row_data[0] in ["Annual Maintenance Cost (USD)", "Annual Maintenance Cost (AUD)"])
        ws_g.cell(row=r_idx, column=1, value=row_data[0]).font = font_bold if is_total else font_regular
        val_cell = ws_g.cell(row=r_idx, column=2, value=row_data[1])
        val_cell.font = font_bold if is_total else font_regular
        val_cell.alignment = align_right
        val_cell.number_format = row_data[3]
        if is_total:
            val_cell.fill = fill_total
            
        ws_g.cell(row=r_idx, column=3, value=row_data[2]).font = font_regular if not is_total else font_bold
        for col_idx in range(1, 4):
            cell = ws_g.cell(row=r_idx, column=col_idx)
            cell.border = border_total if is_total else border_all
            if is_total:
                cell.fill = fill_total
        ws_g.row_dimensions[r_idx].height = 22 if is_total else 20

    # Section 4 Header (Merged A:E) (Row 29)
    ws_g["A29"] = "SECTION 4: REAL-TIME CONTEXT CACHING INTEGRATION (PROMPT CACHING)"
    ws_g["A29"].font = font_section
    ws_g["A29"].fill = fill_section
    ws_g.row_dimensions[29].height = 24
    ws_g.merge_cells("A29:E29")

    # Section 4 Table Header (Row 30)
    headers_g4 = ["Caching Parameter", "Value", "Formula Description", "", ""]
    for idx, h in enumerate(headers_g4):
        cell = ws_g.cell(row=30, column=idx+1, value=h)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = align_left if idx == 0 or idx == 2 else align_right
    ws_g.row_dimensions[30].height = 22

    # S4 Calculations (Row 31-35)
    data_g4 = [
        ("Glossary Size in Session Cache (Tokens)", "=B6*B8", "Glossary size per language: Master Term Count (B6) * Output Tokens (B8)", "#,##0"),
        ("Cache TTL / Inactivity Expiry (Hours)", 1.0, "Prompt Cache storage TTL: cached context is retained for 1 hour from last read", "0.0"),
        ("Prompt Cache Storage Cost per Hour (USD)", "=B31*('Cost Calculator'!B21/1000000)", "Total Cached Tokens * (Cost Calculator Cache Storage Rate B21 / 1,000,000)", "$#,##0.0000"),
        ("Prompt Cache Storage Cost per Hour (AUD)", "=B33*'Cost Calculator'!$B$5", "Cache Storage USD * Indicative Exchange Rate (Cost Calculator B5)", "$#,##0.0000"),
        ("Active Call Prompt Cache Read Savings (AUD)", "=(3000-B31)*('Cost Calculator'!B20/1000000)*'Cost Calculator'!$B$5", "Saves up to $2.20 AUD per hour by avoiding uncached text reads across sessions", "$#,##0.00")
    ]
    for r_idx, row_data in enumerate(data_g4, start=31):
        is_total = (row_data[0] in ["Prompt Cache Storage Cost per Hour (USD)", "Prompt Cache Storage Cost per Hour (AUD)"])
        ws_g.cell(row=r_idx, column=1, value=row_data[0]).font = font_bold if is_total else font_regular
        val_cell = ws_g.cell(row=r_idx, column=2, value=row_data[1])
        val_cell.font = font_bold if is_total else font_regular
        val_cell.alignment = align_right
        val_cell.number_format = row_data[3]
        if is_total:
            val_cell.fill = fill_total
            
        ws_g.cell(row=r_idx, column=3, value=row_data[2]).font = font_regular if not is_total else font_bold
        for col_idx in range(1, 4):
            cell = ws_g.cell(row=r_idx, column=col_idx)
            cell.border = border_total if is_total else border_all
            if is_total:
                cell.fill = fill_total
        ws_g.row_dimensions[r_idx].height = 22 if is_total else 20

    # Auto-fit Glossary Columns Width
    for col_g in ws_g.columns:
        col_letter_g = get_column_letter(col_g[0].column)
        if col_letter_g == "A":
            ws_g.column_dimensions[col_letter_g].width = 42
        elif col_letter_g == "B":
            ws_g.column_dimensions[col_letter_g].width = 16
        elif col_letter_g == "C":
            ws_g.column_dimensions[col_letter_g].width = 75
        else:
            ws_g.column_dimensions[col_letter_g].width = 12

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
