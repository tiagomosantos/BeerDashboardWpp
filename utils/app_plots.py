import streamlit as st
import pandas as pd
import plotly.express as px
import emoji
import os
from typing import Tuple

# Dictionary that maps textual descriptions of drink sizes to their respective emoji.
EMOJI_MAPPING = {'mini': '🍺', 'média': '🍻', 'litrosa': '🍾', 'vinho': '🍷'}


# Function to calculate key statistics like total volume, average daily consumption, top consumer, and favorite beer.
def calculate_stats(df: pd.DataFrame) -> Tuple[float, float, str, str]:
    total_volume = df['Quantidade (L)'].sum()
    avg_daily_consumption = df.groupby('Date')['Quantidade (L)'].sum().mean()
    top_consumer = df.groupby('Pessoa')['Quantidade (L)'].sum().idxmax()
    favorite_beer = df['Emoji'].mode().values[0]
    return total_volume, avg_daily_consumption, top_consumer, favorite_beer


# Function to display key metrics in the dashboard, using Streamlit's metric widgets.
def display_key_metrics(total_volume: float, avg_daily_consumption: float, top_consumer: str, favorite_beer: str):
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Consumo Total" + emoji.emojize(':fuel_pump:'), f"{total_volume:.2f}L")
    col2.metric("Média de Consumo Diária" + emoji.emojize(':stopwatch:'), f"{avg_daily_consumption:.2f}L")
    col3.metric("Principal Consumidor " + emoji.emojize(':trophy:'), top_consumer)
    col4.metric("Cerveja Favorita" + emoji.emojize(':sports_medal:'), favorite_beer)


# Function to display the latest updates (last 5 entries) in the dashboard.
def display_latest_news(df: pd.DataFrame):
    last_records = df.tail(5)[::-1]
    for _, row in last_records.iterrows():
        with st.container():
            cols = st.columns([1, 25])
            with cols[0]:
                image_name = f"{row['Pessoa']}.png"
                image_path = os.path.join('circular_profile_images', image_name)
                st.image(image_path, width=50)
            with cols[1]:
                emoji_ = EMOJI_MAPPING[row['Emoji'].lower()]
                message = f"[{row['Hour']}] {row['Pessoa']} bebeu uma {row['Emoji'].lower()}" + emoji_
                st.markdown(f'<div class="log-text">{message}</div>', unsafe_allow_html=True)


# Function to create a bar plot for total consumption by person.
def plot_total_consumption(df: pd.DataFrame, quantity_filter: str):
    total_consumption = df.groupby('Pessoa')[quantity_filter].sum().sort_values(ascending=False).reset_index()
    
    if quantity_filter == 'Quantidade (L)':
        y_axis = 'Consumo Total (L)'
    else:
        y_axis = 'Número de Cervejas'

    fig_total = px.bar(total_consumption, x='Pessoa', y=quantity_filter, labels={quantity_filter: y_axis})
    
    fig_total.update_layout(height=500)
    st.plotly_chart(fig_total, use_container_width=True)


# Function to create a bar plot for consumption by beer type (emoji).
def plot_consumption_by_type(df: pd.DataFrame, value_col: str):
    emoji_consumption = df.groupby('Emoji')[value_col].sum().reset_index()
    
    if value_col == 'Quantidade (L)':
        y_axis = 'Consumo Total (L)'
    else:
        y_axis = 'Número de Cervejas'

    fig_emoji = px.bar(emoji_consumption, x='Emoji', y=value_col, hover_data=[value_col], labels={y_axis: y_axis})
    fig_emoji.update_layout(xaxis_title='Emoji', yaxis_title=y_axis, uniformtext_minsize=8, uniformtext_mode='hide')
    
    st.plotly_chart(fig_emoji, use_container_width=True)


# Function to plot the weekly consumption pattern (grouping by day of the week).
def weekly_consumption_pattern(df, quantity_filter):
    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
    df['Day'] = df['Date'].dt.day_name()

    # Map the day names from English to Portuguese.
    df['Day'] = df['Day'].map({'Monday': 'Segunda', 'Tuesday': 'Terça', 'Wednesday': 'Quarta', 'Thursday': 'Quinta', 'Friday': 'Sexta', 'Saturday': 'Sábado', 'Sunday': 'Domingo'})
    
    weekly_consumption = df.groupby('Day')[quantity_filter].sum().reindex(['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo'])
    
    if quantity_filter == 'Quantidade (L)':
        y_axis = 'Consumo Total (L)'
    else:
        y_axis = 'Número de Cervejas'

    fig = px.bar(x=weekly_consumption.index, y=weekly_consumption.values, labels={'x': 'Dia da Semana', 'y': y_axis})
    
    st.plotly_chart(fig, use_container_width=True)


# Function to plot the hourly consumption pattern (grouping by hour of the day).
def hourly_consumption_pattern(df, quantity_filter):
    df['Hora'] = df['Hour'].apply(lambda x: x.split(':')[0])
    df['Hora'] = df['Hora'].astype(int)

    hourly_consumption = df.groupby('Hora')[quantity_filter].sum().reset_index()

    # Ensure all hours from 0 to 23 are included, even if there's no data.
    all_hours = pd.DataFrame({'Hora': range(24)})
    hourly_consumption = pd.merge(all_hours, hourly_consumption, on='Hora', how='left')

    hourly_consumption[quantity_filter].fillna(0, inplace=True)

    fig = px.line(hourly_consumption, x='Hora', y=quantity_filter)

    if quantity_filter == 'Quantidade (L)':
        y_axis = 'Consumo Total (L)'
    else:
        y_axis = 'Número de Cervejas'

    fig.update_layout(xaxis_title='Hora do Dia', yaxis_title=y_axis)
    fig.update_xaxes(tickmode='linear', tick0=0, dtick=1)
    fig.update_xaxes(tickvals=list(range(24)), ticktext=[f'{h:02d}:00' for h in range(24)])

    st.plotly_chart(fig, use_container_width=True)
