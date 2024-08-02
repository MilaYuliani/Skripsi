import mysql.connector
import numpy as np
import pandas as pd

# Koneksi ke database MySQL


def connect_to_db():
    connection = mysql.connector.connect(
        host='localhost',  # Ubah sesuai dengan host MySQL Anda
        user='root',
        password='',
        database='databanjir'
    )
    return connection

# Mendapatkan data dari tabel clusters


def fetch_data():
    connection = connect_to_db()
    query = "SELECT cluster_id, text FROM clusters"
    df = pd.read_sql(query, connection)
    connection.close()
    return df

# Menyimpan hasil tokenisasi dan NER ke tabel ner


def save_results_to_db(tokens):
    connection = connect_to_db()
    cursor = connection.cursor()

    for token in tokens:
        cursor.execute("""
            INSERT INTO ner (cluster_id, token_string, token_kind, contextual_features, morphological_features, part_of_speech_features, entity_type) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            token['cluster_id'], token['string'], token['token_kind'],
            token['contextual_features'], token['morphological_features'],
            token['part_of_speech_features'], token['entity_type']
        ))

    connection.commit()
    cursor.close()
    connection.close()

# Menyimpan hasil TF-IDF ke tabel hybrid_tfidf


def save_tfidf_results_to_db(cluster_id, document, tfidf_scores, W_S, nf_S):
    connection = connect_to_db()
    cursor = connection.cursor()

    for term, scores in tfidf_scores.items():
        cursor.execute("""
            INSERT INTO hybrid_tfidf (cluster_id, text, tf, idf, tfidf, W_wi, W_S, nf_S) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            cluster_id, document, float(scores['tf']), float(
                scores['idf']), float(scores['tfidf']),
            float(scores['W_wi']), float(W_S), float(nf_S)
        ))

    connection.commit()
    cursor.close()
    connection.close()

# Fungsi untuk memeriksa apakah string cocok dengan pola tanggal


def is_date_string(word):
    parts = word.split('/')
    if len(parts) == 3 and all(part.isdigit() for part in parts):
        return len(parts[0]) == 2 and len(parts[1]) == 2 and len(parts[2]) == 4
    return False

# Fungsi untuk tokenisasi dan pemberian fitur


def tokenize_and_assign_features(text, cluster_id):
    tokens = []
    words = [word for word in text.split() if word]
    for i, word in enumerate(words):
        token_kind = 'NUM' if is_date_string(word) else 'WORD' if word.isalpha(
        ) else 'EPUNC' if word == ')' else 'SPUNC' if word == ',' else 'OPUNC' if word == '(' else 'SPUNC' if word == '.' else 'OPUNC'

        # Morphological features
        morphological_features = 'TitleCase, CapStart' if word.istitle() else 'LowerCase'
        if is_date_string(word):
            morphological_features = 'DigitSlash'

        # Part-of-speech features
        part_of_speech_features = 'N/A'
        if word.lower() in ["banjir", "jalan", "raya", "kaligawe", "semarang", "demak", "jawa", "tengah"]:
            part_of_speech_features = 'NOUN'
        elif word.lower() == "masih":
            part_of_speech_features = 'ADV'
        elif word.lower() == "menggenangi":
            part_of_speech_features = 'VACT'
        elif word.lower() == "atau":
            part_of_speech_features = 'C'
        elif word.lower() == "pada":
            part_of_speech_features = 'PREP'
        elif word.lower() == "minggu":
            part_of_speech_features = 'NOUN'
        elif word.lower() == "pagi":
            part_of_speech_features = 'NOUN'
        elif is_date_string(word):
            part_of_speech_features = 'DATE'

        # Contextual features
        contextual_features = 'OOV' if word not in ["banjir", "jalan", "raya", "kaligawe", "semarang",
                                                    "demak", "jawa", "tengah", "masih", "menggenangi", "atau", "pada", "minggu", "pagi"] else ''
        if word.lower() in ["jalan", "jawa"]:
            if i > 0 and words[i-1].lower() == "jalan":
                contextual_features = 'LPRE'
            elif i < len(words) - 1 and words[i+1].lower() == "tengah":
                contextual_features = 'LSUF'

        token = {
            'string': word,
            'cluster_id': cluster_id,
            'token_kind': token_kind,
            'contextual_features': contextual_features,
            'morphological_features': morphological_features,
            'part_of_speech_features': part_of_speech_features,
            'entity_type': ""
        }
        tokens.append(token)
    return tokens

# Fungsi untuk menghitung TF (Term Frequency)


def compute_tf(term, document):
    return document.count(term) / len(document.split())

# Fungsi untuk menghitung IDF (Inverse Document Frequency)


