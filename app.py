import streamlit as st
import pandas as pd
from io import StringIO
from datetime import datetime

# =========================
# Column synonyms mapping
# =========================
COLUMN_SYNONYMS = {
    'Sales Order No.': [
        'sales order no', 'sales order number', 'hdr', 'hdr ref', 'po ref', 'order',
        'header reference', 'header ref', 'po number', 'ref', 'reference', 'so no',
        'po', 'order no', 'sales order', 'ref#', 'ref #', 'ref no', 'ref number'
    ],
    'Pick Date': [
        'pick date', 'date picked', 'ship date', 'date ship', 'order date', 'date',
        'receipt date', 'date to ship', 'date shipped', 'pickdate'
    ],
    'Item No.': [
        'item no', 'item number', 'product', 'sku', 'item', 'product code', 'Item No',
        'sku code', 'sku#', 'sku no', 'sku number', 'item code'
    ],
    'Each Qty': [
        'each qty', 'quantity', 'qty', 'units'
    ],
    'WHSE': [
        'whse', 'warehouse', 'warehouse code', 'Whse', 'warehouse no'
    ],
    'Ship To': [
        'ship to', 'recipient', 'consign', 'name', 'to', 'customer name'
    ],
    'Ship To Code': [
        'ship to code', 'ship code', 'consign code', 'shipto code'
    ],
    'Ship To Address 2': [
        'ship addr 2', 'ship address 2', 'address 2', 'adr 2'
    ],
    'Street': [
        'street', 'address', 'addr 1', 'ship from address', 'ship to address',
        'consign address', 'address line 1'
    ],
    'City': [
        'city', 'town', 'county', 'municipality'
    ],
    'Zip Code': [
        'zip code', 'zip', 'postal', 'postal code', 'postcode'
    ],
    'Country/Region': [
        'country/region', 'country', 'nation'
    ],
    'state': [
        'state', 'province', 'region'
    ],
    'Ref 1': [
        'ref 1', 'reference 1', 'header ref 1', 'header reference 1'
    ],
    'Ref 2': [
        'ref 2', 'reference 2', 'header ref 2', 'header reference 2'
    ],
    'Ref 3': [
        'ref 3', 'reference 3', 'header ref 3', 'header reference 3'
    ],
    'Pro Number': [
        'pro number', 'pro', 'tracking no', 'tracking'
    ],
    'Carrier Code': [
        'carrier code', 'scac', 'scac code'
    ],
    'Carrier Name': [
        'carrier', 'carrier name', 'scac name', 'truck', 'truck name', 'Carrier'
    ],
    'CLIENT': [
        'client', 'customer id', 'depositor', 'agent', 'client code', 'Client'
    ],
    'Date2': [
        'date2', 'date 2', 'delivery date', 'ship date 2', 'actual ship date',
        'expected delivery', 'delivery'
    ]
}

# =========================
# Address Validation
# =========================
CANADA_PROVINCES = ["AB","BC","MB","NB","NL","NS","NT","NU","ON","PE","QC","SK","YT"]
US_STATES = ["AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA","KS",
             "KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY",
             "NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT","VA","WA","WV","WI","WY","DC"]

def validate_address(row):
    country_raw = row.get("Country/Region", "")
    if pd.isna(country_raw) or str(country_raw).strip() == "":
        return "Valid"
    country = str(country_raw).strip().upper()
    province = str(row.get("state", "")).strip()
    postal = str(row.get("Zip Code", "")).strip().replace(" ", "")
    if country not in ["CA", "US"]:
        return "Invalid country"
    if country == "CA":
        if postal and len(postal) != 6:
            return "Invalid Canadian postal code"
        if province.upper() not in CANADA_PROVINCES:
            return "Invalid province"
    elif country == "US":
        if postal and not (len(postal) == 5 or len(postal) == 9):
            return "Invalid US ZIP code"
        if province.upper() not in US_STATES:
            return "Invalid state"
    return "Valid"

