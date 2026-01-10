from urllib.request import urlopen
from bs4 import BeautifulSoup

def parse_azubiyo():

 url = 'https://www.azubiyo.de/ausbildung/koeln/fachinformatiker-systemintegration/'

 file = open("azubi.txt", "w", encoding='utf-8') 
  
 html_code = str(urlopen(url).read(),'utf-8')
 soup = BeautifulSoup(html_code, "html.parser")
#h1
 t = soup.find('title').text
 print("===" + t + "===")

 file.write("===" + t + "===" + '\n\n')
#vacancies + count
 all_vacancies = []
 total_count = 0

# ersten 3 seiten (4 ist schon zu viel)
 for page_num in range(1, 3):  
    # URL der seite
     if page_num == 1:
        page_url = url
     else:
        page_url = url + str(page_num) + '/'
    
     print(f"\n--- parsing Prozess... {page_num}: {page_url} ---")
    
     try:
        html_code = str(urlopen(page_url).read(), 'utf-8')
        soup = BeautifulSoup(html_code, "html.parser")
        
        # suche nach passende <div>
        vacancies = soup.find_all(attrs={"data-ng-controller": "JobOfferTeaserController"})
        page_count = len(vacancies)
        
        print(f"auf der  {page_num}. seite wurden {page_count} stelle gefunden")
        
        # zusammenbringen
        total_count += page_count
        
        for vacancy in vacancies:
            vacancy_text = vacancy.get_text(separator=' ', strip=True)
             
             # reinigung
            if vacancy_text.startswith('? Eignung'):
                 vacancy_text = vacancy_text[9:].strip()
            if vacancy_text.endswith('Job melden'):
                vacancy_text = vacancy_text[:-10].strip()
            if vacancy_text.endswith('Schnellbewerbung'):
                vacancy_text = vacancy_text[:-16].strip()
            if vacancy_text.startswith('Ausbildung'):
                 vacancy_text = vacancy_text[10:].strip()
            if vacancy_text.startswith('zum'):
                 vacancy_text = vacancy_text[4:].strip()
            if vacancy_text.startswith('-'):
                 vacancy_text = vacancy_text[1:].strip()
            if vacancy_text.startswith(' '):
                 vacancy_text = vacancy_text[1:].strip()
            if vacancy_text.startswith('Fachlagerist'):
                 vacancy_text = '!' + vacancy_text 

            if vacancy_text and vacancy_text not in all_vacancies: 
                all_vacancies.append(vacancy_text)
                print(vacancy_text)
                file.write(vacancy_text + '\n\n')

    
     except Exception as e:
        print(f"der Fehler während des Prozesses {page_num}: {e}")
        break  # wenn es keine seite gibt

# die summe
 print(f"\n=== Insgesamt (faktisch!): {total_count} ===")
 return all_vacancies
 file.write(f"\n=== Insgesamt (faktisch!): {total_count} ===")
 return all_vacancies
 file.close()

