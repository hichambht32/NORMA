from flask import jsonify
from bs4 import BeautifulSoup
from api.session import session
import re 
from api.models import Importers,codification
from api.api_api import views_app
from api.connection import db

def get_importers(code):

    url = f"https://www.douane.gov.ma/adil/oper_Ii.asp?pos={code}"
    
    # Set headers to mimic a browser request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    
    # Send a GET request to the URL
    print("Sending GET request to:", url)
    response = session.get(url, headers=headers)
    print("Response status code:", response.status_code)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all table rows (tr) containing importer names
        importer_rows = soup.find_all('td', class_='Style7')
        print("Number of importer rows found:", len(importer_rows))
        
        # Extract the importer names
        importer_names = [row.get_text(strip=True) for row in importer_rows]
        print("Importer names:", importer_names)

        # Construct the response dictionary
        if attention(soup):
            raise Exception("No importers found as of date")
        else:
            return importer_names
    else:
        raise Exception("Failed to retrieve the webpage")

def get_exporters(code):
    print(f"Fetching exporters for code: {code}")
    url = f"https://www.douane.gov.ma/adil/oper_EE.asp?pos={code}"
    
    # Set headers to mimic a browser request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    
    # Send a GET request to the URL
    response = session.get(url, headers=headers)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        print(f"Request successful for code: {code}")
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all table rows (tr) containing importer names
        exporter_rows = soup.find_all('span', class_='Style7')
        
        # Extract the importer names
        exporter_names = [row.get_text(strip=True) for row in exporter_rows]

        # Construct the response dictionary
        if attention(soup):
            raise Exception("No exporters found as of date")
        else:
            return exporter_names
            
    else:
        print(f"Request failed for code: {code}")
        raise Exception("Failed to retrieve the webpage")

def attention(soup):
    attention_img = soup.find('img', src="images/attention.gif")
    if attention_img:
        return True
    else :
        return False

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
        data = {}

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

                if current_country in data:
                    data[current_country].append({
                        "Agreement": agreement_type,
                        "DI Percentage": di_percentage,
                        "TPI Percentage": tpi_percentage
                    })
                else:
                    data[current_country] = [{
                        "Agreement": agreement_type,
                        "DI Percentage": di_percentage,
                        "TPI Percentage": tpi_percentage
                    }]
        print(f"Data extracted: {data}")
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

    # Send a GET request to the URL
    response = session.get(url, headers=headers)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the table containing the data
        table = soup.find('table', width="60%")

        # Initialize data list
        documents = []

        if table:  # If table is found
            # Check if there are any rows in the table
            rows = table.find_all('tr')
            if len(rows) > 3:  # If there are rows, extract data
                rows = rows[5:]  # Exclude first four rows
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 3:  # Ensure at least 3 columns exist
                        document_number = cols[0].text.strip()
                        document_name = cols[1].text.strip()
                        libelle_d_extrait = cols[2].text.strip()
                        issuer = cols[3].text.strip()
                        documents.append({
                            "Document Number": document_number,
                            "Document Name": document_name,
                            "Libelle d'Extrait": libelle_d_extrait,
                            "Issuer": issuer
                        })
            else:  # If there are no rows, extract the message
                no_document_msg = rows[1].text.strip()
                documents.append({"No Document Needed": no_document_msg})
        else:  # If no table is found
            documents.append({"error": "No table found on the page."})


        # Return the scraped data
        return documents
    else:
        raise Exception("Failed to retrieve the webpage")

def import_duties(code):
    # URL of the ADiL page
    url = f"https://www.douane.gov.ma/adil/info_2.asp?pos={code}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

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
                for line in lines:
                    # Split the line by ':' and '\n'
                    key, *value = re.split(r'[:\n]', line, maxsplit=1)

                    # Remove leading and trailing whitespaces from the key and value
                    key = key.strip()

                    # Join the value parts with a space and remove leading and trailing whitespaces
                    value = ' '.join(value).strip()

                    # Store the key-value pair in the data dictionary
                    data[key] = value

        print(f"Data extracted: {data}")
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
    response = session.get(url, headers=headers)

    if response.status_code == 200:
        print(f"Request successful for URL: {url}")
        soup = BeautifulSoup(response.text, 'html.parser') #lxml

        # Check if the alternative message exists
        alternative_message_div = soup.find('div', class_='Style100')
        if alternative_message_div:
            print(f"Alternative message found: {alternative_message_div.get_text(strip=True)}")
            return jsonify({"page_name": page_name, "message": alternative_message_div.get_text(strip=True)})
        
        # Find the correct table based on its surrounding elements or content
        correct_table = soup.find('table', bordercolor='#111111')

        if correct_table:
            print(f"Table found for URL: {url}")
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
            print(f"No table found for URL: {url}")
            raise Exception("No data available for the specified position")
    else:
        print(f"Request failed for URL: {url}")
        raise Exception("Failed to retrieve the webpage")

