import json
import os
from datetime import datetime
import hashlib
import argparse #CLI
import sys #CLI

from parser_azubi import parse_azubiyo
from parser_stellen import parse_stellen

def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Azubi Vacancy Parser mit Cache',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False,
        epilog="""
Hilfe:
 python main.py                    # checken neue stellenangebote
 python main.py --all              # zeigen alles
 python main.py --cache            # cache zeigen
 python main.py --clear-cache      # cache leeren
        """
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='alle stelleangebote zeigen'
    )
    
    parser.add_argument(
        '--cache',
        action='store_true',
        help='cache zeigen'
    )
    
    parser.add_argument(
        '--clear-cache',
        action='store_true',
        help='cache leeren'
    )

    parser.add_argument(
        '--help', '-h',
        action='store_true',
        help='hinweis anzeigen'
    )
    
    return parser.parse_args()

CACHE_FILE = 'vacancies_cache.json'

def generate_vacancy_id(vacancy_text):
    """
    unique ID für jede stelle
    """
    # hash MD5
    text_hash = hashlib.md5(vacancy_text.encode('utf-8')).hexdigest()
    return f"vac_{text_hash[:50]}"

def load_cache():
    """
    returns {vacancy_id: vacancy_data} für die schnellsuche
    """
    if not os.path.exists(CACHE_FILE):
        return {}
    
    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            cache_dict = {}
            for item in data:
                cache_dict[item['id']] = item
            return cache_dict
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def save_cache(vacancies_list):
    """cache in JSON"""
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(vacancies_list, f, ensure_ascii=False, indent=2)

def enrich_vacancy_data(raw_vacancies, source='azubiyo'):
    """
    daten = id+hash
    """
    enriched = []
   
    for text in raw_vacancies:
       if not text or not text.strip():
           continue
           
       vacancy = {
           'id': generate_vacancy_id(text),
           'text': text.strip(),
           'source': source,
           'first_seen': datetime.now().isoformat()
       }
       enriched.append(vacancy)
   
    return enriched

def main():
    """
    main funktion
    """
    args = parse_arguments()

    if args.help:
        print("=" * 60)
        print("AZUBI VACANCY PARSER - HILFE")
        print("=" * 60)
        print("\nVerwendung:")
        print("  python main.py                    # Neue Stellenangebote prüfen")
        print("  python main.py --all              # Alle Stellenangebote anzeigen")
        print("  python main.py --cache            # Cache-Inhalt anzeigen")
        print("  python main.py --clear-cache      # Cache leeren")
        print("  python main.py --help             # Diese Hilfe anzeigen")
        print("\n" + "=" * 60)
        return 
    
    print("=" * 60)
    print("AZUBI VACANCY CHECKER MIT CACHE")
    print("=" * 60)
    
    print("\n[1/4] parsing prozess...")
    azubi_vacancies = parse_azubiyo()
    stellen_vacancies = parse_stellen()
    
    # alles
    all_vacancies = azubi_vacancies + stellen_vacancies
    
    print(f"    ✓  {len(all_vacancies)} stelleangebote gefunden")
    
    print("\n[2/4] verarbeiten daten...")
    
    
    azubi_enriched = enrich_vacancy_data(azubi_vacancies, source='azubiyo')
    stellen_enriched = enrich_vacancy_data(stellen_vacancies, source='ausbildungsstellen')
    current_vacancies = azubi_enriched + stellen_enriched
    
    print(f"    ✓  {len(current_vacancies)} bearbeitet")
    
    print("\n[3/4] cache laden...")
    cache_dict = load_cache()
    print(f"    ✓ {len(cache_dict)} stelleangebote im cache")
    
    print("\n[4/4] vergleichen...")
    new_vacancies = []
    
    for vacancy in current_vacancies:
        vacancy_id = vacancy['id']
        if vacancy_id not in cache_dict:
            new_vacancies.append(vacancy)
    
    if new_vacancies:
        print(f"\n GEFUNDEN: {len(new_vacancies)}")
        print("-" * 60)
        
        for i, vacancy in enumerate(new_vacancies, 1):
            text_preview = vacancy['text'][:150] + "..." if len(vacancy['text']) > 150 else vacancy['text']
            print(f"\n{i:2d}. [{vacancy['id']}] ({vacancy['source']})")
            print(f"    {text_preview}")
        
        print(f"\n update...")
        
        updated_cache = list(cache_dict.values()) + new_vacancies
        
        if len(updated_cache) > 200:
            updated_cache = updated_cache[-200:]
        
        save_cache(updated_cache)
        print(f"    ✓ insgesamt im cache {len(updated_cache)}")
        
    else:
        print("\n keine neuen stelleangebotte gefunden")
        
    print("\n" + "=" * 60)
    print("probe abgeschlossen")
    print("=" * 60)

if __name__ == "__main__":    
    main()
