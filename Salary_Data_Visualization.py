import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

#here are our import statements so we can actually make the plots 

# This line connects to the SQL database
conn = sqlite3.connect("usajobs.db")
query = """
SELECT salary_min, salary_max
FROM Jobs
WHERE salary_min IS NOT NULL AND salary_max IS NOT NULL
"""

#this part only grabs jobs where it shows us both the minimum and max salaries, 
#so our data looks more complete. 


df = pd.read_sql_query(query, conn)
conn.close()



#here is where we actually make the plot by setting up a blank canvas of
# 6 in. by 8 in. 
plt.figure(figsize=(8, 6))
#this part plots the data
plt.scatter(df['salary_min'], df['salary_max'], alpha=0.6, color='purple')
#these lines label the plot so it is clear what the plot is showing 
plt.title('Minimum vs Maximum Salary')
plt.xlabel('Minimum Salary ($)')
plt.ylabel('Maximum Salary ($)')
#plt.grid(True) helps to add a background 
plt.grid(True)
plt.tight_layout()
plt.savefig("min_vs_max_salary.png")
#displays the plot 
plt.show()