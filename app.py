import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

from backend.parser import parse_transaction
from backend.categoriser import categoriser

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Transaction Ledger Engine",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Constants ─────────────────────────────────────────────────────────────────
CATEGORY_META = {
    "Travel & Transport":            {"color": "#3B82F6", "icon": "✈️"},
    "Software & SaaS":               {"color": "#8B5CF6", "icon": "💻"},
    "Food & Dining":                 {"color": "#F59E0B", "icon": "🍜"},
    "Office Supplies":               {"color": "#10B981", "icon": "🖊️"},
    "Utilities & Bills":             {"color": "#6B7280", "icon": "⚡"},
    "Advertising & Marketing":       {"color": "#EC4899", "icon": "📣"},
    "Professional Services":         {"color": "#14B8A6", "icon": "💼"},
    "Banking & Finance":             {"color": "#1D4ED8", "icon": "🏦"},
    "Subscriptions & Entertainment": {"color": "#F97316", "icon": "🎬"},
    "Healthcare & Wellbeing":        {"color": "#22C55E", "icon": "💊"},
    "Uncategorised":                 {"color": "#9CA3AF", "icon": "❓"},
    "Income":                        {"color": "#10B981", "icon": "💰"},
}

SAMPLES = [
    "25/03 UBER *TRIP SYDNEY AUD 42.50",
    "PAYPAL *SPOTIFY AU 10.99",
    "AMZN MKTP AU*2K4XR9 84.00",
    "01/07 OFFICEWORKS PTY LTD CLAYTON 67.40",
    "TELSTRA BILL PAY 89.00",
    "GOOGLE ADS 2025-07-01 250.00",
    "28/06 NETFLIX.COM 22.99",
    "SQ *MARIO KART CAFE MELB 26.50",
    "ANZ LOAN REPAYMENT 1200.00",
    "CHEMIST WAREHOUSE 0421 34.95",
    "Commonwealth Bank Fee 25/06/25 12.00",
    "ADOBE *CREATIVE CLD 82.49",
]

