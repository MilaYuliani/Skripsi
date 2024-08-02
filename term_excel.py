import pandas as pd
import mysql.connector
from collections import Counter
import os
import re

# Konfigurasi koneksi database sesuai dengan pengaturan PHP Anda
config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'databanjir'
}

# Buat koneksi ke database
conn = mysql.connector.connect(**config)

# Ambil data dari tabel 'clusters'
query = "SELECT cluster_id, text FROM clusters"
df = pd.read_sql(query, conn)

# Tutup koneksi
conn.close()

# Periksa apakah kolom 'text' ada dalam DataFrame
if 'text' not in df.columns:
    print("Kolom 'text' tidak ditemukan dalam tabel 'clusters'")
    print("Kolom yang tersedia:", df.columns)
    exit()

# Fungsi untuk menghitung frekuensi kata (terms) per dokumen dalam klaster


def count_terms_per_document(documents):
    term_frequencies_per_document = []
    for doc in documents:
        terms = re.findall(r'\b\w+\b', doc.lower())
        term_frequencies_per_document.append(Counter(terms))
    return term_frequencies_per_document

# Fungsi untuk mengekstrak dan menghitung lokasi per dokumen dalam klaster


def extract_and_count_locations_per_document(documents, location_dict):
    location_counts_per_document = []
    all_detected_locations = []
    for doc in documents:
        found_locations = []
        for keyword, location in location_dict.items():
            if re.search(r'\b' + re.escape(keyword) + r'\b', doc, re.IGNORECASE):
                found_locations.append(location)
        location_counts_per_document.extend(found_locations)
        all_detected_locations.extend(found_locations)
    return Counter(location_counts_per_document), all_detected_locations


# Daftar kata kunci lokasi dan wilayahnya
location_dict = {
    'jakarta': 'Jakarta', 'bandung': 'Jawa Barat', 'cirebon': 'Jawa Barat',
    'semarang': 'Jawa Tengah', 'surabaya': 'Jawa Timur', 'demak': 'Jawa Tengah',
    'padang': 'Sumatra Barat', 'sumatra barat': 'Sumatra Barat',
    'gunung marapi': 'Sumatra Barat', 'tanah datar': 'Sumatra Barat',
    'agam': 'Sumatra Barat', 'indonesia': 'Indonesia', 'sumsel': 'Sumatra Selatan',
    'lumajang': 'Jawa Timur', 'aceh': 'Aceh', 'bali': 'Bali', 'banten': 'Banten',
    'bengkulu': 'Bengkulu', 'gorontalo': 'Gorontalo', 'jambi': 'Jambi',
    'jawa barat': 'Jawa Barat', 'jawa tengah': 'Jawa Tengah', 'jawa timur': 'Jawa Timur',
    'kalimantan barat': 'Kalimantan Barat', 'kalimantan selatan': 'Kalimantan Selatan',
    'kalimantan tengah': 'Kalimantan Tengah', 'kalimantan timur': 'Kalimantan Timur',
    'kalimantan utara': 'Kalimantan Utara', 'kepulauan bangka belitung': 'Kepulauan Bangka Belitung',
    'kepulauan riau': 'Kepulauan Riau', 'lampung': 'Lampung', 'maluku': 'Maluku',
    'maluku utara': 'Maluku Utara', 'nusa tenggara barat': 'Nusa Tenggara Barat',
    'nusa tenggara timur': 'Nusa Tenggara Timur', 'papua': 'Papua',
    'papua barat': 'Papua Barat', 'riau': 'Riau', 'sulawesi barat': 'Sulawesi Barat',
    'sulawesi selatan': 'Sulawesi Selatan', 'sulawesi tengah': 'Sulawesi Tengah',
    'sulawesi tenggara': 'Sulawesi Tenggara', 'sulawesi utara': 'Sulawesi Utara',
    'sumatra selatan': 'Sumatra Selatan', 'sumatra utara': 'Sumatra Utara'
}

# Pisahkan dokumen berdasarkan klaster
clusters = df.groupby('cluster_id')['text'].apply(list).to_dict()

