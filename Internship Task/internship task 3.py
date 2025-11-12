import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Load the dataset
df = pd.read_csv("Play Store Data.csv")

# Clean and convert relevant columns
df['Installs'] = df['Installs'].astype(str).str.replace('[+,]', '', regex=True)
df = df[df['Installs'].str.isnumeric()]
df['Installs'] = df['Installs'].astype(float)

df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
df['Size'] = df['Size'].astype(str).str.replace('M', '').replace('Varies with device', None)
df['Size'] = pd.to_numeric(df['Size'], errors='coerce')
df['Android Ver'] = df['Android Ver'].astype(str).str.extract('(\d+\.\d+)')
df['Android Ver'] = pd.to_numeric(df['Android Ver'], errors='coerce')
df['App'] = df['App'].astype(str)
df['Content Rating'] = df['Content Rating'].astype(str)

# Calculate revenue for paid apps
df['Revenue'] = df.apply(lambda x: x['Price'] * x['Installs'] if x['Type'] == 'Paid' else 0, axis=1)

# Apply filters
filtered_df = df[
    (df['Installs'] >= 10000) &
    (df['Revenue'] >= 10000) &
    (df['Android Ver'] > 4.0) &
    (df['Size'] > 15) &
    (df['Content Rating'] == 'Everyone') &
    (df['App'].str.len() <= 30)
]

# Identify top 3 categories by total installs
top_categories = filtered_df.groupby('Category')['Installs'].sum().sort_values(ascending=False).head(3).index
top_df = filtered_df[filtered_df['Category'].isin(top_categories)]

# Aggregate average installs and revenue by category and type
agg_df = top_df.groupby(['Category', 'Type']).agg({
    'Installs': 'mean',
    'Revenue': 'mean'
}).reset_index()

# Time-based visibility control
current_hour = datetime.now().hour
if 13 <= current_hour < 14:
    fig = go.Figure()

    for app_type in ['Free', 'Paid']:
        sub_df = agg_df[agg_df['Type'] == app_type]
        fig.add_trace(go.Bar(x=sub_df['Category'], y=sub_df['Installs'],
                             name=f'{app_type} Apps - Installs', yaxis='y1'))
        fig.add_trace(go.Scatter(x=sub_df['Category'], y=sub_df['Revenue'],
                                 name=f'{app_type} Apps - Revenue', yaxis='y2', mode='lines+markers'))

    fig.update_layout(
        title='Average Installs vs Revenue for Free vs Paid Apps (Top 3 Categories)',
        xaxis=dict(title='App Category'),
        yaxis=dict(title='Average Installs', side='left'),
        yaxis2=dict(title='Average Revenue', overlaying='y', side='right'),
        barmode='group'
    )
    fig.show()
else:
    print("⏳ This chart is only visible between 1PM and 2PM IST.")