SAMPLE_CSV = """\
Date,Description,Debit,Credit,Balance
01/06/2025,SALARY PAYMENT - ACME CORP,,5200.00,5200.00
02/06/2025,UBER *TRIP SYDNEY AUD,42.50,,5157.50
03/06/2025,PAYPAL *SPOTIFY AU,10.99,,5146.51
04/06/2025,AMZN MKTP AU*2K4XR9,84.00,,5062.51
05/06/2025,OFFICEWORKS PTY LTD CLAYTON,67.40,,4995.11
06/06/2025,TELSTRA BILL PAY,89.00,,4906.11
07/06/2025,GOOGLE ADS PAYMENT,250.00,,4656.11
08/06/2025,NETFLIX.COM,22.99,,4633.12
09/06/2025,SQ *MARIO KART CAFE MELB,26.50,,4606.62
10/06/2025,ANZ LOAN REPAYMENT,1200.00,,3406.62
11/06/2025,CHEMIST WAREHOUSE 0421,34.95,,3371.67
12/06/2025,Commonwealth Bank Fee,12.00,,3359.67
13/06/2025,ADOBE *CREATIVE CLD,82.49,,3277.18
14/06/2025,FREELANCE CONSULTING FEE,,1500.00,4777.18
15/06/2025,XERO AUSTRALIA PTY LTD,70.00,,4707.18
16/06/2025,WOOLWORTHS SUPERMARKET 4421,156.30,,4550.88
17/06/2025,QANTAS AIRWAYS 0123,380.00,,4170.88
18/06/2025,SLACK *PREMIUM AUS,12.50,,4158.38
19/06/2025,DR SINGH MEDICAL CENTRE,85.00,,4073.38
20/06/2025,LINKEDIN *PREMIUM AUS,47.99,,4025.39
"""

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  .main .block-container { padding: 1.5rem 2rem 3rem; max-width: 1300px; }
  .stTabs [data-baseweb="tab-list"] { gap: 6px; }
  .stTabs [data-baseweb="tab"] { border-radius: 8px; padding: 8px 22px; }
  div[data-testid="metric-container"] {
    background: #161B22;
    border: 1px solid #21262D;
    border-radius: 10px;
    padding: 1rem 1.2rem;
  }
  div[data-testid="stDataFrame"] { border-radius: 8px; }
  .stButton > button { font-weight: 600; }
  .stDownloadButton > button {
    background: #161B22 !important;
    border: 1px solid #30363D !important;
    color: #8B949E !important;
    font-size: 0.85rem !important;
  }
  footer { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:20px 0 28px;">
  <div style="font-size:2.3rem;font-weight:900;color:#F9FAFB;letter-spacing:-0.5px;">🏦 Transaction Ledger Engine</div>
  <div style="color:#8B949E;font-size:1rem;margin-top:10px;max-width:600px;margin-inline:auto;line-height:1.7;">
    Every bank export your business receives looks like noise.<br>
    <code style="background:#21262D;color:#10B981;padding:2px 8px;border-radius:4px;font-size:0.88rem;">AMZN MKTP AU*2K4XR9 84.00</code>
    &nbsp;→&nbsp;
    <code style="background:#21262D;color:#6366F1;padding:2px 8px;border-radius:4px;font-size:0.88rem;">Office Supplies · $84.00</code><br>
    <span style="color:#6B7280;font-size:0.82rem;">The same normalisation problem MYOB, Xero, and QuickBooks solve — rebuilt from scratch, locally.</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["⚡  Single Transaction", "📊  Upload Bank Statement"])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Single transaction
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:

    if "raw_val" not in st.session_state:
        st.session_state["raw_val"] = ""

    col_in, col_out = st.columns([1.3, 1])

    with col_in:
        raw_input = st.text_input(
            "Paste any raw bank feed string:",
            value=st.session_state["raw_val"],
            placeholder="e.g.  25/03 UBER *TRIP SYDNEY AUD 42.50",
            key="raw_field",
        )

        st.markdown(
            "<div style='color:#6B7280;font-size:0.78rem;margin:10px 0 6px;text-transform:uppercase;"
            "letter-spacing:1px;'>Quick samples — click to load</div>",
            unsafe_allow_html=True,
        )
        sample_cols = st.columns(2)
        for i, s in enumerate(SAMPLES):
            if sample_cols[i % 2].button(s, key=f"s{i}", use_container_width=True):
                st.session_state["raw_val"] = s
                st.rerun()

    with col_out:
        raw = raw_input.strip() or st.session_state["raw_val"].strip()
        if raw:
            parsed = parse_transaction(raw)
            cat    = categoriser.categorise(parsed["vendor"])

            vendor   = parsed["vendor"] or "—"
            amount   = f"${parsed['amount']:.2f}" if parsed["amount"] else "—"
            date     = parsed["date"] or "—"
            category = cat["category"]
            conf     = min(int(cat["confidence"] * 100), 100)

            meta  = CATEGORY_META.get(category, CATEGORY_META["Uncategorised"])
            color = meta["color"]
            icon  = meta["icon"]

            st.markdown(f"""
<div style="background:#111827;border:2px solid {color};border-radius:14px;padding:22px;margin-top:4px;">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:18px;">
    <div>
      <div style="color:#6B7280;font-size:0.68rem;text-transform:uppercase;letter-spacing:1.5px;">VENDOR</div>
      <div style="color:#F9FAFB;font-size:1.45rem;font-weight:800;margin-top:4px;">{vendor}</div>
    </div>
    <div style="text-align:right;">
      <div style="color:#6B7280;font-size:0.68rem;text-transform:uppercase;letter-spacing:1.5px;">AMOUNT</div>
      <div style="color:#10B981;font-size:1.7rem;font-weight:800;margin-top:4px;">{amount}</div>
    </div>
  </div>
  <div style="border-top:1px solid #1F2937;padding:12px 0 14px;">
    <div style="color:#6B7280;font-size:0.68rem;text-transform:uppercase;letter-spacing:1.5px;">DATE</div>
    <div style="color:#D1D5DB;font-size:0.95rem;margin-top:4px;">{date}</div>
  </div>
  <div style="margin-bottom:14px;">
    <div style="display:inline-flex;align-items:center;gap:8px;
                background:{color}1A;border:1.5px solid {color};border-radius:22px;padding:7px 18px;">
      <span style="font-size:1.1rem;">{icon}</span>
      <span style="color:{color};font-weight:700;font-size:0.95rem;">{category}</span>
    </div>
  </div>
  <div style="color:#6B7280;font-size:0.72rem;margin-bottom:5px;">Model confidence — {conf}%</div>
  <div style="background:#1F2937;border-radius:6px;height:7px;">
    <div style="background:linear-gradient(90deg,{color}99,{color});
                width:{conf}%;height:100%;border-radius:6px;"></div>
  </div>
</div>
""", unsafe_allow_html=True)
        else:
            st.markdown("""
<div style="background:#111827;border:1px dashed #374151;border-radius:14px;
            padding:40px;text-align:center;color:#4B5563;margin-top:4px;">
  ← Paste a bank feed string or click a sample
</div>
""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
<div style="background:#161B22;border:1px solid #21262D;border-radius:10px;padding:18px 20px;">
  <div style="color:#8B949E;font-size:0.72rem;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:12px;">⚙️ Pipeline</div>
  <div style="display:flex;gap:12px;flex-wrap:wrap;">
    <div style="flex:1;min-width:180px;background:#0D1117;border-radius:8px;padding:12px 14px;">
      <div style="color:#10B981;font-size:0.75rem;font-weight:700;margin-bottom:4px;">① Regex</div>
      <div style="color:#9CA3AF;font-size:0.82rem;line-height:1.5;">Extracts <b>amount</b> and <b>date</b> deterministically — 5 AU/ISO format patterns, ordered to avoid false matches</div>
    </div>
    <div style="flex:1;min-width:180px;background:#0D1117;border-radius:8px;padding:12px 14px;">
      <div style="color:#3B82F6;font-size:0.75rem;font-weight:700;margin-bottom:4px;">② spaCy NER</div>
      <div style="color:#9CA3AF;font-size:0.82rem;line-height:1.5;">Pre-filters vendor token with regex (split on digit/✶//) then runs NER on the clean substring — fixes domain gap on all-caps bank strings</div>
    </div>
    <div style="flex:1;min-width:180px;background:#0D1117;border-radius:8px;padding:12px 14px;">
      <div style="color:#8B5CF6;font-size:0.75rem;font-weight:700;margin-bottom:4px;">③ TF-IDF</div>
      <div style="color:#9CA3AF;font-size:0.82rem;line-height:1.5;">Cosine similarity to 10 category seed vocabularies — zero training data, immediately explainable, extensible by editing a dict</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Upload statement
# ═══════════════════════════════════════════════════════════════════════════════
def _parse_csv(df: pd.DataFrame) -> pd.DataFrame:
    cols = {c.lower().strip(): c for c in df.columns}

    desc_col = None
    for k in ["description", "narrative", "details", "memo", "transaction", "particulars"]:
        if k in cols:
            desc_col = cols[k]
            break
    if desc_col is None:
        desc_col = df.columns[min(1, len(df.columns) - 1)]

    debit_col = credit_col = amount_col = date_col = None
    for k, col in cols.items():
        if any(x in k for x in ["debit", "withdrawal", "dr"]):
            debit_col = col
        elif any(x in k for x in ["credit", "deposit", "cr"]):
            credit_col = col
        elif any(x in k for x in ["amount", "value", "sum"]):
            amount_col = col
        if any(x in k for x in ["date", "posted", "trans"]):
            date_col = col

    if date_col is None:
        date_col = df.columns[0]

    rows = []
    for _, row in df.iterrows():
        desc = str(row.get(desc_col, "")).strip()
        if not desc or desc == "nan":
            continue

        is_income = False
        amount = None

        if debit_col and credit_col:
            dv = pd.to_numeric(str(row.get(debit_col, "")).replace(",", ""), errors="coerce")
            cv = pd.to_numeric(str(row.get(credit_col, "")).replace(",", ""), errors="coerce")
            if pd.notna(cv) and cv > 0:
                amount = float(cv); is_income = True
            elif pd.notna(dv) and dv > 0:
                amount = float(dv)
        elif amount_col:
            v = pd.to_numeric(str(row.get(amount_col, "")).replace(",", ""), errors="coerce")
            if pd.notna(v):
                if v < 0:
                    amount = abs(float(v)); is_income = True
                else:
                    amount = float(v)

        date_val = str(row.get(date_col, "—")).strip()

        if is_income:
            vendor = desc[:40]
            category = "Income"
        else:
            raw_for_parser = f"{desc} {amount:.2f}" if amount else desc
            parsed   = parse_transaction(raw_for_parser)
            cat_res  = categoriser.categorise(parsed["vendor"])
            vendor   = parsed["vendor"] or desc[:30]
            category = cat_res["category"]

        rows.append({
            "Date":     date_val,
            "Raw":      desc,
            "Vendor":   vendor,
            "Amount":   amount or 0.0,
            "Flow":     "Income" if is_income else "Expense",
            "Category": category,
        })

    return pd.DataFrame(rows)


def _parse_pdf(file_bytes: bytes) -> pd.DataFrame:
    try:
        import pdfplumber
        rows = []
        with pdfplumber.open(BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                for line in text.splitlines():
                    line = line.strip()
                    if len(line) < 5:
                        continue
                    parsed = parse_transaction(line)
                    if parsed["amount"] is not None:
                        cat_res = categoriser.categorise(parsed["vendor"])
                        rows.append({
                            "Date":     parsed["date"] or "—",
                            "Raw":      line[:60],
                            "Vendor":   parsed["vendor"] or line[:30],
                            "Amount":   parsed["amount"],
                            "Flow":     "Expense",
                            "Category": cat_res["category"],
                        })
        return pd.DataFrame(rows) if rows else pd.DataFrame()
    except ImportError:
        st.error("pdfplumber not installed. Upload a CSV instead.")
        return pd.DataFrame()


def _render_dashboard(df: pd.DataFrame):
    expenses = df[df["Flow"] == "Expense"]
    income   = df[df["Flow"] == "Income"]

    total_in  = income["Amount"].sum()
    total_out = expenses["Amount"].sum()
    net       = total_in - total_out

    # ── KPI metrics ──
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Total Income",   f"${total_in:,.2f}")
    c2.metric("💸 Total Expenses", f"${total_out:,.2f}")
    delta_str = f"+${net:,.2f}" if net >= 0 else f"-${abs(net):,.2f}"
    c3.metric("📊 Net Cash Flow",  f"${net:,.2f}", delta=delta_str)
    c4.metric("📋 Transactions",   str(len(df)))

    st.markdown("---")

    # ── Charts ──
    chart_left, chart_right = st.columns(2)

    with chart_left:
        st.markdown("#### Spending by Category")
        if not expenses.empty:
            cat_totals = (
                expenses.groupby("Category")["Amount"]
                .sum()
                .reset_index()
                .rename(columns={"Amount": "Total"})
                .sort_values("Total", ascending=False)
            )
            colors = [
                CATEGORY_META.get(c, CATEGORY_META["Uncategorised"])["color"]
                for c in cat_totals["Category"]
            ]
            fig = px.pie(
                cat_totals, names="Category", values="Total",
                hole=0.48, color_discrete_sequence=colors,
            )
            fig.update_traces(
                textposition="outside", textinfo="percent+label",
                textfont_size=11,
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#E5E7EB", size=11),
                showlegend=False,
                margin=dict(t=20, b=20, l=20, r=20),
                height=320,
            )
            st.plotly_chart(fig, use_container_width=True)

    with chart_right:
        st.markdown("#### Top Vendors by Spend")
        if not expenses.empty:
            top = (
                expenses.groupby("Vendor")["Amount"]
                .sum()
                .nlargest(8)
                .reset_index()
                .rename(columns={"Amount": "Total"})
                .sort_values("Total")
            )
            fig2 = px.bar(
                top, x="Total", y="Vendor", orientation="h",
                color="Total",
                color_continuous_scale=["#1D4ED8", "#6366F1", "#8B5CF6"],
                text=top["Total"].apply(lambda x: f"${x:,.0f}"),
            )
            fig2.update_traces(textposition="outside")
            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#E5E7EB"),
                xaxis=dict(showgrid=True, gridcolor="#21262D", color="#8B949E", title=""),
                yaxis=dict(showgrid=False, color="#E5E7EB", title=""),
                coloraxis_showscale=False,
                margin=dict(t=20, b=20, l=20, r=60),
                height=320,
            )
            st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # ── Debt / Finance tracker ──
    debt_kw   = ["loan", "repayment", "mortgage", "interest", "bnpl", "afterpay", "zip pay"]
    debt_mask = (
        (df["Category"] == "Banking & Finance") |
        df["Raw"].str.lower().str.contains("|".join(debt_kw), na=False)
    ) & (df["Flow"] == "Expense")
    debt_df = df[debt_mask]

    if not debt_df.empty:
        debt_total = debt_df["Amount"].sum()
        pct        = (debt_total / total_out * 100) if total_out > 0 else 0
        st.markdown(f"""
<div style="background:#161B22;border:1px solid #1D4ED8;border-radius:10px;
            padding:16px 20px;margin-bottom:16px;display:flex;
            justify-content:space-between;align-items:center;">
  <div>
    <div style="color:#60A5FA;font-size:0.72rem;text-transform:uppercase;
                letter-spacing:1.5px;margin-bottom:5px;">🏦 Debt Servicing & Finance</div>
    <div style="color:#F9FAFB;font-size:1.5rem;font-weight:800;">${debt_total:,.2f}</div>
    <div style="color:#8B949E;font-size:0.8rem;margin-top:3px;">
      {len(debt_df)} transaction{'s' if len(debt_df) != 1 else ''} &nbsp;·&nbsp; {pct:.1f}% of total expenses
    </div>
  </div>
  <div style="text-align:right;">
    {''.join(f'<div style="color:#9CA3AF;font-size:0.83rem;margin-bottom:3px;">{r["Vendor"]} — <span style=\'color:#F87171;\'>−${r[\'Amount\']:,.2f}</span></div>' for _, r in debt_df.head(4).iterrows())}
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Transaction table ──
    st.markdown("#### Full Transaction Ledger")

    f_col1, f_col2 = st.columns([2, 1])
    search   = f_col1.text_input("🔍 Search", placeholder="Filter by vendor, category, date…", key="tbl_search", label_visibility="collapsed")
    all_cats = ["All categories"] + sorted(df["Category"].unique().tolist())
    cat_filt = f_col2.selectbox("", all_cats, key="tbl_cat", label_visibility="collapsed")

    filtered = df.copy()
    if search:
        mask     = filtered.apply(lambda r: search.lower() in str(r).lower(), axis=1)
        filtered = filtered[mask]
    if cat_filt != "All categories":
        filtered = filtered[filtered["Category"] == cat_filt]

    display = filtered[["Date", "Vendor", "Amount", "Flow", "Category"]].copy()
    display["Amount"] = display.apply(
        lambda r: f"+${r['Amount']:,.2f}" if r["Flow"] == "Income" else f"−${r['Amount']:,.2f}",
        axis=1,
    )
    display = display.rename(columns={"Flow": "Type"})

    st.dataframe(
        display,
        use_container_width=True,
        height=min(450, 56 + len(filtered) * 36),
        hide_index=True,
        column_config={
            "Date":     st.column_config.TextColumn("Date",     width="small"),
            "Vendor":   st.column_config.TextColumn("Vendor",   width="medium"),
            "Amount":   st.column_config.TextColumn("Amount",   width="small"),
            "Type":     st.column_config.TextColumn("Type",     width="small"),
            "Category": st.column_config.TextColumn("Category", width="medium"),
        },
    )
    st.caption(f"Showing {len(filtered)} of {len(df)} transactions")


with tab2:
    st.markdown(
        "<div style='color:#8B949E;margin-bottom:16px;font-size:0.95rem;'>"
        "Upload any standard bank export — the engine auto-detects columns, parses every row through "
        "the NLP pipeline, and builds a financial intelligence dashboard. "
        "No data leaves this environment.</div>",
        unsafe_allow_html=True,
    )

    up_col, dl_col = st.columns([3, 1])
    with up_col:
        uploaded = st.file_uploader(
            "Drag & drop your bank statement",
            type=["csv", "pdf"],
            label_visibility="visible",
        )
    with dl_col:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        st.download_button(
            label="⬇  Download Sample CSV",
            data=SAMPLE_CSV.encode(),
            file_name="sample_bank_statement.csv",
            mime="text/csv",
            use_container_width=True,
        )
        st.caption("20 realistic AU bank transactions")

    if uploaded is not None:
        with st.spinner("Parsing transactions through the NLP pipeline…"):
            try:
                if uploaded.name.lower().endswith(".pdf"):
                    results = _parse_pdf(uploaded.read())
                else:
                    df_raw  = pd.read_csv(uploaded)
                    results = _parse_csv(df_raw)
            except Exception as e:
                st.error(f"Could not read file: {e}")
                results = pd.DataFrame()

        if results.empty:
            st.warning("No transactions found. Check the file has a description column and numeric amounts.")
        else:
            st.success(f"✅ Parsed **{len(results)} transactions** from `{uploaded.name}`")
            st.markdown("---")
            _render_dashboard(results)

    else:
        st.markdown("""
<div style="background:#111827;border:1px dashed #374151;border-radius:12px;padding:50px;text-align:center;">
  <div style="font-size:3rem;margin-bottom:14px;">📂</div>
  <div style="color:#6B7280;font-size:0.95rem;line-height:1.7;">
    Upload a bank statement CSV above, or<br>
    click <b style='color:#8B949E;'>⬇ Download Sample CSV</b> to try with a pre-built example
  </div>
</div>
""", unsafe_allow_html=True)
