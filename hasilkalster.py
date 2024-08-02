import mysql.connector
import pandas as pd
from collections import Counter
import re
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import numpy as np

# Fungsi untuk menghubungkan ke database


def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='databanjir'
        )
        print("Koneksi ke database berhasil")
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# Membaca data dari tabel clusters dan hybrid_tfidf


def read_data_from_db():
    connection = connect_to_db()
    if connection is None:
        return None, None

    query_clusters = 'SELECT cluster_id, text FROM clusters'
    query_tfidf = 'SELECT cluster_id, text, w_wi AS tfidf FROM hybrid_tfidf'

    df_clusters = pd.read_sql(query_clusters, con=connection)
    df_tfidf = pd.read_sql(query_tfidf, con=connection)

    connection.close()
    return df_clusters, df_tfidf

# Menyimpan hasil analisis ke tabel analisis


def save_analysis_to_db(df):
    connection = connect_to_db()
    if connection is None:
        print("Koneksi ke database gagal")
        return
    cursor = connection.cursor()
    try:
        for index, row in df.iterrows():
            cursor.execute('''
                INSERT INTO analisis (cluster_id, text, locations, pca_one, pca_two, cluster_name)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (row['cluster_id'], row['text'], ','.join(row['locations']), row['pca_one'], row['pca_two'], row['cluster_name']))
        connection.commit()
        print("Data berhasil disimpan ke database")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        connection.close()


# Daftar kota/kabupaten dan provinsi di Indonesia
location_to_province = {
    'cirebon': 'jawa barat',
    'demak': 'jawa tengah',
    'bandung': 'jawa barat',
    'semarang': 'jawa tengah',
    'surabaya': 'jawa timur',
    'lumajang': 'jawa timut',
    'jakarta': 'dki jakarta',
    # Tambahkan lebih banyak kota/kabupaten dan provinsi sesuai kebutuhan
    'aceh': 'aceh', 'bali': 'bali', 'banten': 'banten', 'bengkulu': 'bengkulu', 'gorontalo': 'gorontalo', 'jambi': 'jambi',
    'jawa timur': 'jawa timur', 'kalimantan barat': 'kalimantan barat', 'kalimantan selatan': 'kalimantan selatan',
    'kalimantan tengah': 'kalimantan tengah', 'kalimantan timur': 'kalimantan timur', 'kalimantan utara': 'kalimantan utara', 'kepulauan bangka belitung': 'kepulauan bangka belitung', 'kepulauan riau': 'kepulauan riau',
    'lampung': 'lampung', 'maluku': 'maluku', 'maluku utara': 'maluku utara', 'nusa tenggara barat': 'nusa tenggara barat', 'nusa tenggara timur': 'nusa tenggara timur', 'papua': 'papua', 'papua barat': 'papua barat',
    'riau': 'riau', 'sulawesi barat': 'sulawesi barat', 'sulawesi selatan': 'sulawesi selatan',
    'sulawesi tengah': 'sulawesi tengah', 'sulawesi tenggara': 'sulawesi tenggara', 'sulawesi utara': 'sulawesi utara',
    'sumatra barat': 'sumatra barat', 'sumatra selatan': 'sumatra selatan', 'sumatra utara': 'sumatra utara',
    'yogyakarta': 'yogyakarta'
}

# Fungsi untuk mengekstrak provinsi dari teks berdasarkan kota/kabupaten


def extract_locations(text, location_to_province):
    found_locations = []
    for loc, prov in location_to_province.items():
        if re.search(r'\b' + loc + r'\b', text):
            found_locations.append(prov)
    return list(set(found_locations))  # Menghilangkan duplikat


# Membaca data dari database
df_clusters, df_tfidf = read_data_from_db()
if df_clusters is not None and df_tfidf is not None:
    # Add a column with extracted locations
    df_clusters['locations'] = df_clusters['text'].apply(
        lambda x: extract_locations(x, location_to_province))

    # Profiling Cluster for locations
    def profile_cluster_locations(df, cluster_id):
        cluster_data = df[df['cluster_id'] == cluster_id]
        all_locations = [loc for sublist in cluster_data['locations']
                         for loc in sublist]
        location_freq = Counter(all_locations)
        return location_freq

    # Profiling all clusters
    cluster_profiles = {}
    for cluster_id in df_clusters['cluster_id'].unique():
        cluster_profiles[cluster_id] = profile_cluster_locations(
            df_clusters, cluster_id)

    # Display the profiling results
    print("Profiling Results for Locations:")
    for cluster_id, profile in cluster_profiles.items():
        print(f'\nCluster {cluster_id} locations:')
        for loc, freq in profile.items():
            print(f'  {loc}: {freq}')

    # Aggregate TF-IDF values for each cluster
    tfidf_matrix = df_tfidf.pivot_table(
        index='cluster_id', columns='text', values='tfidf', aggfunc='mean').fillna(0)

    # Reduce dimensions using PCA
    pca = PCA(n_components=2)
    pca_result = pca.fit_transform(tfidf_matrix)

    # Create a dataframe for the PCA results
    pca_df = pd.DataFrame(pca_result, index=tfidf_matrix.index, columns=[
                          'pca_one', 'pca_two'])

    # Merge the PCA results with the original clusters dataframe
    df_clusters = df_clusters.merge(
        pca_df, left_on='cluster_id', right_index=True, how='left')

    # Ensure unique colors for each cluster in the visualization
    unique_clusters = df_clusters['cluster_id'].unique()
    colors = plt.cm.viridis(np.linspace(0, 1, len(unique_clusters)))

    # Visualize the PCA result
    plt.figure(figsize=(10, 10))
    scatter = plt.scatter(
        df_clusters['pca_one'], df_clusters['pca_two'], c=df_clusters['cluster_id'], cmap='viridis')
    plt.legend(handles=scatter.legend_elements()[0], labels=[
               str(cluster) for cluster in unique_clusters])
    plt.title('PCA of Clusters')
    plt.xlabel('PCA One')
    plt.ylabel('PCA Two')
    plt.show()

    # Function to profile keywords for each cluster
    def profile_cluster_keywords(df_tfidf, cluster_id):
        cluster_data = df_tfidf[df_tfidf['cluster_id'] == cluster_id]
        word_freq = cluster_data.set_index(
            'text')['tfidf'].sort_values(ascending=False)
        return word_freq.head(10)

    # Profiling all clusters for keywords
    keyword_profiles = {}
    for cluster_id in df_clusters['cluster_id'].unique():
        keyword_profiles[cluster_id] = profile_cluster_keywords(
            df_tfidf, cluster_id)

    # Display the keyword profiles and assign names to clusters
    print("\nProfiling Results for Keywords:")
    cluster_names = {}
    for cluster_id, keywords in keyword_profiles.items():
        print(f'\nCluster {cluster_id} top words:')
        for word, freq in keywords.items():
            print(f'  {word}: {freq}')
        # Use the most common location to name the cluster
        most_common_location = cluster_profiles[cluster_id].most_common(1)
        if most_common_location:
            cluster_name = "banjir " + most_common_location[0][0]
        else:
            # If no location is found, check top words for location names
            for word, freq in keywords.items():
                if word in location_to_province.values():
                    cluster_name = "banjir " + word
                    break
            else:
                # If no location is found, use the top 3 words as the cluster name
                cluster_name = "banjir " + \
                    ' '.join([word for word in keywords.index[:3]])
        cluster_names[cluster_id] = cluster_name

    # Display the cluster names
    print("\nCluster Names:")
    for cluster_id, name in cluster_names.items():
        print(f'  Cluster {cluster_id}: {name}')

    # Add cluster names to the dataframe for further analysis
    df_clusters['cluster_name'] = df_clusters['cluster_id'].map(cluster_names)

    # Menyimpan hasil ke tabel analisis di database
    save_analysis_to_db(df_clusters)
else:
    print("Tidak ada data yang dapat diolah.")
