from flask import jsonify
from bs4 import BeautifulSoup
from api.session import session
import re 
from api.models import AnnualExport, AnnualImport, Clients, DocumentRequired, Fournisseurs, ImportDuty, Importers,codification,Exporters,AccordConvention
from api.api_api import views_app
from api.connection import db
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def get_importers(code):

    url = f"https://www.douane.gov.ma/adil/oper_Ii.asp?pos={code}"
    
    # Set headers to mimic a browser request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    # Send a GET request to the URL
    print("Sending GET request to:", url)
    response = session.get(url, headers=headers)
    print("Response status code:", response.status_code)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        all_importer_names = []
        # Check if there are multiple pages
        page_info = soup.find_all('span', class_='Style14')[-1]
        if page_info:
            total_pages = int(page_info.find_all('b')[1].get_text())
            # Enumerate through pages and collect importer names
            all_importer_names = []
            for page in range(1, total_pages + 1):
                page_url = f"https://www.douane.gov.ma/adil/oper_ii.asp?Page={page}&Recherche={code}"
                print("Processing page:", page)
                page_response = session.get(page_url, headers=headers)
                
                if page_response.status_code == 200:
                    page_soup = BeautifulSoup(page_response.text, 'html.parser')
                    importer_rows = page_soup.find_all('td', class_='Style7')
                    page_importer_names = [row.get_text(strip=True) for row in importer_rows]
                    all_importer_names.extend(page_importer_names)
                    print("Importer names on page", page, ":", page_importer_names)

        # Construct the response dictionary
        if not all_importer_names:
            return {
                "importers": "there is no importer data as of date"
            }
        else:
            return all_importer_names

        
    else:
        raise Exception("Failed to retrieve the webpage")

def get_exporters(code):
    print(f"Fetching exporters for code: {code}")
    url = f"https://www.douane.gov.ma/adil/oper_EE.asp?pos={code}"
    print(url)
    # Set headers to mimic a browser request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    print(f"expo :{code}")
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    # Send a GET request to the URL
    response = session.get(url, headers=headers)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        all_exporters_names = []
        # Check if there are multiple pages
        page_info = soup.find_all('span', class_='Style14')[-1]
        if page_info:
            total_pages = int(page_info.find_all('b')[1].get_text())
            
            # Enumerate through pages and collect importer names
            all_exporters_names = []
            for page in range(1, total_pages + 1):
                page_url = f"https://www.douane.gov.ma/adil/oper_EE.asp?Page={page}&Recherche={code}"
                page_response = session.get(page_url, headers=headers)
                
                if page_response.status_code == 200:
                    page_soup = BeautifulSoup(page_response.text, 'html.parser')
                    # Find all table rows (tr) containing importer names
                    exporter_rows = page_soup.find_all('span', class_='Style7')
        
                    # Extract the importer names
                    exporter_names = [row.get_text(strip=True) for row in exporter_rows]
                    all_exporters_names.extend(exporter_names)
                    print("exporters names on page", page, ":", exporter_names)

        # Construct the response dictionary
        if not all_exporters_names:
            return {
                "exporters": "there is no importer data as of date"
            }
        else:
            return all_exporters_names

        
            
    else:
        print(f"Request failed for code: {code}")
        raise Exception("Failed to retrieve the webpage")

def attention(soup):
    attention_img = soup.find('img', src="images/attention.gif")
    if attention_img:
        return True
    else :
        return False

def get_with_retry(url, headers=None):
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    response = session.get(url, headers=headers)
    return response