def compute_idf(term, documents):
    num_documents_with_term = sum([1 for doc in documents if term in doc])
    return np.log(len(documents) / (1 + num_documents_with_term))

# Fungsi untuk menghitung bobot W(wi)


def compute_w_wi(tf, idf):
    return tf * np.log2(1 + idf)

# Fungsi untuk menghitung TF-IDF Hybrid


def compute_hybrid_tf_idf(documents):
    tf_idf_scores = []
    for document in documents:
        tf_idf_doc = {}
        terms = set(document.split())
        for term in terms:
            tf = compute_tf(term, document)
            idf = compute_idf(term, documents)
            tfidf = tf * idf
            tf_idf_doc[term] = {'tf': tf, 'idf': idf,
                                'tfidf': tfidf, 'W_wi': compute_w_wi(tf, idf)}
        tf_idf_scores.append(tf_idf_doc)
    return tf_idf_scores

# Fungsi untuk menghitung W(S) dan nf(S) untuk semua kalimat dalam cluster


def compute_w_s_and_nf_s(documents, tf_idf_scores):
    all_weights = []
    min_thresholds = []

    for document, tf_idf_doc in zip(documents, tf_idf_scores):
        terms = document.split()
        weights = [tf_idf_doc[term]['W_wi']
                   for term in terms if term in tf_idf_doc]
        all_weights.append(weights)
        min_thresholds.append(np.min(weights))

    min_threshold = np.mean(min_thresholds)
    nf_S = max(min_threshold, np.mean([len(doc.split()) for doc in documents]))

    sentence_scores = []
    for weights in all_weights:
        W_S = sum(weights) / nf_S
        sentence_scores.append(W_S)

    return sentence_scores, nf_S

# Fungsi untuk menerapkan aturan NER pada token-token


def apply_ner_rules(tokens):
    for i, token in enumerate(tokens):
        # Rule for DISASTER
        if (token['token_kind'] == 'WORD' and
            token['string'].lower() in ['banjir', 'bandang', 'lahar', 'rob'] and
                token['part_of_speech_features'] == 'NOUN'):
            token['entity_type'] = "DISASTER"

        # Rule for LOCATION
        elif (token['token_kind'] == 'WORD' and
              token['string'].lower() in ["jalan", "raya", "kaligawe", "semarang", "demak", "jawa", "tengah"] and
              token['part_of_speech_features'] == 'NOUN'):
            token['entity_type'] = "LOCATION"

        # Rule for ORGANIZATION
        elif (token['token_kind'] == 'WORD' and
              token['string'].istitle() and
              token['contextual_features'] == 'OOV'):
            token['entity_type'] = "ORGANIZATION"

        # If not classified into any of the above, keep as ""
        else:
            token['entity_type'] = "OTHER"

    return tokens

# Fungsi utama


def main():
    # Mengambil data dari tabel clusters
    df = fetch_data()
    print("Kolom yang tersedia dalam DataFrame:", df.columns)

    # Pastikan kolom 'text' ada dalam DataFrame
    if 'text' not in df.columns:
        print("Kolom 'text' tidak ditemukan dalam tabel clusters.")
        return

    documents = df['text'].tolist()
    cluster_ids = df['cluster_id'].tolist()

    # Menghitung nilai TF-IDF untuk setiap dokumen
    tf_idf_scores = compute_hybrid_tf_idf(documents)

    # Menghitung nilai W(S) dan nf(S) untuk setiap kalimat
    sentence_scores, nf_S = compute_w_s_and_nf_s(documents, tf_idf_scores)

    if sentence_scores:
        for i, score in enumerate(sentence_scores):
            document = documents[i]
            cluster_id = cluster_ids[i]
            tfidf_scores = tf_idf_scores[i]
            W_S = score

            # Menyimpan hasil TF-IDF ke tabel hybrid_tfidf
            save_tfidf_results_to_db(
                cluster_id, document, tfidf_scores, W_S, nf_S)

        # Menentukan kalimat utama
        main_sentence_index = np.argmax(sentence_scores)
        main_sentence = documents[main_sentence_index]
        main_sentence_cluster = cluster_ids[main_sentence_index]

        print("Kalimat utama yang ditemukan:")
        print(f"Kalimat: {main_sentence}")
        print(f"Cluster ID: {main_sentence_cluster}")

        # Melakukan tokenisasi dan NER pada kalimat utama
        tokens = tokenize_and_assign_features(
            main_sentence, main_sentence_cluster)
        tokens = apply_ner_rules(tokens)

        # Menyimpan hasil ke tabel ner
        save_results_to_db(tokens)
    else:
        print("Tidak ada kalimat yang ditemukan.")


if __name__ == "__main__":
    main()
