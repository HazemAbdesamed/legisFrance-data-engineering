# legisFrance-data-engineering
This project aims to collect legal text data from the website [Légisfrance](https://www.legifrance.gouv.fr/search/lois?tab_selection=lawarticledecree&searchField=ALL&query=*&searchType=ALL&nature=ORDONNANCE&nature=DECRET&nature=ARRETE&etatArticle=VIGUEUR&etatArticle=ABROGE_DIFF&etatTexte=VIGUEUR&etatTexte=ABROGE_DIFF&typeRecherche=date&dateVersion=18%2F04%2F2023&typePagination=DEFAUT&sortValue=SIGNATURE_DATE_DESC&pageSize=100&page=1&tab_selection=lawarticledecree#lois), store the data and visualizing it.

## Step 1 : Legal Text Scraping

The first step involves scraping the most recent 200 legal texts of nature (Arrêté, Décret or Ordonnance).

The approach followed is to get all the links of (version initiale), navigating through each of them and getting information about the legal text and its articles.

The data collected is stored in a [csv file](https://github.com/HazemAbdesamed/legisFrance-data-engineering/blob/main/csv_files/legal_texts.csv).

![alt text](https://user-images.githubusercontent.com/48518599/234459110-cfb9c71f-aca8-4dca-8dfc-6e9a4349cf6c.png "csv file")


The code implemented to scrape data can be found in [scrape.py file](https://github.com/HazemAbdesamed/legisFrance-data-engineering/blob/main/airflow/dags/functions/scrape.py).

## Step 2 : Data Modelling and ETL Pipeline

### Data modeling
The fields retrieved are : 
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

Also, in this part we load the data into the mongodb after performing some transformations in order to respect the structure of the mongodb collection.

The code used to load data can be found in [load_to_db.py file](https://github.com/HazemAbdesamed/legisFrance-data-engineering/blob/main/airflow/dags/functions/load_to_db.py).
![alt text](https://user-images.githubusercontent.com/48518599/234460528-74538ff4-f103-4769-ac84-403afbfd5385.png "example")
![image](https://user-images.githubusercontent.com/48518599/234460609-734ed455-4ca7-4c23-9738-2de69c978182.png "number of documents")
![alt text](https://user-images.githubusercontent.com/48518599/234668931-65d758e4-0588-4f01-b183-2dda23f3f0c6.png "NOR, title and nature fields")
![alt text](https://user-images.githubusercontent.com/48518599/234669462-39da5e03-4da7-4052-b7f5-04b12dca3818.png "distinct nature values ")


**We can remark that legal text of nature "Ordonnance" were not signed during this period**


### ETL Pipeline
In this step we implement the data pipeline.

The code implemented to orchestrate the data pipeline can be found in [this file](https://github.com/HazemAbdesamed/legisFrance-data-engineering/blob/main/airflow/dags/main.py).

![alt text](https://user-images.githubusercontent.com/48518599/234460700-c1edfe17-a8bd-49e8-bdb8-fac19ac1d905.png "the pipeline run successfully")


## STEP 3 : Data Visualization

In this step we create visualizations related to the legal text.

The first two visualizations represent respectively the number of legal texts by nature by day and the cumulative count of legal texts by nature over time.


![alt text](https://user-images.githubusercontent.com/48518599/234665158-156492de-a3f9-4063-8dca-48ef857e074b.png "counts by nature over time and cumulative counts by nature over time")


Another visualization shows the average number of articles by the nature of the legal text.

![image](https://user-images.githubusercontent.com/48518599/234834929-b4e63337-fadc-4897-b662-82821f62d516.png "average number of articles by nature")


This visualization show the average number of characters, words and paragraphs by the nature of the legal text.

![image](https://user-images.githubusercontent.com/48518599/236078168-af661bd5-fdd2-42ae-a2d6-977f1a3fea64.png "average number of characters, words and paragraphs")

The other visualizations represent the wordcloud for content of the article texts and title texts.

We have created a stopwords list that can be improved as needed for efficient words retrieving.

![alt text](https://user-images.githubusercontent.com/48518599/234665698-627a2d46-fb1c-449c-a527-795083876045.png "wordcloud for titles and content of text ")


The visualisations are stored in [this folder](https://github.com/HazemAbdesamed/legisFrance-data-engineering/tree/main/airflow/visualizations) along with the stopwords list. 

These visuals can be used later for analysis ( Reporting or Dashboard ).

The DAG after adding the data visualization task : 

![alt text](https://user-images.githubusercontent.com/48518599/234666740-4df39f95-50f7-43be-ab63-5be59f44f2ac.png "the dag with data visualization task")


## Step 4 : Data Pipeline Monitoring
In this step we track and visualize metrics and indicators related to the performance of the data pipeline using the tools (StatsD, Prometheus and Grafana).
The dashboard can be configured to be visualized in different periods of time.

These indicators are used in the dashboard, they consist of 
* **Scheduler heartbeat** will indicate that the airflow scheduler is working.
* **Number of Dag Runs** will indicate the number of dags runs.
* **Tasks Average Durations** will indicate for each task, the time the duration for its completion.
* **Tasks failure** will indicate that a task has failed, if so, an alert will be fired and the user will be notified by a mail .
* **Dag Duration** is a metric that will indicate the durations for the dags over the time, the user will be alerted if the average surpasses a certain limit of time.
* **DAG Run dependency Check Time** is a metric used to be aware of the time taken to check for dependecies.

![image](https://user-images.githubusercontent.com/48518599/235801522-7d059be7-c379-4524-8e69-013a99170fc9.png "Dashboard")

When an alert is fired

![image](https://user-images.githubusercontent.com/48518599/235802841-a0686db5-b5dd-48d1-9e7f-70bfef07ab08.png "task failed alert")

An email is sent to the user

![image](https://user-images.githubusercontent.com/48518599/235803250-95849982-dd71-4226-b32f-7f1bace2eec3.png "alert email")

## Requirements : 
* docker desktop v4.15.0
* docker v20.10.21
* docker-compose v2.13.0

## Usage :
* Download the folder of the project.
* Navigate to the folder on your marchine.
* execute : <code> docker-compose up --build -d </code>, it will take some time for the first time as it will download the images and the dependecies.
* The data pipeline is scheduled to be executed every week. However, to run the data pipeline manually, navigate to localhost:8080, turn on the DAG and trigger it.

![image](https://user-images.githubusercontent.com/48518599/234822563-e89e35c0-26e4-4438-b08b-dd0d69f65e41.png "running a data pipeline")


