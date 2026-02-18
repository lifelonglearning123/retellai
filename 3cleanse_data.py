import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Phone Formatter", page_icon="📞")
st.title("📞 Phone Number Formatter")
st.write("Formats UK numbers and ensures they remain as text. No rows will be deleted.")

# 1. File Uploader
uploaded_file = st.file_uploader("Upload CSV or XLSX", type=['csv', 'xlsx'])

def clean_to_string(val):
    s = str(val).strip()
    if s.endswith('.0'): s = s[:-2] 
    if s.lower() in ['nan', 'none', '']: return ""
    # We ensure a '+' exists to prevent Excel from auto-formatting as a number
    if not s.startswith('+'): 
        s = '+' + s
    return s

def transform_prefixes(val):
    # Case 1: Already correct (+447...) -> Do nothing
    if val.startswith('+447'):
        return val
    # Case 2: Local format (07...) -> Convert to +447...
    # Note: clean_to_string will have turned 07 into +07
    elif val.startswith('+07'):
        return '+447' + val[3:]
    # Case 3: Partial international (+7...) -> Convert to +447...
    elif val.startswith('+7'):
        return '+447' + val[2:]
    # Case 4: No plus but correct digits (447...)
    # Note: clean_to_string will have turned 447 into +447, handled by Case 1
    return val

if uploaded_file is not None:
    try:
        # 2. Load with string enforcement
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, dtype={'Phone': str}) 
        else:
            df = pd.read_excel(uploaded_file, dtype={'Phone': str}, engine='openpyxl') 

        if 'Phone' in df.columns:
            # 3. Processing Logic (Filtering line REMOVED)
            df['Phone'] = df['Phone'].apply(clean_to_string)
            df['Phone'] = df['Phone'].apply(transform_prefixes)

            st.success(f"Processing Complete! Kept all {len(df)} rows.")
            st.dataframe(df.head())

            # 4. Save as Text-Safe CSV
            output = io.StringIO()
            # quoting=1 wraps numbers in "" so Excel doesn't truncate them
            df.to_csv(output, index=False, quoting=1) 
            
            st.download_button(
                label="Download Processed CSV",
                data=output.getvalue(),
                file_name="Formatted_Contacts.csv",
                mime="text/csv"
            )
        else:
            st.error("Error: Could not find a 'Phone' column.")
    except Exception as e:
        st.error(f"An error occurred: {e}")