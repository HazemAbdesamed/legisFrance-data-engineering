# legisFrance-data-engineering
This project aims to collect legal text data from the website [Légisfrance](https://www.legifrance.gouv.fr/search/lois?tab_selection=lawarticledecree&searchField=ALL&query=*&searchType=ALL&nature=ORDONNANCE&nature=DECRET&nature=ARRETE&etatArticle=VIGUEUR&etatArticle=ABROGE_DIFF&etatTexte=VIGUEUR&etatTexte=ABROGE_DIFF&typeRecherche=date&dateVersion=18%2F04%2F2023&typePagination=DEFAUT&sortValue=SIGNATURE_DATE_DESC&pageSize=100&page=1&tab_selection=lawarticledecree#lois), store the data and visualizing it.

## Step 1 : Legal Text Scraping

The first step involves scraping the most recent 200 legal texts of nature (Arrêté, Décret or Ordonnance).

The approach followed is to get all the links of (version initiale), navigating through each of them and getting information about the legal text and its articles.

The data collected is stored in a [csv file](https://github.com/HazemAbdesamed/legisFrance-data-engineering/blob/main/csv_files/legal_texts.csv)

[!alt text](https://user-images.githubusercontent.com/48518599/234459110-cfb9c71f-aca8-4dca-8dfc-6e9a4349cf6c.png "csv file")


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

Assuming that the articles are generally queried with their respective legal texts, the legal text and its articles are put in the same collection.

Assuming that the fields that are used the most are **nature** and **date**, two indexes are created for these fields.

Also, in this part we load the data into the mongodb db after performing some transformations to respect the structure of the mongodb collection.

The code used to load data can be found in [load_to_db.py file](https://github.com/HazemAbdesamed/legisFrance-data-engineering/blob/main/airflow/dags/functions/load_to_db.py)
![alt text](https://user-images.githubusercontent.com/48518599/234460528-74538ff4-f103-4769-ac84-403afbfd5385.png "example")
![image](https://user-images.githubusercontent.com/48518599/234460609-734ed455-4ca7-4c23-9738-2de69c978182.png "number of documents")


### ETL Pipeline
In this step we implement the data pipeline.

The code implemented to orchestrate the data pipeline can be found in [this file](https://github.com/HazemAbdesamed/legisFrance-data-engineering/blob/main/airflow/dags/main.py)

![alt text](https://user-images.githubusercontent.com/48518599/234460700-c1edfe17-a8bd-49e8-bdb8-fac19ac1d905.png "the pipeline run successfully")


## STEP 3 : Data Visualization

In this step we create visualizations related to the legal text.

The first [two visualizations](https://github.com/HazemAbdesamed/legisFrance-data-engineering/blob/main/airflow/visualizations/legal_text_by_nature_over_time.png) represent respectively the number of legal texts by nature by day and the cumulative count of legal texts by nature over time.


![alt text](https://user-images.githubusercontent.com/48518599/234665158-156492de-a3f9-4063-8dca-48ef857e074b.png "counts by nature over time and cumulative counts by nature over time")


The [other visualizations](https://github.com/HazemAbdesamed/legisFrance-data-engineering/blob/main/airflow/visualizations/wordcloud.png) represent the wordcloud for content of the article texts and title texts.

We have created a stopwords list that can be improved as needed for efficient words retrieving.

![alt text](https://user-images.githubusercontent.com/48518599/234665698-627a2d46-fb1c-449c-a527-795083876045.png "wordcloud for titles and content of text ")

The visualisations are stored in [this folder](https://github.com/HazemAbdesamed/legisFrance-data-engineering/tree/main/airflow/visualizations) along with the stopwords list. 

These visuals can be used later for analysis ( Reporting or Dashboard ).

The DAG after adding the data visualization task : 

![alt text](https://user-images.githubusercontent.com/48518599/234666740-4df39f95-50f7-43be-ab63-5be59f44f2ac.png "the dag with data visualization task")



