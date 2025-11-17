import pandas as pd
import plotly.express as px
import datetime

# Load datasets
apps_df = pd.read_csv("Play Store Data.csv")
reviews_df = pd.read_csv("User Reviews.csv")

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
# Merge with reviews for sentiment subjectivity
# -----------------------------
merged_df = pd.merge(apps_df, reviews_df[['App','Sentiment_Subjectivity']], on='App', how='inner')

# -----------------------------
# Apply filters
# -----------------------------
categories = ['Game','Beauty','Business','Comics','Communication','Dating','Entertainment','Social','Events']

filtered_df = merged_df[
    (merged_df['Rating'] > 3.5) &
    (merged_df['Category'].isin(categories)) &
    (merged_df['Reviews'] > 500) &
    (~merged_df['App'].str.contains('S')) &
    (merged_df['Sentiment_Subjectivity'] > 0.5) &
    (merged_df['Installs'] > 50000)
].copy()

# Translate categories
category_map = {
    'Beauty': 'सौंदर्य',        # Hindi
    'Business': 'வணிகம்',       # Tamil
    'Dating': 'Dating (Deutsch)' # German
}
filtered_df['Category'] = filtered_df['Category'].replace(category_map)

# -----------------------------
# Time restriction: 5–7 PM IST
# -----------------------------
current_time = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5,minutes=30)))

if 17 <= current_time.hour < 19:
    fig = px.scatter(
        filtered_df,
        x='Size',
        y='Rating',
        size='Installs',
        color='Category',
        title='Bubble Chart: App Size vs Rating (Bubble = Installs)',
        hover_name='App',
        size_max=60
    )

    # Highlight Game category in pink
    fig.for_each_trace(
        lambda trace: trace.update(marker=dict(color="pink")) if trace.name == "Game" else ()
    )

    fig.show()
else:
    print("Chart is not displayed outside 5 PM - 7 PM IST window.")
