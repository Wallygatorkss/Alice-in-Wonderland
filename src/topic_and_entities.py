from src.loader import *
import re
from stop_words import get_stop_words
import spacy
import logging
import requests
from spacy.lang.en.examples import sentences 


black_liste = set(['the', 'and', 'that', 'with', 'this', 'for', 'from', 'are', 'was', 'but', 'not', 
                   'all', 'his', 'her', 'they', 'their', 'she', 'he', 'project', 'gutenberg', 'ebook',
                   'etext', 'license', 'copyright', 'illustration', 'illustrations', 'contents',
                   'content','chapter', 'chapters', 'preface', 'introduction', 'prologue', 'epilogue',
                   'edition', 'publisher', 'published', 'printing', 'volume', 'vol',
                   'title', 'author', 'authors', 'translator', 'editor', 'editors','“and', 'it’s', 'there’s', 'that’s', 'what’s', 'who’s', 'where’s', 'when’s', 'why’s', 'how’s', 'let’s', 'i’m', 'you’re', 'he’s', 'she’s', 'we’re', 'they’re', 'i’ve', 'you’ve', 'we’ve', 'they’ve',
                   'transcriber', 'proofreader', 'proofreaders', "don’t", "doesn’t", "didn’t", "can’t", "couldn’t", "won’t", "wouldn’t", "shouldn’t", 'i’ll',
                   'www', 'http', 'https', 'org', 'net', 'MILLENNIUM', 'millennium', 'FULCRUM', 'fulcrum', 'EDITION', 'Contents',
                   'ascii', 'utf', 'unicode', 'Lewis', 'lewis', 'Carroll', 'carroll', '\n', 'i’m', 'you’re', 'he’s', 'she’s', 'it’s', 'we’re', 'they’re', 'i’ve', 'you’ve', 'we’ve', 'they’ve',
                   'start', 'end', 'produced', 'distributed', 'release', 'released',
                   'character', 'set', 'file', 'text', 'header', 'footer',
                   's Tink',
                   'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII', 'XIII', 'XIV', 'XV', 'XVI', 'XVII', 'XVIII', 'XIX', 'XX', 'XXI', 'XXII', 'XXIII', 'XXIV', 'XXV', 'XXVI', 'XXVII', 'XXVIII', 'XXIX', 'XXX',
                   'i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x', 'xi', 'xii', 'xiii', 'xiv', 'xv', 'xvi', 'xvii', 'xviii', 'xix', 'xx', 'xxi', 'xxii', 'xxiii', 'xxiv', 'xxv', 'xxvi', 'xxvii', 'xxviii', 'xxix', 'xxx',
                   ])

nlp = None


def _get_nlp():
    global nlp
    if nlp is None:
        try:
            nlp = spacy.load("en_core_web_sm")
        except OSError as exc:
            raise RuntimeError(
                "Le modele spaCy 'en_core_web_sm' est introuvable. "
                "Installez-le avec: python3 -m spacy download en_core_web_sm"
            ) from exc
    return nlp


def normalize_entity(value: str) -> str:
    value = " ".join(value.split())
    value = value.replace("’", "'").replace("‘", "'")

    value = re.sub(r"\b([A-Za-z]+)(?:'s|s')\b", r"\1", value)

    value = re.sub(r"^s\s+", "", value, flags=re.IGNORECASE)

    value = value.strip("[]'\"“”`.,;:!?-_")
    value = re.sub(r"^(?:the|a|an)\s+", "", value, flags=re.IGNORECASE)
    return value.strip()


def is_noise(value: str):
    cleaned = normalize_entity(value)

    if not cleaned:
        return True, ""

    if any(ch in cleaned for ch in ["'", "’", "‘", '"', "“", "”"]):
        return True, ""

    cleaned_lowered = cleaned.lower()
    if "chapter" in cleaned_lowered:
        return True, ""
    if any(ch.isdigit() for ch in cleaned):
        return True, ""
    if "_" in cleaned:
        return True, ""
    if len(cleaned) < 2:
        return True, ""

    return False, cleaned

def book_exists(book_id: int | str) -> bool:
    urls = [
        f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt",
        f"https://www.gutenberg.org/files/{book_id}/{book_id}.txt",
    ]
    for url in urls:
        try:
            r = requests.get(url, timeout=8)
            if r.status_code == 200:
                return True
        except requests.RequestException:
            continue
    return False

def get_topics(book_id):
    dict_sections = {}
    if not isinstance(book_id, int) or book_id <= 0:
        logging.warning(f"ID invalide: {book_id}")
        return dict_sections
    if not book_exists(book_id):
        logging.warning(f"ID introuvable sur Gutenberg: {book_id}")
        return dict_sections
    
    extra_stop_words = get_stop_words('en')
    sections = get_sections(book_id)
    black_liste.update(extra_stop_words)
    
    
    for index, section in enumerate(sections, start=1):
        dict_main_topics = {}
        if len(sections) > 0:
            
            if len(section) > 0:
                liste_mots = tokenize(section)
                bracket_chunks = re.findall(r"\[([^\]]+)\]", section.lower())

                for chunk in bracket_chunks:
                    for w in chunk.split():
                        black_liste.add(w.lower())

                for mot in liste_mots:
                    mot = mot.lower().strip("[]'’‘“”\"")
                    if not mot:
                        continue
                    if mot not in black_liste:
                        if mot in dict_main_topics:
                            dict_main_topics[mot] += 1
                        else:
                            dict_main_topics[mot] = 1
                top_10 = sorted(dict_main_topics.items(), key=lambda item: item[1], reverse=True)[:10]
                dict_sections[index] = [word for word, _count in top_10]
            else:
                logging.warning("Aucune sous-section trouvée pour ce livre")
        else:
            logging.warning("Aucune section trouvée pour ce livre")
    return dict_sections

def get_entities(book_id):
    dict_entities = {"characters": [], "locations": []}
    if not isinstance(book_id, int) or book_id <= 0:
        logging.warning(f" ID invalide: {book_id}")
        return dict_entities
    if not book_exists(book_id):
        logging.warning(f" ID introuvable sur Gutenberg: {book_id}")
        return dict_entities
    
    text = fetch_book(book_id)
    cleaned_text = clean_text(text)
    if not cleaned_text or not cleaned_text.strip():
        logging.warning("Il n'y a pas de texte à analyser.")
        return dict_entities

    doc = _get_nlp()(cleaned_text)

    for ent in doc.ents:
        if ent.label_ == "PERSON":
            noise, cleaned_name = is_noise(ent.text)
            if not noise and cleaned_name not in black_liste:
                if not any(cleaned_name.lower() == c.lower() for c in dict_entities["characters"]):
                    dict_entities["characters"].append(cleaned_name)

        elif ent.label_ in {"GPE", "LOC"}:
            noise, cleaned_location = is_noise(ent.text)
            if not noise and cleaned_location not in black_liste:
                if not any(cleaned_location.lower() == loc.lower() for loc in dict_entities["locations"]):
                    dict_entities["locations"].append(cleaned_location)
    return dict_entities
