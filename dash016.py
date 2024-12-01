import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
import altair as alt  # Import Altair for static charts

# Page configuration to hide the sidebar navigation by default
st.set_page_config(
    page_title="Dashboard de Inscrições do Edital",
    page_icon="📈",
    layout="wide",  # Keep 'wide' layout for customization
    initial_sidebar_state="collapsed"  # Collapse the sidebar
)

# Theme-aware CSS styles
st.markdown(
    """
    <style>
        /* Adjust the block container's width and padding */
        .block-container {
            max-width: 1000px; /* Set desired maximum width in pixels */
            padding-left: 1rem;
            padding-right: 1rem;
            margin: 0 auto; /* Center the content */
        }

        /* Center the banner */
        .centered-banner img {
            display: block;
            margin-left: auto;
            margin-right: auto;
        }

        /* Style headers to use theme colors */
        h1, h2, h3, h4, h5, h6 {
            color: var(--text-color);
        }

        /* Style the text input to match theme */
        .stTextInput input {
            background-color: var(--secondary-background-color);
            color: var(--text-color);
        }

        /* Style the AgGrid component */
        .ag-theme-material {
            max-width: 700px;
            margin: 0 auto;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Header - Center the banner
st.markdown(
    """
    <div class="centered-banner">
        <img src="https://i.postimg.cc/nhM4cdnw/banner6.png" alt="Banner" width="800">
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    "<h1 style='text-align: center; font-size: 24px;'>📈 Dashboard de Inscrições do Edital 027/2024 📈</h1>",
    unsafe_allow_html=True
)
st.markdown("---")

# Sidebar - only general settings
with st.sidebar:
    st.markdown("## Configurações")
    rows_per_page = st.selectbox('Linhas por página', options=[25, 50, 100], index=0)

# Função para carregar os dados da planilha
@st.cache_data(ttl=200)
def load_data(spreadsheet_id, sheet_name):
    try:
        csv_export_url = f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'
        df = pd.read_csv(csv_export_url)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar a aba '{sheet_name}': {e}")
        return pd.DataFrame()

# Spreadsheet ID
spreadsheet_id = '1AqbLEIwV_gsDwrw8nLYFq0M4t3LBw28X1dQCI86_Mrs'

# Load 'prof' and 'sup' sheets
df_prof = load_data(spreadsheet_id, 'dashprof')
df_sup = load_data(spreadsheet_id, 'dashsup')
df_ap = load_data(spreadsheet_id, 'dashap')

# Check if 'VAGA' and 'INSCRITOS' columns exist and sort DataFrames
if 'VAGA' in df_prof.columns and 'INSCRITOS' in df_prof.columns:
    df_prof = df_prof[['VAGA', 'INSCRITOS']].sort_values(by='INSCRITOS', ascending=False)
else:
    st.error("As colunas 'VAGA' e 'INSCRITOS' não foram encontradas na aba 'prof'.")

if 'VAGA' in df_sup.columns and 'INSCRITOS' in df_sup.columns:
    df_sup = df_sup[['VAGA', 'INSCRITOS']].sort_values(by='INSCRITOS', ascending=False)
else:
    st.error("As colunas 'VAGA' e 'INSCRITOS' não foram encontradas na aba 'sup'.")
if 'VAGA' in df_ap.columns and 'INSCRITOS' in df_ap.columns:
    df_ap = df_ap[['VAGA', 'INSCRITOS']].sort_values(by='INSCRITOS', ascending=False)
else:
    st.error("As colunas 'VAGA' e 'INSCRITOS' não foram encontradas na aba 'sup'.")

# Calculate total inscriptions
total_inscritos_prof = df_prof['INSCRITOS'].sum()
total_inscritos_sup = df_sup['INSCRITOS'].sum()
total_inscritos_ap = df_ap['INSCRITOS'].sum()

# DataFrame with totals
df_totals = pd.DataFrame({
    'Cargo': ['Professor', 'Supervisor', 'Apoio'],
    'Total de Inscrições': [total_inscritos_prof, total_inscritos_sup, total_inscritos_ap]
})

