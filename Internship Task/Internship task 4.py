import pandas as pd
import plotly.express as px
import datetime

# Load dataset
apps_df = pd.read_csv("Play Store Data.csv")

# -----------------------------
# Convert numeric columns
# -----------------------------
# Reviews → integer
apps_df['Reviews'] = pd.to_numeric(apps_df['Reviews'], errors='coerce')

# Installs → integer (remove commas and + signs first)
apps_df['Installs'] = apps_df['Installs'].str.replace('[+,]', '', regex=True)
apps_df['Installs'] = pd.to_numeric(apps_df['Installs'], errors='coerce')

# Size → MB (convert 'M' to numeric, handle 'k' or 'Varies with device')
def size_to_mb(x):
    if isinstance(x, str):
        if 'M' in x:
            return float(x.replace('M',''))
        elif 'k' in x:
            return float(x.replace('k',''))/1024
        else:
            return None
    return x

apps_df['Size'] = apps_df['Size'].apply(size_to_mb)

# -----------------------------
# Apply filters
# -----------------------------
filtered_df = apps_df[
    (apps_df['Reviews'] > 500) &
    (~apps_df['App'].str.startswith(('x','y','z','X','Y','Z'))) &
    (~apps_df['App'].str.contains('S')) &
    (apps_df['Category'].str.startswith(('E','C','B')))
].copy()

# Translate categories
category_map = {
    'Beauty': 'सौंदर्य',        # Hindi
    'Business': 'வணிகம்',       # Tamil
    'Dating': 'Dating (Deutsch)' # German
}
filtered_df['Category'] = filtered_df['Category'].replace(category_map)

# Convert Last Updated to datetime
filtered_df['Last Updated'] = pd.to_datetime(filtered_df['Last Updated'], errors='coerce')

# Group by month and category
filtered_df['Month'] = filtered_df['Last Updated'].dt.to_period('M')
installs_by_month = (
    filtered_df.groupby(['Month','Category'])['Installs']
    .sum()
    .reset_index()
)
installs_by_month['Month'] = installs_by_month['Month'].dt.to_timestamp()

# Calculate month-over-month growth
installs_by_month['Growth'] = installs_by_month.groupby('Category')['Installs'].pct_change()

# -----------------------------
# Time restriction: 6–9 PM IST
# -----------------------------
current_time = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5,minutes=30)))

if 18 <= current_time.hour < 21:
    fig = px.line(
        installs_by_month,
        x='Month',
        y='Installs',
        color='Category',
        title='Total Installs Trend by Category'
    )

    # Highlight growth > 20%
    for category in installs_by_month['Category'].unique():
        cat_data = installs_by_month[installs_by_month['Category'] == category]
        growth_periods = cat_data[cat_data['Growth'] > 0.2]
        for _, row in growth_periods.iterrows():
            fig.add_vrect(
                x0=row['Month'] - pd.DateOffset(days=15),
                x1=row['Month'] + pd.DateOffset(days=15),
                fillcolor="lightblue",
                opacity=0.3,
                line_width=0
            )

    fig.show()
else:
    print("Chart is not displayed outside 6 PM - 9 PM IST window.")
