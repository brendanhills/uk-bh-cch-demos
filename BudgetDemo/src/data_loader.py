import os
import pandas as pd

def load_nominal_gdp(file_path: str) -> pd.DataFrame:
    """
    Loads and cleans the Nominal GDP supplementary Excel file.
    
    Args:
        file_path: Absolute or relative path to bp1_s2-data-nominal-GDP.xlsx
        
    Returns:
        pd.DataFrame: Cleaned DataFrame with columns 'Year', '2026-27 Budget', '2025-26 MYEFO'
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    # Read the sheet
    df = pd.read_excel(file_path, sheet_name='Supplementary Data')
    
    # Check if empty
    if df.empty:
        return pd.DataFrame(columns=["Year", "2026-27 Budget", "2025-26 MYEFO"])
        
    # Standardize column headers using row 0 (which contains headers)
    df.columns = [str(df.iloc[0, i]).strip() if pd.notna(df.iloc[0, i]) else f"Col_{i}" for i in range(len(df.columns))]
    df = df.iloc[1:].reset_index(drop=True)
    
    # Rename columns to standard simple names
    df.rename(columns={
        df.columns[0]: "Year",
        "Nominal GDP - 2026-27 Budget": "2026-27 Budget",
        "Nominal GDP - 2025-26 MYEFO": "2025-26 MYEFO"
    }, inplace=True)
    
    # Clean Year column - remove any trailing whitespace or formatting
    df["Year"] = df["Year"].astype(str).str.strip()
    
    # Convert values to numeric (handling empty cells / NaN)
    df["2026-27 Budget"] = pd.to_numeric(df["2026-27 Budget"], errors='coerce')
    df["2025-26 MYEFO"] = pd.to_numeric(df["2025-26 MYEFO"], errors='coerce')
    
    return df

def load_receipts_csv(file_path: str) -> pd.DataFrame:
    """
    Loads and cleans the Tax Receipts or Revenue CSV files (T1 or T3).
    
    Args:
        file_path: Path to bp1_s5-online_t1.csv or bp1_s5-online_t3.csv
        
    Returns:
        pd.DataFrame: Cleaned DataFrame where the first column is 'Category'
                      and subsequent columns are years ($m).
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    df = pd.read_csv(file_path)
    
    if df.empty:
        return pd.DataFrame()
        
    # Rename first column to 'Category'
    df.rename(columns={df.columns[0]: "Category"}, inplace=True)
    
    # Clean category column
    df["Category"] = df["Category"].astype(str).str.strip()
    
    # Remove empty or footer spacer rows if Category is blank
    df = df[df["Category"] != ""]
    df = df[df["Category"] != "nan"]
    
    return df

def load_receipts_percentages_csv(file_path: str) -> pd.DataFrame:
    """
    Loads and cleans the Table 2 Receipts % of GDP CSV.
    
    Args:
        file_path: Path to bp1_s5-online_t2.csv
        
    Returns:
        pd.DataFrame: Cleaned DataFrame with 'Year' as first column
                      and percent columns.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    df = pd.read_csv(file_path)
    
    if df.empty:
        return pd.DataFrame()
        
    # Rename first column to 'Year'
    df.rename(columns={df.columns[0]: "Year"}, inplace=True)
    
    # Clean Year column
    df["Year"] = df["Year"].astype(str).str.strip()
    
    return df

def get_category_time_series(df: pd.DataFrame, category_name: str) -> pd.DataFrame:
    """
    Given a receipts/revenue DataFrame (from load_receipts_csv), extracts a clean
    plottable time series DataFrame for a specific category.
    
    Args:
        df: The receipts/revenue DataFrame
        category_name: The target category to extract
        
    Returns:
        pd.DataFrame: A DataFrame with columns 'Year' and 'Value ($m)'
    """
    # Find the row matching category_name
    row = df[df["Category"].str.lower() == category_name.lower().strip()]
    if row.empty:
        return pd.DataFrame(columns=["Year", "Value ($m)"])
        
    # Extract year columns and their values
    years = []
    values = []
    
    for col in df.columns[1:]:
        # Extract the value
        val_str = str(row[col].values[0]).replace(",", "").strip()
        try:
            val = float(val_str)
        except ValueError:
            val = None
            
        # Clean year label (e.g., '2025-26 (est) ($m)' -> '2025-26')
        year_label = col.split(" ")[0].strip()
        
        years.append(year_label)
        values.append(val)
        
    series_df = pd.DataFrame({
        "Year": years,
        "Value ($m)": values
    })
    
    # Drop rows with None/NaN values
    series_df.dropna(subset=["Value ($m)"], inplace=True)
    
    return series_df
