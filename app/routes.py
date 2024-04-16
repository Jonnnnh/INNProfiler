from flask import render_template, request

def configure_routes(app):
    from src.companydetailsfetcher import CompanyDetailsFetcher
    fetcher = CompanyDetailsFetcher()

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/details', methods=['GET', 'POST'])
    def details():
        if request.method == 'POST':
            inn = request.form['inn']
            company_info = fetcher.get_company_details(inn)
            return render_template('details.html', company_info=company_info, inn=inn)
        return render_template('index.html')

    @app.route('/details/<inn>')
    def show_details(inn):
        company_info = fetcher.get_company_details(inn)
        return render_template('details.html', company_info=company_info, inn=inn)
