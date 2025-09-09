import streamlit as st
import pandas as pd

# Judul utama
st.markdown("<h1 style='text-align: center;'> Program Katalog UMKM </h1>", unsafe_allow_html=True)

# Inisialisasi variabel biar aman
if "data" not in st.session_state:
    st.session_state["data"] = None
if "filters" not in st.session_state:
    st.session_state["filters"] = {}
    
data = st.session_state["data"]  # supaya aman dipanggil
filtered = None

# ================= TAMBAH PRODUK =================

st.header("Upload File Data")

upload_file = st.file_uploader("Masukkan file CSV/Excel", type=["csv", "xlsx"])
if upload_file is None:
    st.info("Silakan upload file csv/excel anda")
    with st.expander("Lihat Ini"):
            st.warning("Program ini masih level MVP artinya tdk semua file csv/excel akan berhasil diupload")
else:
    try:
        if upload_file.name.endswith(".csv"):
            data = pd.read_csv(upload_file, delimiter=";")
        else:
            data = pd.read_excel(upload_file)

        
        # Bersihkan data
        data = data.dropna(how="all")
        data = data.dropna(axis=1, how="all")
        data.columns = [col.strip() for col in data.columns]

        # Simpan di session_state
        st.session_state["data"] = data
        st.success("File berhasil diupload!")
        with st.expander("Kualitas File Anda"):
            rows, cols = data.shape
            st.write(f"File terbaca: **{rows} baris, {cols} kolom**")
            missing = data.isnull().sum()
            missing_percent = (missing / len(data)) * 100
            for col, val in missing_percent.items():
                if val > 0:
                    st.write(f"Kolom **{col}**: {val:.1f}% kosong")
    
            for col in data.columns:
                numeric_col = pd.to_numeric(data[col], errors="coerce")

                if numeric_col.notnull().sum() > 0:  # ada angka valid
                    st.write(f"Kolom **{col}**: min={numeric_col.min()}, max={numeric_col.max()}")

                    if numeric_col.isnull().sum() > 0:
                        st.warning(f"Kolom {col} ada nilai non-numeric!")

        # Deteksi kolom teks yang harusnya numeric (ID/EAN)
            for col in data.columns:
                if data[col].dtype == "object":
                    # cek kalau mayoritas berupa angka
                    numeric_ratio = data[col].str.isnumeric().mean()
                    if numeric_ratio > 0.8:
                        lengths = data[col].dropna().astype(str).str.len().value_counts()
                        if len(lengths) > 1:
                            st.warning(f"Kolom **{col}** panjangnya tidak konsisten.")
                            st.write(f"Distribusi panjang {col}:")
                            st.write(lengths)
            st.warning("Program ini masih level MVP artinya tdk semua file csv/excel akan berhasil diupload")
        st.divider()

    except Exception as e:
        st.error(f"Gagal memproses file: {e}")

# ================= EDIT PRODUK =================
col1, col2 = st.columns([1, 2])
with col1:
    st.header("Filter Data")
    if st.session_state["data"] is not None:
        data = st.session_state["data"]
    
        try:
            col_to_filter = data.select_dtypes(include=["object", "string"]).columns

            for col in col_to_filter:
                options = list(pd.unique(data[col].dropna()))

                # Default: semua opsi dipilih
                if col not in st.session_state["filters"]:
                    st.session_state["filters"][col] = options

                selected = st.multiselect(
                    f"Filter {col}",
                    options=options,
                    default=st.session_state["filters"][col]
                )
            
                st.session_state["filters"][col] = selected

                # Terapkan filter
                filtered = data.copy()
                for col, selected in st.session_state["filters"].items():
                    if selected and len(selected) < len(data[col].unique()):
                        filtered = filtered[filtered[col].isin(selected)]

                st.success("Filter berhasil diterapkan!")
        except Exception as e:
            st.error(f"Gagal memproses filter: {e}")
    
    else:
        st.warning("Belum ada data. Silakan upload file terlebih dahulu di menu Tambah Produk.")
    st.divider()
with col2:
    st.header("Visualisasi data")
    if filtered is None:
        st.warning("Belum ada data. Silakan upload file terlebih dahulu di menu Tambah Produk.")
        
    else:
        col_chart = st.selectbox("Pilih kolom untuk divisualisasikan", filtered.columns)
    st.divider()
        
# ================= KATALOG =================

st.header("Katalog Produk")
tab1, tab2, tab3 = st.tabs(["Tabel Asli","Tabel Hasil Filter","Visualisasi Data"])
with tab1:
    st.subheader("Tabel")
    if data is None:
        st.warning("Belum ada data. Silakan upload file terlebih dahulu di menu Tambah Produk.")
        st.divider()
    else:
        st.dataframe(data, use_container_width=True)
with tab2:
    st.subheader("Hasil Filter")
    if filtered is None:
        st.warning("Belum ada hasil filter. Silakan filter data terlebih dahulu di menu Tambah Produk.")
        st.divider()
    else:
        if len(filtered) == len(data):
            st.warning("Belum ada hasil filter. Silakan filter data terlebih dahulu di menu Tambah Produk.")
            st.divider()
        else:
            st.dataframe(filtered)
with tab3:
    st.subheader("Visualisasi Data")
    try:
        if data is None:
            st.warning("Belum ada file yg diupload. Silakan upload file terlebih dahulu di menu Tambah Produk.")
            st.divider()
        else:
            if filtered[col_chart].dtype in ["object", "string"]:
                chart_data = filtered[col_chart].value_counts().reset_index()
                chart_data.columns = [col_chart, "Jumlah"]
                st.bar_chart(chart_data.set_index(col_chart))
            else:
                st.line_chart(filtered[col_chart])
    except Exception as e:
        st.error(f"Gagal membuat chart: {e}")
        st.divider()
