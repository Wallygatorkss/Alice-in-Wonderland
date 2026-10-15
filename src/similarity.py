import json
import sys
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BOOKS_INFO = {
    "11": {"title": "Alice's Adventures in Wonderland", "cat": "Children / Young Adult"},
    "12": {"title": "Through the Looking-Glass", "cat": "Children / Young Adult"},
    "16": {"title": "Peter Pan", "cat": "Children / Young Adult"},
    "55": {"title": "The Wonderful Wizard of Oz", "cat": "Children / Young Adult"},
    "113": {"title": "The Secret Garden", "cat": "Children / Young Adult"},
    "120": {"title": "Treasure Island", "cat": "Children / Young Adult"},
    "236": {"title": "The Jungle Book", "cat": "Children / Young Adult"},
    "108": {"title": "The Return of Sherlock Holmes", "cat": "Crime, Mystery & Thriller"},
    "834": {"title": "The Memoirs of Sherlock Holmes", "cat": "Crime, Mystery & Thriller"},
    "863": {"title": "The Mysterious Affair at Styles", "cat": "Crime, Mystery & Thriller"},
    "1661": {"title": "The Adventures of Sherlock Holmes", "cat": "Crime, Mystery & Thriller"},
    "61262": {"title": "Poirot Investigates", "cat": "Crime, Mystery & Thriller"},
    "69087": {"title": "The murder of Roger Ackroyd", "cat": "Crime, Mystery & Thriller"},
    "70114": {"title": "The Big Four", "cat": "Crime, Mystery & Thriller"},
    "35": {"title": "The Time Machine", "cat": "Science-Fiction & Fantasy"},
    "36": {"title": "The War of the Worlds", "cat": "Science-Fiction & Fantasy"},
    "84": {"title": "Frankenstein; Or, The Modern Prometheus", "cat": "Science-Fiction & Fantasy"},
    "159": {"title": "The island of Doctor Moreau", "cat": "Science-Fiction & Fantasy"},
    "164": {"title": "Twenty Thousand Leagues under the Sea", "cat": "Science-Fiction & Fantasy"},
    "345": {"title": "Dracula", "cat": "Science-Fiction & Fantasy"},
    "68283": {"title": "The call of Cthulhu", "cat": "Science-Fiction & Fantasy"}
}

def get_similar_books(target_id):
    target_id_str = str(target_id)

    try:
        with open("src/summaries.json", "r", encoding="utf-8") as f:
            summaries = json.load(f)
    except FileNotFoundError:
        with open("summaries.json", "r", encoding="utf-8") as f:
            summaries = json.load(f)

    if target_id_str not in summaries:
        return []

    ids = list(summaries.keys())
    texts = []
    
    for book_id in ids:
        summary = summaries[book_id]
        category = BOOKS_INFO.get(book_id, {}).get("cat", "")
        texte_combine = summary + (" " + category) * 3
        texts.append(texte_combine)
    
    try:
        target_index = ids.index(target_id_str)
    except ValueError:
        return []

    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(texts)

    cosine_similarities = cosine_similarity(tfidf_matrix[target_index], tfidf_matrix).flatten()

    related_docs_indices = cosine_similarities.argsort()[::-1]
    top_5_indices = related_docs_indices[1:6]

    top_5_titles = []
    for i in top_5_indices:
        book_id = ids[i]
        title = BOOKS_INFO.get(book_id, {}).get("title", f"Unknown Title (ID {book_id})")
        top_5_titles.append(title)

    return top_5_titles