# =========================
# Enhanced Date Parser
# =========================
def parse_to_mm_dd_yyyy(date_input, format_hint="auto", custom_format=""):
    if pd.isna(date_input) or str(date_input).strip() == '':
        return None
    date_str = str(date_input).strip()

    format_map = {
        "MM/DD/YYYY": "%m/%d/%Y",
        "MM-DD-YYYY": "%m-%d-%Y",
        "YYYY-MM-DD": "%Y-%m-%d",
        "DD/MM/YYYY": "%d/%m/%Y",
        "DD-MM-YYYY": "%d-%m-%Y",
        "YYYY/MM/DD": "%Y/%m/%d",
        "MM/DD/YY": "%m/%d/%y",
        "YYYYMMDD": "%Y%m%d",
        "DD-MON-YYYY (e.g., 12-DEC-2025)": "%d-%b-%Y",
        "DD-MON-YY (e.g., 12-DEC-25)": "%d-%b-%y",
        "DDMONYYYY (e.g., 12DEC2025)": "%d%b%Y",
        "DDMONYY (e.g., 12DEC25)": "%d%b%y",
        "DD/MON/YYYY (e.g., 12/DEC/2025)": "%d/%b/%Y",
        "DD/MON/YY (e.g., 12/DEC/25)": "%d/%b/%y",
    }

    if format_hint == "custom":
        try:
            dt = datetime.strptime(date_str, custom_format)
            return dt.strftime("%m/%d/%Y")
        except (ValueError, TypeError):
            return None

    if format_hint in format_map:
        fmt = format_map[format_hint]
        try:
            dt = datetime.strptime(date_str, fmt)
            if "%y" in fmt and dt.year < 1900:
                dt = dt.replace(year=dt.year + 100)
            return dt.strftime("%m/%d/%Y")
        except ValueError:
            return None

    if format_hint == "auto":
        auto_formats = [
            "%m/%d/%Y", "%m-%d-%Y", "%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y",
            "%Y/%m/%d", "%m/%d/%y", "%Y%m%d",
            "%d-%b-%Y", "%d-%b-%y",
            "%d%b%Y", "%d%b%y",
            "%d/%b/%Y", "%d/%b/%y",
            "%d %b %Y", "%b %d, %Y",
        ]
        for fmt in auto_formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                if "%y" in fmt and dt.year < 1900:
                    dt = dt.replace(year=dt.year + 100)
                return dt.strftime("%m/%d/%Y")
            except ValueError:
                continue
        return None

    return None

# =========================
# Helpers
# =========================
def trim_text(val, max_len):
    if pd.isna(val) or str(val).strip() == "":
        return ''
    return str(val).strip()[:max_len]

def standardize_headers(df):
    mapping = {}
    for std_col, synonyms in COLUMN_SYNONYMS.items():
        for col in df.columns:
            if str(col).strip().lower() in [s.lower() for s in synonyms]:
                mapping[col] = std_col
    df.rename(columns=mapping, inplace=True)
    return df

def fill_blank_rows(df):
    first_valid_row = None
    for idx, row in df.iterrows():
        so = row.get('Sales Order No.', '')
        item = row.get('Item No.', '')
        if first_valid_row is None:
            if pd.notna(so) and str(so).strip() != '' and pd.notna(item) and str(item).strip() != '':
                first_valid_row = row.copy()
        elif first_valid_row is not None:
            for col in df.columns:
                if pd.isna(row[col]) or str(row[col]).strip() == '':
                    row[col] = first_valid_row.get(col, '')
    return df

