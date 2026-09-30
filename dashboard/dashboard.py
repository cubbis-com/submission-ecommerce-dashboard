import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ============================================
# KONFIGURASI HALAMAN
# ============================================
st.set_page_config(
    page_title="E-Commerce Dashboard",
    page_icon="🛍️",
    layout="wide"
)

# ============================================
# LOAD DATA
# ============================================
@st.cache_data
def load_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "main_data.csv")
    if not os.path.exists(file_path):
        file_path = "dashboard/main_data.csv"
    df = pd.read_csv(file_path)
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    return df

df = load_data()

# ============================================
# SIDEBAR (FILTER)
# ============================================
st.sidebar.header("🛍️ E-Commerce Dashboard")
st.sidebar.markdown("---")

# Filter Tahun
years = sorted(df['order_purchase_timestamp'].dt.year.unique())
selected_years = st.sidebar.multiselect("Pilih Tahun:", options=years, default=years)

# Filter Kategori
categories = sorted(df['product_category_name_english'].dropna().unique())
selected_cats = st.sidebar.multiselect("Pilih Kategori:", options=categories, default=categories[:10])

st.sidebar.markdown("---")
st.sidebar.markdown("**Dataset:** Brazilian E-Commerce (2016-2018)")

# ============================================
# TERAPKAN FILTER
# ============================================
mask = (
    df['order_purchase_timestamp'].dt.year.isin(selected_years) &
    df['product_category_name_english'].isin(selected_cats)
)
filtered = df[mask].copy()

# ============================================
# HEADER
# ============================================
st.title("📊 Dashboard Analisis E-Commerce")
st.markdown("Analisis untuk menjawab **2 pertanyaan bisnis** utama.")

# ============================================
# KPI CARDS
# ============================================
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Pendapatan", f"R$ {filtered['payment_value'].sum():,.0f}")
c2.metric("Total Pesanan", f"{filtered['order_id'].nunique():,}")
c3.metric("Total Pelanggan", f"{filtered['customer_id'].nunique():,}")
c4.metric("Tingkat Pembatalan", f"{(filtered['order_status']=='canceled').mean()*100:.2f}%")

st.markdown("---")

# ============================================
# TABS
# ============================================
tab1, tab2 = st.tabs([
    "📈 Pertanyaan 1: Pendapatan & Pembatalan",
    "👥 Pertanyaan 2: RFM Analysis"
])

