import sqlite3
import matplotlib.pyplot as plt

# Connect to the database
conn = sqlite3.connect('usajobs.db')
cur = conn.cursor()

# Query to get average salary per location
cur.execute('''
    SELECT L.location, AVG(J.salary_min), AVG(J.salary_max)
    FROM Jobs J
    JOIN Locations L ON J.location_id = L.id
    GROUP BY J.location_id
    ORDER BY AVG(J.salary_min) DESC
    LIMIT 10
''')

rows = cur.fetchall()
conn.close()

# Extract data for plotting
locations = [row[0] for row in rows]
avg_salary_min = [row[1] for row in rows]
avg_salary_max = [row[2] for row in rows]

# Plotting
x = range(len(locations))
bar_width = 0.4

plt.figure(figsize=(12, 6))
plt.bar(x, avg_salary_min, width=bar_width, label='Avg Min Salary', color='#FFC0CB')
plt.bar([i + bar_width for i in x], avg_salary_max, width=bar_width, label='Avg Max Salary', color='#FF69B4')

# Add labels and title
plt.xlabel('Location')
plt.ylabel('Salary (USD)')
plt.title('Average Min and Max Salaries by Location')
plt.xticks([i + bar_width / 2 for i in x], locations, rotation=45, ha='right')
plt.legend()
plt.tight_layout()
plt.grid(axis='y', linestyle='--', alpha=0.6)

# Show the chart
plt.show()
