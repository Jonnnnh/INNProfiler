import requests
from bs4 import BeautifulSoup

from src.config import Config

class CompanyDetailsFetcher:
    def __init__(self, base_url=Config.BASE_URL):
        self.base_url = base_url

    def get_html(self, url):
        response = requests.get(url, headers=Config.HEADERS)
        response.raise_for_status()
        return response.text

    def get_company_details(self, inn):
        try:
            search_url = f"{self.base_url}/search?query={inn}"
            search_html = self.get_html(search_url)
            search_soup = BeautifulSoup(search_html, 'html.parser')
            company_link = search_soup.find('a', class_='search-result__header-link')

            if company_link:
                company_url = self.base_url + company_link['href']
                company_html = self.get_html(company_url)
                company_soup = BeautifulSoup(company_html, 'html.parser')
            else:
                company_soup = search_soup

            return self.parse_company_details(company_soup)
        except requests.RequestException as e:
            return {"error": str(e)}

    def parse_company_details(self, soup):
        return {
            'company_name': self.get_text_or_default(soup, 'title', split_text=' ('),
            'inn_kpp': self.get_text_or_default(soup, 'dd', attrs={'itemprop': 'taxID'}),
            'authorized_capital': self.find_authorized_capital(soup),
            'ogrn': self.get_text_or_default(soup, 'span', attrs={'id': 'clip_ogrn'}),
            'registration_date': self.get_text_or_default(soup, 'dd', attrs={'itemprop': 'foundingDate'}),
            'leader_name': self.parse_leader_name(soup),
            'legal_address': self.get_text_or_default(soup, 'address', attrs={'itemprop': 'address'})
        }

    def get_text_or_default(self, soup, tag, class_name=None, default="Информация не найдена", attrs={},
                            split_text=None):
        try:
            element = soup.find(tag, class_=class_name, **attrs) if class_name else soup.find(tag, **attrs)
            if element:
                text = element.get_text(strip=True)
                return text.split(split_text)[0] if split_text else text
            return default
        except Exception as e:
            print(f"Error parsing {tag} with class {class_name}: {e}")
            return default

    def parse_leader_name(self, soup):
        leader_info_block = soup.find('div', class_='company-row hidden-parent')
        if leader_info_block:
            leader_name_tag = leader_info_block.find('a', class_='gtm_main_fl')
            return leader_name_tag.get_text(strip=True) if leader_name_tag else "Руководитель не найдено"
        return "Руководитель не найдено"

    def find_authorized_capital(self, soup):
        capital_tag = soup.find('dt', string=lambda x: x and 'Уставный капитал' in x)
        if capital_tag:
            dd = capital_tag.find_next_sibling('dd')
            return dd.get_text(strip=True) if dd else "Уставной капитал не найден"
        return "Уставной капитал не найден"
