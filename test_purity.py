import pandas as pd
import mysql.connector

# Fungsi untuk mengambil data teks yang telah diproses dari database


def fetch_processed_data(db_config):
    try:
        conn = mysql.connector.connect(**db_config)
        query = "SELECT text_bersih FROM proses"
        data = pd.read_sql(query, conn)
        conn.close()
        return data
    except Exception as e:
        print("Error:", str(e))
        return pd.DataFrame()

# Fungsi untuk mengambil hasil clustering dari database


def fetch_clusters_from_db(db_config):
    try:
        conn = mysql.connector.connect(**db_config)
        query = "SELECT cluster_id, text, label FROM clusters"
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data
    except Exception as e:
        print("Error:", str(e))
        return []

# Fungsi untuk menghitung purity berdasarkan rumus yang diberikan


def calculate_purity(cluster_data):
    clusters = {}
    total_documents = len(cluster_data)

    # Mengelompokkan dokumen berdasarkan cluster dan menghitung jumlah dokumen per cluster
    for row in cluster_data:
        cluster_id = row['cluster_id']
        label = row['label']
        if cluster_id not in clusters:
            clusters[cluster_id] = {'total_documents': 0, 'label_counts': {}}
        clusters[cluster_id]['total_documents'] += 1

        if label not in clusters[cluster_id]['label_counts']:
            clusters[cluster_id]['label_counts'][label] = 0
        clusters[cluster_id]['label_counts'][label] += 1

    # Menghitung purity per cluster
    total_purity = 0
    purity_per_cluster = []
    for cluster_id, cluster_info in clusters.items():
        total_documents_in_cluster = cluster_info['total_documents']
        majority_label_count = max(cluster_info['label_counts'].values())
        purity = majority_label_count / total_documents_in_cluster
        # Sesuai rumus, menghitung total dokumen mayoritas di semua cluster
        total_purity += majority_label_count
        quality = 'Baik' if purity >= 0.5 else 'Buruk'
        purity_per_cluster.append(
            {'Cluster_ID': cluster_id, 'Purity': purity, 'Quality': quality, 'Jumlah_Tweet': total_documents_in_cluster})

    # Menghitung purity keseluruhan sesuai rumus
    overall_purity = total_purity / total_documents

    # Menghitung purity rata-rata
    average_purity = sum([cluster['Purity']
                         for cluster in purity_per_cluster]) / len(purity_per_cluster)

    return purity_per_cluster, overall_purity, average_purity

# Fungsi untuk menyimpan hasil purity ke database


def save_purity_to_db(purity_results, db_config):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        for row in purity_results:
            cluster_id = row['Cluster_ID']
            purity = row['Purity']
            quality = row['Quality']
            jumlah_tweet = row['Jumlah_Tweet']
            query = "INSERT INTO purity_results (cluster_id, purity, quality, jumlah_tweet) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (cluster_id, purity, quality, jumlah_tweet))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("Error:", str(e))


# Konfigurasi koneksi ke database
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'databanjir'
}

# Membaca hasil clustering dari database
cluster_data = fetch_clusters_from_db(db_config)

# Menghitung purity
purity_results, overall_purity, average_purity = calculate_purity(cluster_data)

# Menyimpan hasil purity per cluster ke database
save_purity_to_db(purity_results, db_config)

# Menampilkan overall purity dan rata-rata purity
# print("Overall Purity: {:.4f}".format(overall_purity))
# print("Average Purity: {:.4f}".format(average_purity))
