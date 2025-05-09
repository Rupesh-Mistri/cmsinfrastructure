import re
import pandas as pd

# Sample raw data (your input text)
data = """
Sanjay BP00061567 Ajay Kumar Follow Up (P) 02-Jul-2024 9905833544 9900833544 Or Sanjay Kumar Dr Sanjay Kur CTVS CTVS BP00203792 BP0015198
Md Shahajad Follow Up (P) 02-Jul-2024 03-Jul-2024 51005480 10:38:54 AM 27-Jun-2024 Sanjay Kumar CTVS BP00199752
Mr. Chandan Kumar Follow Up (P) 28-Jun-2024 +917480857219 +917480857219 11.36.38 AM 21-Jun-2024 Dr Sanjay Kumar CTVS BP00187509
"""

# Define a pattern to capture key fields in the unstructured data
# Adjusted to be more general and flexible to match the provided data
pattern = r"([A-Za-z\s]+)\s+([A-Za-z0-9]+)\s+([A-Za-z\s\(\)]+)\s+(\d{2}-\w{3}-\d{4})\s+(\+?\d{10,15})\s+(\+?\d{10,15})?\s+([A-Za-z\s]+)\s+([A-Za-z\s]+)\s+([A-Za-z]+)\s+([A-Za-z]+)\s+([A-Za-z0-9]+)"

# Find all matches
matches = re.findall(pattern, data)

# Check if we got matches, otherwise print an error
if not matches:
    print("No matches found. Check the regex pattern.")
else:
    # Create a DataFrame from the matches
    columns = ["Name", "ID", "Visit Type", "Visit Date", "Phone Number 1", "Phone Number 2", "Doctor", "Specialization", "Doctor Name", "Specialization", "BP Number"]
    df = pd.DataFrame(matches, columns=columns)

    # Display the resulting DataFrame
    print(df)

    # Optionally, save the DataFrame to a CSV
    df.to_csv("output.csv", index=False)
