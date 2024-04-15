from flask import Flask, request, render_template
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

BASE_URL = "https://www.rusprofile.ru"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/details', methods=['GET', 'POST'])
def details():
    if request.method == 'POST':
        inn = request.form['inn']
        company_info = get_company_details(inn)
        return render_template('details.html', company_info=company_info, inn=inn)
    return render_template('index.html')


@app.route('/details/<inn>')
def show_details(inn):
    company_info = get_company_details(inn)
    return render_template('details.html', company_info=company_info, inn=inn)


def get_html(url):
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.text


def get_company_name_from_title(soup):
    title_tag = soup.find('title')
    if title_tag:
        title_text = title_tag.get_text()
        company_name = title_text.split(' (')[0]
        return company_name
    return "Название не найдено"


def parse_company_details(soup):
    result = {
        'company_name': get_company_name_from_title(soup),
        'inn_kpp': get_text_or_default(soup, 'dd', 'company-info__text has-copy', "ИНН/КПП не найдено",{'itemprop': 'taxID'}),
        'authorized_capital': find_authorized_capital(soup),
        'ogrn': get_text_or_default(soup, 'span', None, "ОГРН не найдено", {'id': 'clip_ogrn'}),
        'registration_date': get_text_or_default(soup, 'dd', None, "Дата регистрации не найдено",{'itemprop': 'foundingDate'}),
        'leader_name': parse_leader_name(soup),
        'legal_address': get_text_or_default(soup, 'address', None, "Юридический адрес не найдено",
{'itemprop': 'address'})
    }
    return result


def parse_leader_name(soup):
    leader_info_block = soup.find('div', class_='company-row hidden-parent')
    if leader_info_block:
        leader_name_tag = leader_info_block.find('a', class_='gtm_main_fl')
        return leader_name_tag.get_text(strip=True) if leader_name_tag else "Руководитель не найдено"
    return "Руководитель не найдено"


def get_text_or_default(soup, tag, class_name, default, attrs={}):
    try:
        if class_name:
            element = soup.find(tag, class_=class_name, **attrs)
        else:
            element = soup.find(tag, **attrs)
        return element.get_text(strip=True) if element else default
    except Exception as e:
        print(f"Error parsing {tag} with class {class_name}: {e}")
        return default


def find_authorized_capital(soup):
    capital_tag = soup.find('dt', string=lambda x: x and 'Уставный капитал' in x)
    if capital_tag:
        dd = capital_tag.find_next_sibling('dd')
        return dd.get_text(strip=True) if dd else "Уставной капитал не найден"
    return "Уставной капитал не найден"


def get_company_details(inn):
    try:
        search_url = f"{BASE_URL}/search?query={inn}"
        search_html = get_html(search_url)
        search_soup = BeautifulSoup(search_html, 'html.parser')
        company_link = search_soup.find('a', class_='search-result__header-link')

        if company_link:
            company_url = BASE_URL + company_link['href']
            company_html = get_html(company_url)
            company_soup = BeautifulSoup(company_html, 'html.parser')
            return parse_company_details(company_soup)
        else:
            return parse_company_details(search_soup)
    except requests.RequestException as e:
        return {"error": str(e)}


print(get_company_details('7707083893'))

if __name__ == '__main__':
    app.run(debug=True)
