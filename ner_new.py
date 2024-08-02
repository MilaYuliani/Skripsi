import mysql.connector
import json
import sys
import re


def connect_to_db():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='databanjir'
    )
    return connection


def is_date_string(word):
    return bool(re.match(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b', word))


def is_day_string(word):
    days = ["senin", "selasa", "rabu", "kamis", "jumat", "sabtu", "minggu"]
    return word.lower() in days


def tokenize_and_assign_features(text):
    tokens = []
    current_word = ""
    i = 0
    while i < len(text):
        char = text[i]
        if char.isalnum() or char in '/-':
            current_word += char
            if is_date_string(current_word):
                tokens.append(current_word)
                current_word = ""
            elif is_day_string(current_word):
                tokens.append(current_word)
                current_word = ""
        else:
            if current_word:
                tokens.append(current_word)
                current_word = ""
            if char.strip():
                tokens.append(char)
        i += 1
    if current_word:
        tokens.append(current_word)

    processed_tokens = []
    for word in tokens:
        if is_date_string(word):
            token_kind = 'NUM'
            part_of_speech_features = 'DATE'
            morphological_features = 'DigitSlash'
        elif is_day_string(word):
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

        location_keywords = [
            "wilayah", "jalan", "kabupaten", "kecamatan", "provinsi", "kota", "desa",
            "kelurahan", "gunung", "merapi", "bukit", "sungai", "danau", "pulau", "pantai", "musi", "perkampungan"
            "tanah", "bumbu", "dusun", "lembah", "lereng", "rawa"
        ]
        frequently_flooded_areas = [
            "jakarta", "bekasi", "bogor", "bandung", "cirebon", "semarang", "sukabumi",
            "cianjur", "solo", "yogyakarta", "surabaya", "malang", "sidoarjo", "makasar", "sumbawa", "Agam", "datar",
            "medan", "palembang", "jambi", "pekanbaru", "denpasar",
            "pontianak", "banjarmasin", "manado", "padang", "ambon", "jayapura", "ulupulu", "agam",
            "tangerang", "tangerang", "depok", "probolinggo", "kediri", "lombok"
        ]
        frequently_flooded_provinces = [
            "aceh", "bali", "banten", "bengkulu", "jambi" "yogyakarta", "dki",
            "gorontalo", "jambi", "jawa", "kalimantan", "kepulauan", "bangka", "belitung", "riau", "lampung", "maluku",
            "papua", "sulawesi", "sumatera", "nusa", "ntt", "lampung"

        ]
        direction_keywords = ["tengah", "utara",
                              "selatan", "barat", "tenggara", "timur"]
        common_non_location_words = ["yang", "dan", "dengan",
                                     "untuk", "oleh", "serta", "atau", "namun", "antaranya", "terendam", "rawan", "pada", "memastikan", "mulai", "ada", "harus", "nugini"]

        if word.lower() in location_keywords or word.lower() in frequently_flooded_areas or word.lower() in frequently_flooded_provinces:
            contextual_features = 'LPRE'
        elif word.lower() in direction_keywords:
            contextual_features = 'LSUF'
        elif word.lower() in ["tanah", "longsor", "banjir", "bandang", "lahar", "dingin", "rob", "gempa", "kebakaran", "angin", "puting", "beliung"]:
            contextual_features = 'OOV'
        elif word.lower() in ["badan", "nasional", "penanggulangan", "bencana", "daerah", "bnpb", "bpbd", "bmkg", "Meteorologi", "Klimatologi", "Geofisika" "pemkab", "pemkot"]:
            contextual_features = 'OCON'
        elif word.lower() in ["di", "ke", "dari"]:
            contextual_features = 'LOPP'
        elif word.lower() in ["dr.", "pak", "k.h.", "prof.", "ibu"]:
            contextual_features = 'PPRE'
        elif word.lower() in common_non_location_words:
            contextual_features = 'NONLOCATION'
        else:
            contextual_features = ''

        token = {
            'teks_kata': word,
            'jenis_kata': token_kind,
            'kontektual': contextual_features,
            'morfologi': morphological_features,
            'spech': part_of_speech_features,
            'type_ner': ""
        }
        processed_tokens.append(token)
    return processed_tokens


def apply_ner_rules(tokens):
    for i in range(len(tokens)):
        token = tokens[i]

        if (token['jenis_kata'] == 'WORD' and token['kontektual'] in ['LPRE', 'LSUF', 'LOPP']):
            token['type_ner'] = "LOCATION"
            if (i + 1 < len(tokens) and tokens[i + 1]['jenis_kata'] == 'WORD' and tokens[i + 1]['kontektual'] not in ['NONLOCATION']):
                tokens[i + 1]['type_ner'] = "LOCATION"

        # Mengubah aturan untuk kata 'bencana'
        elif (token['jenis_kata'] == 'WORD' and token['teks_kata'].lower() == 'bencana'):
            # Cek konteks sebelumnya untuk menentukan apakah 'bencana' adalah 'ORGANIZATION'
            if (i > 0 and tokens[i - 1]['teks_kata'].lower() in ['penanggulangan', 'bpbd']) or \
                    (i > 2 and ' '.join([tokens[i - 3]['teks_kata'].lower(), tokens[i - 2]['teks_kata'].lower(), tokens[i - 1]['teks_kata'].lower()]) == 'badan nasional penanggulangan'):
                token['type_ner'] = "ORGANIZATION"
            else:
                token['type_ner'] = "DISASTER"

        elif (token['jenis_kata'] == 'WORD' and token['kontektual'] == 'OOV' and token['teks_kata'].lower() in ["tanah", "longsor", "banjir", "bandang", "lahar", "dingin", "rob", "gempa", "bumi", "angin", "puting", "beliung"]):
            token['type_ner'] = "DISASTER"

        elif (token['jenis_kata'] == 'WORD' and token['kontektual'] in ['OCON', 'PPRE']):
            token['type_ner'] = "ORGANIZATION"

        elif (token['type_ner'] == "" and token['jenis_kata'] == 'WORD' and (token['morfologi'] == 'TitleCase' and not is_day_string(token['teks_kata']))):
            if (i + 1 < len(tokens) and tokens[i + 1]['jenis_kata'] == 'WORD' and tokens[i + 1]['morfologi'] == 'TitleCase'):
                token['type_ner'] = "PERSON"
                tokens[i + 1]['type_ner'] = "PERSON"
            else:
                token['type_ner'] = "PERSON"

        elif (token['jenis_kata'] == 'NUM' and token['spech'] == 'DATE'):
            token['type_ner'] = "DATE"

        elif (token['jenis_kata'] == 'WORD' and token['teks_kata'].lower() in ["senin", "selasa", "rabu", "kamis", "jumat", "sabtu", "minggu"]):
            token['type_ner'] = "DAY"

        if token['type_ner'] == "" and token['kontektual'] != 'OTHER':
            token['type_ner'] = "OTHER"

    return tokens


def save_results_to_db(tokens, table_name="ner_testing"):
    connection = connect_to_db()
    cursor = connection.cursor()

    try:
        for token in tokens:
            cursor.execute(f"""
                INSERT INTO ner_testing (teks_kata, jenis_kata, kontektual, morfologi, spech, type_ner) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                token['teks_kata'], token['jenis_kata'],
                token['kontektual'], token['morfologi'],
                token['spech'], token['type_ner']
            ))

        connection.commit()
    except Exception as e:
        print(f"Gagal menyimpan data ke database ner_testing:", e)
    finally:
        cursor.close()
        connection.close()


def process_new_sentence(sentence, table_name="ner_testing"):
    tokens = tokenize_and_assign_features(sentence)
    tokens = apply_ner_rules(tokens)
    save_results_to_db(tokens, table_name)
    return tokens


if __name__ == "__main__":
    sentence = sys.argv[1]
    tokens = process_new_sentence(sentence)
    print(json.dumps(tokens, ensure_ascii=False, indent=4))
