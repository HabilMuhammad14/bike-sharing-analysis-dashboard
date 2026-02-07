import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
import matplotlib.ticker as ticker
sns.set(style='dark')


# Helper function
def create_daily_rentals_df(df):
    daily_rentals_df = df.resample(rule='D', on='dteday').agg({
        "cnt": "sum"
    })
    daily_rentals_df = daily_rentals_df.reset_index()
    daily_rentals_df.rename(columns={
        "cnt": "total_rentals"
    }, inplace=True)
    
    return daily_rentals_df

def create_monthly_rentals_df(df):
    monthly_rentals_df = df.groupby(df['dteday'].dt.to_period('M')).agg({
        "cnt": "sum"
    })
    monthly_rentals_df.index = monthly_rentals_df.index.to_timestamp()
    monthly_rentals_df = monthly_rentals_df.reset_index()
    monthly_rentals_df.rename(columns={
        "cnt": "total_rentals"
    }, inplace=True)
    
    return monthly_rentals_df

def create_season_rentals_df(df):
    season_rentals_df = df.groupby("season").agg({
        "cnt": "mean"
    }).reset_index()
    season_map = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
    season_rentals_df['season_name'] = season_rentals_df['season'].map(season_map)
    
    return season_rentals_df

# Load data
all_df = pd.read_csv("day.csv")

all_df['dteday'] = pd.to_datetime(all_df['dteday'])

all_df.sort_values(by="dteday", inplace=True)
all_df.reset_index(drop=True, inplace=True)



# Filter berdasarkan tanggal
min_date = all_df["dteday"].min()
max_date = all_df["dteday"].max()

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2972/2972185.png")
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["dteday"] >= str(start_date)) & 
                 (all_df["dteday"] <= str(end_date))]

daily_rentals_df = create_daily_rentals_df(main_df)
monthly_rentals_df = create_monthly_rentals_df(main_df)
season_rentals_df = create_season_rentals_df(main_df)


# Header Dashboard
st.header('Bike Sharing Dashboard :sparkles:')

st.subheader('Daily Rentals')

col1, col2, col3 = st.columns(3)

with col1:
    total_rentals = main_df['cnt'].sum()
    st.metric("Total Rentals", value=total_rentals)

with col2:
    total_casual = main_df['casual'].sum() 
    st.metric("Casual Users", value=total_casual)

with col3:
    total_registered = main_df['registered'].sum()
    st.metric("Registered Users", value=total_registered)


# Pertanyaan 1: Tren pertumbuhan 2011 vs 2012
st.subheader('Bike Rental Growth: 2011 vs 2012')

yearly_rentals = main_df.groupby(main_df['dteday'].dt.year).agg({
    'cnt': 'sum'
}).reset_index()
yearly_rentals.columns = ['year', 'total_rentals']

fig, ax = plt.subplots(figsize=(10, 5))
colors = ["#72BCD4", "#D3D3D3"]

ax.bar(yearly_rentals['year'], yearly_rentals['total_rentals'], color=colors)
ax.set_title('Total Bike Rentals: 2011 vs 2012', fontsize=20)
ax.set_xlabel('Year', fontsize=15)
ax.set_ylabel('Total Rentals', fontsize=15)
ax.tick_params(axis='x', labelsize=12)
ax.tick_params(axis='y', labelsize=12)

ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))

for i, v in enumerate(yearly_rentals['total_rentals']):
    ax.text(yearly_rentals['year'].iloc[i], v, f'{v:,.0f}',  
            ha='center', va='bottom', fontsize=12)  

st.pyplot(fig)

st.subheader('Monthly Rental Trends')

fig, ax = plt.subplots(figsize=(12, 6))
monthly_rentals_df['month'] = pd.to_datetime(monthly_rentals_df['dteday']).dt.month
monthly_rentals_df['year'] = pd.to_datetime(monthly_rentals_df['dteday']).dt.year

for year in monthly_rentals_df['year'].unique():
    data = monthly_rentals_df[monthly_rentals_df['year'] == year]
    ax.plot(data['month'], data['total_rentals'], marker='o', linewidth=2, label=f'Year {year}')