def get_classification_commerciale(t, code):
    print(f"Fetching classification commerciale for code: {code}")
    # URL of the ADiL page
    if t == "i":
        url = f"https://www.douane.gov.ma/adil/info_21.asp?pos={code}"
    elif t == "n":
        url = f"https://www.douane.gov.ma/adil/info_20.asp?pos={code}"
    else:
        raise ValueError("Invalid input: 't' must be either 'n' or 'i'")

    # Set headers to mimic a browser request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    # Send a GET request to the URL
    response = session.get(url, headers=headers)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        print(f"Request successful for code: {code}")
        soup = BeautifulSoup(response.text, 'html.parser')

        if attention(soup):
            raise Exception("No data available")

        # Parse the HTML content
        correct_table = soup.find('table', width="99%")

        if correct_table:
            print("Correct table found")
            rows = correct_table.find_all('tr')

            # Initialize dictionary to store data
            data = {}

            # Initialize variable to hold the current table title
            current_title = None

            # Loop through table rows
            for row in rows:
                # Check if the row contains a table title
                title_cell = row.find('td', bgcolor="#6DA0E7")
                if title_cell:
                    print(f"Table title found: {title_cell.text.strip()}")
                    current_title = title_cell.text.strip()
                    data[current_title] = {}
                else:
                    # Extract column titles and values
                    if bool(current_title):
                        print(f"Row for table {current_title} found")
                        cells = row.find_all('td')
                        if len(cells) == 2:
                            column_title = cells[0].text.strip()
                            value = cells[1].text.strip()
                            data[current_title][column_title] = value
                    else:
                        print("Row for table title not found")
                        cells = row.find_all('td')
                        if len(cells) == 2:
                            column_title = cells[0].text.strip()
                            value = cells[1].text.strip()
                            data[column_title] = value  
            return data
        else:
            print("Failed to find inner table")
            raise Exception("Failed to find inner table")
    else:
        print(f"Request failed for code: {code}")
        raise Exception("Failed to retrieve the webpage")

def get_accord_convention(code):
    # URL of the ADiL page
    url = f"https://www.douane.gov.ma/adil/info_3.asp?pos={code}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    # Send a GET request to the URL
    response = session.get(url, headers=headers)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        print(f"Request successful for code: {code}")
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the table containing the data
        table = soup.find('table', width="52%")

        # Initialize data dictionary
        data = []

        # Extract data from the table
        rows = table.find_all('tr')[2:-1]  # Exclude first two rows
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:  # Ensure at least 4 columns exist
                if  len(cols) < 5:
                    agreement_type = cols[0].text.strip()
                    di_percentage = cols[1].text.strip()
                    tpi_percentage = cols[2].text.strip()
                    if current_country:
                        country_name = current_country
                    else:
                        country_name = ""
                else:
                    country_name = cols[1].text.strip()
                    agreement_type = cols[2].text.strip()
                    di_percentage = cols[3].text.strip()
                    tpi_percentage = cols[4].text.strip()
                    current_country = country_name

                data.append({
                    "Agreement": agreement_type,
                    "DI Percentage": di_percentage,
                    "TPI Percentage": tpi_percentage,
                    "country": current_country
                })
        return data
    else:
        print(f"Request failed for code: {code}")
        raise Exception("Failed to retrieve the webpage")

def documents_required(code):
    # URL of the ADiL page
    url = f"https://www.douane.gov.ma/adil/info_4.asp?pos={code}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    print(f"sending request for doc required for:{code}")
    # Send a GET request to the URL
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    response = session.get(url, headers=headers)
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Debug statement 2: Print the soup content
        

        # Find the table containing the data
        table = soup.find('table', width="60%")

        # Initialize data list
        documents = []

        if table:  # If table is found
            # Check if there are any rows in the table
            rows = table.find_all('tr')
            if len(rows) > 3:  # If there are rows, extract data
                rows = rows[4:]  # Exclude first four rows
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) ==4:
                        if len(cols[3].text.strip())==0:  # Ensure at least 3 columns exist
                            document_number = cols[0].text.strip()
                            document_name = cols[1].text.strip()
                            issuer = cols[2].text.strip()
                            documents.append({
                                "Document Number": document_number,
                                "Document Name": document_name,
                                "Issuer": issuer
                            })
                        elif cols[3].text.strip() == 'Emetteur':
                            continue
                        else:
                            document_number = cols[0].text.strip()
                            document_name = cols[1].text.strip()
                            libelle_d_extrait = cols[2].text.strip()
                            issuer = cols[3].text.strip()
                            documents.append({
                                "Document Number": document_number,
                                "Document Name": document_name,
                                "libelle_d_extrait": libelle_d_extrait,
                                "Issuer": issuer
                            })  
            else:  # If there are no rows, extract the message
                no_document_msg = rows[1].text.strip()
                documents.append({"No Document Needed": no_document_msg})
        else:  # If no table is found
            documents.append({"error": "No table found on the page."})
        return documents
    else:
        raise Exception("Failed to retrieve the webpage")
    
