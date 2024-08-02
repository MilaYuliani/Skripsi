import pandas as pd
import mysql.connector
import random
import sys

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

# Fungsi untuk mengambil hasil clustering dari database dengan LIMIT dan urutan


def fetch_clusters_from_db_with_limit_and_order(db_config, start, limit, order_by):
    try:
        conn = mysql.connector.connect(**db_config)
        query = "SELECT cluster_id, text, label FROM clusters ORDER BY {} LIMIT %s, %s".format(
            order_by)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, (start, limit))
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data
    except Exception as e:
        print("Error:", str(e))
        return []

# Fungsi untuk mengambil 100 dokumen acak dari seluruh dataset


def fetch_100_random_documents(db_config):
    try:
        conn = mysql.connector.connect(**db_config)
        seed = 12345  # Misalnya, menggunakan seed 12345
        query = "SELECT cluster_id, text, label FROM clusters ORDER BY RAND(%s) LIMIT 100"
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, (seed,))
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data
    except Exception as e:
        print("Error:", str(e))
        return []

# Fungsi untuk mengambil 200 dokumen acak dari seluruh dataset


def fetch_200_random_documents(db_config):
    try:
        conn = mysql.connector.connect(**db_config)
        seed = 54321  # Misalnya, menggunakan seed 54321
        query = "SELECT cluster_id, text, label FROM clusters ORDER BY RAND(%s) LIMIT 200"
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, (seed,))
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
        purity = majority_label_count / \
            total_documents_in_cluster if total_documents_in_cluster > 0 else 0
        total_purity += majority_label_count
        quality = 'Baik' if purity >= 0.5 else 'Buruk'
        purity_per_cluster.append({
            'Cluster_ID': cluster_id,
            'Purity': purity,
            'Quality': quality,
            'Jumlah_Tweet': total_documents_in_cluster
        })

    # Menghitung purity keseluruhan sesuai rumus
    overall_purity = total_purity / total_documents if total_documents > 0 else 0

    # Menghitung purity rata-rata
    average_purity = sum([cluster['Purity'] for cluster in purity_per_cluster]) / \
        len(purity_per_cluster) if len(purity_per_cluster) > 0 else 0

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

# Fungsi utama untuk mengatur alur eksekusi dan output


def main():
    try:
        # Konfigurasi koneksi ke database
        db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': '',
            'database': 'databanjir'
        }

        # Menjalankan fungsi untuk mengambil data dari database
        cluster_data_100_random = fetch_100_random_documents(db_config)
        cluster_data_200_random = fetch_200_random_documents(db_config)
        cluster_data_all = fetch_clusters_from_db_with_limit_and_order(
            db_config, 0, 9999999, "id")

        # Menghitung purity untuk masing-masing jenis dokumen
        purity_results_100_random, overall_purity_100_random, average_purity_100_random = calculate_purity(
            cluster_data_100_random)
        purity_results_200_random, overall_purity_200_random, average_purity_200_random = calculate_purity(
            cluster_data_200_random)
        purity_results_all, overall_purity_all, average_purity_all = calculate_purity(
            cluster_data_all)

        # Menyimpan hasil purity ke database
        save_purity_to_db(purity_results_all, db_config)

        # Menampilkan hasil purity keseluruhan dari skrip Python
        print(overall_purity_100_random)
        print(overall_purity_200_random)
        print(overall_purity_all)

    except Exception as e:
        print("Error:", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
