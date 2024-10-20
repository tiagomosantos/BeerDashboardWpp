import streamlit as st
import pandas as pd
import os
from typing import Tuple, List
from datetime import date
from utils.update_data import update_chat_data
from utils.google_api import authenticate, get_file_id_by_name, get_latest_file
from utils.data_extraction import load_data, delete_all_files_in_folder
from utils.app_plots import calculate_stats, display_key_metrics, display_latest_news, plot_total_consumption, weekly_consumption_pattern, plot_consumption_by_type, hourly_consumption_pattern

def set_page_config_():
    # Set the configuration for the Streamlit app, including the page title, icon, and layout.
    st.set_page_config(page_title="Petiscos (Contabilidade)", page_icon="circular_profile_images/logo.png", layout="wide")

    # Custom CSS for styling the Streamlit app UI elements (background, padding, fonts, etc.)
    st.markdown("""
        <style>
        .reportview-container { background: #f0f2f6; }
        .main > div { padding-top: 2rem; }
        h1, h2, h3 { color: #1E3A8A; }
        .stApp { font-family: 'Helvetica', sans-serif; }
        .stMetric { background-color: #FFFFFF; border-radius: 5px; padding: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stImage > img { width: 0px; height: 0px; object-fit: cover; border-radius: 50%; margin-right: 0px; }
        .log-entry { display: flex; align-items: center; padding: 5px 0; background-color: #FFFFFF; border-radius: 5px; margin-bottom: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .log-text { font-size: 16px; font-weight: 20; display: flex; height: 50px; }
        .element-container { margin-bottom: -10px; }
        @media (max-width: 768px) { .stMetric { font-size: 12px; } .stImage > img { width: 30px; height: 30px; } .log-text { font-size: 14px; } }
        </style>
    """, unsafe_allow_html=True)


# Function to filter the data based on user-selected filters (date range, people, emojis, and quantity).
def filter_data(df: pd.DataFrame, date_range: Tuple[date, date], people_filter: List[str], emoji_filter: List[str], quantity_filter: List[str]) -> pd.DataFrame:
    # Filter by date range.
    mask = (pd.to_datetime(df['Date'], format='%d/%m/%Y').dt.date >= date_range[0]) & \
           (pd.to_datetime(df['Date'], format='%d/%m/%Y').dt.date <= date_range[1])
    filtered_df = df[mask]
    
    # Filter by selected people, emojis, and quantity type (liters or number of beers).
    if people_filter:
        filtered_df = filtered_df[filtered_df['Pessoa'].isin(people_filter)]
    if emoji_filter:
        filtered_df = filtered_df[filtered_df['Emoji'].isin(emoji_filter)]
    if quantity_filter:
        if quantity_filter == 'Quantidade (L)':
            filtered_df['Value_Col'] = filtered_df['Quantidade (L)']
        else:
            filtered_df['Value_Col'] = filtered_df['Quantidade']

    return filtered_df


# Function to create a table of contents for the dashboard sections.
def create_table_of_contents():
    st.header("Opções de Visualização")
    st.markdown("""
    - [Consumo por Pessoa](#consumo-por-pessoa)
    - [Consumo por Dia da Semana](#consumo-por-dia-da-semana)
    - [Consumo por Tipo de Cerveja](#consumo-por-tipo-de-cerveja)
    - [Consumo por Hora](#consumo-por-hora)
    """)


# Function to update the dashboard with the latest data and display it.
def update_dashboard(file_path: str, dashboard_placeholder: st.empty):
    df = load_data(file_path)
    df['Value_Col'] = df['Quantidade (L)']

    # Sidebar Filters
    st.sidebar.header('Filtros')
    df_date = pd.to_datetime(df['Date'], format='%d/%m/%Y')

    # Date range filter.
    date_range = st.sidebar.date_input(
        'Selecionar Datas',
        value=(df_date.min(), df_date.max()),
        min_value=df_date.min(),
        max_value=df_date.max()
    )
    
    if len(date_range) < 2:
        date_range = (date_range[0], date_range[0])
    
    # People, emoji, and quantity filters.
    people_filter = st.sidebar.multiselect('Selecionar Pessoa', options=df['Pessoa'].unique())
    emoji_filter = st.sidebar.multiselect('Selecionar Emojis', options=df['Emoji'].unique())
    quantity_filter = st.sidebar.multiselect('Selecionar Quantidade', options=['Quantidade (L)', 'Número de Cervejas'])

    if date_range[0] > date_range[1]:
        st.sidebar.error("Erro: Data de início deve ser anterior à data de fim.")
        st.stop()
    
    filtered_df = filter_data(df, date_range, people_filter, emoji_filter, quantity_filter)
    total_volume, avg_daily_consumption, top_consumer, favorite_beer = calculate_stats(filtered_df)
    
    # Handle case when no quantity filter is selected.
    if quantity_filter == []:
        quantity_filter = ['Quantidade (L)']
    elif quantity_filter == ['Número de Cervejas']:
        quantity_filter = ['Quantidade']

    # Display the dashboard with filtered data and charts.
    with dashboard_placeholder.container():
        display_key_metrics(total_volume, avg_daily_consumption, top_consumer, favorite_beer)
        st.markdown("---")

        create_table_of_contents()
        st.markdown("---")
        
        st.header('Últimas Atualizações')
        display_latest_news(df)
        st.markdown("---")

        st.header('Consumo por Pessoa')
        plot_total_consumption(filtered_df, quantity_filter[0])
        st.markdown("---")
        
        st.header("Consumo por Dia da Semana")
        weekly_consumption_pattern(filtered_df, quantity_filter[0])
        st.markdown("---")
        
        st.header('Consumo por Tipo de Cerveja')
        plot_consumption_by_type(filtered_df, quantity_filter[0])
        st.markdown("---")

        st.header("Consumo por Hora")
        hourly_consumption_pattern(filtered_df, quantity_filter[0])
        st.markdown("---")


# Main function to initialize the app, authenticate, and manage data updates.
def main():
    data_folder = 'data'
    zip_file_name = 'chat_data.zip'
    txt_file_name = '_chat.txt'
    google_connection = False
    
    # Authenticate with Google API.
    if google_connection:
        service = authenticate()
    txt_file_path = os.path.join(data_folder, txt_file_name)
    
    # Set the page configuration and title.
    set_page_config_()
    st.title('Contabilidade 🍺')

    # Create a placeholder for dynamically updating the dashboard.
    dashboard_placeholder = st.empty()
    
    # Sidebar button to manually trigger data updates.
    st.sidebar.header('Opções')
    if st.sidebar.button('Atualizar Dados'):
        with st.spinner('Atualizando dados...'):
            if google_connection:
                current_file_id = get_file_id_by_name(service, zip_file_name)
                latest_file_id = get_latest_file(service)
                if latest_file_id != current_file_id:
                    delete_all_files_in_folder(data_folder)
                    update_chat_data(service)
                    st.success('Dados atualizados com sucesso!')
                    st.experimental_rerun()
                else:
                    st.warning('Não há novos dados para atualizar.')
            else:
                pass
            
    # Update and display the dashboard with the latest data.
    update_dashboard(txt_file_path, dashboard_placeholder)

# Run the main function when the script is executed.
if __name__ == '__main__':
    main()
