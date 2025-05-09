import re

# Raw data
raw_text = """
Dr Sanjay Kumar CTVS BP00061567 Mr. Ajay Kumar Follow Up (P) 01-Jul-2024 02-Jul-2024 9905833544 0905833544 Or Sanjay Kumar 11:18:42 AM 03-Jul-2024 CTVS BP00203792 Mrs. SARASWATI DEVI First Visit 03-Jul-2024 + 917992150112-017992350112 Or Sanjay Kumar 08:23:49 AM 02-Jul-2024 CTVS BP00151988 Md Shahajad Follow Up (P) 03-Jul-2024 8651009480 10:38:54 AM 27-Jun-2024 Dr Sanjay Kumar CTVS BP00199752 Mr. Chandan Kumar Follow Up (P) 28-Jun-2024 917480857219 +917480857219 Dr Sanjay Kumar 11:16:38 AM CTVS BP00187509 Mrs. Punam Devi Follow Up (P) 21-Jun-2024 21-Jun-2024 9334902688 1334902668 08:29:24 AM Dr Sanjay Kumar CTVS BP00163032 Mrs. Archana Kuman First Visit 21-Jun-2024 12:22:12 PM 21-Jun-2024 9031616896 Dr Sanjay Kumar CTVS BP00173793 avan Kumar Follow Up (P) 27-Jun-2024 01-Jul-2024 +917909021605 +917909021605 04:39:26 PM Or Sanjay Kumar CTVS BP00126265 Durgawati Devi First Visit 20-Jul-2024 23-Jul-2004 7061068757 7061068757 01:42:10 PM y Kumar CTVS BP00121088 Mr. Chuman Manjhi Follow Up (P) 14-Jul-2024 11:10:22 AM 22-3-2024 6299980853 Or Sanjay Kumar BP00193270 Mr. Baban Prasad Follow Up (P) 12-Jul-2024 15-Jul-2024 9835442755 9835442755 Upadhayay Mrs. Munni Devi 04:00:42 PM Dr Sanjay Kumar CTVS MM02594498 Follow Up (P) 18-Jul-2024 19-Jul-2024 8873042291 8873042291 08:42:38 AM Dr Sanjay Kumar CTVS BP00213188 Ashwani Kumar Follow Up JP) 10-Aug-2024 12-Aug-2024 8826833177 826833177 11:31:25 AM Dr Sanjay Kumar CTVS BP00209923 Naresh Kumar First Visit 22-Jul-2024 23-Jul-2024 916204903812 -916204903812 08:03:10 AM 03-Aug-2024 Or Sanjay Kumar CTVS Uttam pandit First Visit 05-Aug-2024 +917643034080 +917643034080 01:15:08 PM Or Sanjay Kumar CTV Uttam pandit First Visit 05-Aug-2024 06-Aug-2024 917643034080 -917643034080 01:17:40 PM 30-Jul-2024 Or Sanjay Kumar CTVS BP00201893 Mr. Virendra Kumar Follow Up (P) 14-Aug-2024 +917017909556 +917017909556 Mishra Mr. Sarweshwar 10:32:24 AM 04-Aug-2024 Dr Sanjay Kumar CTVS BP00178978 Follow Up (P) 05-Aug-2024 9430667780 9430667780 Prasad Verma Mr. Ram Kumar Dr Sanjay Kumar TVS BP00205480 Follow Up (P 30-Jul-2024 31-Jul-2024 8234939217 Paswan Sarju Prasad 10:16:18 AM 05-Aug-2024 Dr Sanjay Kumar CTVS P00169263 Follow Up (P 06-Aug-2024 7004132678 7004132678 12-52:49 PM Dr Sanjay Kumar CTVS BP00137222 Bhagwan Sah Follow Up (P) 30-Jul-2024 31--2024 6201511232 05:24:05 AM Dr Sanjay Kumar CTVS Munmun dubey First Visit 09-Sep-2024 10-Sep-2024 917942773584 +917942773584 07:56:58 AM Dr Sanjay Kumi CTVS 8000050381 Satyendra Prasad Follow Up() 09-Sep-2024 10-Sep-2024 9934257039 9934257039 11:34:30 AM Dr Sanjay Kumar CTVS BP00222616 Shyam Chandra Follow Up (P) 08-Sep-2024 01:47:01 PM 09-Sep-2024 9955537760 Dr Sanjay Kumar CTVS BP00076362 Mr. Deepak Kumar Follow Up (P) 07-Sep-2024 07-Sep-2024 Privadarshi Nasir Uddin Sanjay Kum CTVS MM02414379 First Visit 08-Oct-2024 07:59:57 AM Sanjay Kumar CTVS BP00214741 Kalmun Nisha Follow Up (P) 04:13:08 PM 10-Sep-2024 03:13:46 PM Dr Sanjay Kumar CTVS BP00082033 Arvind Mahto Follow Up (P) 18-Sep-2024 08:06:21 AM 13-Sep-2024 18-Sep-2024 Or Sanjay Kumar BP00228288 Mrs. Rokhsana Khatun Follow Up (P) 11:02:03 AM Or Sanjay Kumar BP00176304 Mr. ASHOK KUMAR Foliow Up (P) SWGH Mr. Minhajul Islam 18-Sep-2024 Dr Sanjay Kum Dr Sanjay Kumar CTVS BP00050985 Follow Up (P) Or Sanjay Kumar CTVS BP00038938 Mr. Jaipal Kisku Follow Up (P) 03:37:33 PM 23-Sep-2024 07:38:21 PM 09-Oct-2024 03-47:17 PM 04-Oct-2024 09-Sep-2024 8409894399 409094399 10-Oct-2024 9654134347 9654134347 11-Sep-2024 6201653495 6201653495 16-Sep-2024 +919430600786 8084514427 01-Oct-2024 919110149394-919110149394 18-Oct-2024 9801491818 7979891765 8210146265 9939593391 Or Sanjay Kumar CTVS BP00033088 Mr. Sanjeev Kumar Jha Follow Up (P) 27-Sep-2024 09:43:50 AM 01-Oct-2024 6205413870 Dr Sanjay Kumar CTVS Kyz First Visit 17-Oct-2024 17-Oct-2024 0000000000 11:50:33 AM Sanjay Kuma CTVS MM02673589 Mr. Shyam Sunder First Visit 18-Oct-2024 21-Oct-2024 7004852006 7004852006 Singh Nanku mahto. 109-25:23 AM Dr Sanjay Kumar CTVS First Visit 17-Oct-2024 08:14:09 AM 17-Oct-2024 + 916392298783 +916392298783 Or Sanjay Kumar CTVS First Visit 17-Oct-2024 11:48:01 AM 17-Oct-2024 0000000000 Dr Sanjay Kumar CTVS First Visit 17-Oct-2024 17-Oct-2024 0000000000 11:48:47 AM Dr Sanjay Kumar CTVS xyz First Visit 17-Oct-2024 17-Oct-2024 0000000000 Or Sanjay Kumar 11:49:54 AM CTVS SP00221578 Mrs. Gayatri Devi Follow Up (P) 17-Nov-2024 19-Nov-2024 9934046015 9934046015
"""

