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

        else:
            title_tag = soup.find('title')
            name = title_tag.get_text().split('(')[0].strip() if title_tag else "Название не найдено"
            inn = soup.find('span', id="clip_inn").get_text(strip=True) if soup.find('span', id="clip_inn") else "ИНН не найдено"
            ogrn = soup.find('span', id="clip_ogrn").get_text(strip=True) if soup.find('span', id="clip_ogrn") else "ОГРН не найдено"
            registration_date = soup.find('dd', itemprop='foundingDate').get_text( strip=True) if soup.find('dd', itemprop='foundingDate') else "Дата регистрации не найдено"
            leader = soup.find('div', {'class': 'chief'}).get_text(strip=True) if soup.find('div', {'class': 'chief'}) else "Руководитель не найдено"
            legal_address = soup.find('address', itemprop='address').get_text(strip=True) if soup.find('span', itemprop='address') else "Юридический адрес не найдено"

        return {
            'company_name': name,
            'inn': inn,
            'ogrn': ogrn,
            'registration_date': registration_date,
            'leader': leader,
            'legal_address': legal_address,
        }
    else:
        return "Ошибка запроса"

print(get_company_details('7710140679'))

if __name__ == '__main__':
    app.run(debug=True)