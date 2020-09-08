import json
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from apis import get_country_codes, get_country_name, get_cases_data, get_location_data

def lambda_handler(event, context):
    country_codes = get_country_codes()
    rows = []
    for code in country_codes:
        country_name = get_country_name(code)
        cases_info = get_cases_data(code)
        location_info = get_location_data(code)
        for date in cases_info.keys():
    
            confirmed = cases_info[date]["Confirmed"]
            log10_confirmed = max(0, np.log10(confirmed))
            ln_confirmed = max(0, np.log(confirmed))
    
            deaths = cases_info[date]["Deaths"]
            log10_deaths = max(0, np.log10(deaths))
            ln_deaths = max(0, np.log(deaths))
    
            rows.append([code, country_name, location_info["Lat"], location_info["Long"], date, 
                         confirmed, deaths, log10_confirmed, log10_deaths, ln_confirmed, ln_deaths])
    
    summary_df = pd.DataFrame(rows, columns=['Country Code', 'Country', 'Lat', 'Long', 'Date', 'Confirmed', "Deaths",
                                            "Log10 Confirmed", "Log10 Deaths", "Ln Confirmed", "Ln Deaths"])

    
    engine = create_engine('postgresql://postgres:data1050-postgres-fa20!@data1050.cdzzrqlrfv5z.us-east-1.rds.amazonaws.com:5432/covid')
    connection = engine.raw_connection()
    cursor = connection.cursor()
    cursor.execute("DROP TABLE IF EXISTS country;")
    connection.commit()
    cursor.close()
    
    summary_df.to_sql('country', engine)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Data update complete!')
    }