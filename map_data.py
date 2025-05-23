import sqlite3
import requests
import re
from collections import Counter
import folium
from folium.plugins import HeatMap
import matplotlib.pyplot as plt

mapbox_token = 'pk.eyJ1IjoiY2VpbGluZSIsImEiOiJjbTkwNGZobnIwanRtMmpwb3dvZTRyMTB4In0.-C6PmulyXbGp8FsLOIuTYw'

# Connect to usajobs.db database
conn = sqlite3.connect("usajobs.db") 
cur = conn.cursor()

# create tables
cur.execute('''
    CREATE TABLE IF NOT EXISTS Coordinates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER,
        latitude REAL,
        longitude REAL,
        FOREIGN KEY(job_id) REFERENCES Jobs(id)
    )
''')

try:
    cur.execute("ALTER TABLE Jobs ADD COLUMN number INTEGER")
    conn.commit()
except sqlite3.OperationalError:
    pass

conn.commit()

# get coordinates（langtitude and longtitude)
def get_coordinates(address):
    try:
        url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{address}.json?access_token={mapbox_token}"
        response = requests.get(url)
        data = response.json()
        if data["features"]:
            coords = data["features"][0]["center"]
            return coords[1], coords[0]  # lat, lon
    except Exception as e:
        print(f"Error fetching the coordinates for {address}: {e}")
    return None
cur.execute('''
    SELECT Jobs.id, Titles.title, Organizations.organization, Locations.location
    FROM Jobs
    JOIN Titles ON Jobs.title_id = Titles.id
    JOIN Organizations ON Jobs.organization_id = Organizations.id
    JOIN Locations ON Jobs.location_id = Locations.id
    WHERE Jobs.id NOT IN (SELECT job_id FROM Coordinates)
''')
jobs_to_add = cur.fetchall()

# max 25 jobs per run
cur.execute("SELECT MAX(number) FROM Jobs")
max_number = cur.fetchone()[0] or 0

# initializer 25 new jobs
inserted = 0
for job in jobs_to_add[:25]:  # Slice to max 25
    job_id, title, org, location = job
    coords = get_coordinates(location)
    if coords:
        lat, lon = coords
        try:
            # coordinates （langtitude and longtitude) linked to the job
            cur.execute("INSERT INTO Coordinates (job_id, latitude, longitude) VALUES (?, ?, ?)", (job_id, lat, lon))
            conn.commit()
            print(f"Inserted the coordinates for: {title} | {location} -> ({lat}, {lon})")
        except Exception as e:
            print(f"Skipped {location}: {e}")

# Process the data: Job counts per state 
cur.execute('''
    SELECT Jobs.id, Titles.title, Organizations.organization, Locations.location
    FROM Jobs
    JOIN Titles ON Jobs.title_id = Titles.id
    JOIN Organizations ON Jobs.organization_id = Organizations.id
    JOIN Locations ON Jobs.location_id = Locations.id
''')
all_jobs = cur.fetchall()
cur.execute('''
    SELECT Locations.location 
    FROM Jobs
    JOIN Locations ON Jobs.location_id = Locations.id
''')
all_locations = [row[0] for row in cur.fetchall()]

# Step 2: Extract state from each location
def extract_state(location):
    if not location:
        return None
    match = re.search(r',\s*([^,]+)$', location)
    if match:
        return match.group(1).strip()
    return None

# Step 3: Count jobs per state
states = [extract_state(loc) for loc in all_locations if extract_state(loc)]
state_counts = Counter(states)

def extract_state(location):
    match = re.search(r',\s*([^,]+)$', location)
    if match:
        return match.group(1).strip()
    return None

states = []
for loc in all_locations:
    state = extract_state(loc)
    if state:
        states.append(state)
state_counts = Counter(states)

# join query to include Coordinates (requirement)
cur.execute('''
    SELECT Locations.location, COUNT(*) 
    FROM Jobs J
    JOIN Coordinates C ON J.id = C.job_id
    JOIN Locations ON J.location_id = Locations.id  -- Join with Locations to get the location
    GROUP BY Locations.location  -- Group by the location in the Locations table
''')
joined_results = cur.fetchall()

joined_states = []
for loc, count in joined_results:
    state = extract_state(loc)
    if state:
        joined_states.extend([state] * count)
joined_counts = Counter(joined_states)

# combined all of the data to txt
with open("state_job_counts_combined.txt", "w") as f:
    f.write("State\tTotal_Jobs\tJobs_With_Coordinates\n")
    all_states = set(state_counts.keys()).union(joined_counts.keys())
    for state in sorted(all_states):
        f.write(f"{state}\t{state_counts[state]}\t{joined_counts[state]}\n")
print("📝 Saved job count summary to state_job_counts_combined.txt")

# Heatmap of job coordinates (first data viz: heat map)
cur.execute("SELECT latitude, longitude FROM Coordinates")
coords = cur.fetchall()
if coords:
    m = folium.Map(location=[39.5, -98.35], zoom_start=4)
    HeatMap(coords).add_to(m)
    m.save("job_heatmap.html")
    print("Heatmap saved to job_heatmap.html")

# mathplotlib data viz: Jobs with Coordinates per State (second data viz: Bar Chart)
plt.figure(figsize=(10, 6))
plt.bar(joined_counts.keys(), joined_counts.values(), color='salmon')
plt.xticks(rotation=45, ha='right')
plt.title("Jobs With Coordinates per State")
plt.tight_layout()
plt.savefig("jobs_with_coords_per_state.png")
print("📊 Bar chart saved to jobs_with_coords_per_state.png")

conn.close()