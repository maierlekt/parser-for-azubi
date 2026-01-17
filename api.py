from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
import json
import os
import hashlib
from typing import List, Dict, Any
import asyncio

from parser_azubi import parse_azubiyo
from parser_stellen import parse_stellen

app = FastAPI(
    title="Vacancy Parser API",
    description="API для парсинга вакансий с кэшированием",
    version="1.0.0"
)

CACHE_FILE = 'vacancies_cache.json'

# cash
def generate_vacancy_id(vacancy_text: str) -> str:
    """Генерирует уникальный ID для вакансии"""
    text_hash = hashlib.md5(vacancy_text.encode('utf-8')).hexdigest()
    return f"vac_{text_hash[:50]}"

def load_cache() -> Dict[str, Dict]:
    """Загружает кэш из файла"""
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

def save_cache(vacancies_list: List[Dict]):
    """Сохраняет кэш в файл"""
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(vacancies_list, f, ensure_ascii=False, indent=2)

def enrich_vacancy_data(raw_vacancies: List[str], source: str = 'azubiyo') -> List[Dict]:
    """Обогащает данные вакансий"""
    enriched = []
    
    for text in raw_vacancies:
        if not text or not text.strip():
            continue
            
        vacancy = {
            'id': generate_vacancy_id(text),
            'text': text.strip(),
            'source': source,
            'first_seen': datetime.now().isoformat(),
            'parsed_at': datetime.now().isoformat()
        }
        enriched.append(vacancy)
    
    return enriched

def get_new_vacancies() -> Dict[str, Any]:
    """Основная функция: парсит и возвращает новые вакансии"""
    print("Начало парсинга...")
    
    
    try:
        azubi_vacancies = parse_azubiyo()
        stellen_vacancies = parse_stellen()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка парсинга: {str(e)}")
    
    
    all_vacancies = azubi_vacancies + stellen_vacancies
    print(f"Найдено всего вакансий: {len(all_vacancies)}")
    
   
    cache_dict = load_cache()
    print(f"В кэше вакансий: {len(cache_dict)}")
    
    # enriched
    azubi_enriched = enrich_vacancy_data(azubi_vacancies, 'azubiyo')
    stellen_enriched = enrich_vacancy_data(stellen_vacancies, 'ausbildungsstellen')
    current_vacancies = azubi_enriched + stellen_enriched
    
 
    new_vacancies = []
    for vacancy in current_vacancies:
        if vacancy['id'] not in cache_dict:
            new_vacancies.append(vacancy)
    
   
    if new_vacancies:
        updated_cache = list(cache_dict.values()) + new_vacancies
        

        if len(updated_cache) > 200:
            updated_cache = updated_cache[-200:]
        
        save_cache(updated_cache)
        print(f"Кэш обновлен. Всего в кэше: {len(updated_cache)}")
    
    return {
        "total_found": len(all_vacancies),
        "new_vacancies": len(new_vacancies),
        "new_vacancies_list": new_vacancies,
        "cache_size": len(cache_dict),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/")
async def root():
    """Корневой эндпоинт с информацией"""
    return {
        "service": "Vacancy Parser API",
        "version": "1.0.0",
        "endpoints": {
            "GET /": "diese info",
            "GET /health": "check",
            "GET /parse": "parse",
            "GET /cache": "cache",
            "GET /cache/size": "cache size",
            "DELETE /cache": "cache leer",
            "GET /stats": "statistiks"
        }
    }

@app.get("/health")
async def health_check():
    """check API...."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "cache_file_exists": os.path.exists(CACHE_FILE)
    }

@app.get("/parse")
async def parse_vacancies(force: bool = False):
    """
    parsing prozess...
    - force True----> alle stellen
    """
    result = get_new_vacancies()
    
    if force:
        cache_dict = load_cache()
        result["all_vacancies"] = list(cache_dict.values())
    
    return JSONResponse(content=result)

@app.get("/cache")
async def get_cache(limit: int = 50, offset: int = 0):
    """cache....."""
    cache_dict = load_cache()
    cache_list = list(cache_dict.values())
    
    # Сортировка по дате (новые первыми)
    cache_list.sort(key=lambda x: x.get('first_seen', ''), reverse=True)
    
    total = len(cache_list)
    paginated = cache_list[offset:offset + limit]
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "vacancies": paginated
    }

@app.get("/cache/size")
async def get_cache_size():
    """cache size..."""
    cache_dict = load_cache()
    return {"size": len(cache_dict)}

@app.delete("/cache")
async def clear_cache():
    """cache leer...."""
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)
        return {"message": "cache ist leer"}
    else:
        return {"message": "cache file nicht existiert"}

@app.get("/stats")
async def get_stats():
    """statistiks..."""
    cache_dict = load_cache()
    
   
    sources = {}
    for item in cache_dict.values():
        source = item.get('source', 'unknown')
        sources[source] = sources.get(source, 0) + 1
    
 
    cache_list = list(cache_dict.values())
    if cache_list:
        cache_list.sort(key=lambda x: x.get('first_seen', ''))
        oldest = cache_list[0]['first_seen'] if cache_list else None
        newest = cache_list[-1]['first_seen'] if cache_list else None
    else:
        oldest = newest = None
    
    return {
        "total_vacancies": len(cache_dict),
        "sources": sources,
        "oldest_vacancy": oldest,
        "newest_vacancy": newest,
        "cache_file_size": os.path.getsize(CACHE_FILE) if os.path.exists(CACHE_FILE) else 0
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)