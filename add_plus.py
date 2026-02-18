import pandas as pd
import csv

# 1. Load your file
file_name = 'final_call_analysis_v3.csv'
# Using dtype=str ensures digits aren't mangled into scientific notation during load
df = pd.read_csv(file_name, dtype=str)

# 2. Function to add '+' prefix and force TEXT format for Excel
def format_as_text_cell(val):
    if pd.isna(val):
        return ""
    
    # Convert to string and clean up any existing Excel formatting or spaces
    # This prevents results like ="="+12345"" if the script is run twice
    s = str(val).replace('=', '').replace('"', '').strip()
    
    # Remove '.0' if the number was read as a decimal
    if s.endswith('.0'):
        s = s[:-2]
        
    # Skip if the cell is empty or says 'nan'
    if s.lower() in ['nan', 'none', '']:
        return ""
    
    # Ensure there is exactly one '+' at the start
    clean_number = s.lstrip('+')
    phone_with_plus = "+" + clean_number
    
    # Wrap in Excel formula to force text: ="+123456789"
    return f'="{phone_with_plus}"'

# 3. Apply the function to the specific columns
columns_to_fix = ['Called Number', 'Calling Number']

for col in columns_to_fix:
    if col in df.columns:
        df[col] = df[col].apply(format_as_text_cell)
        print(f"Successfully formatted: {col}")
    else:
        print(f"Warning: '{col}' column not found in CSV.")

# 4. Save the updated file
output_name = 'final_call_analysis_formatted.csv'
df.to_csv(output_name, index=False, quoting=csv.QUOTE_MINIMAL)

print(f"\nDone! Saved to {output_name}")