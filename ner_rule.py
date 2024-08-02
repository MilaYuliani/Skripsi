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


def save_results_to_db(tokens):
    connection = connect_to_db()
    cursor = connection.cursor()

    try:
        for token in tokens:
            cursor.execute("""
                INSERT INTO ner (token_string, token_kind, contextual_features, morphological_features, part_of_speech_features, entity_type) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                token['string'], token['token_kind'],
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


# Tabel fitur kontekstual dengan dua contoh untuk setiap kategori
contextual_features_map = {
    'dr.': 'PRE', 'pak': 'PRE',  # Person Prefix
    'bin': 'PMID', 'van': 'PMID',  # Person Middle
    's.kom.': 'PSUF', 's.h.': 'PSUF',  # Person Suffix
    'menristek': 'PTIT', 'mendagri': 'PTIT',  # Person Title
    'pt': 'OPRE', 'universitas': 'OPRE',  # Organization Prefix
    'ltd.': 'OSUF', 'corp.': 'OSUF',  # Organization Suffix
    'ketua': 'OPOS', 'presiden': 'OPOS',  # Position in Organization
    'muktamar': 'OCON', 'rakernas': 'OCON',  # Other Organization Contextual
    'kota': 'LPRE', 'provinsi': 'LPRE',  # Location Prefix
    'demak': 'LPRE',
    'utara': 'LSUF', 'timur': 'LSUF',  # Location Suffix
    'gubernur': 'LLDR', 'walikota': 'LLDR',  # Location Leader
    'oleh': 'POLP', 'untuk': 'POLP',  # Preposition with Person Name
    'di': 'LOPP', 'ke': 'LOPP',  # Preposition with Location Name
    'senin': 'DAY', 'jumat': 'DAY',  # Day Name
    'mei': 'MONTH', 'juni': 'MONTH',  # Month Name
}

# Tabel fitur morfologis dengan dua contoh untuk setiap kategori
morphological_features_map = {
    'Soedirman': 'TitleCase', 'Muhammad': 'TitleCase',  # Title Case
    'LeIP': 'MixedCase', 'TeSt': 'MixedCase',  # Mixed Case
    'KPK': 'UpperCase', 'USA': 'UpperCase',  # Upper Case
    'menuntut': 'LowerCase', 'berhasil': 'LowerCase',  # Lower Case
    'P3K': 'CharDigit', 'a1b2': 'CharDigit',  # Char Digit
    '2002': 'Digit', '12345': 'Digit',  # Digit
    '17/5': 'DigitSlash', '01/01': 'DigitSlash',  # Digit Slash
    '20,5': 'Numeric', '17.500,00': 'Numeric',  # Numeric
    'Satu': 'NumStr', 'Dua': 'NumStr',  # Number String
    'VII': 'Roman', 'XI': 'Roman',  # Roman
    '18:05': 'TimeFrom', '07:30': 'TimeFrom',  # Time From
}

# Tabel fitur Part-of-Speech dengan dua contoh untuk setiap kategori
pos_features_map = {
    'si': 'ART', 'sang': 'ART',  # Article
    'indah': 'ADJ', 'baik': 'ADJ', 'tanggap': 'ADJ', 'darurat': 'ADJ', 'dingin': 'ADJ',  # Adjective
    'telah': 'ADV', 'kemarin': 'ADV', 'lalu': 'ADV',  # Adverb
    'harus': 'AUX', 'akan': 'AUX',  # Auxiliary verb
    'dan': 'C', 'atau': 'C', 'yang': 'C',  # Conjunction
    'merupakan': 'DEF', 'adalah': 'DEF',  # Definition
    'rumah': 'NOUN', 'demak': 'NOUN', 'bulan': 'NOUN', 'pemkab': 'NOUN', 'agam': 'NOUN',  # Noun
    'bencana': 'NOUN', 'banjir': 'NOUN', 'rob': 'NOUN', 'bandang': 'NOUN', 'longsor': 'NOUN',
    'desa': 'NOUN', 'kabupaten': 'NOUN', 'datar': 'NOUN', 'status': 'NOUN',
    'badan': 'NOUN', 'nasional': 'NOUN', 'penanggulangan': 'NOUN', 'bnpb': 'NOUN',
    'tanah': 'NOUN', 'bumbu': 'NOUN', 'kalimantan': 'NOUN', 'selatan': 'NOUN',
    'aliran': 'NOUN', 'lahar': 'NOUN',
    'nelayan': 'NOUNP', 'keluarga': 'NOUNP',  # Personal Noun
    'satu': 'NUM', 'dua': 'NUM',  # Number
    'akan': 'MODAL', 'mungkin': 'MODAL',  # Modal
    '-': 'OOV',  # Out of dictionary
    'kah': 'PAR', 'pun': 'PAR',  # Particle
    'di': 'PREP', 'ke': 'PREP',  # Preposition
    'dalam': 'PREP', 'pada': 'PREP', 'atas': 'PREP',
    'saya': 'PRO', 'beliau': 'PRO',  # Pronominal
    'menuduh': 'VACT', 'memukul': 'VACT', 'menetapkan': 'VACT',  # Active Verb
    'dituduh': 'VPAS', 'dilihat': 'VPAS',  # Passive Verb
    'pergi': 'VERB', 'tidur': 'VERB', 'melaporkan': 'VERB',
    'beradaptasi': 'VERB', 'menghadapi': 'VERB', 'berlangsung': 'VERB',  # Verb
}


def determine_morphological_features(word):
    if word in morphological_features_map:
        return morphological_features_map[word]
    elif word.istitle():
        return 'TitleCase'
    elif word.isupper():
        return 'UpperCase'
    elif word.islower():
        return 'LowerCase'
    elif any(char.isdigit() for char in word) and any(char.isalpha() for char in word):
        return 'CharDigit'
    elif word.replace('/', '').isdigit():
        return 'DigitSlash'
    elif word.replace(',', '').replace('.', '').isdigit():
        return 'Numeric'
    elif word.isdigit():
        return 'Digit'
    else:
        return 'LowerCase'


def determine_pos_features(word):
    return pos_features_map.get(word.lower(), 'OOV')


def tokenize_and_assign_features(text):
    location_keywords = [
        "wilayah", "jalan", "kabupaten", "kecamatan", "provinsi", "kota", "desa",
        "kelurahan", "gunung", "merapi", "bukit", "sungai", "danau", "pulau", "pantai",
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
        "dki", "jakarta", "jawa", "sumatera", "kalimantan", "aceh", "banten", "sulawesi", "papua", "lampung", "aceh",
        "nusa", "NTT", "lampung", "riau",
    ]
    direction_keywords = ["tengah", "utara",
                          "selatan", "barat", "tenggara", "timur"]
    common_non_location_words = [
        "dan", "dengan", "untuk", "oleh", "harus", "serta", "atau", "namun", "terendam"]

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
            part_of_speech_features = 'NUM'
            morphological_features = 'DigitSlash'
        elif is_day_string(word):
            token_kind = 'WORD'
            part_of_speech_features = 'DAY'
            morphological_features = 'TitleCase' if word.istitle() else 'LowerCase'
        elif word.isalpha():
            token_kind = 'WORD'
            part_of_speech_features = determine_pos_features(word)
            morphological_features = determine_morphological_features(word)
        elif word in ',()':
            token_kind = 'PUNC'
            part_of_speech_features = '-'
            morphological_features = 'LowerCase'
        else:
            token_kind = 'SPUNC'
            part_of_speech_features = 'PUNC'
            morphological_features = 'LowerCase'

        if word.lower() in location_keywords or word.lower() in frequently_flooded_areas or word.lower() in frequently_flooded_provinces:
            contextual_features = 'LPRE'
        elif word.lower() in direction_keywords:
            contextual_features = 'LSUF'
        elif word.lower() in ["tanah", "longsor", "banjir", "bandang", "lahar", "dingin", "rob", "gempa", "kebakaran", "angin", "puting", "beliung"]:
            contextual_features = 'OOV'
        elif word.lower() in ["badan", "nasional", "penanggulangan", "bencana", "bnpb", "bpbd", "pemkab", "damkar"]:
            contextual_features = 'OCON'
        elif word.lower() in ["di", "ke", "dari"]:
            contextual_features = 'LOPP'
        elif word.lower() in ["dr.", "pak", "k.h.", "prof.", "ibu"]:
            contextual_features = 'PPRE'
        elif word.lower() in common_non_location_words:
            contextual_features = 'NONLOCATION'
        else:
            contextual_features = contextual_features_map.get(word.lower(), '')

        token = {
            'string': word,
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

        if (token['token_kind'] == 'WORD' and token['contextual_features'] in ['LPRE', 'LSUF', 'LOPP']):
            token['entity_type'] = "LOCATION"
            if (i + 1 < len(tokens) and tokens[i + 1]['token_kind'] == 'WORD' and tokens[i + 1]['contextual_features'] not in ['NONLOCATION']):
                tokens[i + 1]['entity_type'] = "LOCATION"

        # Mengubah aturan untuk kata 'bencana'
        elif (token['token_kind'] == 'WORD' and token['string'].lower() == 'bencana'):
            # Cek konteks sebelumnya untuk menentukan apakah 'bencana' adalah 'ORGANIZATION'
            if (i > 0 and (tokens[i - 1]['string'].lower() in ['penanggulangan', 'bpbd'])):
                token['entity_type'] = "ORGANIZATION"
            elif (i > 2 and ' '.join([tokens[i - 3]['string'].lower(), tokens[i - 2]['string'].lower(), tokens[i - 1]['string'].lower()]) == 'badan nasional penanggulangan'):
                token['entity_type'] = "ORGANIZATION"
            else:
                token['entity_type'] = "DISASTER"

        elif (token['token_kind'] == 'WORD' and token['contextual_features'] == 'OOV' and token['string'].lower() in ["tanah", "longsor", "banjir", "bandang", "lahar", "dingin", "rob", "gempa", "kebakaran", "angin", "puting", "beliung"]):
            token['entity_type'] = "DISASTER"

        elif (token['token_kind'] == 'WORD' and token['contextual_features'] in ['OCON', 'PPRE']):
            token['entity_type'] = "ORGANIZATION"

        elif (token['entity_type'] == "" and token['token_kind'] == 'WORD' and (token['morphological_features'] == 'TitleCase' and not is_day_string(token['string']))):
            if (i + 1 < len(tokens) and tokens[i + 1]['token_kind'] == 'WORD' and tokens[i + 1]['morphological_features'] == 'TitleCase'):
                token['entity_type'] = "PERSON"
                tokens[i + 1]['entity_type'] = "PERSON"
            else:
                token['entity_type'] = "PERSON"

        elif (token['token_kind'] == 'NUM' and token['part_of_speech_features'] == 'NUM'):
            token['entity_type'] = "OTHER"

        elif (token['token_kind'] == 'WORD' and token['string'].lower() in ["senin", "selasa", "rabu", "kamis", "jumat", "sabtu", "minggu"]):
            token['entity_type'] = "DAY"

        if token['entity_type'] == "" and token['contextual_features'] != 'OTHER':
            token['entity_type'] = "OTHER"

    return tokens


def process_new_sentence(sentence):
    tokens = tokenize_and_assign_features(sentence)
    tokens = apply_ner_rules(tokens)
    save_results_to_db(tokens)
    return tokens


def main():
    kalimat1 = "Badan Nasional Penanggulangan Bencana (BNPB) melaporkan 24 desa di Kabupaten Tanah Bumbu , Kalimantan Selatan terendam banjir , Jumat (7/6/2024)"
    kalimat2 = "Keluarga Nelayan di Demak harus beradaptasi dalam menghadapi bencana banjir rob yang berlangsung pada bulan lalu"
    kalimat3 = "Pemkab Agam dan Kabupaten Tanah Datar  telah menetapkan status tanggap darurat atas bencana tanah longsor , banjir bandang ,dan aliran lahar dingin selama 14 hari"

    process_new_sentence(kalimat1)
    process_new_sentence(kalimat2)
    process_new_sentence(kalimat3)


if __name__ == "__main__":
    main()
