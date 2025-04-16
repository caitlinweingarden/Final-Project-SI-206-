# import folium
# from folium.plugins import HeatMap
# import requests
# import sqlite3
# import json
# from bs4 import BeautifulSoup

# # Your Mapbox Access Token
# mapbox_token = 'pk.eyJ1IjoiY2VpbGluZSIsImEiOiJjbTkwNGZobnIwanRtMmpwb3dvZTRyMTB4In0.-C6PmulyXbGp8FsLOIuTYw'

# def get_coordinates(address):
#     """Gets latitude and longitude for a given address using Mapbox API."""
#     url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{address.replace(' ', '%20')}.json?access_token={mapbox_token}"
#     response = requests.get(url)
#     if response.status_code != 200:
#         print(f"Error: Mapbox API request failed for {address}. Status code: {response.status_code}")
#         return None

#     try:
#         data = response.json()
#         if 'features' in data and data['features']:
#             lon = data['features'][0]['geometry']['coordinates'][0]
#             lat = data['features'][0]['geometry']['coordinates'][1]
#             return lat, lon
#         else:
#             print(f"Warning: No coordinates found for {address}.")
#             return None
#     except Exception as e:
#         print(f"Error processing API response for {address}: {e}")
#         return None

# # ============ DATABASE SETUP ============

# source_conn = sqlite3.connect('usajobs.db')
# source_cur = source_conn.cursor()

# new_conn = sqlite3.connect('coordinates.db')  # ✅ UPDATED
# new_cur = new_conn.cursor()

# # Create new table for locations with coordinates
# new_cur.execute('''
#     CREATE TABLE IF NOT EXISTS JobLocations (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         title TEXT,
#         organization TEXT,
#         location TEXT,
#         latitude REAL,
#         longitude REAL
#     )
# ''')
# new_conn.commit()

# # Get jobs from source database
# source_cur.execute("SELECT title, organization, location FROM Jobs")
# jobs = source_cur.fetchall()

# job_coords = []
# inserted = 0

# for job in x:
#     title, org, location = job
#     coords = get_coordinates(location)
#     if coords:
#         lat, lon = coords
#         new_cur.execute('''
#             INSERT INTO JobLocations (title, organization, location, latitude, longitude)
#             VALUES (?, ?, ?, ?, ?)
#         ''', (title, org, location, lat, lon))
#         job_coords.append([lat, lon])
#         inserted += 1
#         print(f"✅ {inserted}. {title} | {location} → ({lat}, {lon})")

# new_conn.commit()
# source_conn.close()
# new_conn.close()

# print(f"\n🎯 Done! {inserted} jobs with coordinates saved in 'coordinates.db'.")

# # ============ HEATMAP WITH FOLIUM ============

# m = folium.Map(location=[39.5, -98.35], zoom_start=4)  # center on US
# HeatMap(job_coords).add_to(m)
# m.save("job_heatmap.html")
# print("✅ Heat map saved as job_heatmap.html")

# # ============ EXPORT GEOJSON ============

# features = []

# for coord in job_coords:
#     features.append({
#         "type": "Feature",
#         "geometry": {
#             "type": "Point",
#             "coordinates": [coord[1], coord[0]]  # [lon, lat]
#         }
#     })

# geojson_data = {
#     "type": "FeatureCollection",
#     "features": features
# }

# # Save GeoJSON data
# with open("job_coords.geojson", "w") as f:
#     json.dump(geojson_data, f)

# # ============ CUSTOM HTML LAYOUT WITH BeautifulSoup ============

# # Load the generated HTML from Folium
# with open("job_heatmap.html", "r") as f:
#     soup = BeautifulSoup(f, "html.parser")

# # Add a custom header
# header = soup.new_tag("h1")
# header.string = "📍 USA Jobs Heatmap"
# soup.body.insert(0, header)

# # Add a description paragraph
# desc = soup.new_tag("p")
# desc.string = "This interactive map shows the density of job locations across the US."
# soup.body.insert(1, desc)

# # Save the customized HTML
# with open("custom_heatmap.html", "w") as f:
#     f.write(str(soup))

# print("✅ Custom HTML saved as custom_heatmap.html")

# import requests
# import sqlite3
# import json
# import re
# import time
# from bs4 import BeautifulSoup
# from folium.plugins import HeatMap
# import folium
# import matplotlib.pyplot as plt
# from collections import defaultdict

# mapbox_token = 'pk.eyJ1IjoiY2VpbGluZSIsImEiOiJjbTkwNGZobnIwanRtMmpwb3dvZTRyMTB4In0.-C6PmulyXbGp8FsLOIuTYw'

