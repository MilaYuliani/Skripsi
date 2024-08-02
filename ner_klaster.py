import mysql.connector
from collections import Counter
# Sesuaikan dengan modul NER Anda
from ner_new import tokenize_and_assign_features, apply_ner_rules

# Fungsi koneksi ke database MySQL


def connect_to_db():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='databanjir'
    )
    return connection

# Fungsi untuk mengambil semua klaster dari tabel clusters


def get_clusters():
    connection = connect_to_db()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT cluster_id, COUNT(*) AS jumlah_dokumen FROM clusters GROUP BY cluster_id ORDER BY cluster_id")
        clusters = cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        clusters = []
    finally:
        cursor.close()
        connection.close()

    return clusters

# Fungsi untuk ekstraksi lokasi dari teks klaster dan penyimpanan hasilnya ke dalam tabel analisis


def extract_and_save_locations(cluster_id, texts):
    connection = connect_to_db()
    cursor = connection.cursor()

    try:
        # Gabungkan teks dari semua dokumen dalam klaster
        combined_text = ' '.join(text['text'] for text in texts)

        # Tokenisasi dan penugasan fitur
        tokens = tokenize_and_assign_features(combined_text)

        # Terapkan NER
        ner_results = apply_ner_rules(tokens)

        # Ekstrak lokasi dari hasil NER
        location_entities = [token['teks_kata']
                             for token in ner_results if token['type_ner'] == 'LOCATION']
        location_text = ', '.join(location_entities)

        # Mengambil semua label dari klaster
        labels = get_labels_for_cluster(cluster_id)
        label_utama = ', '.join(labels)

        # Hitung kategori klaster (label mayoritas)
        kategori_klaster = get_majority_label_for_cluster(cluster_id)

        # Tampilkan informasi di terminal
        print(f"Cluster ID: {cluster_id}")
        print(f"Jumlah Dokumen: {len(texts)}")
        print(f"Extracted Locations: {location_text}")
        print(f"All Labels: {label_utama}")
        print(f"Cluster Category (Majority Label): {kategori_klaster}")
        print()

        # Simpan hasil ekstraksi ke dalam tabel analisis
        if location_text.strip():
            save_to_analisis(cluster_id, label_utama,
                             location_text, kategori_klaster)

        print(f"Data untuk cluster ID {cluster_id} berhasil diproses.")
    except mysql.connector.Error as err:
        print(f"Error saat memproses klaster: {err}")
    finally:
        cursor.close()
        connection.close()

# Fungsi untuk mengambil semua label unik dari klaster berdasarkan cluster_id


def get_labels_for_cluster(cluster_id):
    connection = connect_to_db()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "SELECT DISTINCT label FROM clusters WHERE cluster_id = %s", (cluster_id,))
        results = cursor.fetchall()
        labels = [result[0] for result in results]
    except mysql.connector.Error as err:
        print(f"Error while fetching labels for cluster {cluster_id}: {err}")
        labels = []
    finally:
        cursor.close()
        connection.close()

    return labels

# Fungsi untuk menghitung label mayoritas dari klaster berdasarkan cluster_id


def get_majority_label_for_cluster(cluster_id):
    connection = connect_to_db()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "SELECT label FROM clusters WHERE cluster_id = %s", (cluster_id,))
        results = cursor.fetchall()
        labels = [result[0] for result in results]

        # Menghitung frekuensi setiap label
        label_counts = Counter(labels)

        # Menentukan label dengan frekuensi tertinggi sebagai mayoritas
        majority_label = label_counts.most_common(
            1)[0][0] if label_counts else ''

    except mysql.connector.Error as err:
        print(
            f"Error while fetching majority label for cluster {cluster_id}: {err}")
        majority_label = ''
    finally:
        cursor.close()
        connection.close()

    return majority_label

# Fungsi untuk menyimpan hasil ekstraksi ke dalam tabel analisis


def save_to_analisis(cluster_id, label_utama, location_text, kategori_klaster):
    connection = connect_to_db()
    cursor = connection.cursor()

    try:
        cursor.execute("INSERT INTO analisis (cluster_id, label_utama, location, kategori_klaster) VALUES (%s, %s, %s, %s)",
                       (cluster_id, label_utama, location_text, kategori_klaster))
        connection.commit()
        print(
            f"Data untuk cluster ID {cluster_id} berhasil disimpan dengan lokasi: {location_text}")
    except mysql.connector.Error as err:
        print(f"Error saat menyimpan data ke database: {err}")
    finally:
        cursor.close()
        connection.close()

# Fungsi utama untuk memproses semua klaster


def process_clusters():
    clusters = get_clusters()

    # Memproses setiap klaster
    for cluster in clusters:
        cluster_id = cluster['cluster_id']

        # Mengambil semua dokumen dalam klaster
        connection = connect_to_db()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT text FROM clusters WHERE cluster_id = %s", (cluster_id,))
            texts = cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            texts = []
        finally:
            cursor.close()
            connection.close()

        # Ekstraksi dan simpan lokasi dari teks gabungan klaster
        extract_and_save_locations(cluster_id, texts)


if __name__ == "__main__":
    process_clusters()
