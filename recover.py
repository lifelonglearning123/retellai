import pandas as pd

# 1. Load the data into a pandas table
# dtype=str is crucial to prevent the computer from rounding numbers immediately
df = pd.read_csv('file.csv', dtype=str)

# 2. Add the + to the number and force Text Formatting for CSV
def format_for_excel(val):
    if pd.isna(val) or str(val).strip() == "" or str(val).strip().lower() == "nan":
        return ""
    
    s_val = str(val).strip()
    
    # Expand scientific notation (e.g., 4.47E+11 -> 447000000000)
    if 'E+' in s_val.upper():
        try:
            s_val = "{:.0f}".format(float(s_val))
        except:
            pass
    
    # Remove decimal points if any (common when CSVs are pre-opened in Excel)
    clean_digits = s_val.split('.')[0]
    
    # This specific format '="+number"' forces Excel to display it as text
    return f'="+{clean_digits}"'

# Apply formatting to both number columns
df['Called Number'] = df['Called Number'].apply(format_for_excel)
df['Calling Number'] = df['Calling Number'].apply(format_for_excel)

# 3. Rename Attendance to Tag and filter columns
# We now include 'Calling Number' in the final column list
df['Tag'] = df['Attendance']
final_df = df[['Called Number', 'Calling Number', 'Tag']]

# 4. Save to a new CSV file
final_df.to_csv('file_new.csv', index=False)

print("Process complete. File saved as 'file_new.csv'")