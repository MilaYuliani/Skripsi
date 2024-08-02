import pandas as pd
import mysql.connector
from collections import Counter
import re

# Konfigurasi koneksi database
config = {
    'user': 'root',
    'password': '',  # Sesuaikan dengan password MySQL Anda
    'host': 'localhost',
    'database': 'databanjir'  # Sesuaikan dengan nama database Anda
}

# Buat koneksi ke database
conn = mysql.connector.connect(**config)
cursor = conn.cursor()

# Ambil data dari tabel 'clusters'
query = "SELECT cluster_id, text FROM clusters"
df = pd.read_sql(query, conn)

# Periksa apakah kolom 'text' ada dalam DataFrame
if 'text' not in df.columns:
    print("Kolom 'text' tidak ditemukan dalam tabel 'clusters'")
    print("Kolom yang tersedia:", df.columns)
    conn.close()
    exit()

# Fungsi untuk menghitung frekuensi kata


def count_terms(docs):
    all_terms = ' '.join(docs).split()
    term_frequencies = Counter(all_terms)
    return term_frequencies

# Fungsi untuk mengekstrak dan mengumpulkan lokasi dari teks


def extract_locations(texts, location_dict):
    locations = []
    for text in texts:
        found_locations = []
        for keyword in location_dict.keys():
            if re.search(r'\b' + re.escape(keyword) + r'\b', text, re.IGNORECASE):
                found_locations.append(location_dict[keyword])
        locations.extend(found_locations)
    return locations


# Daftar kata kunci lokasi dan wilayahnya
location_dict = {
    'jakarta': 'jakarta', 'bandung': 'jawa barat', 'cirebon': 'jawa barat', 'semarang': 'jawa tengah', 'surabaya': 'jawa timur', 'demak': 'jawa tengah', 'padang': 'sumatra barat',
    'sumatra barat': 'sumatra barat', 'gunung marapi': 'sumatra barat', 'tanah datar': 'sumatra barat', 'agam': 'sumatra barat', 'indonesia': 'indonesia', 'sumsel': 'sumatra selatan', 'lumajang': 'jawa timur',
    'aceh': 'aceh', 'bali': 'bali', 'banten': 'banten', 'bengkulu': 'bengkulu', 'gorontalo': 'gorontalo',
    'jambi': 'jambi', 'jawa barat': 'jawa barat', 'jawa tengah': 'jawa tengah', 'jawa timur': 'jawa timur',
    'kalimantan barat': 'kalimantan barat', 'kalimantan selatan': 'kalimantan selatan', 'kalimantan tengah': 'kalimantan tengah',
    'kalimantan timur': 'kalimantan timur', 'kalimantan utara': 'kalimantan utara', 'kepulauan bangka belitung': 'kepulauan bangka belitung',
    'kepulauan riau': 'kepulauan riau', 'lampung': 'lampung', 'maluku': 'maluku', 'maluku utara': 'maluku utara',
    'nusa tenggara barat': 'nusa tenggara barat', 'nusa tenggara timur': 'nusa tenggara timur', 'papua': 'papua',
    'papua barat': 'papua barat', 'riau': 'riau', 'sulawesi barat': 'sulawesi barat', 'sulawesi selatan': 'sulawesi selatan',
    'sulawesi tengah': 'sulawesi tengah', 'sulawesi tenggara': 'sulawesi tenggara', 'sulawesi utara': 'sulawesi utara',
    'sumatra selatan': 'sumatra selatan', 'sumatra utara': 'sumatra utara'
}

# Daftar kata kunci jenis banjir
banjir_dict = {
    'banjir rob': 'banjir rob', 'banjir bandang': 'banjir bandang', 'banjir lahar': 'banjir lahar',
    'banjir sungai': 'banjir sungai', 'banjir genangan': 'banjir genangan'
}

# Fungsi untuk mengekstrak jenis banjir dari teks


def extract_banjir_type(texts, banjir_dict):
    banjir_types = []
    for text in texts:
        for keyword in banjir_dict.keys():
            if re.search(r'\b' + re.escape(keyword) + r'\b', text, re.IGNORECASE):
                banjir_types.append(banjir_dict[keyword])
    return banjir_types


# Pisahkan dokumen berdasarkan klaster
clusters = df.groupby('cluster_id')['text'].apply(list).to_dict()

# Hitung frekuensi kata untuk setiap klaster
frequencies = {cluster_id: count_terms(docs)
               for cluster_id, docs in clusters.items()}

# Identifikasi tiga term utama untuk setiap klaster beserta frekuensinya


def top_n_terms(frequencies, n=3):
    return dict(Counter(frequencies).most_common(n))


top_terms = {cluster_id: top_n_terms(freq)
             for cluster_id, freq in frequencies.items()}

# Ekstrak lokasi untuk setiap klaster
locations = {cluster_id: extract_locations(
    docs, location_dict) for cluster_id, docs in clusters.items()}

# Ekstrak jenis banjir untuk setiap klaster
banjir_types = {cluster_id: extract_banjir_type(
    docs, banjir_dict) for cluster_id, docs in clusters.items()}

# Buat nama klaster berdasarkan tiga kata teratas, jenis banjir, dan lokasi teratas
cluster_names = {}
for cluster_id in clusters.keys():
    top_3_terms = list(top_terms[cluster_id].keys())
    banjir_type = Counter(banjir_types[cluster_id]).most_common(
        1)[0][0] if banjir_types[cluster_id] else 'banjir'
    location = Counter(locations[cluster_id]).most_common(
        1)[0][0] if locations[cluster_id] else 'Unknown'
    cluster_name = f"{' '.join(top_3_terms[:3])} - {banjir_type} - {location}"
    cluster_names[cluster_id] = cluster_name

# Simpan hasil perhitungan frekuensi kata ke database MySQL
for cluster_id, freq_dict in frequencies.items():
    for term, frequency in freq_dict.items():
        location = Counter(locations[cluster_id]).most_common(
            1)[0][0] if locations[cluster_id] else 'Unknown'
        cluster_name = cluster_names[cluster_id]
        insert_query = "INSERT INTO analisis (cluster_id, text, frequency, location, cluster_name) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(insert_query, (cluster_id, term,
                       frequency, location, cluster_name))

# Commit perubahan dan tutup koneksi
conn.commit()
cursor.close()
conn.close()

# Print hasil analisis klaster untuk verifikasi
for cluster_id in clusters.keys():
    print(f"Cluster ID: {cluster_id}")

    # Menampilkan 3 top term tertinggi
    print("Top 3 Term:")
    for idx, (term, freq) in enumerate(top_terms[cluster_id].items(), 1):
        print(f"{idx}. {term}: {freq}")

    # Menampilkan top lokasi
    print(
        f"Top Location: {Counter(locations[cluster_id]).most_common(1)[0][0] if locations[cluster_id] else 'Unknown'}")

    # Menampilkan jenis banjir teratas
    print(
        f"Top Banjir Type: {Counter(banjir_types[cluster_id]).most_common(1)[0][0] if banjir_types[cluster_id] else 'banjir'}")

    print("\n---------------------------------\n")

print("Hasil telah disimpan ke database MySQL.")
