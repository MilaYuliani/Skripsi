import pandas as pd
import mysql.connector
from clustering import save_cluster_to_database


def fetch_processed_data(db_config):
    try:
        conn = mysql.connector.connect(**db_config)
        query = "SELECT text_bersih FROM proses"
        data = pd.read_sql(query, conn)
        conn.close()
        return data
    except Exception as e:
        print("Error fetching processed data:", str(e))
        return pd.DataFrame()


def jaccard_similarity(list1, list2):
    s1 = set(list1)
    s2 = set(list2)
    return float(len(s1.intersection(s2)) / len(s1.union(s2)))


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
        print("Data Jaccard berhasil disimpan ke database.")
    except Exception as e:
        print("Error saving Jaccard data to database:", str(e))


def perform_clustering(df_twitter, df_filtered):
    all_cluster_list = []
    temp_cluster = []
    exclude_list = []
    score_flag = 0

    while not df_filtered.empty:
        max_similarity = df_filtered['key_score_jaccard'].max()
        max_pairs = df_filtered[df_filtered['key_score_jaccard']
                                == max_similarity]

        for data in max_pairs.itertuples():
            if data.first_pair_jaccard not in exclude_list and data.second_pair_jaccard not in exclude_list:
                temp_cluster.append(data.first_pair_jaccard)
                temp_cluster.append(data.second_pair_jaccard)
                exclude_list.extend(
                    [data.first_pair_jaccard, data.second_pair_jaccard])
                score_flag = data.key_score_jaccard
            elif data.first_pair_jaccard not in exclude_list:
                temp_cluster.append(data.first_pair_jaccard)
                exclude_list.append(data.first_pair_jaccard)
            elif data.second_pair_jaccard not in exclude_list:
                temp_cluster.append(data.second_pair_jaccard)
                exclude_list.append(data.second_pair_jaccard)
            df_filtered = df_filtered.drop(data.Index)

        if score_flag == min_similarity:
            all_cluster_list.append(temp_cluster)
            temp_cluster = []
        else:
            if temp_cluster:
                all_cluster_list.append(temp_cluster)
            temp_cluster = []

    all_documents = set(range(1, len(df_twitter) + 1))
    clustered_documents = set(exclude_list)
    unclustered_documents = all_documents - clustered_documents

    for doc in unclustered_documents:
        all_cluster_list.append([doc])

    return all_cluster_list


if __name__ == "__main__":
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'databanjir'
    }

    try:
        data_twitter = fetch_processed_data(db_config)

        if data_twitter.empty:
            raise Exception("No data fetched from database")

        tweet_list = data_twitter['text_bersih'].tolist()
        df_twitter = pd.DataFrame({'text_bersih': tweet_list})

        first_pair_jaccard = []
        second_pair_jaccard = []
        key_score_jaccard = []

        for row in df_twitter.itertuples():
            for text in df_twitter.itertuples():
                word_set_1 = set(row[1].split())
                word_set_2 = set(text[1].split())
                score_jaccard_tweet = jaccard_similarity(
                    word_set_1, word_set_2)
                if 0 < score_jaccard_tweet <= 0.5:
                    first_pair_jaccard.append(row.Index + 1)
                    second_pair_jaccard.append(text.Index + 1)
                    key_score_jaccard.append(round(score_jaccard_tweet, 2))

        df_jaccard = pd.DataFrame({
            'first_pair_jaccard': first_pair_jaccard,
            'second_pair_jaccard': second_pair_jaccard,
            'key_score_jaccard': key_score_jaccard
        })

        df_jaccard_sorted = df_jaccard.sort_values(
            by='key_score_jaccard', ascending=False)
        min_similarity = df_jaccard_sorted['key_score_jaccard'].min()

        clusters = perform_clustering(df_twitter, df_jaccard_sorted)

        save_cluster_to_database(clusters, db_config, df_twitter)
    except Exception as e:
        print("Main program error:", str(e))
