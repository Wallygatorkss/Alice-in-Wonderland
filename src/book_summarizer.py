from src.loader import *
from summarizer import Summarizer
from transformers import pipeline
import nltk
import textwrap
import re
import json
import os

nltk.download('punkt', quiet=True)

abstractive_summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize_with_transformers(text, chunk_size=3000):
    """
    Prend un texte long, le découpe, et utilise BART pour générer un résumé abstrait.
    """
    chunks = textwrap.wrap(text, chunk_size, break_long_words=False)
    
    summaries = []
    for chunk in chunks:
        try:
            chunk_length = len(chunk.split())
            if chunk_length < 40:
                summaries.append(chunk)
                continue

            max_len = min(200, chunk_length - 10) 

            summary = abstractive_summarizer(chunk, max_length=max_len, min_length=50, do_sample=False)
            summaries.append(summary[0]['summary_text'])
        except Exception as e:
            continue
            
    full_summary = " ".join(summaries)
    
    if len(full_summary) > chunk_size:
        return summarize_with_transformers(full_summary, chunk_size)
        
    return full_summary

def summarize_book(id):
    """
    Résume les premiers chapitres d'un livre (façon 4e de couverture) et sauvegarde dans un JSON.
    """
    print("Chargement du livre")
    raw_text = fetch_book(id)

    title_match = re.search(r"Title:\s*(.+)", raw_text, re.IGNORECASE)
    book_title = title_match.group(1).strip() if title_match else f"Book_ID_{id}"
    
    text = clean_text(raw_text)

    print("Découpage par chapitres")
    chapters_raw = re.split(r'(?i)chapter\s+[IVXLCDM0-9]+\.?', text)

    chapters = [c.strip() for c in chapters_raw if len(c.strip()) > 1000]

    chapters_to_process = chapters[:3]
    
    print(f"Utilisation des {len(chapters_to_process)} premiers chapitres pour la 4e de couverture...")
    bert_model = Summarizer()

    intro_text = " ".join(chapters_to_process)

    print("Extraction des phrases clés du début de l'histoire...")
    best_sentences = bert_model(intro_text, num_sentences=20)

    print("Génération du résumé court...")
    if len(best_sentences.split()) > 40:
        final_blurb = summarize_with_transformers(best_sentences)
    else:
        final_blurb = best_sentences

    match = re.search(r'.*[.!?]', final_blurb, flags=re.DOTALL)
    if match:
        final_blurb = match.group(0)

    if final_blurb.count('“') > final_blurb.count('”'):
        final_blurb += '”'
    elif final_blurb.count('"') % 2 != 0:
        final_blurb += '"'

    json_path = "summaries.json"
    summary_data = {}

    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            try:
                summary_data = json.load(f)
            except json.JSONDecodeError:
                pass

    summary_data[str(id)] = final_blurb

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, ensure_ascii=False, indent=4)
        
    print(f"Résumé sauvegardé dans '{json_path}' pour l'ID : {id}")
    return final_blurb