# # ============================
# # DB SETUP
# # ============================

# conn = sqlite3.connect('final_jobs.db')
# cur = conn.cursor()

# cur.execute('''
# CREATE TABLE IF NOT EXISTS Jobs (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     title TEXT,
#     organization TEXT,
#     location TEXT UNIQUE
# )
# ''')

# cur.execute('''
# CREATE TABLE IF NOT EXISTS JobLocations (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     job_id INTEGER,
#     latitude REAL,
#     longitude REAL,
#     state TEXT,
#     FOREIGN KEY (job_id) REFERENCES Jobs(id)
# )
# ''')

# conn.commit()

# # ============================
# # STEP 1: Load 25 jobs at a time from usajobs.db
# # ============================

# source_conn = sqlite3.connect('usajobs.db')
# source_cur = source_conn.cursor()

# source_cur.execute("SELECT title, organization, location FROM Jobs")
# all_jobs = source_cur.fetchall()
# source_conn.close()

# # Check how many are already inserted
# cur.execute("SELECT COUNT(*) FROM Jobs")
# existing_count = cur.fetchone()[0]
# new_jobs = all_jobs[existing_count:existing_count+25]

# def get_coordinates(address):
#     url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{address.replace(' ', '%20')}.json?access_token={mapbox_token}"
#     response = requests.get(url)
#     if response.status_code != 200:
#         return None
#     try:
#         data = response.json()
#         if 'features' in data and data['features']:
#             lon = data['features'][0]['geometry']['coordinates'][0]
#             lat = data['features'][0]['geometry']['coordinates'][1]
#             return lat, lon
#     except:
#         return None

# inserted = 0
# for job in new_jobs:
#     title, org, loc = job
#     try:
#         cur.execute("INSERT OR IGNORE INTO Jobs (title, organization, location) VALUES (?, ?, ?)", (title, org, loc))
#         conn.commit()
#         cur.execute("SELECT id FROM Jobs WHERE location=?", (loc,))
#         job_id = cur.fetchone()[0]
#         coords = get_coordinates(loc)
#         if coords:
#             lat, lon = coords
#             state_match = re.findall(r',\s*([A-Za-z ]+)$', loc)
#             state = state_match[0] if state_match else None
#             cur.execute('''INSERT INTO JobLocations (job_id, latitude, longitude, state)
#                            VALUES (?, ?, ?, ?)''', (job_id, lat, lon, state))
#             conn.commit()
#             inserted += 1
#             print(f"✅ {inserted}. {loc} → ({lat}, {lon}) | State: {state}")
#     except Exception as e:
#         print(f"Error inserting job: {e}")

# print(f"\n🎯 Inserted {inserted} new jobs into final_jobs.db")
# # ============================
# # STEP 2: Count jobs per state
# # ============================

# cur.execute('''
#     SELECT state, COUNT(*) FROM JobLocations
#     WHERE state IS NOT NULL
#     GROUP BY state
# ''')
# results = cur.fetchall()

# # Write to summary
# with open("summary.txt", "w") as f:
#     for state, count in results:
#         f.write(f"{state}: {count}\n")
# print("✅ Summary written to summary.txt")
# # ============================
# # STEP 3: Visualize
# # ============================

# # Heatmap
# cur.execute("SELECT latitude, longitude FROM JobLocations")
# coords = cur.fetchall()

# m = folium.Map(location=[39.5, -98.35], zoom_start=4)
# HeatMap(coords).add_to(m)
# m.save("job_heatmap.html")
# print("✅ Heat map saved as job_heatmap.html")

# # Add header/description
# with open("job_heatmap.html", "r") as f:
#     soup = BeautifulSoup(f, "html.parser")

# header = soup.new_tag("h1")
# header.string = "📍 USA Jobs Heatmap"
# soup.body.insert(0, header)

# desc = soup.new_tag("p")
# desc.string = "This interactive map shows the density of job locations across the US."
# soup.body.insert(1, desc)

# with open("custom_heatmap.html", "w") as f:
#     f.write(str(soup))

# print("✅ Custom HTML saved as custom_heatmap.html")

# # Bar Chart
# states = [r[0] for r in results]
# counts = [r[1] for r in results]

# plt.figure(figsize=(12,6))
# plt.bar(states, counts, color='skyblue', edgecolor='black')
# plt.xticks(rotation=45, ha='right')
# plt.title("📊 Number of Jobs per State")
# plt.tight_layout()
# plt.savefig("jobs_per_state.png")
# plt.show()
# print("✅ Bar chart saved as jobs_per_state.png")

