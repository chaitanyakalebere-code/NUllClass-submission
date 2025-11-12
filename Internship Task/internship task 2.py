import pandas as pd
import plotly.express as px
from datetime import datetime

# Load the dataset
df = pd.read_csv("Play Store Data.csv")

# Clean and convert relevant columns
df['Installs'] = df['Installs'].astype(str).str.replace('[+,]', '', regex=True)
df = df[df['Installs'].str.isnumeric()]
df['Installs'] = df['Installs'].astype(float)
df['Category'] = df['Category'].astype(str)

# Filter out categories starting with A, C, G, S
df = df[~df['Category'].str.startswith(tuple("ACGS"))]

# Aggregate installs by category
category_installs = df.groupby('Category')['Installs'].sum().reset_index()

# Select top 5 categories by installs
top_categories = category_installs.sort_values(by='Installs', ascending=False).head(5)

# Assign dummy country codes for visualization (since actual country data is missing)
top_categories['Country'] = ['USA', 'IND', 'BRA', 'DEU', 'FRA']  # Replace with actual if available

# Highlight categories with installs > 1 million
top_categories['Highlight'] = top_categories['Installs'].apply(lambda x: 'Yes' if x > 1_000_000 else 'No')

# Time-based visibility control
current_hour = datetime.now().hour
if 18 <= current_hour < 20:
    fig = px.choropleth(top_categories,
                        locations='Country',
                        locationmode='ISO-3',
                        color='Installs',
                        hover_name='Category',
                        title='Global Installs by App Category (Filtered)',
                        color_continuous_scale='Viridis')
    fig.show()
else:
    print("⏳ This map is only visible between 6PM and 8PM IST.")
