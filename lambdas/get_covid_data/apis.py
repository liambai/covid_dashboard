import requests

def get_country_codes():
    country_codes_query = '''
    {
        summary {
            countries {
                Code
        }
      }
    }

    '''
    url = "https://api-corona.azurewebsites.net/graphql"
    country_codes_request = requests.post(url, json={"query": country_codes_query})
    if country_codes_request.status_code != 200:
        raise Exception("Query failed")
        
    country_codes = country_codes_request.json()['data']['summary']['countries']
    return [e['Code'] for e in country_codes if e['Code'] is not None]

def get_country_name(country_code): 
    country_name_query = ''' 
    query getCountryName($countryCode: ID!) {
        country(country: $countryCode) {
            Summary {
                Slug
            }
        }
    }
    '''
    body = {
      "query": country_name_query,
      "variables": {"countryCode": country_code}
    }
    
    url = "https://api-corona.azurewebsites.net/graphql"
    country_name_request = requests.post(url, json=body)
    
    if country_name_request.status_code != 200:
        raise Exception("Query failed.")
    return country_name_request.json()['data']['country']['Summary']['Slug']
    
def get_cases_data(country_code):
    country_data_query = ''' 
    query getCountryData($countryCode: ID!) {
        timelineCountry(country: $countryCode) {
            Country
            Date
            Confirmed
            Deaths
            Lat
            Long
        }
    } 
    '''
    body = {
      "query": country_data_query,
      "variables": {"countryCode": country_code}
    }

    url = "https://api-corona.azurewebsites.net/graphql"
    country_data_request = requests.post(url, json=body)

    if country_data_request.status_code != 200:
        raise Exception("Query failed")
        
    country_info = country_data_request.json()['data']['timelineCountry']
    cases_info = {e['Date']: {"Confirmed": e['Confirmed'], "Deaths": e['Deaths']} for e in country_info} 
    return cases_info
    
def get_location_data(country_code):
    response = requests.get("https://corona.azure-api.net/country/" + country_code)
    country_summary = response.json()["Summary"]
    return {"Lat": country_summary["Lat"], "Long": country_summary["Long_"]}