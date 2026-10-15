from book_summarizer import summarize_book

def main():
    book_ids = [
        61262,
        69087,
        70114,
        35,
        36,
        84,
        159,
        164,
        345,
        4,
        68283
    ]
    
    print(f"Lancement de la génération automatisée pour {len(book_ids)} livres...\n")
    
    for book_id in book_ids:
        print("="*60)
        print(f"Lancement du test pour le livre ID: {book_id}")
        print("="*60)
        
        try:
            result = summarize_book(book_id)
            
            print(f"\n Résultat pour {book_id} :")
            print(result)
            
        except Exception as e:
            print(f"\n Une erreur est survenue lors du test du livre {book_id} : {e}")
            
    print("\n Traitement pour tout les livres terminé ")

if __name__ == "__main__":
    main()
