import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
import datetime

t1 = time.time()
t = datetime.datetime.now()
print(f'Rozpoczęto o {t:%T}')


# uber loop na wszystkie wyniki
link = 'https://www.otomoto.pl/osobowe?page=1'
html_text = requests.get(link).text
soup = BeautifulSoup(html_text, 'lxml')
ile_stron = soup.find_all('a', class_='ooa-g4wbjr ekxs86z0')
ile_stron = int(ile_stron[-1].text)

strony_odwiedzone = 0
dane = []

for i in range(ile_stron + 1):
# for i in range(1, 3):
    t10 = time.time()
    link = f'https://www.otomoto.pl/osobowe?page={i}'
    html_text = requests.get(link).text
    soup = BeautifulSoup(html_text, 'lxml')

    ogloszenia = soup.find('main', class_='ooa-p2z5vl e19uumca5')

    try: ogloszenia = ogloszenia.find_all('article')
    except: continue

    strony_odwiedzone += 1

    # loop tylko do zbierania danych
    for ogloszenie in ogloszenia:
        tytul = ogloszenie.find('a').text

        try: opis = ogloszenie.find('p').text 
        except: opis = None

        # techniczne = ogloszenie.find('ul', class_='e1b25f6f6 ooa-ggoml6-Text eu5v0x0')
        techniczne = ogloszenie.find('ul')
    # 
        lst_techniczne = techniczne.find_all('li')

        try: rok = int(lst_techniczne[0].text)
        except: rok = None

        try: 
            przebieg = lst_techniczne[1].text
            przebieg = przebieg[:-3]
            przebieg = int(przebieg.replace(' ', ''))

        except: przebieg = None
        
        if len(lst_techniczne) == 4:
            try: 
                pojemnosc = lst_techniczne[2].text
                pojemnosc = pojemnosc[:-4]
                pojemnosc = int(pojemnosc.replace(' ', ''))
            except: pojemnosc = None
            paliwo = lst_techniczne[3].text

        elif len(lst_techniczne) == 3:
            pojemnosc = None
            paliwo = lst_techniczne[2].text
    # 
        gdzie = ogloszenie.find('ul', class_='e1b25f6f6 ooa-1enwzw8-Text eu5v0x0')

        try:
            m = gdzie.find('span', class_='ooa-1rwfs5y').text
            m = m.split('(')
            miasto = m[0]
            miasto = miasto[:-1]
            wojewodztwo = m[1]
            wojewodztwo = wojewodztwo.replace(')', '')
            odsw = gdzie.find('li', class_='ooa-0 e1teo0cs0').text
        except: miasto = odsw = wojewodztwo = None
        try:
            cena = ogloszenie.find('span', class_='ooa-epvm6 e1b25f6f7').text
            waluta = cena[-3:]
            cena = cena[:-3]
            cena = int(cena.replace(' ', ''))
        except: cena = waluta = None

        dane.append([tytul, opis, rok, przebieg, pojemnosc, paliwo, miasto, wojewodztwo, odsw, cena, waluta])
        
    t11 = time.time()
    print(f'strona {i + 1}, czas {t11 - t10:,.2f}s')
    

t2 = time.time()
df = pd.DataFrame(dane)
df.columns = ['TYTUŁ', 'OPIS', 'ROK_PRODUKCJI', 'PRZEBIEG(KM)', 'POJEMNOŚĆ_SILNIKA(CM^3)', 'PALIWO', 'MIASTO', 'WOJEWODZTWO', 'OSTATNIA_AKTUALIZACJA', 'CENA', 'WALUTA']

df.to_excel(r'C:\Users\alans\OneDrive\Pulpit\samochodyxlsx.xlsx', index=False, encoding='UTF-8')
df.to_csv(r'C:\Users\alans\OneDrive\Pulpit\samochodycsv.csv', index=False, encoding='UTF-8')
t = datetime.datetime.now()
print(f'Zakończono o {t:%T}')
print(f'{t2 - t1:,.2f}' + 's')
print(f'Odwiedzone strony {strony_odwiedzone} / {ile_stron}')
