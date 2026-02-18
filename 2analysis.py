import pandas as pd
from openai import OpenAI
import time

# 1. Setup
# Recommendation: Use an environment variable for security
client = OpenAI(api_key='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') 
input_file = "retell_calls_full.csv"
output_file = "final_call_analysis_v3.csv"

def analyze_transcript(transcript, reason):
    # Basic check for empty or failed connections
    if not transcript or "No transcript available" in transcript:
        return "Not Available", "No connection established", "N/A"

    # The System Message establishes the persona
    system_msg = "You are the world's best phone call analysis expert."
    
    # The User Prompt defines the logic rules
    user_prompt = f"""
    Objective: Determine if the client (receiver) is attending the exhibition.
    
    Transcript: 
    {transcript}

    Rules:
    - If the receiver is an answering machine or voicemail: Output "Not Available".
    - If the receiver said they are attending: Output "Attend".
    - If the receiver said they are NOT attending: Output "Not Attending".
    - If the receiver answered but did not firmly reject (e.g., "maybe," "call back," or hung up during the pitch): Output "Maybe".

    Return ONLY in this format: Attendance | Reason | Call Type
    (Example: Attend | Customer confirmed they will be there at 10am | Normal)
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0
        )
        # Split the response into the three columns
        parts = response.choices[0].message.content.split(" | ")
        
        # Ensure we always return 3 parts even if GPT formatting slips
        while len(parts) < 3:
            parts.append("N/A")
        return parts[0], parts[1], parts[2]
        
    except Exception as e:
        return "Error", str(e), "Error"

# 2. Process the CSV
df = pd.read_csv(input_file)
# Fill empty transcripts with a placeholder string to prevent errors
df['Full Transcript'] = df['Full Transcript'].fillna("No transcript available")

results = []

print(f"Analyzing {len(df)} calls...")

for index, row in df.iterrows():
    att, res, ctype = analyze_transcript(row['Full Transcript'], row['Disconnection Reason'])
    results.append({'Attendance': att, 'Reason': res, 'Call Type': ctype})
    
    if index % 10 == 0: 
        print(f"Processed {index} calls...")

# 3. Save Results
analysis_df = pd.DataFrame(results)
final_df = pd.concat([df, analysis_df], axis=1)
final_df.to_csv(output_file, index=False)

print(f"Done! Saved to {output_file}")