# --- TAB 1 ---
with tab1:
    st.subheader("Pertanyaan Bisnis 1")
    st.info("Kategori produk apa yang pendapatan tertinggi & pembatalan terbesar (2017-2018)?")

    # Chart 1: Pendapatan
    st.markdown("#### Top 10 Kategori Pendapatan")
    rev = (filtered.groupby('product_category_name_english')['payment_value']
           .sum().sort_values(ascending=False).head(10).reset_index())
    rev.columns = ['Kategori', 'Pendapatan']

    fig1 = px.bar(rev, x='Pendapatan', y='Kategori', orientation='h',
                  color='Pendapatan', color_continuous_scale='Blues')
    fig1.update_layout(yaxis={'categoryorder':'total ascending'},
                       xaxis_title='Pendapatan (R$)', yaxis_title='',
                       height=450, showlegend=False)
    st.plotly_chart(fig1, use_container_width=True)

    # Chart 2: Pembatalan
    st.markdown("#### Top 10 Kategori Pembatalan")
    cancel = (filtered.assign(c=filtered['order_status']=='canceled')
              .groupby('product_category_name_english')['c'].mean()
              .sort_values(ascending=False).head(10).reset_index())
    cancel.columns = ['Kategori', 'Tingkat Pembatalan']
    cancel['Tingkat Pembatalan'] = (cancel['Tingkat Pembatalan'] * 100).round(2)

    fig2 = px.bar(cancel, x='Tingkat Pembatalan', y='Kategori', orientation='h',
                  color='Tingkat Pembatalan', color_continuous_scale='Reds')
    fig2.update_layout(xaxis_title='Tingkat Pembatalan (%)', yaxis_title='',
                       height=450, showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

    # Chart 3: Tren
    st.markdown("#### Tren Bulanan Pendapatan")
    monthly = (filtered.groupby(
                   filtered['order_purchase_timestamp'].dt.strftime('%Y-%m')
               )['payment_value'].sum().reset_index())
    monthly.columns = ['Bulan', 'Pendapatan']

    fig3 = px.line(monthly, x='Bulan', y='Pendapatan', markers=True)
    fig3.update_layout(xaxis_title='Bulan', yaxis_title='Pendapatan (R$)', height=400)
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("**Insight:** Kategori `bed_bath_table` & `health_beauty` "
                "memimpin pendapatan. Tren menunjukkan pola musiman dgn puncak akhir tahun.")

# --- TAB 2 ---
with tab2:
    st.subheader("Pertanyaan Bisnis 2 (RFM Analysis)")
    st.info("Bagaimana distribusi RFM pelanggan? Berapa Champions vs At Risk?")

    # Hitung RFM
    snapshot = filtered['order_purchase_timestamp'].max() + pd.Timedelta(days=1)
    last12m = snapshot - pd.DateOffset(months=12)
    rfm_src = filtered[filtered['order_purchase_timestamp'] >= last12m]

    rfm = rfm_src.groupby('customer_id').agg(
        Recency=('order_purchase_timestamp', lambda x: (snapshot - x.max()).days),
        Frequency=('order_id', 'nunique'),
        Monetary=('payment_value', 'sum')
    ).reset_index()

    # Skor
    rfm['R_s'] = pd.qcut(rfm['Recency'], 5, labels=[5,4,3,2,1]).astype(int)
    rfm['F_s'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1,2,3,4,5]).astype(int)
    rfm['M_s'] = pd.qcut(rfm['Monetary'], 5, labels=[1,2,3,4,5]).astype(int)
    rfm['RFM'] = rfm['R_s'] + rfm['F_s'] + rfm['M_s']

    def seg(r):
        s = r['RFM']
        if s >= 13: return 'Champions'
        elif s >= 11: return 'Loyal Customers'
        elif s >= 9: return 'Potential Loyalist'
        elif s >= 7: return 'At Risk'
        else: return 'Lost / Hibernating'

    rfm['Segmen'] = rfm.apply(seg, axis=1)

    # KPI
    k1, k2, k3 = st.columns(3)
    k1.metric("Rata2 Recency", f"{rfm['Recency'].mean():.0f} hari")
    k2.metric("Rata2 Frequency", f"{rfm['Frequency'].mean():.2f}x")
    k3.metric("Rata2 Monetary", f"R$ {rfm['Monetary'].mean():,.0f}")

    st.markdown("---")

    # Chart: Pie Segmen
    st.markdown("#### Distribusi Segmen RFM")
    seg = rfm['Segmen'].value_counts().reset_index()
    seg.columns = ['Segmen', 'Jumlah']

    fig4 = px.pie(seg, names='Segmen', values='Jumlah', hole=0.4,
                  color='Segmen',
                  color_discrete_map={
                      'Champions':'#2ecc71', 'Loyal Customers':'#3498db',
                      'Potential Loyalist':'#9b59b6', 'At Risk':'#e67e22',
                      'Lost / Hibernating':'#e74c3c'
                  })
    fig4.update_traces(textposition='inside', textinfo='percent+label')
    fig4.update_layout(height=450)
    st.plotly_chart(fig4, use_container_width=True)

    # Chart: Scatter
    st.markdown("#### Peta RFM")
    fig5 = px.scatter(rfm, x='Recency', y='Monetary', size='Frequency',
                      color='Segmen',
                      color_discrete_map={
                          'Champions':'#2ecc71', 'Loyal Customers':'#3498db',
                          'Potential Loyalist':'#9b59b6', 'At Risk':'#e67e22',
                          'Lost / Hibernating':'#e74c3c'
                      })
    fig5.update_layout(xaxis_title='Recency (hari)',
                       yaxis_title='Monetary (R$)', height=500)
    st.plotly_chart(fig5, use_container_width=True)

    # Tabel
    st.markdown("#### Ringkasan Segmen")
    summary = rfm.groupby('Segmen').agg(
        Jumlah=('customer_id','count'),
        Rata2_Recency=('Recency','mean'),
        Rata2_Freq=('Frequency','mean'),
        Total_Monetary=('Monetary','sum')
    ).round(1).reset_index()
    st.dataframe(summary, use_container_width=True, hide_index=True)

    # Insight
    ch = (rfm['Segmen']=='Champions').mean()*100
    ar = (rfm['Segmen']=='At Risk').mean()*100
    st.markdown(f"**Insight:** Champions: **{ch:.1f}%** | At Risk: **{ar:.1f}%**")

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown("<p style='text-align:center;color:gray;'>E-Commerce Dashboard | Made with Streamlit</p>",
            unsafe_allow_html=True)