def import_duties(code):
    # URL of the ADiL page
    url = f"https://www.douane.gov.ma/adil/info_2.asp?pos={code}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    print(f"sending request for import duties for:{code}")
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    # Send a GET request to the URL
    response = session.get(url, headers=headers)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        print(f"Request successful for code: {code}")
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        # Find the table containing the data
        table = soup.find('table', width="60%")

        # Initialize data dictionary
        data = {}

        # Extract data from the table
        rows = table.find_all('tr')[1:]
        for row in rows:
            cols = row.find_all('td')
            if len(cols) == 1:  # Check if the row has only one column

                # Extract the text content of the column
                content = cols[0].text.strip()
                # Extract the key and value from the content
                lines = content.splitlines()
                # Process each line separately
                for idx, line in enumerate(lines):
                    # Split the line by ':' and take the first part as the key and the second part as the value
                    parts = re.split(r':\s*', line, maxsplit=1)
                    key = parts[0].strip()
                    value = parts[1].strip() if len(parts) > 1 else ''

                    # Check if the value is empty and the next line contains a value
                    if not value and idx+1 < len(lines):
                        value = lines[idx+1].strip()

                    # Store the key-value pair in the data dictionary
                    data[key] = value
        return data
    else:
        print(f"Request failed for code: {code}")
        raise Exception("Failed to retrieve the webpage")

def adil_tableaux(n, code):
    # URL of the ADiL page
    url = f"https://www.douane.gov.ma/adil/info_{n}.asp?pos={code}"
    # Determine the page_name based on the value of N in the URL
    if "info_8.asp" in url:
        page_name = "importation_poids"
    elif "info_5.asp" in url:
        page_name = "Historique Droit d'Importation"
    elif "info_9.asp" in url:
        page_name = "exportation_poids"
    elif "info_10.asp" in url:
        page_name = "fournisseurs_poids"
    elif "info_11.asp" in url:
        page_name = "clients_poids"
    elif "info_12.asp" in url:
        page_name = "importation_valeur"
    elif "info_14.asp" in url:
        page_name = "exportation_valeur"
    elif "info_15.asp" in url:
        page_name = "fournisseurs_valeur"
    elif "info_16.asp" in url:
        page_name = "clients_valeur"
    else:
        page_name = "unknown"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    print(f"sending request to {url}")
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    response = session.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser') #lxml

        # Check if the alternative message exists
        alternative_message_div = soup.find('div', class_='Style100')
        if alternative_message_div:
            return jsonify({"page_name": page_name, "message": alternative_message_div.get_text(strip=True)})
        
        # Find the correct table based on its surrounding elements or content
        correct_table = soup.find('table', bordercolor='#111111')

        if correct_table:
            # Initialize an empty dictionary to store the data
            data_dict = {}

            # Find all rows within the correct table
            rows = correct_table.find_all('tr')

            # Extract headers from the first row
            headers = [header.get_text(strip=True) for header in rows[0].find_all('td')]

            # Iterate over each row (starting from index 1 to skip headers)
            for row in rows[1:]:
                columns = row.find_all('td')
                # Extract country name from the first column
                country = columns[0].get_text(strip=True)
                # Extract data from subsequent columns
                data = [column.get_text(strip=True) for column in columns[1:]]
                # Combine headers and corresponding data into a dictionary
                row_dict = {header: value for header, value in zip(headers[1:], data)}
                # Add the row dictionary to the data dictionary under country name
                data_dict[country] = row_dict

            # Return the constructed dictionary directly under page_name
            return data_dict
        else:
            raise Exception("No data available for the specified position")
    else:
        print(f"Request failed for URL: {url}")
        raise Exception("Failed to retrieve the webpage")
 
