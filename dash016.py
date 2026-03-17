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

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'DM Sans', sans-serif;
        }

        .block-container {
            max-width: 1100px;
            padding-left: 2rem;
            padding-right: 2rem;
            padding-top: 1.5rem;
            margin: 0 auto;
        }

        .centered-banner img {
            display: block;
            margin-left: auto;
            margin-right: auto;
            border-radius: 12px;
        }

        /* KPI Grid */
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
            margin: 24px 0;
        }

        .kpi-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 24px 20px;
            text-align: center;
            box-shadow: 0 2px 12px rgba(0,0,0,0.06);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .kpi-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 24px rgba(43,108,176,0.12);
        }

        .kpi-label {
            font-family: 'DM Sans', sans-serif;
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            color: #64748b;
            margin-bottom: 10px;
        }

        .kpi-value {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 42px;
            font-weight: 700;
            color: #1e293b;
            line-height: 1;
        }

        .kpi-value.accent { color: #2b6cb0; }
        .kpi-value.green  { color: #276749; }
        .kpi-value.orange { color: #c05621; }

        .kpi-sub {
            font-size: 11px;
            color: #94a3b8;
            margin-top: 8px;
        }

        /* Section title */
        .section-title {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 18px;
            font-weight: 600;
            color: #1e293b;
            text-align: center;
            letter-spacing: 0.5px;
            margin: 8px 0 16px 0;
        }

        /* Divider */
        .styled-divider {
            border: none;
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(43,108,176,0.25), transparent);
            margin: 28px 0;
        }

        /* Radio buttons */
        div[role="radiogroup"] {
            display: flex;
            gap: 12px;
            justify-content: center;
        }

        div[role="radiogroup"] label {
            background: #f8fafc;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            padding: 8px 20px;
            font-size: 13px;
            font-weight: 600;
            letter-spacing: 0.8px;
            cursor: pointer;
            transition: all 0.2s;
        }

        /* Search input */
        .stTextInput input {
            background: #f8fafc !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 10px !important;
            color: #1e293b !important;
            font-family: 'DM Sans', sans-serif !important;
            font-size: 14px !important;
            padding: 10px 16px !important;
        }

        /* AgGrid wrapper */
        .ag-theme-material {
            max-width: 800px;
            margin: 0 auto;
            border-radius: 12px;
            overflow: hidden;
        }

        /* Footer */
        .footer {
            text-align: center;
            font-size: 12px;
            color: #94a3b8;
            letter-spacing: 2px;
            text-transform: uppercase;
            padding: 16px 0 8px 0;
            font-family: 'DM Sans', sans-serif;
        }

        /* Status badges */
        .badge-row {
            display: flex;
            justify-content: center;
            gap: 24px;
            margin-top: 10px;
        }
        .badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 0.6px;
            padding: 4px 12px;
            border-radius: 20px;
        }
        .badge-valid   { background: rgba(39,103,73,0.08);  color: #276749; border: 1px solid rgba(39,103,73,0.25); }
        .badge-invalid { background: rgba(192,86,33,0.08);  color: #c05621; border: 1px solid rgba(192,86,33,0.25); }
    </style>
    """,
    unsafe_allow_html=True
)

# ── Banner ──────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="centered-banner">
        <img src="https://i.postimg.cc/nhM4cdnw/banner6.png" alt="Banner" width="800">
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    "<h1 style='text-align:center;font-family:Space Grotesk,sans-serif;font-size:22px;"
    "font-weight:700;color:#1e293b;margin:18px 0 4px 0;letter-spacing:0.5px;'>"
    "📈 Dashboard de Inscrições · Edital 004/2026</h1>",
    unsafe_allow_html=True
)

st.markdown("<hr class='styled-divider'>", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configurações")
    rows_per_page = st.selectbox('Linhas por página', options=[25, 50, 100], index=0)

# ── Load data ────────────────────────────────────────────────────────────────
SPREADSHEET_ID = '1p0GTkCTsUcFbGWUUh8wwL5QdKXijtMf6x7fa88orlEk'
EXPECTED_COLS = ['VAGA', 'INSCRITOS', 'VALIDADOS', 'INVALIDADOS']

@st.cache_data(ttl=200)
def load_data(spreadsheet_id, sheet_name):
    try:
        url = (
            f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}'
            f'/gviz/tq?tqx=out:csv&sheet={sheet_name}'
        )
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        for col in ['INSCRITOS', 'VALIDADOS', 'INVALIDADOS']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        if 'VAGA' in df.columns:
            df['VAGA'] = df['VAGA'].astype(str).str.strip()
        return df
    except Exception as e:
        st.error(f"Erro ao carregar '{sheet_name}': {e}")
        return pd.DataFrame()

def prepare(df, label):
    missing = [c for c in EXPECTED_COLS if c not in df.columns]
    if df.empty or missing:
        if missing:
            st.warning(f"Colunas ausentes em '{label}': {missing}")
        return pd.DataFrame({c: [] for c in EXPECTED_COLS})
    return (
        df[EXPECTED_COLS]
        .sort_values('INSCRITOS', ascending=False)
        .reset_index(drop=True)
    )

df_prof  = prepare(load_data(SPREADSHEET_ID, 'dashprof'),  'dashprof')
df_sup   = prepare(load_data(SPREADSHEET_ID, 'dashsup'),   'dashsup')
df_apoio = prepare(load_data(SPREADSHEET_ID, 'dashapoio'), 'dashapoio')

def totals(df):
    if df.empty:
        return 0, 0, 0
    return (
        int(df['INSCRITOS'].sum()),
        int(df['VALIDADOS'].sum()),
        int(df['INVALIDADOS'].sum()),
    )

t_prof_i,  t_prof_v,  t_prof_x  = totals(df_prof)
t_sup_i,   t_sup_v,   t_sup_x   = totals(df_sup)
t_apoio_i, t_apoio_v, t_apoio_x = totals(df_apoio)

total_i = t_prof_i  + t_sup_i  + t_apoio_i
total_v = t_prof_v  + t_sup_v  + t_apoio_v
total_x = t_prof_x  + t_sup_x  + t_apoio_x

# ── KPI cards ────────────────────────────────────────────────────────────────
def kpi_card(label, value, css_class="", sub=""):
    sub_html = f"<div class='kpi-sub'>{sub}</div>" if sub else ""
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value {css_class}">{value:,}</div>
        {sub_html}
    </div>
    """

# Row 1 – grand totals
st.markdown("<p class='section-title'>TOTAIS GERAIS</p>", unsafe_allow_html=True)
st.markdown(
    f"""
    <div class="kpi-grid">
        {kpi_card("Total de Inscritos", total_i, "accent")}
        {kpi_card("Total Validados",    total_v, "green")}
        {kpi_card("Total Invalidados",  total_x, "orange")}
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("<hr class='styled-divider'>", unsafe_allow_html=True)

# Row 2 – per cargo
st.markdown("<p class='section-title'>POR CARGO</p>", unsafe_allow_html=True)

col_p, col_s, col_a = st.columns(3)

def cargo_block(col, label, total, valid, invalid, emoji):
    with col:
        st.markdown(
            f"""
            <div class="kpi-card" style="padding:20px 16px;">
                <div class="kpi-label">{emoji} {label}</div>
                <div class="kpi-value accent" style="font-size:34px;">{total:,}</div>
                <div class="badge-row" style="margin-top:14px;">
                    <span class="badge badge-valid">✔ {valid:,} válidos</span>
                    <span class="badge badge-invalid">✖ {invalid:,} inv.</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

cargo_block(col_p, "Professor",  t_prof_i,  t_prof_v,  t_prof_x,  "🎓")
cargo_block(col_s, "Supervisor", t_sup_i,   t_sup_v,   t_sup_x,   "🔍")
cargo_block(col_a, "Apoio",      t_apoio_i, t_apoio_v, t_apoio_x, "🤝")

st.markdown("<hr class='styled-divider'>", unsafe_allow_html=True)

# ── Bar chart ────────────────────────────────────────────────────────────────
st.markdown("<p class='section-title'>DISTRIBUIÇÃO DE INSCRIÇÕES POR CARGO</p>", unsafe_allow_html=True)

df_chart = pd.DataFrame({
    'Cargo': ['Professor', 'Supervisor', 'Apoio',
              'Professor', 'Supervisor', 'Apoio',
              'Professor', 'Supervisor', 'Apoio'],
    'Categoria': (['Inscritos']*3 + ['Validados']*3 + ['Invalidados']*3),
    'Quantidade': [
        t_prof_i,  t_sup_i,  t_apoio_i,
        t_prof_v,  t_sup_v,  t_apoio_v,
        t_prof_x,  t_sup_x,  t_apoio_x,
    ]
})

color_scale = alt.Scale(
    domain=['Inscritos', 'Validados', 'Invalidados'],
    range=['#3182ce', '#38a169', '#dd6b20']
)

chart = (
    alt.Chart(df_chart)
    .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
    .encode(
        x=alt.X('Categoria:N',
                axis=alt.Axis(labelFontSize=12, labelAngle=0, title=None, labelColor='#475569'),
                sort=['Inscritos', 'Validados', 'Invalidados']),
        y=alt.Y('Quantidade:Q',
                axis=alt.Axis(labelFontSize=12, labelColor='#475569', gridColor='#e2e8f0'),
                title='Quantidade'),
        color=alt.Color('Categoria:N',
                        scale=color_scale,
                        legend=alt.Legend(orient='top', labelFontSize=12, titleFontSize=13,
                                          labelColor='#1e293b', titleColor='#1e293b')),
        column=alt.Column('Cargo:N',
                          header=alt.Header(
                              labelFontSize=13,
                              labelColor='#1e293b',
                              titleFontSize=0,
                          )),
        tooltip=['Cargo', 'Categoria', 'Quantidade']
    )
    .properties(width=220, height=300)
    .configure_view(strokeWidth=0)
    .configure_axis(domainColor='#cbd5e1')
    .configure_legend(labelColor='#1e293b', titleColor='#1e293b')
)

st.altair_chart(chart, use_container_width=True)

st.markdown("<hr class='styled-divider'>", unsafe_allow_html=True)

# ── Tabela detalhada ─────────────────────────────────────────────────────────
st.markdown("<p class='section-title'>DETALHAMENTO POR VAGA</p>", unsafe_allow_html=True)

cargo_selecionado = st.radio(
    'Selecione o cargo',
    ['PROFESSOR', 'SUPERVISOR', 'APOIO'],
    horizontal=True,
    key='cargo_radio'
)

search_term = st.text_input('🔍  Buscar por cidade ou vaga', key='search_input')

cargo_map = {
    'PROFESSOR':  df_prof,
    'SUPERVISOR': df_sup,
    'APOIO':      df_apoio,
}
df_sel = cargo_map[cargo_selecionado].copy()

if search_term:
    df_sel = df_sel[
        df_sel['VAGA'].str.contains(search_term, case=False, na=False)
    ].reset_index(drop=True)

if not df_sel.empty:
    gb = GridOptionsBuilder.from_dataframe(df_sel)
    gb.configure_default_column(editable=False, groupable=False)
    gb.configure_column("VAGA",        header_name="Vaga",        sortable=True, filter=True, flex=3)
    gb.configure_column("INSCRITOS",   header_name="Inscritos",   sortable=True, filter=True, flex=1)
    gb.configure_column("VALIDADOS",   header_name="Validados",   sortable=True, filter=True, flex=1)
    gb.configure_column("INVALIDADOS", header_name="Invalidados", sortable=True, filter=True, flex=1)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=rows_per_page)
    gb.configure_grid_options(rowHeight=28)
    gb.configure_default_column(cellStyle={'font-size': '12px'})

    AgGrid(
        df_sel,
        gridOptions=gb.build(),
        enable_enterprise_modules=False,
        height=380,
        fit_columns_on_grid_load=True,
        theme='material',
        update_mode='MODEL_CHANGED',
        key=f'aggrid_{cargo_selecionado}'
    )
else:
    st.info("Nenhum dado encontrado para os filtros selecionados.")

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("<hr class='styled-divider'>", unsafe_allow_html=True)
st.markdown("<div class='footer'>GEECT</div>", unsafe_allow_html=True)