def check_address_consistency(df):
    mismatch_flag = []
    addr_cols = ['Ship To', 'Ship To Address 2', 'Street', 'City', 'state', 'Zip Code', 'Country/Region']
    for _, row in df.iterrows():
        so_no = str(row.get('Sales Order No.', '')).strip()
        if not so_no or not str(row.get('Country/Region', '')).strip():
            mismatch_flag.append(False)
            continue
        same_so_rows = df[df['Sales Order No.'] == so_no]
        current_addr = tuple(str(row.get(col, '')).strip() for col in addr_cols)
        mismatch = False
        for _, r in same_so_rows.iterrows():
            if str(r.get('Country/Region', '')).strip():
                other_addr = tuple(str(r.get(col, '')).strip() for col in addr_cols)
                if other_addr != current_addr:
                    mismatch = True
                    break
        mismatch_flag.append(mismatch)
    df['Address_Mismatch'] = mismatch_flag
    return df

# =========================
# ✅ Warehouse consistency check across same Ref#
# =========================
def check_warehouse_consistency(df):
    """Flag rows where the same Sales Order No. (Ref#) has multiple warehouses."""
    whse_mismatch = []
    for _, row in df.iterrows():
        so_no = str(row.get('Sales Order No.', '')).strip()
        if not so_no:
            whse_mismatch.append(False)
            continue
        same_so = df[df['Sales Order No.'] == so_no]
        unique_whse = set(
            str(w).strip().upper()
            for w in same_so['WHSE'].tolist()
            if pd.notna(w) and str(w).strip() != ''
        )
        whse_mismatch.append(len(unique_whse) > 1)
    df['Warehouse_Mismatch'] = whse_mismatch
    return df

