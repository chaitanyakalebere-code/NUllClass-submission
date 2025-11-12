import pandas as pd
import plotly.express as px
from datetime import datetime

# Load the dataset
df = pd.read_csv("Play Store Data.csv")

# Ensure 'Installs' column is clean and numeric
if 'Installs' in df.columns:
    df['Installs'] = df['Installs'].astype(str).str.replace('[+,]', '', regex=True)
    df = df[df['Installs'].str.isnumeric()]
    df['Installs'] = df['Installs'].astype(float)

# Clean and convert other columns
df['Size'] = df['Size'].astype(str).str.replace('M', '').str.replace('k', '').replace('Varies with device', None)
df['Size'] = pd.to_numeric(df['Size'], errors='coerce')
df['Last Updated'] = pd.to_datetime(df['Last Updated'], errors='coerce')
df['Reviews'] = pd.to_numeric(df['Reviews'], errors='coerce')
df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')

# Apply filters
filtered_df = df[
    (df['Rating'] >= 4.0) &
    (df['Size'] >= 10) &
    (df['Last Updated'].dt.month == 1)
]

# Aggregate top 10 categories by installs
agg_df = filtered_df.groupby('Category').agg({
    'Rating': 'mean',
    'Reviews': 'sum',
    'Installs': 'sum'
}).sort_values(by='Installs', ascending=False).head(10).reset_index()

# Melt for grouped bar chart
melted_df = agg_df.melt(id_vars='Category', value_vars=['Rating', 'Reviews'],
                        var_name='Metric', value_name='Value')

# Time-based visibility control
current_hour = datetime.now().hour
if 15 <= current_hour < 17:
    fig = px.bar(melted_df, x='Category', y='Value', color='Metric',
                 barmode='group', title='Top 10 App Categories by Installs (Filtered)')
    fig.show()
else:
    print("⏳ This chart is only visible between 3PM and 5PM IST.")