# Divide into columns for KPIs
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        "<h3 style='text-align: center; font-size: 20px;'>Total de Inscritos</h3>",
        unsafe_allow_html=True
    )
    total_inscritos = total_inscritos_prof + total_inscritos_sup
    st.markdown(
        f"<h1 style='text-align: center; font-size: 24px;'>{total_inscritos}</h1>",
        unsafe_allow_html=True
    )
with col2:
    st.markdown(
        "<h3 style='text-align: center; font-size: 20px;'>Inscritos - Professor</h3>",
        unsafe_allow_html=True
    )
    st.markdown(
        f"<h1 style='text-align: center; font-size: 24px;'>{total_inscritos_prof}</h1>",
        unsafe_allow_html=True
    )
with col3:
    st.markdown(
        "<h3 style='text-align: center; font-size: 20px;'>Inscritos - Supervisor</h3>",
        unsafe_allow_html=True
    )
    st.markdown(
        f"<h1 style='text-align: center; font-size: 24px;'>{total_inscritos_sup}</h1>",
        unsafe_allow_html=True
    )
with col4:
    st.markdown(
        "<h3 style='text-align: center; font-size: 20px;'>Inscritos - Apoio</h3>",
        unsafe_allow_html=True
    )
    st.markdown(
        f"<h1 style='text-align: center; font-size: 24px;'>{total_inscritos_ap}</h1>",
        unsafe_allow_html=True
    )

st.markdown("---")

# Center the Altair chart
st.markdown(
    "<h2 style='text-align: center;'>Distribuição de Inscrições por Cargo</h2>",
    unsafe_allow_html=True
)

# Define the 'chart'
chart = alt.Chart(df_totals).mark_bar().encode(
    x=alt.X('Cargo:N', axis=alt.Axis(labelFontSize=14, titleFontSize=16)),
    y=alt.Y('Total de Inscrições:Q', axis=alt.Axis(labelFontSize=14, titleFontSize=16)),
    color=alt.Color('Cargo:N', legend=None, scale=alt.Scale(scheme='tableau10')),  # Use theme-friendly color scheme
    tooltip=['Cargo', 'Total de Inscrições']
).properties(
    width=500,
    height=350
)

st.altair_chart(chart, use_container_width=True)

st.markdown("---")

# Selection of Professor or Supervisor above the table
cargo_selecionado = st.radio('SELECIONE O CARGO', ['PROFESSOR', 'SUPERVISOR', 'APOIO'])

# Search field
search_term = st.text_input('BUSCAR POR CIDADE OU VAGA')

# Select the corresponding DataFrame
if cargo_selecionado == 'PROFESSOR':
    df_selected = df_prof.copy()
    cor_tema = 'material'
elif cargo_selecionado == 'SUPERVISOR':
    df_selected = df_sup.copy()
    cor_tema = 'material'
elif cargo_selecionado == 'APOIO':
    df_selected = df_ap.copy()
    cor_tema = 'material'

# Filter the DataFrame based on the search term
if search_term:
    df_selected = df_selected[df_selected['VAGA'].str.contains(search_term, case=False, na=False)]

# Configure AgGrid
gb = GridOptionsBuilder.from_dataframe(df_selected)
gb.configure_default_column(editable=False, groupable=False)
gb.configure_column("VAGA", header_name="Vaga", sortable=True, filter=True, width=600)
gb.configure_column("INSCRITOS", header_name="Inscritos", sortable=True, filter=True, width=100)
gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=rows_per_page)
gb.configure_grid_options(rowHeight=25)  # Reduce row spacing
gb.configure_default_column(cellStyle={'font-size': '11px'})  # Reduce font size

gridOptions = gb.build()

# Style to narrow the AgGrid component
st.markdown(
    """
    <style>
        .ag-theme-material {
            max-width: 700px;  /* Adjust the maximum width to narrow the component */
            margin: 0 auto;  /* Center the component on the page */
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    f"<h2 style='text-align: center;'>Inscrições - {cargo_selecionado}</h2>",
    unsafe_allow_html=True
)

AgGrid(
    df_selected,
    gridOptions=gridOptions,
    enable_enterprise_modules=False,
    height=800,
    fit_columns_on_grid_load=True,
    theme=cor_tema,
    enable_pagination=True,
    reload_data=True
)

# Footer
st.markdown("---")
st.markdown(
    "<h5 style='text-align: center; color: var(--text-color);'>GEECT</h5>",
    unsafe_allow_html=True
)
