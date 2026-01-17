import requests
from bs4 import BeautifulSoup
import time

def parse_stellen():
    base_url = 'https://www.ausbildungsstellen.de/ausbildungsplaetze-fachinformatiker-in-koeln'
    
    all_vacancies = []
    total_count = 0
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
  
    with open("parse2.txt", "w", encoding='utf-8') as file:
        
        
        for page_num in range(1, 10):  
            
            if page_num == 1:
                page_url = base_url 
            else:
                page_url = f"{base_url}/{page_num}"
            
            print(f"\n--- parsing.. {page_num}: {page_url} ---")
            
            try:
                response = requests.get(page_url, headers=headers, timeout=10)
                response.raise_for_status() 
                soup = BeautifulSoup(response.text, 'html.parser')

                print(f"  HTML: {len(response.text)} symbolen")
                
                
                if page_num == 1:
                    h1 = soup.find('h1')
                    if h1:
                        title = h1.text.strip()
                        print(f"   Заголовок: {title}")
                        file.write(f"=== {title} ===\n\n")
                
           
                vacancies = soup.find_all('span', class_='jobTitle')
                companies = soup.find_all('span', class_='company')
                page_count = len(vacancies)
                
                
                if page_count == 0:
                    print(" wahrscheinlich es gab den letzten seite")
                    break
                
                total_count += page_count
                print(f"   auf dem seite {page_num}  {page_count} gefunden")
                
               
                for i in range(len(vacancies)):
                    job_title = vacancies[i].get_text(strip=True)
                    company_name = companies[i].get_text(strip=True) if i < len(companies) else "N/A"
                    vac_text = f"{job_title} - {company_name}"

                    
                    prefixes_to_remove = [
                        'Ausbildung', 'Auszubildende', ' ', '-', ':', 'zum', 'zur', 'als', '*', '/'
                    ]
                    
                    for prefix in prefixes_to_remove:
                        if vac_text.startswith(prefix):
                            vac_text = vac_text[len(prefix):].strip()

                  
                    if vac_text and vac_text not in all_vacancies:
                        all_vacancies.append(vac_text)
                        print(f"   {vac_text}")
                        file.write(f"seite {page_num}: {vac_text}\n\n")
                
               
                time.sleep(1)
                
            except Exception as e:
                print(f"   fehler {page_num}: {e}")
               
                continue
    
    print(f"\n=== insgesamt: {len(all_vacancies)} ===")
    return all_vacancies

if __name__ == "__main__":
    print("parsing.. Ausbildungsstellen.de")
    print("="*60)
    vacancies = parse_stellen()
    print(f"\ninsgesamt: {len(vacancies)} stelle")
