import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
import altair as alt  # Importamos o Altair para gráficos estáticos

# Configurações da página para esconder a navegação lateral por padrão
st.set_page_config(
    page_title="Dashboard de Inscrições do Edital",
    page_icon="📈",
    layout="wide",  # Mantém o layout 'wide' para permitir personalização
    initial_sidebar_state="collapsed"  # Colapsa a barra lateral
)

# Forçar o tema claro do Streamlit
st.markdown(
    """
     <style>
        html, body, [data-testid="stAppViewContainer"]  {
            color-scheme: light;
        }
        .stTextInput input {
            background-color: #9B9B9B;  /* Define o fundo do campo de entrada para cinza claro */
        }
    </style>
    """,
    unsafe_allow_html=True
)

# CSS personalizado para controlar a largura da página principal
st.markdown(
    """
    <style>
        .block-container {
            max-width: 1000px; /* Define a largura máxima desejada em pixels */
            padding-left: 1rem;
            padding-right: 1rem;
            margin: 0 auto; /* Centraliza o conteúdo */
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Cabeçalho - Centralizar o banner
st.markdown(
    """
    <div style="text-align: center;">
        <img src="https://i.postimg.cc/nhM4cdnw/banner6.png" alt="Banner" width="800">
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    "<h1 style='text-align: center; color: #2E4053; font-size: 24px;'>📈 Dashboard de Inscrições do Edital 016/2024 📈</h1>",
    unsafe_allow_html=True
)
st.markdown("---")

# Barra lateral - apenas configurações gerais
with st.sidebar:
    st.markdown("## Configurações")
    rows_per_page = st.selectbox('Linhas por página', options=[25, 50, 100], index=0)

# Função para carregar os dados da planilha
@st.cache_data
def load_data(spreadsheet_id, sheet_name):
    try:
        csv_export_url = f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'
        df = pd.read_csv(csv_export_url)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar a aba '{sheet_name}': {e}")
        return pd.DataFrame()

# ID da planilha
spreadsheet_id = '1Ggz7VJfWHxnJokCgxSoWkuby2LCUM7R9ALULv4b5PBY'

# Carregar as abas 'prof' e 'sup'
df_prof = load_data(spreadsheet_id, 'prof')
df_sup = load_data(spreadsheet_id, 'sup')

# Verificar se as colunas 'VAGA' e 'INSCRITOS' existem e ordenar os DataFrames
if 'VAGA' in df_prof.columns and 'INSCRITOS' in df_prof.columns:
    df_prof = df_prof[['VAGA', 'INSCRITOS']].sort_values(by='INSCRITOS', ascending=False)
else:
    st.error("As colunas 'VAGA' e 'INSCRITOS' não foram encontradas na aba 'prof'.")

if 'VAGA' in df_sup.columns and 'INSCRITOS' in df_sup.columns:
    df_sup = df_sup[['VAGA', 'INSCRITOS']].sort_values(by='INSCRITOS', ascending=False)
else:
    st.error("As colunas 'VAGA' e 'INSCRITOS' não foram encontradas na aba 'sup'.")

# Calcular total de inscritos
total_inscritos_prof = df_prof['INSCRITOS'].sum()
total_inscritos_sup = df_sup['INSCRITOS'].sum()

# DataFrame com os totais
df_totals = pd.DataFrame({
    'Cargo': ['Professor', 'Supervisor'],
    'Total de Inscrições': [total_inscritos_prof, total_inscritos_sup]
})

# Divisão em colunas para os KPIs
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        "<h3 style='text-align: center; font-size: 20px; color: #2874A6;'>Total de Inscritos</h3>",
        unsafe_allow_html=True
    )
    total_inscritos = total_inscritos_prof + total_inscritos_sup
    st.markdown(
        f"<h1 style='text-align: center; font-size: 24px; color: #2874A6;'>{total_inscritos}</h1>",
        unsafe_allow_html=True
    )
with col2:
    st.markdown(
        "<h3 style='text-align: center; font-size: 20px; color: #229954;'>Inscritos - Professor</h3>",
        unsafe_allow_html=True
    )
    st.markdown(
        f"<h1 style='text-align: center; font-size: 24px; color: #229954;'>{total_inscritos_prof}</h1>",
        unsafe_allow_html=True
    )
with col3:
    st.markdown(
        "<h3 style='text-align: center; font-size: 20px; color: #AF7AC5;'>Inscritos - Supervisor</h3>",
        unsafe_allow_html=True
    )
    st.markdown(
        f"<h1 style='text-align: center; font-size: 24px; color: #AF7AC5;'>{total_inscritos_sup}</h1>",
        unsafe_allow_html=True
    )

st.markdown("---")

# Centralizar o gráfico Altair
st.markdown(
    "<h2 style='text-align: center; color: #2E4053;'>Distribuição de Inscrições por Cargo</h2>",
    unsafe_allow_html=True
)

# Definir o gráfico 'chart'
chart = alt.Chart(df_totals).mark_bar().encode(
    x=alt.X('Cargo:N', axis=alt.Axis(labelFontSize=14, titleFontSize=16)),
    y=alt.Y('Total de Inscrições:Q', axis=alt.Axis(labelFontSize=14, titleFontSize=16)),
    color=alt.Color('Cargo:N', legend=None, scale=alt.Scale(range=['#229954', '#AF7AC5'])),
    tooltip=['Cargo', 'Total de Inscrições']
).properties(
    width=500,
    height=350
)

st.altair_chart(chart, use_container_width=True)

st.markdown("---")

# Seleção de Professor ou Supervisor acima da tabela

cargo_selecionado = st.radio('SELECIONE O CARGO', ['PROFESSOR', 'SUPERVISOR'])

# Campo de busca
search_term = st.text_input('BUSCAR POR CIDADE OU VAGA')

# Selecionar o DataFrame correspondente
if cargo_selecionado == 'PROFESSOR':
    df_selected = df_prof.copy()
    cor_tema = 'material'
elif cargo_selecionado == 'SUPERVISOR':
    df_selected = df_sup.copy()
    cor_tema = 'material'

# Filtrar o DataFrame com base no termo de busca
if search_term:
    df_selected = df_selected[df_selected['VAGA'].str.contains(search_term, case=False, na=False)]

# Configurar o AgGrid
gb = GridOptionsBuilder.from_dataframe(df_selected)
gb.configure_default_column(editable=False, groupable=False)
gb.configure_column("VAGA", header_name="Vaga", sortable=True, filter=True, width=600)
gb.configure_column("INSCRITOS", header_name="Inscritos", sortable=True, filter=True, width=100)
gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=rows_per_page)
gb.configure_grid_options(rowHeight=25)  # Reduz o espaçamento entre linhas
gb.configure_default_column(cellStyle={'font-size': '11px'})  # Reduz o tamanho da fonte

gridOptions = gb.build()

# Estilo para estreitar o componente AgGrid
st.markdown(
    """
    <style>
        .ag-theme-material {
            max-width: 700px;  /* Ajuste a largura máxima para estreitar o componente */
            margin: 0 auto;  /* Centralizar o componente na página */
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    f"<h2 style='text-align: center; color: #2E4053;'>Inscrições - {cargo_selecionado}</h2>",
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

# Rodapé
st.markdown("---")
st.markdown(
    "<h5 style='text-align: center; color: #839192;'>GEECT</h5>",
    unsafe_allow_html=True
)