import numpy as np
import pandas as pd

# Data sample
data = {
    'cluster_id': [1, 1, 2, 2, 2],
    'text': [
        'gempa bumi kuat magnitudo guncang kabupaten garut jawa barat sabtu malam',
        'gempa bumi kuat magnitudo jadi kabupaten pangandaran jawa barat ada dalam kilometer',
        'banjir bandang demak',
        'banjir bandang tanah longsor terjang sumbawa',
        'peduli bencana sumatra barat gadai salur bantu korban banjir bandang'
    ]
}

# Membuat DataFrame dari data sample
df = pd.DataFrame(data)


def compute_tf(term, cluster_documents):
    term_count = sum(doc.split().count(term) for doc in cluster_documents)
    total_terms = sum(len(doc.split()) for doc in cluster_documents)
    return term_count / total_terms if total_terms > 0 else 0


def compute_idf(term, all_documents, cluster_documents):
    num_cluster_documents_with_term = sum(
        1 for doc in cluster_documents if term in doc.split())
    num_cluster_documents = len(cluster_documents)
    return num_cluster_documents / num_cluster_documents_with_term if num_cluster_documents_with_term > 0 else 0


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
                # Menggunakan rumus W_wi dengan log basis 2
                W_wi = tf * np.log2(idf) if idf > 0 else 0
                tf_idf_doc[term] = {'term': term, 'tf': tf, 'idf': idf,
                                    'tfidf': tfidf, 'W_wi': W_wi}
        tf_idf_scores.append(tf_idf_doc)
    return tf_idf_scores


def compute_w_s_and_nf_s(cluster_documents, tf_idf_scores, min_threshold=1):
    all_weights = []
    # Jumlah term dalam setiap dokumen
    term_counts = [len(doc.split()) for doc in cluster_documents]

    for document, tf_idf_doc, term_count in zip(cluster_documents, tf_idf_scores, term_counts):
        terms = document.split()
        weights = [tf_idf_doc[term]['W_wi']
                   for term in terms if term in tf_idf_doc]
        all_weights.append(weights)

    min_threshold = min(
        min([w for weights in all_weights for w in weights], default=1), min_threshold)
    # Menggunakan maksimum antara min_threshold dan jumlah term maksimum per dokumen
    nf_S = max(min_threshold, max(term_counts))

    sentence_scores = []
    for weights in all_weights:
        W_S = sum(weights) / nf_S if nf_S != 0 else 0
        sentence_scores.append(W_S)

    return sentence_scores, nf_S


def select_best_sentence(cluster_id, cluster_documents):
    all_documents = df['text'].tolist()  # Semua dokumen dalam dataset
    tf_idf_scores = compute_hybrid_tf_idf(cluster_documents, all_documents)
    sentence_scores, nf_S = compute_w_s_and_nf_s(
        cluster_documents, tf_idf_scores)

    # Memilih kalimat dengan nilai W_S tertinggi
    best_tweet_idx = np.argmax(sentence_scores)
    best_tweet_score = sentence_scores[best_tweet_idx]
    best_tweet_text = cluster_documents[best_tweet_idx]

    return cluster_id, best_tweet_text, best_tweet_score, tf_idf_scores, nf_S, sentence_scores


def main():
    results = []

    grouped = df.groupby('cluster_id')

    for cluster_id, group in grouped:
        cluster_documents = group['text'].tolist()

        print(f"Cluster ID: {cluster_id}")
        for idx, doc in enumerate(cluster_documents, start=1):
            num_words = len(doc.split())
            print(f"Dokumen {idx}: Jumlah kata = {num_words}")

        cluster_id, best_sentence, best_score, best_tf_idf_scores, nf_S, sentence_scores = select_best_sentence(
            cluster_id, cluster_documents)

        print(f"\nKalimat utama yang ditemukan untuk Cluster ID {cluster_id}:")
        print(f"Kalimat: {best_sentence}")
        print(f"W_S: {best_score}")
        print(f"nf_S: {nf_S}")
        print()

        for tf_idf_doc in best_tf_idf_scores:
            for term, term_scores in tf_idf_doc.items():
                term_scores['Cluster ID'] = cluster_id
                term_scores['W_S'] = best_score
                results.append(term_scores)

    # Membuat DataFrame hasil
    results_df = pd.DataFrame(results)

    # Mengurutkan kolom sesuai kebutuhan
    results_df = results_df[['Cluster ID', 'term',
                             'tf', 'idf', 'W_wi', 'tfidf', 'W_S']]

    # Menampilkan tabel hasil
    print("Tabel hasil:")
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(results_df)
    print()


if __name__ == "__main__":
    main()