@views_app.route('/get_data/<code>',methods=['GET'])
def get_and_save_data(code):
    n_page_names = {
        "5": "Historique Droit d'Importation",
        "8": "importation1",
        "9": "exportation1",
        "10": "fournisseurs_poids",
        "11": "clients_poids",
        "12": "importation2",
        "14": "exportation2",
        "15": "fournisseurs_valeur",
        "16": "clients_valeur"
    }
    
    codification_id = codification.query.filter_by(code=code).first().id
    data = {}
    
    # Importers
    try:
        importer_data = get_importers(code)
        data['importers'] = importer_data
        for element in importer_data:
            print(element)
            importer = Importers(name=element,codification_id=codification_id)
            db.session.add(importer)
            db.session.commit()

    except Exception as e:
        print(f"Error getting importer data for code {code}: {e}")
        data['importers'] = {"error": f"Failed to get importer data for code {code}"}
    # Exporters
    # try:
    #     exporter_data = get_exporters(code)
    #     data['exporters'] = exporter_data
    # except Exception as e:
    #     print(f"Error getting exporter data for code {code}: {e}")
    #     data['exporters'] = {"error": f"Failed to get exporter data for code {code}"}
    
    # # Classification Commerciale
    # try:
    #     classification_commerciale_n_data = get_classification_commerciale('n', code)
    #     data['classification_commerciale_n'] = classification_commerciale_n_data
    # except Exception as e:
    #     print(f"Error getting classification commerciale (n) data for code {code}: {e}")
    #     data['classification_commerciale_n'] = {"error": f"Failed to get classification commerciale (n) data for code {code}"}
    
    # try:
    #     classification_commerciale_i_data = get_classification_commerciale('i', code)
    #     data['classification_commerciale_i'] = classification_commerciale_i_data
    # except Exception as e:
    #     print(f"Error getting classification commerciale (i) data for code {code}: {e}")
    #     data['classification_commerciale_i'] = {"error": f"Failed to get classification commerciale (i) data for code {code}"}
    
    # # Accord Convention
    # try:
    #     accord_convention_data = get_accord_convention(code)
    #     data['accord_convention'] = accord_convention_data
    # except Exception as e:
    #     print(f"Error getting accord convention data for code {code}: {e}")
    #     data['accord_convention'] = {"error": f"Failed to get accord convention data for code {code}"}
    
    # # Documents Required
    # try:
    #     documents_required_data = documents_required(code)
    #     data['documents_required'] = documents_required_data
    # except Exception as e:
    #     print(f"Error getting documents required data for code {code}: {e}")
    #     data['documents_required'] = {"error": f"Failed to get documents required data for code {code}"}
    
    # # Import Duties
    # try:
    #     import_duties_data = import_duties(code)
    #     data['import_duties'] = import_duties_data
    # except Exception as e:
    #     print(f"Error getting import duties data for code {code}: {e}")
    #     data['import_duties'] = {"error": f"Failed to get import duties data for code {code}"}
    
    # # Adil Tableaux
    # adil_tableaux_data = {}
    # for n_value in n_page_names:
    #     try:
    #         adil_tableaux_data[n_page_names[n_value]] = adil_tableaux(n_value, code)
    #     except Exception as e:
    #         print(f"Error getting adil tableaux data for code {code}, n={n_value}: {e}")
    #         adil_tableaux_data[n_page_names[n_value]] = {"error": f"Failed to get adil tableaux data for code {code}, n={n_value}"}
    
    # data['adil_tableaux'] = adil_tableaux_data
    
    # print(data['importers'])
    return ("all good")