# Hitung frekuensi kata per dokumen untuk setiap klaster
term_frequencies = {cluster_id: count_terms_per_document(
    docs) for cluster_id, docs in clusters.items()}

# Ekstrak dan hitung lokasi per dokumen untuk setiap klaster
location_counts = {cluster_id: extract_and_count_locations_per_document(
    docs, location_dict) for cluster_id, docs in clusters.items()}

# Buat DataFrame untuk menyimpan hasil analisis klaster
result_data = {
    'Cluster ID': [],
    'Top Term 1': [],
    'Top Term 1 Frequency': [],
    'Top Term 2': [],
    'Top Term 2 Frequency': [],
    'Top Term 3': [],
    'Top Term 3 Frequency': [],
    'Location': [],
    'Location Frequency': [],
    'All Locations': [],
    'Cluster Name': []
}

# Mengisi data ke dalam result_data
for cluster_id, term_freqs in term_frequencies.items():
    result_data['Cluster ID'].append(cluster_id)
    terms_combined = Counter()
    for term_freq in term_freqs:
        terms_combined.update(term_freq)
    top_terms = terms_combined.most_common(3)
    result_data['Top Term 1'].append(
        top_terms[0][0] if len(top_terms) > 0 else '')
    result_data['Top Term 1 Frequency'].append(
        top_terms[0][1] if len(top_terms) > 0 else 0)
    result_data['Top Term 2'].append(
        top_terms[1][0] if len(top_terms) > 1 else '')
    result_data['Top Term 2 Frequency'].append(
        top_terms[1][1] if len(top_terms) > 1 else 0)
    result_data['Top Term 3'].append(
        top_terms[2][0] if len(top_terms) > 2 else '')
    result_data['Top Term 3 Frequency'].append(
        top_terms[2][1] if len(top_terms) > 2 else 0)

    locations_combined, all_locations = location_counts[cluster_id]
    if locations_combined:
        top_location = locations_combined.most_common(
            1)[0]  # Mengambil yang paling umum
        result_data['Location'].append(top_location[0])
        result_data['Location Frequency'].append(top_location[1])
        result_data['All Locations'].append(
            ', '.join([f"{loc} ({freq})" for loc, freq in locations_combined.items()]))
    else:
        result_data['Location'].append('Unknown')
        result_data['Location Frequency'].append(0)
        result_data['All Locations'].append('')

    if result_data['Location'][-1] != 'Unknown':
        result_data['Cluster Name'].append(
            f"{result_data['Top Term 1'][-1]} - {result_data['Location'][-1]}")
    else:
        result_data['Cluster Name'].append(
            f"{result_data['Top Term 1'][-1]} - Unknown")

# Membuat DataFrame dari result_data
df_result = pd.DataFrame(result_data)

# Tentukan path absolut untuk menyimpan file Excel
output_dir = os.path.abspath('.')
excel_filename = os.path.join(output_dir, 'hasil_analisis_klaster.xlsx')

# Simpan hasil ke dalam file Excel
with pd.ExcelWriter(excel_filename) as writer:
    # Menyimpan hasil analisis klaster ke dalam sheet 'Hasil Analisis Klaster'
    df_result.to_excel(
        writer, sheet_name='Hasil Analisis Klaster', index=False)

    # Menyiapkan data untuk frekuensi kata
    term_frequency_data = []
    for cluster_id, term_freqs in term_frequencies.items():
        cluster_terms = {}
        for term_freq in term_freqs:
            cluster_terms.update(term_freq)
        cluster_terms['Cluster ID'] = cluster_id
        term_frequency_data.append(cluster_terms)

    # Membuat DataFrame untuk frekuensi kata per klaster
    df_term_frequency = pd.DataFrame(term_frequency_data)

    # Menyimpan frekuensi kata ke dalam sheet 'Frekuensi Kata per Klaster'
    df_term_frequency.to_excel(
        writer, sheet_name='Frekuensi Kata per Klaster', index=False)

print(
    f"Hasil analisis klaster dan frekuensi kata telah disimpan ke dalam file {excel_filename}")
