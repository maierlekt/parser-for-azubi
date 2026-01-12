import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode

def parse_stellen():
 base_url = 'https://www.ausbildungsstellen.de/ausbildungsplaetze-fachinformatiker-in-koeln'
    
 all_vacancies = []
 total_count = 0
    
    # Используем with open для автоматического закрытия файла
 with open("parse2.txt", "w", encoding='utf-8') as file:
        
  # Парсим первые 3 страницы
  for page_num in range(1, 10):  
     # Правильная пагинация
      if page_num == 1:
       page_url = base_url  # Первая страница без параметра
      else:
       page_url = f"{base_url}/{page_num}"
            
      print(f"\n--- Парсинг страницы {page_num}: {page_url} ---")
            
      try:
          headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
          response = requests.get(page_url, headers=headers, timeout=10)
          response.raise_for_status()  # Проверяем на ошибки
          soup = BeautifulSoup(response.text, 'html.parser')

          print(f"   Длина HTML: {len(response.text)} символов")
                
          if page_num == 1:
           h1 = soup.find('h1')
          if h1:
           title = h1.text.strip()
          print(f"   Заголовок: {title}")
          file.write(f"=== {title} ===\n\n")
                
          vacancies = soup.find_all('span', class_='jobTitle')
          companies = soup.find_all('span', class_='company')
          page_count = len(vacancies)
          total_count += page_count
                
          print(f" Auf der {page_num}. seite {page_count} ausbildungsstellen gefunden")
                
          for i in range(len(vacancies)):
            job_title = vacancies[i].get_text(strip=True)
            company_name = companies[i].get_text(strip=True) if i < len(companies) else "N/A"
            vac_text = f"{job_title} - {company_name}"

          # reinigung
            if vac_text.startswith('Ausbildung'):
             vac_text = vac_text[10:].strip()
            if vac_text.startswith('Auszubildende'):
             vac_text = vac_text[13:].strip()
            if vac_text.startswith(' '):
             vac_text = vac_text[1:].strip()  
            if vac_text.startswith('-'):
             vac_text = vac_text[1:].strip()
            if vac_text.startswith(':'):
             vac_text = vac_text[1:].strip() 
            if vac_text.startswith('zum'):
             vac_text = vac_text[3:].strip()
            if vac_text.startswith('zur'):
             vac_text = vac_text[3:].strip()
            if vac_text.startswith('als'):
             vac_text = vac_text[3:].strip()
            if vac_text.startswith('*'):
             vac_text = vac_text[1:].strip()  
            if vac_text.startswith('/'):                     
             vac_text = vac_text[1:].strip()


            if vac_text:
               all_vacancies.append(vac_text)
               print(vac_text)
               file.write(f"seite {page_num}: {vac_text}\n\n")   
            all_vacancies.append(vac_text)
                    
            file.write(f"seite {page_num}: {vac_text}\n")
                
            if page_count == 0:
               print("   no stellen mehr vielleicht keine seite mehr")
               break
                    
               import time
               time.sleep(1)
                
      except Exception as e:
       print(f"   fehler auf {page_num}. seite: {e}")
      continue       
 #final1
 print(f"=== Insgesamt: {total_count} ===")   
 return all_vacancies
#final
if __name__ == "__main__":
    print("parsing prozess... Ausbildungsstellen.de")
    print("="*60)
    
    vacancies = parse_stellen()


#######################################################################################################
               



        