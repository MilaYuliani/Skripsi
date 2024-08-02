import mysql.connector
import numpy as np
import pandas as pd


def connect_to_db():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='databanjir'
    )
    return connection

#mengambil data klaster
def fetch_data():
    connection = connect_to_db()
    query = "SELECT cluster_id, text FROM clusters ORDER BY cluster_id"
    df = pd.read_sql(query, connection)
    connection.close()
    return df


def save_results_to_db(results):
    connection = connect_to_db()
    cursor = connection.cursor()

    for result in results:
        cursor.execute("""
            INSERT INTO hybrid_tfidf (cluster_id, text, tf, idf, tfidf, W_wi, W_S, nf_S, best_percluster) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            result['cluster_id'], result['text'], float(result['tf']),
            float(result['idf']), float(result['tfidf']),
            float(result['W_wi']), float(result['W_S']),
            float(result['nf_S']), result['best_percluster']
        ))

    connection.commit()
    cursor.close()
    connection.close()

# Menghitung TF
def compute_tf(term, cluster_documents):
    term_count = sum(doc.split().count(term) for doc in cluster_documents)
    total_terms = sum(len(doc.split()) for doc in cluster_documents)
    return term_count / total_terms if total_terms > 0 else 0

#menghitung IDF
def compute_idf(term, all_documents, cluster_documents):
    num_cluster_documents_with_term = sum(
        1 for doc in cluster_documents if term in doc.split())
    num_cluster_documents = len(cluster_documents)
    return num_cluster_documents / num_cluster_documents_with_term if num_cluster_documents_with_term > 0 else 0

# Menghitung Bobot Kata
def compute_hybrid_tf_idf(cluster_documents, all_documents):
    tf_idf_scores = []
    for document in cluster_documents:
        tf_idf_doc = {}
        terms = document.split()
        for term in terms:
            if term not in tf_idf_doc:
                tf = compute_tf(term, cluster_documents)
                idf = compute_idf(term, all_documents, cluster_documents)
                tfidf = tf * idf
                W_wi = tf * np.log2(idf) if idf > 0 else 0
                tf_idf_doc[term] = {'tf': tf, 'idf': idf,
                                    'tfidf': tfidf, 'W_wi': W_wi}
        tf_idf_scores.append(tf_idf_doc)
    return tf_idf_scores

#menghitung Bobot Kalimat
def compute_w_s_and_nf_s(cluster_documents, tf_idf_scores, min_threshold=1):
    all_weights = []
    term_counts = [len(doc.split()) for doc in cluster_documents]

    for document, tf_idf_doc, term_count in zip(cluster_documents, tf_idf_scores, term_counts):
        terms = document.split()
        weights = [tf_idf_doc[term]['W_wi']
                   for term in terms if term in tf_idf_doc]
        all_weights.append(weights)

    min_threshold = min(
        min([w for weights in all_weights for w in weights], default=1), min_threshold)
    nf_S = max(min_threshold, max(term_counts))

    sentence_scores = []
    for weights in all_weights:
        W_S = sum(weights) / nf_S if nf_S != 0 else 0
        sentence_scores.append(W_S)

    return sentence_scores, nf_S


def main():
    df = fetch_data()
    print("Kolom yang tersedia dalam DataFrame:", df.columns)

    if 'text' not in df.columns:
        print("Kolom 'text' tidak ditemukan dalam tabel clusters.")
        return

    results = []
    cluster_best_sentences = []

    grouped = df.groupby('cluster_id')

    for cluster_id, group in grouped:
        cluster_documents = group['text'].tolist()
        all_documents = df['text'].tolist()  # Semua dokumen dalam dataset
        tf_idf_scores = compute_hybrid_tf_idf(cluster_documents, all_documents)
        sentence_scores, nf_S = compute_w_s_and_nf_s(
            cluster_documents, tf_idf_scores)

        best_tweet_idx = np.argmax(sentence_scores)
        best_tweet_score = sentence_scores[best_tweet_idx]
        best_tweet_text = cluster_documents[best_tweet_idx]

        cluster_best_sentences.append(
            (cluster_id, best_tweet_text, best_tweet_score))

        for i, document in enumerate(cluster_documents):
            W_S = sentence_scores[i]
            best_percluster = 1 if i == best_tweet_idx else 0

            for term, scores in tf_idf_scores[i].items():
                result = {
                    'cluster_id': cluster_id,
                    'text': term,
                    'tf': scores['tf'],
                    'idf': scores['idf'],
                    'tfidf': scores['tfidf'],
                    'W_wi': scores['W_wi'],
                    'W_S': W_S,
                    'nf_S': nf_S,
                    'best_percluster': best_percluster
                }
                results.append(result)

    save_results_to_db(results)

    # Mengurutkan berdasarkan nilai W_S tertinggi
    cluster_best_sentences.sort(key=lambda x: x[2], reverse=True)

    for cluster_id, best_sentence, best_score in cluster_best_sentences:
        print(f"Kalimat utama yang ditemukan untuk Cluster ID {cluster_id}:")
        print(f"Kalimat: {best_sentence}")
        print(f"Nilai W_S: {best_score}")
        print()


if __name__ == "__main__":
    main()
