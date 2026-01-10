import json
import os
from datetime import datetime

CACHE_FILE = 'vacancies_cache.json'
def load_cache():
    
    if not os.path.exists(CACHE_FILE):
        return []
    
    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []
        
    def save_cache(vacancies):
     """speichert cache"""
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(vacancies, f, ensure_ascii=False, indent=2)

def get_new_vacancies(current_vacancies, cached_vacancies):
    """NUR neue stelle zurückgibt]"""
    cached_ids = {v['id'] for v in cached_vacancies}
    return [v for v in current_vacancies if v['id'] not in cached_ids]

def update_cache(new_vacancies, cached_vacancies):
    """update"""
    #timestamp
    for v in new_vacancies:
        v['first_seen'] = datetime.now().isoformat()
    
    updated = new_vacancies + cached_vacancies
    
    # begrenzte cache
    if len(updated) > 100:
        updated = updated[:100]
    
    return updated    