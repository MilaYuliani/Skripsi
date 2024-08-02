import pandas as pd
import re
import mysql.connector
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory, ArrayDictionary, StopWordRemover
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

# Inisialisasi Sastrawi
stopword_factory = StopWordRemoverFactory()
stopword_remover = stopword_factory.create_stop_word_remover()

stemmer_factory = StemmerFactory()
stemmer = stemmer_factory.create_stemmer()

# Fungsi Case Folding


def case_folding(text):
    return text.lower()


# Konfigurasi koneksi ke database
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'databanjir'
}

# Mengambil data teks dan kamus normalisasi dari database


def fetch_text_from_database(db_config):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        query = "SELECT tweet_id, full_text FROM datacraw"
        cursor.execute(query)
        data = cursor.fetchall()

        query_kamus = "SELECT informal, formal FROM kamus"
        cursor.execute(query_kamus)
        normalization_data = cursor.fetchall()
        normalization_dict = {norm[0]: norm[1] for norm in normalization_data}

        cursor.close()
        conn.close()
        return data, normalization_dict
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return [], {}

# Menyimpan data ke dalam database


def save_to_database(data, db_config):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        query = """
            INSERT INTO proses (tweet_id, full_text, text_bersih)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
            full_text = VALUES(full_text),
            text_bersih = VALUES(text_bersih),
            updated_at = CURRENT_TIMESTAMP
        """
        cursor.executemany(query, data)
        conn.commit()

        cursor.close()
        conn.close()
        print("Data berhasil disimpan ke database.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")


# Mendapatkan teks dari database
texts_from_database, normalization_dict_from_db = fetch_text_from_database(
    db_config)
df = pd.DataFrame(texts_from_database, columns=['tweet_id', 'full_text'])

# Filtering berdasarkan keyword
# keywords = ["banjir", "tanah longsor", "gempa bumi",
#    "banjir tanah longsor", "banjir bandang tanah longsor"]
# df = df[df['full_text'].str.contains('|'.join(keywords), case=False, na=False)]

# Fungsi Preprocessing Teks


def preprocess_text(text):
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'@[A-Za-z0-9_]+', '', text)
    text = re.sub(r'#\w+', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


# Normalisasi teks
initial_normalization_dict = {
    'rp': 'rupiah', 'sumatera': 'sumatra', 'sumbar': 'sumatra barat', 'monggo': 'silahkan', 'gedeg': 'jengkel',
    'fansnya': 'penggemarnya', 'vs': 'dengan', 'dilanjutin': 'lanjutkan', 'i': 'aku', 'love': 'cinta', 'pulak': 'pula',
    'familiar': 'umum', 'gede': 'besar', 'kyak': 'seperti'
}

combined_normalization_dict = {
    **initial_normalization_dict, **normalization_dict_from_db}


def normalize_text(text):
    for informal, formal in combined_normalization_dict.items():
        text = re.sub(r'\b{}\b'.format(re.escape(informal)), formal, text)
    return text


df['full_text'] = df['full_text'].apply(case_folding)
df['normalized'] = df['full_text'].apply(preprocess_text).apply(normalize_text)

# Tokenisasi teks
df['tokenized'] = df['normalized'].apply(lambda x: x.split())

# Menghapus kata-kata stop
stop_words_factory = StopWordRemoverFactory()
stop_words = stop_words_factory.get_stop_words()
stop_words.extend([
    "nya", "wow", "loh", "lah", "hmmm", "deh", "xixixi", "halo", "mah", "dong", "awoakwokaok", "untuk",
    "dengan", "dari", "oleh", "akan", "dalam", "telah", "hihi", "ke", "bangsat", "kok", "juga", "taiii",
    "anjing", "ih", "wkwk", "woy", "elahhh", "um", "in", "kan", "iya", "jadi", "dulu", "adalah", "orang", "tewas", "ungsi",
    "oke", "hehe", "ck", "hehe", "hihi", "txt", "haha", "tidak", "ini", "itu", "an", "ah", "ya", "nah", "lama", "via", "hari", "per"
])
stop_words_remover = StopWordRemover(ArrayDictionary(stop_words))


def remove_stopwords(tokens):
    return [token for token in tokens if token not in stop_words]


df['stopwords_removed'] = df['tokenized'].apply(remove_stopwords)

# Stemming teks


def stem_tokens(tokens):
    return ' '.join(stemmer.stem(token) for token in tokens)


df['text_bersih'] = df['stopwords_removed'].apply(stem_tokens)

# Menghapus baris duplikat berdasarkan kolom 'tweet_id' dan 'text_bersih'
df = df.drop_duplicates(subset=['tweet_id', 'text_bersih'])

# Persiapan data untuk disimpan ke database
data_to_save = df[['tweet_id', 'full_text', 'text_bersih']].values.tolist()

# Menyimpan data ke database
save_to_database(data_to_save, db_config)
