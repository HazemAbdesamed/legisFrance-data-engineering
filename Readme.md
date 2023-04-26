# legisFrance-data-engineering
This project aims to collect legal text data from the website Légisfrance, store the data and visualizing it.

## Step 1 : Legal Text Scraping

The first step involves scraping the most recent 200 legal texts of nature (Arrêté, Décret or Ordonnance).

The approach followed is to get all the links of (version initiale), navigating through each of them and getting information about the legal text and its articles.

The data collected is stored in a [csv file](https://github.com/HazemAbdesamed/legisFrance-data-engineering/blob/main/csv_files/legal_texts.csv)

The code used to scrape data can be found in [scrape.py file](https://github.com/HazemAbdesamed/legisFrance-data-engineering/blob/main/airflow/dags/functions/scrape.py)

## Step 2 : Data Modelling and ETL Pipeline

### Data modeling
The fields used retrieved are : 
* **title** is the title of the legal text.
* **nature** is the nature of the legal text.
* **date** is the signature date of the legal text.
* **NOR** is the Reference Order Number of the legal text.
* **ELI** is the European Legislation Identifier.
* **jorf** is the Official Journal of the French Republic in which the legal text was published.
* **jorf_link** is the URL of the legal text in the JORF.
* **jorf_text_num** The JORF reference number for the legal text.
* **preface** is the introductory text of the legal text.
* **article_title** it the title of an individual article within the legal text.
* **article_text** is the text of an individual article within the legal text.
* **article_link** is the URL of the individual article within the legal text.
* **article_tables** contains tables in html format included in the article if they exist.
* **annexe**  contains the appendice if included in the legal text if it exists.
* **annexe_tables** any tables included in the annexes if they exist.
* **annexe_summary** A summary of the content of the annexes.
* **jorf_pdf** the link to PDF version of the legal text in the JORF.

The schema :
<pre><code>

      legalText: {
        title: 'string',
        nature: 'string',
        date: 'date',
        NOR: 'string',
        ELI: 'string',
        jorf: 'string',
        jorf_link: 'string',
        jorf_text_number: 'string',
        preface: 'string',
        annexe: 'string',
        annexe_tables: 'string',
        annexe_summary: 'string',
        jorf_pdf: 'string',
        articles: [
           { 
              article_title: 'string',
              article_text: 'string',
              article_link: 'string',
              article_tables: 'string',
           }
        ]
    }
</pre></code>

Assuming that the articles are generaly retrieved with their respective legal texts, we have put the legal text and its articles in the same collection.

Assuming that the fields that are used the most are **nature** and **date**, two indexes are created for these fields.

### ETL Pipeline

In this part we load the data into the mongodb db after performing some transformations to respect the structure of the mongodb collection.

The code used to implement this step can be found in [load_to_db.py file](https://github.com/HazemAbdesamed/legisFrance-data-engineering/blob/main/airflow/dags/functions/load_to_db.py)

