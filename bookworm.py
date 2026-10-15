import argparse
import json
from src.loader import *
from src.book_summarizer import *
from src.similarity import *
from src.topic_and_entities import *

def main():
    parser = argparse.ArgumentParser(description='BookWorm: Analyseur de textes du Project Gutenberg')
    parser.add_argument('--lexdiv', action='store_true', help="Affiche les statistiques de diversité lexicale")
    parser.add_argument('id', help='ID du livre sur Project Gutenberg')
    parser.add_argument("--topics", action="store_true", help="Extrait les thèmes principaux par section")
    parser.add_argument("--entities", action="store_true", help="Extrait les entités nommées (personnages, lieux)")
    parser.add_argument("--summary", action="store_true", help="Génère un résumé du livre via IA")
    parser.add_argument("--cover", action="store_true", help="Télécharge la couverture")
    parser.add_argument("--cloud", action="store_true", help="Génère le nuage de mots")
    parser.add_argument("--summarize", action="store_true", help="Résume le livre")
    parser.add_argument("--similar", action="store_true", help="Affiche les livres similaires basés sur la similarité de contenu")
    parser.add_argument("--card", action="store_true", help="Affiche la fiche technique du livre")
    args = parser.parse_args()

    if args.id:
        if args.lexdiv:
            print(f"Analyse lexicale de {args.id}...")
            print(get_lexdiv(args.id))

        if args.cover:
            print(f"Récupération de la couverture pour {args.id}...")
            path = fetch_cover(args.id)
            print(f"Image sauvegardée ici : {path}" if path else "Pas de couverture trouvée.")

        if args.cloud:
            print(f"Génération du nuage de mots pour {args.id} (sois patient)...")
            path = generate_wordcloud(args.id)
            print(f"Nuage sauvegardé ici : {path}")

        if args.summarize:
            print(f"Résumé de {args.id}...")
            print(summarize_book(args.id))

        if args.similar:
            print(f"Recherche de livres similaires à {args.id}...")
            print(get_similar_books(args.id))

        if args.topics:
            print(f"Extraction des thèmes principaux pour {args.id}...")
            print(get_topics(int(args.id)))

        if args.entities:
            print(f"Extraction des entités nommées pour {args.id}...")
            print(get_entities(int(args.id)))

        if args.card:
            print(f"Affichage de la fiche technique pour {args.id}...")
            info = get_book_info(args.id)
            lexdiv = get_lexdiv(args.id)
            topics = get_topics(int(args.id))
            entities = get_entities(int(args.id))
            summary = summarize_book(args.id)
            similar = get_similar_books(args.id)
            card = {
                "info": info,
                "lexdiv": lexdiv,
                "topics": topics,
                "entities": entities,
                "summary": summary,
                "similar": similar
            }
            for section, value in card.items():
                print(f"{section}:")
                print(json.dumps(value, ensure_ascii=False, indent=2))
                print()
    else:
        print("Veuillez fournir un argument suivi de l'ID du livre sur Project Gutenberg. Utilisez --help pour plus d'informations.")

    if not args.id:
        print("Veuillez fournir un ID de livre sur Project Gutenberg.")
        return

if __name__ == "__main__":
    main()