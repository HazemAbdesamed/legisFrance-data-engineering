from pymongo import MongoClient, UpdateOne
import csv
import pandas as pd

def convert_date(date_str):
    # Split the date string into day, month, and year
    day, month, year = date_str.split(' ')

    # Define a dictionary mapping month names to month numbers
    month_map = {
        'janvier': '01',
        'février': '02',
        'mars': '03',
        'avril': '04',
        'mai': '05',
        'juin': '06',
        'juillet': '07',
        'août': '08',
        'septembre': '09',
        'octobre': '10',
        'novembre': '11',
        'décembre': '12',
    }

    # Use the month map to get the month number
    month_num = month_map[month.lower()]

    # Return the date in the desired format
    return f"{year}-{month_num}-{day}"



def load_data_to_db() :


    client = MongoClient("mongodb://root:root@mongodb:27017/")
    db = client["legisFrance"]
    collection = db["legalText"]


    # limit the field size to 50MB
    csv.field_size_limit(50000000)
    # read data from CSV file
    with open('/csv_files/legal_texts.csv', 'r') as file:
        reader = csv.reader(file, delimiter='|')
        header = next(reader)
        data = [row for row in reader]

    # insert data to a df
    df = pd.DataFrame(data, columns=header)


    df['date'] = df['date'].apply(convert_date)
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')

    # group by an identifier of the legal text
    groups = df.groupby('NOR')


    documents = []
    for nor, group_df in groups:
        document = {
            "title": group_df['title'].iloc[0],
            "nature": group_df['nature'].iloc[0],
            "date": group_df['date'].iloc[0],
            "NOR" : group_df['NOR'].iloc[0],
            "ELI" : group_df['ELI'].iloc[0],
            "jorf" : group_df['jorf'].iloc[0],
            "jorf_link" : group_df['jorf_link'].iloc[0],
            "jorf_text_num" : group_df['jorf_text_num'].iloc[0],
            "preface" : group_df['preface'].iloc[0],
            "articles" : [],
            "annexe" : group_df['annexe'].iloc[0],
            "annexe_tables" : group_df['annexe_tables'].iloc[0],
            "annexe_summary" : group_df['annexe_summary'].iloc[0], 
            "jorf_pdf" : group_df['jorf_pdf'].iloc[0]
        }


        for _, article in group_df.iterrows():
            document['articles'].append(
                {
                    "article_title" : article['article_title'], 
                    "article_text" : article['article_text'], 
                    "article_link" : article['article_link'], 
                    "article_tables" : article['article_tables'],
                }
            )
        documents.append(document)    


    # create a list of update operations
    updates = [
        UpdateOne(
            {'NOR': document['NOR']},  # filter to match documents
            {'$set': document},  # update operations
            upsert=True  # insert a new document if it doesn't exist
        )
        for document in documents
    ]

    # execute the update operations
    collection.bulk_write(updates)
    

    # close MongoDB connection
    client.close()
