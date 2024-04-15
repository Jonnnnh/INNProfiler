import requests
from flask import Flask, request, render_template
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/details', methods=['GET', 'POST'], endpoint='details_form')
def show_details_form():
    if request.method == 'POST':
        inn = request.form['inn']
        company_info = get_company_details(inn)
        return render_template('details.html', company_info=company_info, inn=inn)
    return render_template('index.html')

@app.route('/details/<inn>', endpoint='details_inn')
def show_details(inn):
    company_info = get_company_details(inn)
    print("Отправляемые данные:", company_info)
    return render_template('details.html', company_info=company_info, inn=inn)

def get_company_details(inn):
    url = f"https://www.rusprofile.ru/search?query={inn}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        company_link = soup.find('a', class_='search-result__header-link')

        if company_link:
            company_url = "https://www.rusprofile.ru" + company_link['href']
            company_response = requests.get(company_url, headers=headers)
            company_soup = BeautifulSoup(company_response.text, 'html.parser')

            name = company_soup.find('div', class_='company-name').get_text(strip=True) if company_soup.find('div', class_='company-name') else "Название не найдено"
            inn_kpp = company_soup.find('dd', class_='company-info__text has-copy', itemprop='taxID').get_text(strip=True) if company_soup.find('dd', class_='company-info__text has-copy', itemprop='taxID') else "ИНН/КПП не найдено"

            authorized_capital = None
            for dt in company_soup.find_all('dt', class_='company-info__title'):
                if dt.get_text(strip=True) == 'Уставный капитал':
                    dd = dt.find_next_sibling('dd')
                    if dd:
                        authorized_capital = dd.get_text(strip=True)
            authorized_capital = authorized_capital or "Уставной капитал не найден"

            leader_info_block = company_soup.find('div', class_='company-row hidden-parent')
            if leader_info_block:
                leader_name_tag = leader_info_block.find('a', class_='gtm_main_fl')
                leader_name = leader_name_tag.get_text(strip=True) if leader_name_tag else "Руководитель не найдено"
            else:
                leader_name = "Руководитель не найдено"

            legal_address = company_soup.find('address', itemprop='address').get_text(strip=True) if company_soup.find(
                'address', itemprop='address') else "Юридический адрес не найдено"

        else:
            title_tag = soup.find('title')
            name = title_tag.get_text().split('(')[0].strip() if title_tag else "Название не найдено"
            inn_kpp = soup.find('dd', class_='company-info__text has-copy', itemprop='taxID').get_text(strip=True) if soup.find('dd', class_='company-info__text has-copy', itemprop='taxID') else "ИНН/КПП не найдено"

            authorized_capital = None
            for dt in soup.find_all('dt', class_='company-info__title'):
                if dt.get_text(strip=True) == 'Уставный капитал':
                    dd = dt.find_next_sibling('dd')
                    if dd:
                        authorized_capital = dd.get_text(strip=True)
            authorized_capital = authorized_capital or "Уставной капитал не найден"

            ogrn = soup.find('span', id="clip_ogrn").get_text(strip=True) if soup.find('span', id="clip_ogrn") else "ОГРН не найдено"
            registration_date = soup.find('dd', itemprop='foundingDate').get_text( strip=True) if soup.find('dd', itemprop='foundingDate') else "Дата регистрации не найдено"

            leader_info_block = soup.find('div', class_='company-row hidden-parent')
            if leader_info_block:
                leader_name_tag = leader_info_block.find('a', class_='gtm_main_fl')
                leader_name = leader_name_tag.get_text(strip=True) if leader_name_tag else "Руководитель не найдено"
            else:
                leader_name = "Руководитель не найдено"

            legal_address = soup.find('address', itemprop='address').get_text(strip=True) if soup.find(
                'address', itemprop='address') else "Юридический адрес не найдено"
        return {
            'company_name': name,
            'inn_kpp': inn_kpp,
            'authorized_capital': authorized_capital,
            'ogrn': ogrn,
            'registration_date': registration_date,
            'leader_name': leader_name,
            'legal_address': legal_address,
        }
    else:
        return "Ошибка запроса"

print(get_company_details('7710140679'))

if __name__ == '__main__':
    app.run(debug=True)