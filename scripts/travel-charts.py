import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

paths = {
    "schools":    os.path.join(root, "england_secondary_schools.parquet"),
    "travel_time":os.path.join(root, "data", "lsoa_travel_times.parquet"),
    "nts_9908":   os.path.join(root, "data", "nts9908.ods"),
    "output":     os.path.join(root, "outputs", "commuter_behavior_report.csv"),
    "gla":        os.path.join(root, "data", "London_GLA_Boundary.shp"),
    "outputs":    os.path.join(root, "outputs"),
    "charts":     os.path.join(root, "outputs", "charts"),
}

df_raw = pd.read_parquet(paths["schools"])

open_schools = df_raw[
    (df_raw['gor_name'] == 'London') & 
    (df_raw['establishment_status'] == 'Open')
].copy()

# Create the 'borough_short' column as per your original code
open_schools['borough_short'] = open_schools['la_name'].str.replace(
    r"London Borough of |Royal Borough of |City of ", "", regex=True
)

# Aggregate: Count schools per borough and take the Top 10
la_counts = (
    open_schools['borough_short']
    .value_counts()
    .head(10)
    .reset_index()
)
la_counts.columns = ['borough_short', 'school_count']

# Generate the simplified chart
plt.figure(figsize=(10, 6))
sns.set_style("whitegrid")

# Create a simple horizontal bar chart
ax = sns.barplot(
    data=la_counts, 
    x='school_count', 
    y='borough_short', 
    color='#3498db' # Simple blue color
)

# Formatting to match your requested title and style
plt.title('Secondary schools per borough — top 10', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Number of Schools', fontsize=11)
plt.ylabel('Borough', fontsize=11)

# Add numeric labels to the end of each bar
for i, count in enumerate(la_counts['school_count']):
    plt.text(count + 0.3, i, str(int(count)), va='center', fontsize=10, fontweight='bold')

sns.despine() # Removes top and right borders for a cleaner look
plt.tight_layout()
plt.show()