ax.set_title('Monthly Bike Rental Trends', fontsize=20)
ax.set_xlabel('Month', fontsize=15)
ax.set_ylabel('Total Rentals', fontsize=15)
ax.legend(fontsize=12)
ax.grid(True, alpha=0.3)
plt.xticks(range(1, 13))

st.pyplot(fig)

# Pertanyaan 2: Bulan dengan peminjaman tertinggi dan terendah + faktor cuaca
st.subheader('Monthly Rentals & Weather Factors')

monthly_avg = main_df.groupby(main_df['dteday'].dt.month).agg({
    'cnt': 'mean',
    'temp': 'mean',
    'hum': 'mean',
    'windspeed': 'mean'
}).reset_index()
monthly_avg.columns = ['month', 'avg_rentals', 'avg_temp', 'avg_hum', 'avg_windspeed']

fig, ax = plt.subplots(figsize=(12, 6))
colors_month = ['#72BCD4' if x == monthly_avg['avg_rentals'].max() else '#D3D3D3' if x == monthly_avg['avg_rentals'].min() else '#90CAF9' for x in monthly_avg['avg_rentals']]

ax.bar(monthly_avg['month'], monthly_avg['avg_rentals'], color=colors_month)
ax.set_title('Average Bike Rentals by Month', fontsize=20)
ax.set_xlabel('Month', fontsize=15)
ax.set_ylabel('Average Rentals', fontsize=15)
ax.tick_params(axis='x', labelsize=12)
ax.tick_params(axis='y', labelsize=12)

st.pyplot(fig)

st.subheader('Weather Impact on Bike Rentals')

fig, axes = plt.subplots(2, 2, figsize=(15, 10))
fig.suptitle('Weather Factors Impact on Bike Rentals', fontsize=20)

axes[0, 0].scatter(main_df['temp'], main_df['cnt'], alpha=0.5, color='#72BCD4')
axes[0, 0].set_xlabel('Temperature (normalized)', fontsize=12)
axes[0, 0].set_ylabel('Total Rentals', fontsize=12)
axes[0, 0].set_title('Temperature vs Rentals', fontsize=14)
axes[0, 0].grid(True, alpha=0.3)

axes[0, 1].scatter(main_df['hum'], main_df['cnt'], alpha=0.5, color='#90CAF9')
axes[0, 1].set_xlabel('Humidity (normalized)', fontsize=12)
axes[0, 1].set_ylabel('Total Rentals', fontsize=12)
axes[0, 1].set_title('Humidity vs Rentals', fontsize=14)
axes[0, 1].grid(True, alpha=0.3)

axes[1, 0].scatter(main_df['windspeed'], main_df['cnt'], alpha=0.5, color='#64B5F6')
axes[1, 0].set_xlabel('Wind Speed (normalized)', fontsize=12)
axes[1, 0].set_ylabel('Total Rentals', fontsize=12)
axes[1, 0].set_title('Wind Speed vs Rentals', fontsize=14)
axes[1, 0].grid(True, alpha=0.3)

axes[1, 1].scatter(main_df['weathersit'], main_df['cnt'], alpha=0.5, color='#42A5F5')
axes[1, 1].set_xlabel('Weather Situation', fontsize=12)
axes[1, 1].set_ylabel('Total Rentals', fontsize=12)
axes[1, 1].set_title('Weather Situation vs Rentals', fontsize=14)
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
st.pyplot(fig)

st.subheader('Seasonal Rentals')

fig, ax = plt.subplots(figsize=(10, 6))
colors_season = ["#72BCD4", "#90CAF9", "#64B5F6", "#42A5F5"]

season_data = season_rentals_df.sort_values('cnt', ascending=False)
ax.bar(season_data['season_name'], season_data['cnt'], color=colors_season)
ax.set_title('Average Bike Rentals by Season', fontsize=20)
ax.set_xlabel('Season', fontsize=15)
ax.set_ylabel('Average Rentals', fontsize=15)
ax.tick_params(axis='x', labelsize=12)
ax.tick_params(axis='y', labelsize=12)

st.pyplot(fig)

st.caption('Copyright © Bike Sharing Dashboard 2024')