# Regular expression to extract data
pattern = re.compile(r"""
    (Dr\.?\s\S+\s\S+)       # Doctor's name
    \s(CTVS)                # Department
    \s(BP\d+)               # Patient ID
    \s([\w\s.]+?)           # Patient name
    \s(Follow\sUp\s\(P\)|First\sVisit) # Visit type
    \s(\d{2}-[A-Za-z]+-\d{4}) # Visit date
    (?:\s(\d{2}-[A-Za-z]+-\d{4}|-))?  # Next visit date (optional)
    \s([\d+-]+)             # Contact 1
    (?:\s([\d+-]+))?        # Contact 2 (optional)
    \s([\d:AMP]+)           # Timestamp
""", re.VERBOSE)

# Extract and structure the data
data = []
for match in pattern.finditer(raw_text):
    data.append([
        match.group(1),  # Doctor
        match.group(2),  # Department
        match.group(3),  # Patient ID
        match.group(4).strip(),  # Patient Name
        match.group(5),  # Visit Type
        match.group(6),  # Visit Date
        match.group(7) if match.group(7) else "-",  # Next Visit Date
        match.group(8),  # Contact 1
        match.group(9) if match.group(9) else "-",  # Contact 2
        match.group(10),  # Timestamp
    ])

# Print the structured data
for record in data:
    print(record)
