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
            max-width: 1300px;
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
            max-width: 100%;
            margin: 0 auto;
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
    </style>
    """,
    unsafe_allow_html=True
)

# ── Banner ──────────────────────────────────────────────────────────────────
# st.markdown(
#     """
#     <div class="centered-banner">
#         <img src="https://i.postimg.cc/nhM4cdnw/banner6.png" alt="Banner" width="800">
#     </div>
#     """,
#     unsafe_allow_html=True
# )

st.markdown(
    "<h1 style='text-align:center;font-family:Space Grotesk,sans-serif;font-size:22px;"
    "font-weight:700;color:#1e293b;margin:18px 0 4px 0;letter-spacing:0.5px;'>"
    "📈 Dashboard de Inscrições · Edital 019/2026</h1>",
    unsafe_allow_html=True
)

st.markdown("<hr class='styled-divider'>", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configurações")
    rows_per_page = st.selectbox('Linhas por página', options=[25, 50, 100], index=0)

# ── Load data ────────────────────────────────────────────────────────────────
SPREADSHEET_ID = '1qnX7mYrwIWr3zAE-Zbc5OYlh3RjdcPfdvPii1iycfkY'
EXPECTED_COLS = ['VAGA', 'INSCRITOS']

@st.cache_data(ttl=200)
def load_data(spreadsheet_id, sheet_name):
    try:
        url = (
            f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}'
            f'/gviz/tq?tqx=out:csv&sheet={sheet_name}'
        )
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        if 'INSCRITOS' in df.columns:
            df['INSCRITOS'] = pd.to_numeric(df['INSCRITOS'], errors='coerce').fillna(0).astype(int)
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

# ── PROFESSOR: não há vaga para este cargo neste edital, dados desativados ──
# df_prof  = prepare(load_data(SPREADSHEET_ID, 'dashprof'),  'dashprof')
df_sup   = prepare(load_data(SPREADSHEET_ID, 'dashsup'),   'dashsup')
df_PROFESSOR = prepare(load_data(SPREADSHEET_ID, 'dashPROFESSOR'), 'dashPROFESSOR')

def totals(df):
    if df.empty:
        return 0
    return int(df['INSCRITOS'].sum())

# t_prof_i = totals(df_prof)
t_sup_i        = totals(df_sup)
t_PROFESSOR_i  = totals(df_PROFESSOR)

total_i = t_sup_i + t_PROFESSOR_i

# ── KPI card ─────────────────────────────────────────────────────────────────
def kpi_card(label, value, css_class="", sub=""):
    sub_html = f"<div class='kpi-sub'>{sub}</div>" if sub else ""
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value {css_class}">{value:,}</div>
        {sub_html}
    </div>
    """

# Total geral
st.markdown("<p class='section-title'>TOTAL GERAL</p>", unsafe_allow_html=True)
st.markdown(
    f"""
    <div class="kpi-grid" style="grid-template-columns: 1fr;max-width:340px;margin-left:auto;margin-right:auto;">
        {kpi_card("Total de Inscritos", total_i, "accent")}
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("<hr class='styled-divider'>", unsafe_allow_html=True)

# Por cargo (apenas Supervisor e PROFESSOR; Professor não participa deste edital)
st.markdown("<p class='section-title'>POR CARGO</p>", unsafe_allow_html=True)

col_s, col_a = st.columns(2)

