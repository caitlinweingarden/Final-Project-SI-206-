import sqlite3
import matplotlib.pyplot as plt
from collections import Counter
import folium
from folium.plugins import HeatMap
import re

# Connect to the existing database
conn = sqlite3.connect("usajobs.db")
cur = conn.cursor()

cur.execute("SELECT latitude, longitude FROM Coordinates")
coords = cur.fetchall()

if coords:
    heat_map = folium.Map(location=[39.5, -98.35], zoom_start=4)
    HeatMap(coords).add_to(heat_map)
    heat_map.save("job_heatmap.html")
    print("🗺️ Heatmap saved to job_heatmap.html")

def extract_state(location):
    import re
    match = re.search(r',\s*([^,]+)$', location)
    if match:
        return match.group(1).strip()
    return None

cur.execute('''
    SELECT Locations.location, COUNT(*) 
    FROM Jobs J
    JOIN Coordinates C ON J.id = C.job_id
    JOIN Locations ON J.location_id = Locations.id
    GROUP BY Locations.location
''')
joined_results = cur.fetchall()

joined_states = []
for loc, count in joined_results:
    state = extract_state(loc)
    if state:
        joined_states.extend([state] * count)

joined_counts = Counter(joined_states)

# Bar chart
plt.figure(figsize=(12, 6))
sorted_states = sorted(joined_counts.items(), key=lambda x: x[1], reverse=True)
states, counts = zip(*sorted_states)

plt.bar(states, counts, color='teal')
plt.xticks(rotation=45, ha='right')
plt.title("Jobs With Coordinates per State")
plt.ylabel("Number of Jobs")
plt.tight_layout()
plt.savefig("jobs_with_coords_per_state.png")

# Show the chart
plt.show()
print("Bar chart saved to jobs_with_coords_per_state.png")