import streamlit as st
import pandas as pd
import altair as alt

# Page configuration
st.set_page_config(
    page_title="Dashboard de Inscrições do Edital",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 10px;
            color: white;
            text-align: center;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            padding-left: 20px;
            padding-right: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
    <div style="text-align: center;">
        <img src="https://i.postimg.cc/nhM4cdnw/banner6.png" alt="Banner" width="800">
    </div>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>📈 Dashboard de Inscrições - Edital 026/2025</h1>", unsafe_allow_html=True)
st.markdown("---")

# Load data function
@st.cache_data(ttl=200)
def load_data(spreadsheet_id, sheet_name):
    try:
        csv_export_url = f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'
        df = pd.read_csv(csv_export_url)
        df.columns = df.columns.str.strip()
        
        if 'VAGA' in df.columns:
            df['VAGA'] = df['VAGA'].astype(str).str.strip()
            # Extrair cidade da vaga
            df['CIDADE'] = df['VAGA'].str.extract(r'([A-ZÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑ\s]+)')[0].str.strip()
        if 'INSCRITOS' in df.columns:
            df['INSCRITOS'] = pd.to_numeric(df['INSCRITOS'], errors='coerce').fillna(0).astype(int)
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

# Load data
spreadsheet_id = '1wl3W1249brMi--ds-4KL2poBJSJ2jKpDKZAfAogGLrQ'
df_prof = load_data(spreadsheet_id, 'dashprof')
df_sup = load_data(spreadsheet_id, 'dashsup')

# Validate data
if df_prof.empty or df_sup.empty:
    st.error("Erro ao carregar os dados. Verifique a conexão com a planilha.")
    st.stop()

# Add cargo column
df_prof['CARGO'] = 'Professor'
df_sup['CARGO'] = 'Supervisor'

# Combine dataframes
df_all = pd.concat([df_prof, df_sup], ignore_index=True)

# Sidebar filters
st.sidebar.markdown("## 🔍 Filtros")

cargo_filter = st.sidebar.multiselect(
    'Cargo',
    options=['Professor', 'Supervisor'],
    default=['Professor', 'Supervisor']
)

if 'CIDADE' in df_all.columns:
    cidades_disponiveis = sorted(df_all['CIDADE'].dropna().unique())
    cidade_filter = st.sidebar.multiselect(
        'Cidade',
        options=cidades_disponiveis,
        default=[]
    )
else:
    cidade_filter = []

min_inscritos = st.sidebar.number_input('Mínimo de Inscritos', min_value=0, value=0)

search_term = st.sidebar.text_input('🔎 Buscar na vaga', '')

# Apply filters
df_filtered = df_all[df_all['CARGO'].isin(cargo_filter)]

if cidade_filter:
    df_filtered = df_filtered[df_filtered['CIDADE'].isin(cidade_filter)]

if min_inscritos > 0:
    df_filtered = df_filtered[df_filtered['INSCRITOS'] >= min_inscritos]

if search_term:
    df_filtered = df_filtered[df_filtered['VAGA'].str.contains(search_term, case=False, na=False)]

# Calculate metrics
total_inscritos = int(df_all['INSCRITOS'].sum())
total_prof = int(df_prof['INSCRITOS'].sum())
total_sup = int(df_sup['INSCRITOS'].sum())
total_vagas = len(df_all)
media_inscritos = df_all['INSCRITOS'].mean()

# KPIs
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total de Inscritos", f"{total_inscritos:,}", help="Total geral de inscrições")

with col2:
    st.metric("Professor", f"{total_prof:,}", help="Inscrições para Professor")

with col3:
    st.metric("Supervisor", f"{total_sup:,}", help="Inscrições para Supervisor")

with col4:
    st.metric("Total de Vagas", f"{total_vagas:,}", help="Número de vagas no edital")

with col5:
    st.metric("Média por Vaga", f"{media_inscritos:.1f}", help="Média de inscritos por vaga")

st.markdown("---")

# Tabs for different views
tab1, tab2, tab3, tab4 = st.tabs(["📊 Visão Geral", "🏆 Top Vagas", "🗺️ Por Cidade", "📋 Lista Completa"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Distribuição por Cargo")
        df_cargo = df_all.groupby('CARGO')['INSCRITOS'].sum().reset_index()
        
        chart_cargo = alt.Chart(df_cargo).mark_arc(innerRadius=50).encode(
            theta=alt.Theta(field="INSCRITOS", type="quantitative"),
            color=alt.Color(field="CARGO", type="nominal", scale=alt.Scale(scheme='tableau10')),
            tooltip=['CARGO', 'INSCRITOS']
        ).properties(height=300)
        
        st.altair_chart(chart_cargo, use_container_width=True)
    
    with col2:
        st.markdown("### Distribuição de Inscritos")
        
        # Histogram
        hist_chart = alt.Chart(df_all).mark_bar().encode(
            alt.X('INSCRITOS:Q', bin=alt.Bin(maxbins=30), title='Número de Inscritos'),
            alt.Y('count()', title='Quantidade de Vagas'),
            tooltip=['count()']
        ).properties(height=300)
        
        st.altair_chart(hist_chart, use_container_width=True)
    
    st.markdown("### Análise de Concorrência")
    
    # Statistics by cargo
    stats_df = df_all.groupby('CARGO')['INSCRITOS'].agg([
        ('Mínimo', 'min'),
        ('Máximo', 'max'),
        ('Média', 'mean'),
        ('Mediana', 'median'),
        ('Total', 'sum')
    ]).reset_index()
    
    st.dataframe(stats_df.style.format({
        'Mínimo': '{:.0f}',
        'Máximo': '{:.0f}',
        'Média': '{:.2f}',
        'Mediana': '{:.2f}',
        'Total': '{:.0f}'
    }), use_container_width=True)

with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔥 Top 20 Vagas Mais Concorridas")
        top_20 = df_filtered.nlargest(20, 'INSCRITOS')[['VAGA', 'INSCRITOS', 'CARGO']]
        
        chart_top = alt.Chart(top_20).mark_bar().encode(
            x=alt.X('INSCRITOS:Q', title='Número de Inscritos'),
            y=alt.Y('VAGA:N', sort='-x', title=None),
            color=alt.Color('CARGO:N', scale=alt.Scale(scheme='tableau10')),
            tooltip=['VAGA', 'INSCRITOS', 'CARGO']
        ).properties(height=500)
        
        st.altair_chart(chart_top, use_container_width=True)
    
    with col2:
        st.markdown("### 😌 Top 20 Vagas Menos Concorridas")
        bottom_20 = df_filtered.nsmallest(20, 'INSCRITOS')[['VAGA', 'INSCRITOS', 'CARGO']]
        
        chart_bottom = alt.Chart(bottom_20).mark_bar().encode(
            x=alt.X('INSCRITOS:Q', title='Número de Inscritos'),
            y=alt.Y('VAGA:N', sort='x', title=None),
            color=alt.Color('CARGO:N', scale=alt.Scale(scheme='tableau10')),
            tooltip=['VAGA', 'INSCRITOS', 'CARGO']
        ).properties(height=500)
        
        st.altair_chart(chart_bottom, use_container_width=True)

with tab3:
    if 'CIDADE' in df_filtered.columns:
        st.markdown("### 🗺️ Inscrições por Cidade")
        
        # Group by city
        df_cidade = df_filtered.groupby(['CIDADE', 'CARGO'])['INSCRITOS'].sum().reset_index()
        
        # Sort by total
        cidade_totals = df_cidade.groupby('CIDADE')['INSCRITOS'].sum().sort_values(ascending=False)
        top_cidades = cidade_totals.head(30).index.tolist()
        df_cidade_top = df_cidade[df_cidade['CIDADE'].isin(top_cidades)]
        
        chart_cidade = alt.Chart(df_cidade_top).mark_bar().encode(
            x=alt.X('INSCRITOS:Q', title='Número de Inscritos'),
            y=alt.Y('CIDADE:N', sort='-x', title=None),
            color=alt.Color('CARGO:N', scale=alt.Scale(scheme='tableau10')),
            tooltip=['CIDADE', 'CARGO', 'INSCRITOS']
        ).properties(height=700)
        
        st.altair_chart(chart_cidade, use_container_width=True)
        
        # Summary table
        st.markdown("### Resumo por Cidade")
        cidade_summary = df_filtered.groupby('CIDADE').agg({
            'INSCRITOS': ['sum', 'count', 'mean']
        }).reset_index()
        cidade_summary.columns = ['Cidade', 'Total Inscritos', 'Nº Vagas', 'Média por Vaga']
        cidade_summary = cidade_summary.sort_values('Total Inscritos', ascending=False)
        
        st.dataframe(
            cidade_summary.style.format({
                'Total Inscritos': '{:.0f}',
                'Nº Vagas': '{:.0f}',
                'Média por Vaga': '{:.2f}'
            }),
            use_container_width=True,
            height=400
        )
    else:
        st.info("Dados de cidade não disponíveis")

with tab4:
    st.markdown(f"### 📋 Lista Completa ({len(df_filtered)} vagas)")
    
    # Sort options
    col1, col2 = st.columns([3, 1])
    with col1:
        sort_by = st.selectbox('Ordenar por', ['Mais Concorridas', 'Menos Concorridas', 'Alfabética'])
    with col2:
        items_per_page = st.selectbox('Itens por página', [50, 100, 200, 500], index=1)
    
    # Apply sorting
    if sort_by == 'Mais Concorridas':
        df_display = df_filtered.sort_values('INSCRITOS', ascending=False)
    elif sort_by == 'Menos Concorridas':
        df_display = df_filtered.sort_values('INSCRITOS', ascending=True)
    else:
        df_display = df_filtered.sort_values('VAGA')
    
    df_display = df_display.reset_index(drop=True)
    
    # Pagination
    total_items = len(df_display)
    total_pages = (total_items - 1) // items_per_page + 1
    
    page = st.number_input('Página', min_value=1, max_value=total_pages, value=1, step=1)
    
    start_idx = (page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)
    
    st.info(f"Mostrando {start_idx + 1} a {end_idx} de {total_items} vagas (Página {page} de {total_pages})")
    
    # Display table
    df_page = df_display.iloc[start_idx:end_idx][['VAGA', 'INSCRITOS', 'CARGO']]
    
    # Color coding
    def color_inscritos(val):
        if val > df_all['INSCRITOS'].quantile(0.75):
            color = '#ff4b4b'
        elif val > df_all['INSCRITOS'].quantile(0.5):
            color = '#ffa500'
        elif val > df_all['INSCRITOS'].quantile(0.25):
            color = '#ffeb3b'
        else:
            color = '#4caf50'
        return f'background-color: {color}; color: white; font-weight: bold'
    
    st.dataframe(
        df_page.style.applymap(color_inscritos, subset=['INSCRITOS']),
        use_container_width=True,
        height=600
    )
    
    # Download button
    csv = df_filtered.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Baixar dados filtrados (CSV)",
        data=csv,
        file_name="inscricoes_edital_026_2025.csv",
        mime="text/csv",
    )

# Footer
st.markdown("---")
st.markdown("<h5 style='text-align: center;'>GEECT - Atualizado automaticamente</h5>", unsafe_allow_html=True)