# =========================
# Main Processing Function
# =========================
def process_inbound_tsv(raw_text, date_format_hint="auto", custom_format=""):
    try:
        df = pd.read_csv(StringIO(raw_text), delimiter='\t', dtype=str)
    except Exception as e:
        st.error(f"Error parsing TSV: {e}")
        return None

    df = standardize_headers(df)

    # ✅ Required columns
    required_cols = ['Sales Order No.', 'Item No.', 'Each Qty', 'WHSE']
    for col in required_cols:
        if col not in df.columns:
            st.error(f"Required column missing: '{col}'")
            return None

    has_pick_date = 'Pick Date' in df.columns
    has_date2 = 'Date2' in df.columns
    if not has_pick_date and not has_date2:
        st.error("Required column missing: 'Pick Date' (or 'Delivery Date' as a fallback)")
        return None

    if 'Pick Date' not in df.columns:
        df['Pick Date'] = ''
    if 'Date2' not in df.columns:
        df['Date2'] = ''

    # Fallback: Delivery Date ↔ Pick Date
    df['Pick Date'] = df.apply(
        lambda r: r['Date2'] if (pd.isna(r['Pick Date']) or str(r['Pick Date']).strip() == '')
                              and not (pd.isna(r['Date2']) or str(r['Date2']).strip() == '')
                  else r['Pick Date'],
        axis=1
    )
    df['Date2'] = df.apply(
        lambda r: r['Pick Date'] if (pd.isna(r['Date2']) or str(r['Date2']).strip() == '')
                                and not (pd.isna(r['Pick Date']) or str(r['Pick Date']).strip() == '')
                   else r['Date2'],
        axis=1
    )

    optional_cols = [
        'Ship To', 'Ship To Code', 'Ship To Address 2', 'Street', 'City', 'state',
        'Zip Code', 'Country/Region', 'Customer PO', 'Ref 1', 'Ref 2', 'Ref 3',
        'Carrier Code', 'Carrier Name', 'CLIENT'
    ]
    for col in optional_cols:
        if col not in df.columns:
            df[col] = ''

    df = fill_blank_rows(df)

    # Auto-fill CLIENT
    df['CLIENT'] = df['CLIENT'].apply(
        lambda x: 'BS04' if pd.isna(x) or str(x).strip() == '' else str(x).strip()
    )

    # Auto-fill WHSE (normalize uppercase)
    df['WHSE'] = df['WHSE'].apply(
        lambda x: 'BLUNDELL2' if pd.isna(x) or str(x).strip() == '' else str(x).strip().upper()
    )

    df['Validation Status'] = df.apply(validate_address, axis=1)

    # Parse dates
    if date_format_hint == "custom":
        df['Pick Date Clean'] = df['Pick Date'].apply(
            lambda x: parse_to_mm_dd_yyyy(x, format_hint="custom", custom_format=custom_format)
        )
        df['Date2 Clean'] = df['Date2'].apply(
            lambda x: parse_to_mm_dd_yyyy(x, format_hint="custom", custom_format=custom_format)
        )
    else:
        df['Pick Date Clean'] = df['Pick Date'].apply(
            lambda x: parse_to_mm_dd_yyyy(x, format_hint=date_format_hint)
        )
        df['Date2 Clean'] = df['Date2'].apply(
            lambda x: parse_to_mm_dd_yyyy(x, format_hint=date_format_hint)
        )

    invalid_date_rows = df[df['Pick Date Clean'].isna() & df['Pick Date'].notna()]
    if not invalid_date_rows.empty:
        st.warning(f"⚠️ {len(invalid_date_rows)} row(s) have unparseable date and will be skipped.")

    # ✅ Address consistency check
    df = check_address_consistency(df)
    if df['Address_Mismatch'].any():
        st.error("⚠️ Address mismatch detected!")
        st.dataframe(df[df['Address_Mismatch']][['Sales Order No.', 'Street', 'City', 'state', 'Zip Code', 'Country/Region']])
        return None

    # ✅ Warehouse consistency check (same Ref# must have same warehouse)
    df = check_warehouse_consistency(df)
    if df['Warehouse_Mismatch'].any():
        st.error("⚠️ Warehouse mismatch detected! The same Ref# appears with different warehouses.")
        bad_refs = df[df['Warehouse_Mismatch']]['Sales Order No.'].unique().tolist()
        for ref in bad_refs:
            group = df[df['Sales Order No.'] == ref][['Sales Order No.', 'WHSE']]
            st.write(f"**Ref# {ref}** has multiple warehouses:")
            st.dataframe(group)
        return None

    # ✅ Sort/group rows by Ref# so identical orders are consecutive
    df = df.sort_values(by=['Sales Order No.'], kind='stable').reset_index(drop=True)

    output_rows = []
    all_cols = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ") + [f"A{chr(i)}" for i in range(ord('A'), ord('Z') + 1)]

    for _, row in df.iterrows():
        so_val      = row.get('Sales Order No.', '')
        item_val    = row.get('Item No.', '')
        qty_val     = row.get('Each Qty', '')
        whse_val    = row.get('WHSE', '')
        date_val    = row['Pick Date Clean']
        is_addr_valid = (row['Validation Status'] == "Valid")

        valid = all([
            pd.notna(so_val) and str(so_val).strip() != '',
            pd.notna(item_val) and str(item_val).strip() != '',
            pd.notna(qty_val) and str(qty_val).strip() != '',
            pd.notna(whse_val) and str(whse_val).strip() != '',
            date_val is not None,
            is_addr_valid
        ])

        if valid:
            out_row = {col: '' for col in all_cols}
            out_row['A'] = 'BC'
            out_row['B'] = trim_text(row.get('CLIENT', 'BS04'), 10)
            out_row['C'] = trim_text(row['Sales Order No.'], 30)
            out_row['D'] = trim_text(row.get('Customer PO', ''), 30)
            out_row['E'] = date_val
            out_row['G'] = trim_text(row.get('Ship To Code', ''), 10)
            out_row['H'] = trim_text(row.get('Ship To', ''), 45)
            out_row['J'] = trim_text(row.get('Street', ''), 30)
            out_row['K'] = trim_text(row.get('Ship To Address 2', ''), 30)
            out_row['L'] = trim_text(row.get('City', ''), 10)
            out_row['M'] = trim_text(row.get('state', ''), 10)
            out_row['N'] = trim_text(row.get('Zip Code', ''), 10)
            out_row['O'] = trim_text(row.get('Country/Region', ''), 10)
            out_row['P'] = trim_text(row.get('Carrier Code', ''), 10)
            out_row['Q'] = trim_text(row.get('Carrier Name', ''), 20)
            out_row['R'] = trim_text(row.get('WHSE', ''), 10)
            out_row['S'] = trim_text(row.get('Ref 1', ''), 30)
            out_row['T'] = trim_text(row.get('Ref 2', ''), 30)
            out_row['U'] = trim_text(row.get('Ref 3', ''), 30)
            out_row['V'] = trim_text(row['Item No.'], 20)
            out_row['W'] = trim_text(row['Each Qty'], 10)
            out_row['X'] = trim_text(row['Each Qty'], 10)
            date2_clean = row.get('Date2 Clean', None)
            out_row['AH'] = date2_clean if date2_clean is not None else ''
            output_rows.append(out_row)

    if not output_rows:
        st.warning("No valid rows found.")
        return None
    else:
        st.info(f"✅ Processed {len(output_rows)} valid row(s).")

    return pd.DataFrame(output_rows)