import sqlite3
import requests
import re
from collections import Counter
import folium
from folium.plugins import HeatMap
import matplotlib.pyplot as plt

# Mapbox Token (Replace with your own)
mapbox_token = 'pk.eyJ1IjoiY2VpbGluZSIsImEiOiJjbTkwNGZobnIwanRtMmpwb3dvZTRyMTB4In0.-C6PmulyXbGp8FsLOIuTYw'

# Connect to final database
conn = sqlite3.connect("usajobs.db") 
cur = conn.cursor()

# --- STEP 1: Create tables ---
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
    # Column already exists
    pass

conn.commit()

# --- STEP 2: Function to get coordinates ---
def get_coordinates(address):
    try:
        url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{address}.json?access_token={mapbox_token}"
        response = requests.get(url)
        data = response.json()
        if data["features"]:
            coords = data["features"][0]["center"]
            return coords[1], coords[0]  # lat, lon
    except Exception as e:
        print(f"❌ Error fetching coords for {address}: {e}")
    return None

cur.execute('''
    SELECT id, title, organization, location FROM Jobs
    WHERE id NOT IN (SELECT job_id FROM Coordinates)
''')
jobs_to_add = cur.fetchall()


# --- STEP 5: Add max 25 jobs per run ---
# Ensure that max_number is fetched before the loop starts
cur.execute("SELECT MAX(number) FROM Jobs")
max_number = cur.fetchone()[0] or 0

# Insert up to 25 new jobs
inserted = 0
for job in jobs_to_add[:25]:  # Slice to max 25
    job_id, title, org, location = job
    coords = get_coordinates(location)
    if coords:
        lat, lon = coords
        try:
            # Insert coordinates linked to the job
            cur.execute("INSERT INTO Coordinates (job_id, latitude, longitude) VALUES (?, ?, ?)", (job_id, lat, lon))
            conn.commit()
            print(f"✅ Inserted coordinates for: {title} | {location} → ({lat}, {lon})")
        except Exception as e:
            print(f"⚠️ Skipped {location}: {e}")

# --- STEP 6: Process data - Job counts per state ---
cur.execute("SELECT location FROM Jobs")
locations = [row[0] for row in cur.fetchall()]

def extract_state(location):
    match = re.search(r',\s*([^,]+)$', location)
    if match:
        return match.group(1).strip()
    return None

states = [extract_state(loc) for loc in locations if extract_state(loc)]
state_counts = Counter(states)

# --- STEP 7: Join query to include Coordinates ---
cur.execute('''
    SELECT J.location, COUNT(*) 
    FROM Jobs J 
    JOIN Coordinates C ON J.id = C.job_id 
    GROUP BY J.location
''')
joined_results = cur.fetchall()

joined_states = []
for loc, count in joined_results:
    state = extract_state(loc)
    if state:
        joined_states.extend([state] * count)
joined_counts = Counter(joined_states)

# --- STEP 8: Save combined stats to text ---
with open("state_job_counts_combined.txt", "w") as f:
    f.write("State\tTotal_Jobs\tJobs_With_Coordinates\n")
    all_states = set(state_counts.keys()).union(joined_counts.keys())
    for state in sorted(all_states):
        f.write(f"{state}\t{state_counts[state]}\t{joined_counts[state]}\n")
print("📝 Saved job count summary to state_job_counts_combined.txt")

# --- STEP 9: Heatmap of job coordinates ---
cur.execute("SELECT latitude, longitude FROM Coordinates")
coords = cur.fetchall()
if coords:
    m = folium.Map(location=[39.5, -98.35], zoom_start=4)
    HeatMap(coords).add_to(m)
    m.save("job_heatmap.html")
    print("🗺️ Heatmap saved to job_heatmap.html")

# --- STEP 10: Visualizations with Matplotlib ---
# Visualization 1: Total Jobs per State (Bar Chart)
plt.figure(figsize=(10, 6))
plt.bar(state_counts.keys(), state_counts.values(), color='skyblue')
plt.xticks(rotation=45, ha='right')
plt.title("Total Jobs per State")
plt.tight_layout()
plt.savefig("jobs_per_state.png")
print("📊 Bar chart saved to jobs_per_state.png")

# Visualization 2: Jobs with Coordinates per State (Bar Chart)
plt.figure(figsize=(10, 6))
plt.bar(joined_counts.keys(), joined_counts.values(), color='salmon')
plt.xticks(rotation=45, ha='right')
plt.title("Jobs With Coordinates per State")
plt.tight_layout()
plt.savefig("jobs_with_coords_per_state.png")
print("📊 Bar chart saved to jobs_with_coords_per_state.png")

conn.close()
