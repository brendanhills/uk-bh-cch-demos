import pdfplumber
import pandas as pd
import re

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts all text from a PDF file."""
    text_list = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                text_list.append(text)
    return "\n".join(text_list)

def extract_tables_from_pdf(pdf_path: str, page_num: int = None) -> list:
    """Extracts all tables from a PDF or a specific page (1-based index)."""
    tables = []
    with pdfplumber.open(pdf_path) as pdf:
        if page_num is not None:
            if page_num <= len(pdf.pages):
                page = pdf.pages[page_num - 1]
                page_tables = page.extract_tables()
                if page_tables:
                    tables.extend(page_tables)
        else:
            for page in pdf.pages:
                page_tables = page.extract_tables()
                if page_tables:
                    tables.extend(page_tables)
    return tables

def parse_budget_table(pdf_path: str, page_num: int) -> pd.DataFrame:
    """
    Extracts and normalizes the first table on a specific page of a PDF.
    Standardizes columns to 'Category' or 'Item' and specific years.
    """
    tables = extract_tables_from_pdf(pdf_path, page_num=page_num)
    if not tables:
        return pd.DataFrame()
    
    table = tables[0]
    if len(table) < 2:
        return pd.DataFrame()
    
    # Locate header row containing years like '2025-26'
    header_idx = 0
    years_pattern = re.compile(r'\d{4}-\d{2}')
    for i, row in enumerate(table):
        row_str = " ".join([str(cell) for cell in row if cell])
        if years_pattern.search(row_str):
            header_idx = i
            break
            
    # Extract headers
    headers = []
    header_row = table[header_idx]
    
    # First column is usually Category or Item
    first_col_val = str(header_row[0]).strip() if header_row[0] else ""
    if not first_col_val or years_pattern.match(first_col_val):
        headers.append("Category")
    else:
        headers.append(first_col_val)
        
    for cell in header_row[1:]:
        val = str(cell).strip() if cell else ""
        headers.append(val)
        
    # Standardize column headers
    # Fill in empty headers if any
    for i in range(len(headers)):
        if not headers[i]:
            headers[i] = f"Col_{i}"
            
    # Build DataFrame from the rows after the header
    data_rows = table[header_idx + 1:]
    
    # Ensure all rows have the same length as headers
    cleaned_rows = []
    for row in data_rows:
        cleaned_row = []
        for cell in row[:len(headers)]:
            val = str(cell).strip() if cell is not None else ""
            cleaned_row.append(val)
        # Pad row if too short
        while len(cleaned_row) < len(headers):
            cleaned_row.append("")
        cleaned_rows.append(cleaned_row)
        
    df = pd.DataFrame(cleaned_rows, columns=headers)
    
    # Rename first column to 'Category' if not already
    if df.columns[0] != "Category":
        df.rename(columns={df.columns[0]: "Category"}, inplace=True)
        
    # Clean rows: remove rows where first column is empty
    df = df[df["Category"] != ""]
    
    return df
