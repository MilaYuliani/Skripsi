import mysql.connector
import numpy as np
import pandas as pd
import re


def connect_to_db():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='databanjir'
    )
    return connection


def fetch_data():
    connection = connect_to_db()
    query = "SELECT cluster_id, text FROM clusters"
    df = pd.read_sql(query, connection)
    connection.close()
    return df


def save_results_to_db(tokens):
    connection = connect_to_db()
    cursor = connection.cursor()

    try:
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
    except Exception as e:
        print("Gagal menyimpan data ke database:", e)
    finally:
        cursor.close()
        connection.close()


def is_date_string(word):
    return bool(re.match(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b', word))


def is_day_string(word):
    days = ["senin", "selasa", "rabu", "kamis", "jumat", "sabtu", "minggu"]
    return word.lower() in days


def tokenize_and_assign_features(text, cluster_id):
    tokens = []
    current_word = ""
    i = 0
    while i < len(text):
        char = text[i]
        if char.isalnum() or char in '/-':  # Bagian dari kata atau tanggal
            current_word += char
            if is_date_string(current_word):
                tokens.append(current_word)
                current_word = ""
            elif is_day_string(current_word):  # Tambahkan pemeriksaan hari
                tokens.append(current_word)
                current_word = ""
        else:  # Tanda baca atau spasi
            if current_word:
                tokens.append(current_word)
                current_word = ""
            if char.strip():  # Jika bukan spasi, tambahkan sebagai token terpisah
                tokens.append(char)
        i += 1
    if current_word:  # Tambahkan kata terakhir jika ada
        tokens.append(current_word)

    processed_tokens = []
    for word in tokens:
        if is_date_string(word):
            token_kind = 'NUM'
            part_of_speech_features = 'DATE'
            morphological_features = 'DigitSlash'
        elif is_day_string(word):  # Tambahkan pemeriksaan hari
            token_kind = 'WORD'
            part_of_speech_features = 'DAY'
            morphological_features = 'TitleCase' if word.istitle() else 'LowerCase'
        elif word.isalpha():
            token_kind = 'WORD'
            part_of_speech_features = 'NOUN'
            morphological_features = 'TitleCase' if word.istitle() else 'LowerCase'
        elif word in ',()':
            token_kind = 'PUNC'
            part_of_speech_features = 'PUNC'
            morphological_features = 'LowerCase'
        else:
            token_kind = 'SPUNC'
            part_of_speech_features = 'SPUNC'
            morphological_features = 'LowerCase'

        # Daftar lokasi dan provinsi
        location_keywords = [
            "wilayah", "jalan", "kabupaten", "kecamatan", "provinsi", "kota", "desa",
            "kelurahan", "gunung", "bukit", "sungai", "danau", "pulau", "pantai", "tanah"
        ]
        frequently_flooded_areas = [
            "jakarta", "bekasi", "bogor", "bandung", "cirebon", "semarang",
            "solo", "yogyakarta", "surabaya", "malang", "sidoarjo", "makassar",
            "medan", "palembang", "jambi", "pekanbaru", "banda aceh", "denpasar",
            "pontianak", "banjarmasin", "manado", "padang", "ambon", "jayapura", "ulupulu", "agam"
        ]
        frequently_flooded_provinces = [
            "dki jakarta", "jawa", "sumatera", "kalimantan", "aceh", "banten", "sulawesi", "nusa", "NTT"
        ]
        direction_keywords = ["tengah", "utara",
                              "selatan", "barat", "tenggara", "timur"]

        # Contextual features
        if word.lower() in location_keywords or word.lower() in frequently_flooded_areas or word.lower() in frequently_flooded_provinces:
            contextual_features = 'LPRE'
        elif word.lower() in direction_keywords:
            contextual_features = 'LSUF'
        elif word.lower() in ["bencana", "longsor", "banjir", "bandang", "lahar", "rob"]:
            contextual_features = 'OOV'
        elif word.lower() in ["badan", "nasional", "penanggulangan", "bencana", "bnpb", "pemkab"]:
            contextual_features = 'OCON'
        elif word.lower() in ["di", "ke", "dari"]:
            contextual_features = 'LOPP'
        elif word.lower() in ["dr.", "pak", "k.h.", "prof.", "ibu"]:
            contextual_features = 'PPRE'
        else:
            contextual_features = ''

        token = {
            'string': word,
            'cluster_id': cluster_id,
            'token_kind': token_kind,
            'contextual_features': contextual_features,
            'morphological_features': morphological_features,
            'part_of_speech_features': part_of_speech_features,
            'entity_type': ""
        }
        processed_tokens.append(token)
    return processed_tokens


def apply_ner_rules(tokens):
    for i in range(len(tokens)):
        token = tokens[i]

        # Rule for LOCATION
        if (token['token_kind'] == 'WORD' and token['contextual_features'] in ['LPRE', 'LSUF', 'LOPP']):
            # Exclude certain words from being marked as LOCATION
            if token['string'].lower() not in ['dan', 'terendam']:
                token['entity_type'] = "LOCATION"
                if (i + 1 < len(tokens) and tokens[i + 1]['token_kind'] == 'WORD' and tokens[i + 1]['entity_type'] == ""):
                    tokens[i + 1]['entity_type'] = "LOCATION"

        # Rule for DISASTER
        elif (token['token_kind'] == 'WORD' and token['contextual_features'] == 'OOV' and token['string'].lower() in ["bencana", "banjir", "longsor", "bandang", "lahar"] and token['part_of_speech_features'] == 'NOUN'):
            token['entity_type'] = "DISASTER"

        # Rule for ORGANIZATION
        elif (token['token_kind'] == 'WORD' and token['contextual_features'] in ['OCON', 'PPRE']):
            token['entity_type'] = "ORGANIZATION"

        # Rule for PERSON (apply only if not already marked as LOCATION)
        elif (token['entity_type'] == "" and token['token_kind'] == 'WORD' and (token['morphological_features'] == 'TitleCase' and not is_day_string(token['string']))):
            if (i + 1 < len(tokens) and tokens[i + 1]['token_kind'] == 'WORD' and tokens[i + 1]['morphological_features'] == 'TitleCase'):
                token['entity_type'] = "PERSON"
                tokens[i + 1]['entity_type'] = "PERSON"
            else:
                token['entity_type'] = "PERSON"

        # Rule for DATE
        elif (token['token_kind'] == 'NUM' and token['part_of_speech_features'] == 'DATE'):
            token['entity_type'] = "DATE"

        # Rule for DAY
        elif (token['token_kind'] == 'WORD' and token['string'].lower() in ["senin", "selasa", "rabu", "kamis", "jumat", "sabtu", "minggu"]):
            token['entity_type'] = "DAY"

        # Rule for OTHER (applied if no other rule matches)
        if token['entity_type'] == "":
            token['entity_type'] = "OTHER"

    return tokens


def process_new_sentence(sentence, cluster_id):
    tokens = tokenize_and_assign_features(sentence, cluster_id)
    tokens = apply_ner_rules(tokens)
    save_results_to_db(tokens)
    return tokens


def main():
    kalimat1 = "Badan Nasional Penanggulangan Bencana (BNPB) melaporkan 24 desa di Kabupaten Tanah Bumbu , Kalimantan Selatan terendam banjir , Jumat (7/6/2024)"
    kalimat2 = "Pemkab Agam dan Kabupaten Tanah Datar telah menetapkan status tanggap darurat atas bencana tanah longsor banjir bandang dan aliran lahar dingin selama 14 hari"

    process_new_sentence(kalimat1, 1)
    process_new_sentence(kalimat2, 2)


if __name__ == "__main__":
    main()
