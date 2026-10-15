import pathlib
from collections import Counter
import requests
from string import punctuation
import json
import re
from wordcloud import WordCloud, STOPWORDS

# Récupération des informations de base d'un livre à partir de son ID sur Project Gutenberg, avec mise en cache locale pour éviter les requêtes répétées

def get_book_info(ID):
    url = f'https://www.gutenberg.org/ebooks/{ID}'
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            title_match = re.search(r'<h1 class="header">(.+?)</h1>', response.text)
            author_match = re.search(r'<a href="/author/\d+" class="link">(.+?)</a>', response.text)
            title = title_match.group(1).strip() if title_match else f"Book_ID_{ID}"
            author = author_match.group(1).strip() if author_match else "Unknown Author"
            return {"title": title, "author": author}
    except Exception:
        pass
    return {"title": f"Book_ID_{ID}", "author": "Unknown Author"}

# Récupération du texte d'un livre à partir de son ID sur Project Gutenberg, avec mise en cache locale

def fetch_book(ID):
    path = pathlib.Path(__file__).parent / 'data' / 'raw' / f'{ID}.txt'
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        with open(path, 'r') as f:
            return f.read()
    else:
        url = f'https://www.gutenberg.org/files/{ID}/{ID}-0.txt'  
        response = requests.get(url)
        if response.status_code != 200:
            sec_url = f'https://www.gutenberg.org/files/{ID}/{ID}.txt' 
            sec = requests.get(sec_url)
            response = sec
        if response.status_code == 200:
            text = response.text
            with open(path, 'w', encoding='utf-8') as f:
                f.write(text)
            return text
        else:
            raise Exception(f'Erreur {ID}. HTTP code: {response.status_code}')
        
# Nettoyage du texte pour enlever les métadonnées et les notes de bas de page
        
def clean_text(text):
    start = text.find('*** START OF')
    end = text.find('*** END OF')
    if start != -1 and end != -1:
        text_clean = text.find('\n', start) + 1
        return text[text_clean:end].strip()
    else:
        return text.strip()
    
# Tokenisation du texte en mots, en supprimant la ponctuation et en convertissant en minuscules
    
def tokenize(text):
    words = text.lower().translate(str.maketrans('', '', punctuation)).split()
    return words

# Calcul des différentes mesures de diversité lexicale, avec mise en cache locale des résultats pour éviter les recalculs futurs

def get_lexdiv(ID):
    path = pathlib.Path(__file__).parent / 'data' / 'processed' / f'{ID}.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        with open(path, 'r') as f:
            return json.load(f) 
    else:
        words = tokenize(clean_text(fetch_book(ID)))
        counts = Counter(words)
        final = {}
        final['tok'] = len(words)
        final['typ'] = len(set(words))
        final['hap'] = len([word for word, count in counts.items() if count == 1])
        final['ttr'] = final['typ'] / final['tok'] if final['tok'] else 0
        final['mwl'] = sum(len(word) for word in words) / len(words) if words else 0
        final['mwf'] = final['tok'] / final['typ'] if final['typ'] else 0
        with open(path, 'w') as f:
            json.dump(final, f)
        return final
    
# Petit bonus : découpage du texte en sections à partir des titres de chapitres

def get_sections(ID):
    text = clean_text(fetch_book(ID))
    sections = re.split(r'(?i)chapter\s+[0-9ivxlc]+', text)
    return [section.strip() for section in sections if section.strip()]

# Bonus 2 : récupération de la couverture du livre, avec mise en cache locale pour éviter les téléchargements répétés

def fetch_cover(ID):
    path = pathlib.Path(__file__).parent / 'data' / 'covers' / f'{ID}.jpg'
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return str(path)
    url = f'https://www.gutenberg.org/cache/epub/{ID}/pg{ID}.cover.medium.jpg'
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            with open(path, 'wb') as f:
                f.write(response.content)
            return str(path)
    except Exception:
        pass
    return None

# Bonus 3 : génération d'un nuage de mots à partir du texte du livre, avec mise en cache locale pour éviter les recalculs futurs
    
def generate_wordcloud(ID):
    path = pathlib.Path(__file__).parent / 'data' / 'processed' / f'{ID}.png'
    path.parent.mkdir(parents=True, exist_ok=True)
    text = clean_text(fetch_book(ID))
    wordcloud = WordCloud(width=800, height=400, background_color='white', stopwords=STOPWORDS).generate(text)
    wordcloud.to_file(path)
    return str(path)