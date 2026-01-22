import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
import altair as alt

# Page configuration
st.set_page_config(
    page_title="Dashboard de Inscrições do Edital",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Theme-aware CSS styles
st.markdown(
    """
    <style>
        .block-container {
            max-width: 1000px;
            padding-left: 1rem;
            padding-right: 1rem;
            margin: 0 auto;
        }
        .centered-banner img {
            display: block;
            margin-left: auto;
            margin-right: auto;
        }
        .ag-theme-material {
            max-width: 700px;
            margin: 0 auto;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Header
st.markdown(
    """
    <div class="centered-banner">
        <img src="https://i.postimg.cc/nhM4cdnw/banner6.png" alt="Banner" width="800">
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    "<h1 style='text-align: center; font-size: 24px;'>📈 Dashboard de Inscrições do Edital 026/2025 📈</h1>",
    unsafe_allow_html=True
)
st.markdown("---")

# Sidebar
with st.sidebar:
    st.markdown("## Configurações")
    rows_per_page = st.selectbox('Linhas por página', options=[25, 50, 100], index=0)

# Function to load data
@st.cache_data(ttl=200)
def load_data(spreadsheet_id, sheet_name):
    try:
        csv_export_url = f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'
        df = pd.read_csv(csv_export_url)
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Ensure data types are correct
        if 'VAGA' in df.columns:
            df['VAGA'] = df['VAGA'].astype(str).str.strip()
        if 'INSCRITOS' in df.columns:
            df['INSCRITOS'] = pd.to_numeric(df['INSCRITOS'], errors='coerce').fillna(0).astype(int)
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar a aba '{sheet_name}': {e}")
        return pd.DataFrame()

# Spreadsheet ID
spreadsheet_id = '1wl3W1249brMi--ds-4KL2poBJSJ2jKpDKZAfAogGLrQ'

# Load data
df_prof = load_data(spreadsheet_id, 'dashprof')
df_sup = load_data(spreadsheet_id, 'dashsup')

# Validate and prepare data
if not df_prof.empty and 'VAGA' in df_prof.columns and 'INSCRITOS' in df_prof.columns:
    df_prof = df_prof[['VAGA', 'INSCRITOS']].sort_values(by='INSCRITOS', ascending=False).reset_index(drop=True)
else:
    st.error("As colunas 'VAGA' e 'INSCRITOS' não foram encontradas na aba 'prof'.")
    df_prof = pd.DataFrame({'VAGA': [], 'INSCRITOS': []})

if not df_sup.empty and 'VAGA' in df_sup.columns and 'INSCRITOS' in df_sup.columns:
    df_sup = df_sup[['VAGA', 'INSCRITOS']].sort_values(by='INSCRITOS', ascending=False).reset_index(drop=True)
else:
    st.error("As colunas 'VAGA' e 'INSCRITOS' não foram encontradas na aba 'sup'.")
    df_sup = pd.DataFrame({'VAGA': [], 'INSCRITOS': []})

# Calculate totals
total_inscritos_prof = int(df_prof['INSCRITOS'].sum()) if not df_prof.empty else 0
total_inscritos_sup = int(df_sup['INSCRITOS'].sum()) if not df_sup.empty else 0
total_inscritos = total_inscritos_prof + total_inscritos_sup

# KPIs
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        "<h3 style='text-align: center; font-size: 20px;'>Total de Inscritos</h3>",
        unsafe_allow_html=True
    )
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

st.markdown("---")

# Chart
st.markdown(
    "<h2 style='text-align: center;'>Distribuição de Inscrições por Cargo</h2>",
    unsafe_allow_html=True
)

df_totals = pd.DataFrame({
    'Cargo': ['Professor', 'Supervisor'],
    'Total de Inscrições': [total_inscritos_prof, total_inscritos_sup]
})

chart = alt.Chart(df_totals).mark_bar().encode(
    x=alt.X('Cargo:N', axis=alt.Axis(labelFontSize=14, titleFontSize=16)),
    y=alt.Y('Total de Inscrições:Q', axis=alt.Axis(labelFontSize=14, titleFontSize=16)),
    color=alt.Color('Cargo:N', legend=None, scale=alt.Scale(scheme='tableau10')),
    tooltip=['Cargo', 'Total de Inscrições']
).properties(
    width=500,
    height=350
)

st.altair_chart(chart, use_container_width=True)

st.markdown("---")

# Selection and search
cargo_selecionado = st.radio('SELECIONE O CARGO', ['PROFESSOR', 'SUPERVISOR'], key='cargo_radio')
search_term = st.text_input('BUSCAR POR CIDADE OU VAGA', key='search_input')

# Select DataFrame
df_selected = df_prof.copy() if cargo_selecionado == 'PROFESSOR' else df_sup.copy()

# Filter
if search_term:
    df_selected = df_selected[df_selected['VAGA'].str.contains(search_term, case=False, na=False)].reset_index(drop=True)

# AgGrid configuration
if not df_selected.empty:
    gb = GridOptionsBuilder.from_dataframe(df_selected)
    gb.configure_default_column(editable=False, groupable=False)
    gb.configure_column("VAGA", header_name="Vaga", sortable=True, filter=True, width=600)
    gb.configure_column("INSCRITOS", header_name="Inscritos", sortable=True, filter=True, width=100)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=rows_per_page)
    gb.configure_grid_options(rowHeight=25)
    gb.configure_default_column(cellStyle={'font-size': '11px'})
    
    gridOptions = gb.build()
    
    st.markdown(
        f"<h2 style='text-align: center;'>Inscrições - {cargo_selecionado}</h2>",
        unsafe_allow_html=True
    )
    
    AgGrid(
        df_selected,
        gridOptions=gridOptions,
        enable_enterprise_modules=False,
        height=350,
        fit_columns_on_grid_load=True,
        theme='material',
        update_mode='MODEL_CHANGED',
        key=f'aggrid_{cargo_selecionado}'
    )
else:
    st.info("Nenhum dado encontrado para os filtros selecionados.")

# Footer
st.markdown("---")
st.markdown(
    "<h5 style='text-align: center; color: var(--text-color);'>GEECT</h5>",
    unsafe_allow_html=True
)
