import mysql.connector
from collections import Counter

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

try:
    # Ambil data dari tabel 'clusters'
    select_query = "SELECT cluster_id, label FROM clusters"
    cursor.execute(select_query)
    clusters_data = cursor.fetchall()

    # Periksa apakah data diambil dengan benar
    if not clusters_data:
        print("Tidak ada data yang ditemukan di tabel 'clusters'")
        conn.close()
        exit()

    # Menghitung jumlah tweet per label dan per cluster_id
    tweet_counts = {}
    total_tweets_per_cluster = {}
    for cluster_id, label in clusters_data:
        if cluster_id not in tweet_counts:
            tweet_counts[cluster_id] = Counter()
        tweet_counts[cluster_id][label] += 1

        if cluster_id not in total_tweets_per_cluster:
            total_tweets_per_cluster[cluster_id] = 0
        total_tweets_per_cluster[cluster_id] += 1

    # Fungsi untuk menentukan label terbanyak dalam setiap klaster
    def most_common_label(cluster_id):
        if cluster_id in tweet_counts:
            return tweet_counts[cluster_id].most_common(1)[0]
        else:
            return ('Unknown', 0)

    # Mengurutkan cluster_id
    sorted_cluster_ids = sorted(tweet_counts.keys())

    # Print hasil untuk verifikasi
    for cluster_id in sorted_cluster_ids:
        cluster_name, tweet_count = most_common_label(cluster_id)
        total_tweets = total_tweets_per_cluster[cluster_id]
        print(f"Cluster ID: {cluster_id}")
        print(f"Cluster Name: {cluster_name}")
        print(f"Jumlah Tweets: {total_tweets}")
        print("\n---------------------------------\n")

    print("Nama klaster ditampilkan di terminal, diurutkan berdasarkan cluster_id.")

except mysql.connector.Error as err:
    print(f"Error: {err}")

finally:
    # Tutup koneksi
    cursor.close()
    conn.close()
