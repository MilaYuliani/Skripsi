import pandas as pd
import numpy as np

# Data tweet dari gambar
data_twitter = pd.DataFrame({
    'Dokumen': ['D1', 'D2', 'D3', 'D4', 'D5'],
    'Tweet': [
        'peduli bencana sumatera barat gadai salur bantu korban banjir bandang',
        'bencana banjir lahar dingin landa sumatra barat renggut nyawa',
        'banjir bandang demak',
        'bmkg potensi banjir rob wilayah pesisir indonesia april',
        'banjir bandang terjang camat bonebone kabupaten luwu utara'
    ]
})

# Mengambil kolom 'Tweet' sebagai list
tweet_list = data_twitter['Tweet'].tolist()

# Membuat dataframe dari daftar tweet yang telah dibersihkan
df_twitter = pd.DataFrame({'Tweet': tweet_list})

# Fungsi untuk menghitung Jaccard Similarity


def jaccard_similarity(list1, list2):
    s1 = set(list1)
    s2 = set(list2)
    return float(len(s1.intersection(s2)) / len(s1.union(s2)))


# Variabel untuk menyimpan hasil perhitungan Jaccard
first_pair_jaccard = []
second_pair_jaccard = []
key_score_jaccard = []

# Membuat matriks Jaccard similarity
num_tweets = len(df_twitter)
jaccard_matrix = np.zeros((num_tweets, num_tweets))

for i in range(num_tweets):
    for j in range(num_tweets):
        if i != j:  # Menghindari perbandingan dengan diri sendiri
            tweet_i = df_twitter.iloc[i]['Tweet'].split()
            tweet_j = df_twitter.iloc[j]['Tweet'].split()
            score_jaccard_tweet = jaccard_similarity(tweet_i, tweet_j)
            jaccard_matrix[i, j] = score_jaccard_tweet
            if 0 < score_jaccard_tweet <= 0.5:
                first_pair_jaccard.append(i + 1)
                second_pair_jaccard.append(j + 1)
                key_score_jaccard.append(round(score_jaccard_tweet, 2))

# Menampilkan matriks Jaccard similarity
print("Matriks Jaccard Similarity:")
print(pd.DataFrame(jaccard_matrix, columns=[
      'D1', 'D2', 'D3', 'D4', 'D5'], index=['D1', 'D2', 'D3', 'D4', 'D5']))

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

# Variabel untuk menyimpan hasil clustering
all_cluster_list = []
temp_cluster = []
exclude_list = []
score_flag = 0

# Membuat matriks maksimum capturing
max_capturing_matrix = np.zeros((num_tweets, num_tweets))

# Loop untuk melakukan clustering berdasarkan nilai Jaccard
min_similarity = df_filtered['key_score_jaccard'].min()

step = 1
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
            max_capturing_matrix[data.first_pair_jaccard -
                                 1, data.second_pair_jaccard - 1] = score_flag
            max_capturing_matrix[data.second_pair_jaccard -
                                 1, data.first_pair_jaccard - 1] = score_flag
            jaccard_matrix[data.first_pair_jaccard -
                           1, data.second_pair_jaccard - 1] = 0
            jaccard_matrix[data.second_pair_jaccard -
                           1, data.first_pair_jaccard - 1] = 0

        # Jika satu dokumen dalam pasangan belum dikelompokkan
        elif data.first_pair_jaccard not in exclude_list:
            temp_cluster.append(data.first_pair_jaccard)
            exclude_list.append(data.first_pair_jaccard)
            max_capturing_matrix[data.first_pair_jaccard -
                                 1, data.second_pair_jaccard - 1] = score_flag
            max_capturing_matrix[data.second_pair_jaccard -
                                 1, data.first_pair_jaccard - 1] = score_flag
            jaccard_matrix[data.first_pair_jaccard -
                           1, data.second_pair_jaccard - 1] = 0
            jaccard_matrix[data.second_pair_jaccard -
                           1, data.first_pair_jaccard - 1] = 0

        elif data.second_pair_jaccard not in exclude_list:
            temp_cluster.append(data.second_pair_jaccard)
            exclude_list.append(data.second_pair_jaccard)
            max_capturing_matrix[data.first_pair_jaccard -
                                 1, data.second_pair_jaccard - 1] = score_flag
            max_capturing_matrix[data.second_pair_jaccard -
                                 1, data.first_pair_jaccard - 1] = score_flag
            jaccard_matrix[data.first_pair_jaccard -
                           1, data.second_pair_jaccard - 1] = 0
            jaccard_matrix[data.second_pair_jaccard -
                           1, data.first_pair_jaccard - 1] = 0

        # Step 4: Menghapus pasangan dokumen dari dataframe setelah diproses
        df_filtered = df_filtered.drop(data.Index)

    # Menampilkan matriks Jaccard similarity yang diperbarui pada setiap langkah
    print(f"\nMatriks Jaccard Similarity pada Langkah {step}:")
    print(pd.DataFrame(jaccard_matrix, columns=[
          'D1', 'D2', 'D3', 'D4', 'D5'], index=['D1', 'D2', 'D3', 'D4', 'D5']))

    # Menampilkan matriks maksimum capturing pada setiap langkah
    print(f"\nMatriks Maksimum Capturing pada Langkah {step}:")
    print(pd.DataFrame(max_capturing_matrix, columns=[
          'D1', 'D2', 'D3', 'D4', 'D5'], index=['D1', 'D2', 'D3', 'D4', 'D5']))

    step += 1

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

# Menampilkan hasil clustering
print("\nHasil Clustering:")
for idx, cluster in enumerate(final_cluster):
    print(f"Cluster {idx + 1}: {sorted(list(cluster))}")

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

# Menampilkan dataframe dengan cluster
print("\nDataframe dengan Cluster:")
print(df_twitter)