# =========================
# Streamlit UI
# =========================
st.title("Inbound TSV to CSV Converter")
st.markdown("""
Paste your TSV data below.  
✅ **Required fields**: `Ref#`, `Sku Code`, `Qty`, `Warehouse`, and a date  
✅ **`Delivery Date`** auto-fills **Pick Date (E)** and **Delivery Date (AH)**  
✅ **CLIENT** auto-fills to **`BS04`** if blank  
✅ **Warehouse** auto-fills to **`BLUNDELL2`** if blank  
✅ **Output is grouped by Ref#** so identical orders appear consecutively  
✅ **Warehouse mismatch check**: same Ref# must use the same warehouse  
✅ **Quantity** appears in **columns W and X**
""")

raw_data = st.text_area("Paste your TSV data here:", height=300)

st.markdown("### 📅 Date Format Handling")
date_format_option = st.selectbox(
    "How should dates be interpreted?",
    options=[
        "Auto-detect (recommended)",
        "MM/DD/YYYY",
        "MM-DD-YYYY",
        "YYYY-MM-DD",
        "DD/MM/YYYY",
        "DD-MM-YYYY",
        "YYYY/MM/DD",
        "MM/DD/YY",
        "YYYYMMDD",
        "DD-MON-YYYY (e.g., 12-DEC-2025)",
        "DD-MON-YY (e.g., 12-DEC-25)",
        "DDMONYYYY (e.g., 12DEC2025)",
        "DDMONYY (e.g., 12DEC25)",
        "DD/MON/YYYY (e.g., 12/DEC/2025)",
        "DD/MON/YY (e.g., 12/DEC/25)",
        "Custom format (enter below)"
    ],
    index=0
)

custom_format = ""
if date_format_option == "Custom format (enter below)":
    custom_format = st.text_input(
        "Enter Python strftime format (e.g., %d.%m.%Y):",
        value="%m/%d/%Y"
    )

if st.button("Generate Inbound CSV"):
    if not raw_data.strip():
        st.warning("Please paste your TSV data.")
    else:
        if date_format_option == "Custom format (enter below)":
            if not custom_format.strip():
                st.error("Please enter a custom date format.")
                st.stop()
            actual_format = "custom"
        elif date_format_option == "Auto-detect (recommended)":
            actual_format = "auto"
        else:
            actual_format = date_format_option

        processed_df = process_inbound_tsv(
            raw_data,
            date_format_hint=actual_format,
            custom_format=custom_format
        )
        if processed_df is not None:
            csv_data = processed_df.to_csv(index=False, header=False, encoding='cp1252').replace('\n', '\r\n')
            st.download_button(
                label="📥 Download CSV",
                data=csv_data,
                file_name="rinbound_output.csv",
                mime="text/csv"
            )
            st.success("✅ CSV generated successfully!")
