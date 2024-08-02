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


# Konfigurasi koneksi ke database
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'databanjir'
}

# Mengambil data yang telah diproses
data_twitter = fetch_processed_data(db_config)

# Mengambil kolom 'text_bersih' sebagai list
tweet_list = data_twitter['text_bersih'].tolist()

# Membuat dataframe dari daftar tweet yang telah dibersihkan
df_twitter = pd.DataFrame({'text_bersih': tweet_list})

# Fungsi untuk menghitung Jaccard Similarity


def jaccard_similarity(list1, list2):
    s1 = set(list1)
    s2 = set(list2)
    return float(len(s1.intersection(s2)) / len(s1.union(s2)))


# Variabel untuk menyimpan hasil perhitungan Jaccard
first_pair_jaccard = []
second_pair_jaccard = []
key_score_jaccard = []

# Loop untuk menghitung nilai Jaccard antara setiap pasangan tweet
for row in df_twitter.itertuples():
    for text in df_twitter.itertuples():
        word_set_1 = set(row[1].split())
        word_set_2 = set(text[1].split())
        score_jaccard_tweet = jaccard_similarity(word_set_1, word_set_2)
        if 0 < score_jaccard_tweet <= 0.5:  # Menghindari nilai Jaccard 0 dan 1
            first_pair_jaccard.append(row.Index + 1)
            second_pair_jaccard.append(text.Index + 1)
            key_score_jaccard.append(round(score_jaccard_tweet, 2))

# Membuat dataframe dari hasil perhitungan Jaccard
df_jaccard = pd.DataFrame({
    'first_pair_jaccard': first_pair_jaccard,
    'second_pair_jaccard': second_pair_jaccard,
    'key_score_jaccard': key_score_jaccard
})

# Mengurutkan dataframe berdasarkan nilai Jaccard
df_jaccard_sorted = df_jaccard.sort_values(
    'key_score_jaccard', ascending=False)

# Menyaring dataframe untuk menghapus baris dengan nilai Jaccard 0.0
df_filtered = df_jaccard_sorted[df_jaccard_sorted['key_score_jaccard'] != 0.00]

# Fungsi untuk menyimpan hasil Jaccard ke database


