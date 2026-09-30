# E-Commerce Public Dataset Dashboard 🛍️

Dashboard interaktif berbasis Streamlit untuk menganalisis data transaksi E-Commerce publik (Brazilian E-Commerce dataset).

## Pertanyaan Bisnis
1. Kategori produk apa saja yang menghasilkan total pendapatan tertinggi dan memiliki tingkat pembatalan order terbesar selama periode Januari 2017 hingga Desember 2018?
2. Bagaimana distribusi RFM (Recency, Frequency, Monetary) pelanggan berdasarkan transaksi 12 bulan terakhir dataset, dan berapa persen pelanggan yang termasuk segmen Champions dibandingkan segmen At Risk?

---

## Setup Environment - Anaconda
```bash
conda create --name main-ds python=3.9
conda activate main-ds
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal
```bash
mkdir proyek_analisis_data
cd proyek_analisis_data
pipenv install
pipenv shell
pip install -r requirements.txt
```

Atau menggunakan `venv` bawaan Python:
```bash
python -m venv venv
source venv/bin/activate  # Untuk Linux/macOS
# venv\Scripts\activate   # Untuk Windows
pip install -r requirements.txt
```

---

## Run Streamlit App
Jalankan perintah berikut dari root direktori proyek:
```bash
streamlit run dashboard/dashboard.py
```

Atau jika berpindah ke dalam folder `dashboard`:
```bash
cd dashboard
streamlit run dashboard.py
```

---

## Live Dashboard URL
Aplikasi dashboard ini juga dapat diakses secara daring melalui Streamlit Cloud:
- **URL:** [https://submission-ecommerce-dashboard-89intb4uch9vxy63w3svh3.streamlit.app/](https://submission-ecommerce-dashboard-89intb4uch9vxy63w3svh3.streamlit.app/)