@views_app.route('/get_data/<code>',methods=['GET'])
def get_and_save_data(code):
    
    codification_id = codification.query.filter_by(code=code).first().id

    # Importers
    try:
        importer_data = get_importers(code)
        for element in importer_data:
            existing_importer = Importers.query.filter_by(name=element, codification_id=codification_id).first()
            if not existing_importer:
                importer = Importers(name=element, codification_id=codification_id, code=code)
                db.session.add(importer)
                db.session.commit()
                print(f"Added importer {element}")
            else:
                print(f"Importer {element} already exists for codification {codification_id}")
    except Exception as e:
        print(f"Error getting importer data for code {code}: {e}")
    

    # Exporters
    try:
        exporter_data = get_exporters(code)
        for element in exporter_data:
            existing_exporter = Exporters.query.filter_by(name=element,codification_id=codification_id).first()
            if not existing_exporter:
                print(f"added new exporter:{element}")
                exporter = Exporters(name =element,codification_id=codification_id, code=code)
                db.session.add(exporter)
                db.session.commit()
    except Exception as e:
        print(f"Error getting exporter data for code {code}: {e}")
    
    # Classification Commerciale
    # try:
    #     classification_commerciale_n_data = get_classification_commerciale('n', code)
    # except Exception as e:
    #     print(f"Error getting classification commerciale (n) data for code {code}: {e}")
    
    # try:
    #     classification_commerciale_i_data = get_classification_commerciale('i', code)
    # except Exception as e:
    #     print(f"Error getting classification commerciale (i) data for code {code}: {e}")
    
    # Accord Convention
    try:
        accord_convention_data = get_accord_convention(code)
        for element in accord_convention_data:
            print(element['Agreement'])
            existing_accord_convention = AccordConvention.query.filter_by(country=element['country'], agreement=element['Agreement'], codification_id=codification_id).first()
            if not existing_accord_convention:
                accord_convention = AccordConvention(country=element['country'], agreement=element['Agreement'], di_percentage=element['DI Percentage'], tpi_percentage=element['TPI Percentage'], codification_id=codification_id, code=code)
                db.session.add(accord_convention)
                db.session.commit()
                print(f"Added accord convention for {element['country']}")
            else:
                print(f"Accord convention for {element['country']} already exists")
    except Exception as e:
        print(f"Error getting accord convention data for code {code}: {e}")
    
    # Documents Required
    try:
        documents_required_data = documents_required(code)
        print(documents_required_data)
        for element in documents_required_data:
        # Check if Document Required already exists
            existing_document_required = DocumentRequired.query.filter_by(document_number=element['Document Number'], document_name=element['Document Name'], codification_id=codification_id).first()
            if not existing_document_required:
                    print("we're inserting")
                    print(len(element))
                    if len(documents_required_data)==4:
                        document_required = DocumentRequired(document_number=element['Document Number'], document_name=element['Document Name'], libelle_d_extrait=element['libelle_d_extrait'], issuer=element['Issuer'], codification_id=codification_id, code=code)
                    else:
                        document_required = DocumentRequired(document_number=element['Document Number'], document_name=element['Document Name'],issuer=element['Issuer'], codification_id=codification_id, code=code)
                    db.session.add(document_required)
                    db.session.commit()
                    print(f"Added document required for {code} : {element['Document Name']}")
            else:
                print(f"Document required for {element['Document Name']} already exists")
    except Exception as e:
        print(f"Error getting documents required data for code {code}: {e}")
     
    # Import Duties
    try:
        element = import_duties(code)
        # Check if Import Duty already exists
        existing_import_duty = ImportDuty.query.filter_by(codification_id=codification_id).first()
        if not existing_import_duty:
            import_duty = ImportDuty(DI=element["-  Droit d'Importation* ( DI )"],TPI=element["- Taxe Parafiscale à l'Importation* ( TPI )"],TVA=element["- Taxe sur la Valeur Ajoutée à l'Import. ( TVA )"],codification_id=codification_id, code=code)
            db.session.add(import_duty)
            db.session.commit()
            print(f"Added import duty")
        else: 
            print(f"Import duty already exists")
    except Exception as e:
        print(f"Error getting import duties data for code {code}: {e}")
    
    # AnnualImport
    try:
        poids_imports=adil_tableaux("8", code)
        val_imports=adil_tableaux("12", code)
        for year, weight in poids_imports['Poids'].items():
            existing_AnnualImport = AnnualImport.query.filter_by(year=year,codification_id=codification_id).first()
            if not existing_AnnualImport :
                value = val_imports['Valeur'].get(year)
                annual_import = AnnualImport(year=year, weight=weight, value=value, codification_id=codification_id, code=code)
                db.session.add(annual_import)
                db.session.commit()
                print(f"Saved import data for year {year}")  
            else:
                print(f"Import data already exists")
    except Exception as e:
        print(f"Error getting import data for code {code}: {e}")

    # AnnualExports
    try:
        poids_exports=adil_tableaux("9", code)
        val_exports=adil_tableaux("14", code)
        for year, weight in poids_exports['Poids'].items():
            existing_annual_export = AnnualExport.query.filter_by(year=year, codification_id=codification_id).first()
            if not existing_annual_export:
                value = val_exports['Valeur'].get(year)
                annual_export = AnnualExport(year=year, weight=weight, value=value, codification_id=codification_id, code=code)
                db.session.add(annual_export)
                db.session.commit()
                print(f"Saved export data for year {year}")
            else:
                print(f"export data already exists")
    except Exception as e:
        print(f"Error saving export data: {e}")
    
    # Fournisseurs
    try:
        poids_fourn=adil_tableaux("10", code)
        val_fourn=adil_tableaux("15", code)
        for country,weight in poids_fourn['Poids'].items():
            existing_Fournisseurs = Fournisseurs.query.filter_by(country=country, codification_id=codification_id).first()
            if not existing_Fournisseurs:
                value = val_fourn['Valeur'].get(country)
                fournisseur = Fournisseurs(country=country, weight=weight, value=value, codification_id=codification_id, code=code)
                db.session.add(fournisseur)
                db.session.commit()
                print(f"Saved fournisseur data for country {country}")
            else:
                print(f"fournisseur {country} data already exists")
    except Exception as e:
        print(f"Error saving fournisseurs data: {e}")

    # Clients
    try:
        poids_Clients=adil_tableaux("11", code)
        val_Clients=adil_tableaux("16", code)
        for country,weight in poids_Clients['Poids'].items():
            existing_Clients = Clients.query.filter_by(country=country, codification_id=codification_id).first()
            if not existing_Clients:
                value = val_Clients['Valeur'].get(country)
                fournisseur = Clients(country=country, weight=weight, value=value, codification_id=codification_id, code=code)
                db.session.add(fournisseur)
                db.session.commit()
                print(f"Saved Client data for country {country}")
            else:
                print(f"client {country} data already exists")
    except Exception as e:
        print(f"Error saving Clients data: {e}") 
 
    try:
        return ("all is good")
    except Exception as e:
        print(f"error: {e}") 