def save_jaccard_to_database(df, db_config):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        for row in df.itertuples():
            query = """
                INSERT INTO model (first_pair_jaccard, second_pair_jaccard, key_score_jaccard)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query, (row.first_pair_jaccard,
                           row.second_pair_jaccard, row.key_score_jaccard))
        conn.commit()
        cursor.close()
        conn.close()
        print("Data berhasil disimpan ke database.")
    except Exception as e:
        print("Error:", str(e))


# Menyimpan hasil Jaccard similarity ke dalam database
save_jaccard_to_database(df_filtered, db_config)

# Variabel untuk menyimpan hasil clustering
all_cluster_list = []
temp_cluster = []
exclude_list = []
score_flag = 0

# Membuat matriks kesamaan awal
initial_matrix = [[jaccard_similarity(set(row[1].split()), set(text[1].split(
))) for text in df_twitter.itertuples()] for row in df_twitter.itertuples()]

# Loop untuk melakukan clustering berdasarkan nilai Jaccard
min_similarity = df_filtered['key_score_jaccard'].min()

while not df_filtered.empty:
    # Step 3: Menemukan nilai maksimum dalam matriks A
    max_similarity = df_filtered['key_score_jaccard'].max()

    # Step 3: Menemukan semua pasangan dokumen yang belum dikelompokkan dengan nilai maksimum
    max_pairs = df_filtered[df_filtered['key_score_jaccard'] == max_similarity]

    for data in max_pairs.itertuples():
        # Step 4: Jika kedua dokumen dalam pasangan belum dikelompokkan
        if data.first_pair_jaccard not in exclude_list and data.second_pair_jaccard not in exclude_list:
            temp_cluster.append(data.first_pair_jaccard)
            temp_cluster.append(data.second_pair_jaccard)
            exclude_list.extend(
                [data.first_pair_jaccard, data.second_pair_jaccard])
            score_flag = data.key_score_jaccard

        # Jika satu dokumen dalam pasangan belum dikelompokkan
        elif data.first_pair_jaccard not in exclude_list:
            temp_cluster.append(data.first_pair_jaccard)
            exclude_list.append(data.first_pair_jaccard)

        elif data.second_pair_jaccard not in exclude_list:
            temp_cluster.append(data.second_pair_jaccard)
            exclude_list.append(data.second_pair_jaccard)

        # Step 4: Menghapus pasangan dokumen dari dataframe setelah diproses
        df_filtered = df_filtered.drop(data.Index)

    # Step 4: Membandingkan nilai maksimum dengan nilai minimum
    if score_flag == min_similarity:
        all_cluster_list.append(temp_cluster)
        temp_cluster = []
    else:
        if temp_cluster:
            all_cluster_list.append(temp_cluster)
        temp_cluster = []

# Step 5: Menangani dokumen yang belum terklaster
all_documents = set(range(1, len(df_twitter) + 1))
clustered_documents = set(exclude_list)
unclustered_documents = all_documents - clustered_documents

for doc in unclustered_documents:
    all_cluster_list.append([doc])

# Menyimpan kluster yang tidak kosong ke dalam final_cluster
final_cluster = [x for x in all_cluster_list if x]

# Menambahkan kolom label manual ke dataframe
df_twitter['label_manual'] = ""

# Fungsi untuk menambahkan label manual berdasarkan teks


def add_manual_labels(df):
    labels = {
        "DKI Jakarta": ["jakarta", "dki"],
        "Jawa Timur": ["jawa timur", "jatim"],
        "Jawa Barat": ["jawa barat", "jabar"],
        "Jawa Tengah": ["jawa tengah", "jateng"],
        "Sumatra Barat": ["sumatra barat", "sumbar"],
        "Sumatra Utara": ["sumatra utara", "sumut"],
        "Sulawesi Selatan": ["sulawesi selatan", "sulsel"],
        "Sumatra Selatan": ["sumatra selatan", "sumsel"],
        "Kalimantan": ["kalimantan"],
        "Papua": ["papua"],
        "Umum": []
    }

    for index, row in df.iterrows():
        text = row['text_bersih'].lower()
        label_assigned = False
        for label, keywords in labels.items():
            if any(keyword in text for keyword in keywords):
                df.at[index, 'label_manual'] = label
                label_assigned = True
                break
        if not label_assigned:
            df.at[index, 'label_manual'] = "Umum"


# Menambahkan label manual ke dataframe
add_manual_labels(df_twitter)

# Menambahkan hasil klustering ke dataframe
cluster_labels = []
for i, cluster in enumerate(final_cluster):
    for tweet_id in cluster:
        cluster_labels.append((tweet_id, i + 1))

# Mengurutkan berdasarkan tweet_id
cluster_labels.sort()

# Menambahkan label kluster ke dataframe
cluster_labels_only = [label[1] for label in cluster_labels]
df_twitter['cluster'] = cluster_labels_only

# Fungsi untuk menyimpan hasil clustering dan label manual ke database


def save_cluster_to_database(clusters, db_config, df_twitter):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Clear the clusters table
        cursor.execute("DELETE FROM clusters")

        for cluster_id, cluster in enumerate(clusters, start=1):
            for tweet_id in cluster:
                # Mengecek apakah tweet_id dalam rentang indeks yang valid
                if tweet_id <= len(df_twitter):
                    query = """
                        INSERT INTO clusters (id, cluster_id, text, label)
                        VALUES (%s, %s, %s, %s)
                    """
                    # Mengambil teks tweet dan label manual berdasarkan tweet_id
                    tweet_text = df_twitter.loc[tweet_id - 1, 'text_bersih']
                    label_manual = df_twitter.loc[tweet_id - 1, 'label_manual']
                    cursor.execute(query, (tweet_id, cluster_id,
                                   tweet_text, label_manual))
        conn.commit()
        cursor.close()
        conn.close()
        print("Cluster data berhasil disimpan ke database.")
    except Exception as e:
        print("Error:", str(e))


# Menyimpan hasil clustering dan label manual ke dalam database
save_cluster_to_database(final_cluster, db_config, df_twitter)
