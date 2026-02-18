import csv
from datetime import datetime
from retell import Retell

# Initialize the client
# NOTE: It's recommended to use environment variables for security!
client = Retell(api_key="key_d334b402b76604bfff9f0892ca4e")

def format_time(ms_timestamp):
    """Converts Retell's millisecond timestamp to a readable date/time string."""
    if not ms_timestamp:
        return "N/A"
    return datetime.fromtimestamp(ms_timestamp / 1000.0).strftime('%Y-%m-%d %H:%M:%S')

def format_transcript(call):
    """Extracts the full transcript from the call object."""
    if hasattr(call, 'transcript') and call.transcript:
        return call.transcript
    
    transcript_list = getattr(call, 'transcript_object', [])
    if transcript_list:
        lines = []
        for turn in transcript_list:
            role = getattr(turn, 'role', 'unknown').capitalize()
            content = getattr(turn, 'content', '')
            lines.append(f"{role}: {content}")
        return "\n".join(lines)
    
    return "No transcript available"

def download_calls_to_csv(filename="retell_calls_full.csv", limit=1300):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        header = [
            'Name', 'Start Time', 'End Time', 'Duration (sec)', 
            'Called Number', 'Calling Number', 'Status', 
            'Disconnection Reason', 'Full Transcript'
        ]
        writer.writerow(header)

        print(f"Fetching up to {limit} calls...")
        
        all_calls = []
        # Retell API usually limits single requests to 100 or 1000
        response = client.call.list(limit=min(limit, 1000))
        all_calls.extend(response)
        
        if len(all_calls) < limit and len(response) > 0:
            last_call_id = all_calls[-1].call_id
            remaining = limit - len(all_calls)
            if remaining > 0:
                next_page = client.call.list(limit=remaining, pagination_key=last_call_id)
                all_calls.extend(next_page)

        for call in all_calls:
            # 1. TIME EXTRACTION
            start_ms = getattr(call, 'start_timestamp', 0)
            end_ms = getattr(call, 'end_timestamp', 0)
            
            start_time = format_time(start_ms)
            end_time = format_time(end_ms)
            duration_sec = (end_ms - start_ms) / 1000 if end_ms and start_ms else 0

            # 2. PHONE NUMBERS (Formatted as Text Cells)
            # Using the ="{value}" trick ensures Excel treats these as literal strings.
            called_raw = getattr(call, 'to_number', "N/A")
            calling_raw = getattr(call, 'from_number', "N/A")
            
            called_number = f'="{called_raw}"'
            calling_number = f'="{calling_raw}"'
            
            # 3. METADATA (NAME)
            metadata = getattr(call, 'metadata', {}) or {}
            dynamic_vars = getattr(call, 'retell_llm_dynamic_variables', {}) or {}
            name = (metadata.get('customer_name') or 
                    metadata.get('name') or 
                    dynamic_vars.get('customer_name') or 
                    "Unknown")
            
            # 4. STATUS & TRANSCRIPT
            status = getattr(call, 'call_status', "N/A")
            disconnection = getattr(call, 'disconnection_reason', "N/A")
            full_transcript = format_transcript(call)
            
            writer.writerow([
                name, start_time, end_time, round(duration_sec, 2),
                called_number, calling_number, status, 
                disconnection, full_transcript
            ])
            
    print(f"Successfully saved {len(all_calls)} calls to {filename}")

if __name__ == "__main__":
    download_calls_to_csv()