def cargo_block(col, label, total, emoji):
    with col:
        st.markdown(
            f"""
            <div class="kpi-card" style="padding:20px 16px;">
                <div class="kpi-label">{emoji} {label}</div>
                <div class="kpi-value accent" style="font-size:34px;">{total:,}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

# cargo_block(col_p, "Professor", t_prof_i, "🎓")
cargo_block(col_s, "Supervisor", t_sup_i,       "🔍")
cargo_block(col_a, "PROFESSOR",  t_PROFESSOR_i, "🤝")

st.markdown("<hr class='styled-divider'>", unsafe_allow_html=True)

# ── Bar chart ────────────────────────────────────────────────────────────────
st.markdown("<p class='section-title'>INSCRIÇÕES POR CARGO</p>", unsafe_allow_html=True)

df_chart = pd.DataFrame({
    'Cargo': ['Supervisor', 'PROFESSOR'],
    'Inscritos': [t_sup_i, t_PROFESSOR_i],
})

chart = (
    alt.Chart(df_chart)
    .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4, size=60)
    .encode(
        x=alt.X('Cargo:N',
                axis=alt.Axis(labelFontSize=12, labelAngle=0, title=None, labelColor='#475569')),
        y=alt.Y('Inscritos:Q',
                axis=alt.Axis(labelFontSize=11, labelColor='#475569', gridColor='#e2e8f0'),
                title='Inscritos'),
        color=alt.value('#3182ce'),
        tooltip=['Cargo', 'Inscritos']
    )
    .properties(width='container', height=260)
    .configure_view(strokeWidth=0)
    .configure_axis(domainColor='#cbd5e1')
)
st.altair_chart(chart, use_container_width=True)

st.markdown("<hr class='styled-divider'>", unsafe_allow_html=True)

# ── Tabela detalhada ─────────────────────────────────────────────────────────
st.markdown("<p class='section-title'>DETALHAMENTO POR VAGA</p>", unsafe_allow_html=True)

cargo_selecionado = st.radio(
    'Selecione o cargo',
    ['SUPERVISOR', 'PROFESSOR'],   # 'PROFESSOR' removido: sem vagas neste edital
    horizontal=True,
    key='cargo_radio'
)

search_term = st.text_input('🔍  Buscar por cidade ou vaga', key='search_input')

cargo_map = {
    # 'PROFESSOR':  df_prof,
    'SUPERVISOR': df_sup,
    'PROFESSOR':      df_PROFESSOR,
}
df_sel = cargo_map[cargo_selecionado].copy()

if search_term:
    df_sel = df_sel[
        df_sel['VAGA'].str.contains(search_term, case=False, na=False)
    ].reset_index(drop=True)

if not df_sel.empty:
    gb = GridOptionsBuilder.from_dataframe(df_sel)
    gb.configure_default_column(
        editable=False,
        groupable=False,
        resizable=True,
        cellStyle={'font-size': '14px'},
    )
    # Coluna "Vaga": ocupa todo o espaço que sobrar (flex alto), com quebra de
    # linha (wrapText) para nunca truncar o nome, mesmo em telas menores.
    gb.configure_column(
        "VAGA",
        header_name="Vaga",
        sortable=True,
        filter=True,
        flex=6,
        minWidth=260,
        wrapText=True,
        tooltipField="VAGA",
        cellStyle={'font-size': '14px', 'lineHeight': '1.3', 'padding-top': '6px', 'padding-bottom': '6px'},
    )
    # Coluna numérica: largura fixa (sem flex) e ampla o bastante para o
    # cabeçalho não cortar. suppressSizeToFit trava essa largura mesmo se
    # algum recálculo automático do grid tentar reduzir.
    gb.configure_column(
        "INSCRITOS", header_name="Inscritos", sortable=True, filter=True,
        width=130, minWidth=120, flex=0, suppressSizeToFit=True,
        cellStyle={'font-size': '14px', 'textAlign': 'center'},
    )
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=rows_per_page)
    gb.configure_grid_options(rowHeight=40, domLayout='normal')

    AgGrid(
        df_sel,
        gridOptions=gb.build(),
        enable_enterprise_modules=False,
        height=520,
        # IMPORTANTE: desativado. Esse parâmetro forçava o AgGrid a espremer
        # todas as colunas (inclusive os cabeçalhos) para caber na tela,
        # ignorando os "width"/"flex" definidos acima — era a causa do
        # corte em "Ins...", "Vali...", "Inva...".
        fit_columns_on_grid_load=False,
        theme='material',
        update_mode='NO_UPDATE',
        allow_unsafe_jscode=True,
        key=f'aggrid_{cargo_selecionado}',
        # O CSS injetado via st.markdown na página principal NÃO alcança o
        # AgGrid, pois ele renderiza dentro de um <iframe> isolado. Por isso
        # o rodapé de paginação era "comido" — precisa ir por aqui.
        custom_css={
            '.ag-root-wrapper': {
                'border-radius': '12px !important',
            },
            '.ag-paging-panel': {
                'height': '48px !important',
                'min-height': '48px !important',
                'display': 'flex !important',
                'align-items': 'center !important',
                'justify-content': 'flex-end !important',
                'gap': '16px !important',
                'font-size': '13px !important',
                'color': '#1e293b !important',
                'border-top': '1px solid #e2e8f0 !important',
                'background': '#ffffff !important',
                'overflow': 'visible !important',
                'white-space': 'nowrap !important',
                'flex-shrink': '0 !important',
                'padding': '0 12px !important',
            },
            '.ag-paging-row-summary-panel, .ag-paging-page-summary-panel': {
                'overflow': 'visible !important',
                'white-space': 'nowrap !important',
            },
        }
    )
else:
    st.info("Nenhum dado encontrado para os filtros selecionados.")

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("<hr class='styled-divider'>", unsafe_allow_html=True)
st.markdown("<div class='footer'>GEECT</div>", unsafe_allow_html=True)
