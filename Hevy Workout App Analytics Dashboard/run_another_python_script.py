    
import subprocess
import re
import streamlit as st

def run_sub_script_with_progress(command):
    # command example: python another_script.py --key 1234  # Use 'python3' if required

    # Launch the subprocess
    with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
        while True:
            # Read the next line from stdout
            output = process.stdout.readline()

            # If output is empty and process has finished, break the loop
            if output == '' and process.poll() is not None:
                break

            if output:
                # Display the full log line
                st.write(output.strip())

                # Optionally parse specific information from logs
                # For example, matching lines with 'Fetching workouts from page'
                match = re.search(r'Fetching workouts from page: (\d+) \(pageSize:\d+\)', output)
                if match:
                    page_number = match.group(1)
                    st.write(f"Progress: Fetching data from page {page_number}")

        # Check for any errors
        stderr = process.stderr.read()
        if stderr:
            st.write(f"Error: {stderr}")