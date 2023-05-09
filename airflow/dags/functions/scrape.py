from bs4 import BeautifulSoup
import re
import traceback
import logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from selenium.webdriver import Remote

import pandas as pd



# this is a function to get the html code of a table in an element
def get_tables(element):
    tables = element.select('table')
    result = ''
    for table in tables:
        result += str(table) + '\n'
    return result

def scrape():
    
    options = Options() 

    options.add_argument('--headless')
    options.add_experimental_option('excludeSwitches', ['enable-logging']) 
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option('detach', True)
    options.add_argument("--dns-prefetch-disable")
    options.add_argument("enable-features=NetworkServiceInProcess")
    # options.add_argument("disable-features=NetworkService") 

    driver = Remote(command_executor=f"http://chrome:4444/wd/hub", options=options)
    
    # variables used to navigate through the pages
    base_url = 'https://www.legifrance.gouv.fr'
    results_per_page = 100
    page_num = 1
    nb_results = 200

    # a list to hold the legal_texts objects
    legal_texts =[]
    try:
        # a variable to help us check the number of results
        j = results_per_page
        while j <= nb_results:
            print("page : ", page_num)
            print("j : ", j)
            print("results per page : ", results_per_page)
            print("nb results : ", nb_results)

            url = f"https://www.legifrance.gouv.fr/search/lois?tab_selection=lawarticledecree&searchField=ALL&query=*&searchType=ALL&nature=ORDONNANCE&nature=DECRET&nature=ARRETE&etatArticle=VIGUEUR&etatArticle=ABROGE_DIFF&etatTexte=VIGUEUR&etatTexte=ABROGE_DIFF&typeRecherche=date&typePagination=DEFAUT&sortValue=SIGNATURE_DATE_DESC&pageSize={results_per_page}&page={page_num}"
            
            # add results_per_page to j in order to check if we have reached the number of results needed
            j+=results_per_page

            # increment i to go to the next page in the next iteration
            page_num+=1 

            # go to the page
            driver.get(url)

            try:
                # Wait for the page to fully load
                wait = WebDriverWait(driver, 10)
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "js-tabcontent")))
            except Exception as e :
                tb = traceback.format_exc()
                logging.error(f"An error occurred: {e}. Traceback: {tb}")
                print("a connection problem has occured")
                raise
            # extract legal_texts
            whole_page= BeautifulSoup(driver.page_source, 'html.parser')

            # get all links to initial versions in the page
            vi_links= [base_url + tag.get('href') for tag in whole_page.select("ul.links-versions > li:first-child > a")]

            # working with the initial version of the legal text, get into each link and extract information
            for link in vi_links :
                print(link)
                # go to the legal text page
                driver.get(link)
                # parse the html of the page
                page = BeautifulSoup(driver.page_source, 'html.parser')
                
                # creating an object that will hold the legal text information   
                legal_text_obj = {}
                
                # extract the title of the legal text
                title = page.select_one('.main-title, .main-title-light, .main-title-bold').text.strip()
                legal_text_obj['title'] = title
                # print("title : ", title)


                # extract the nature from the title
                legal_text_obj['nature'] = title.split(' ')[0]
                # extract the date from the title
                date_match = re.search(r'du\s+(\d{1,2}\s+[a-zA-Zéû]+\s+\d{4})', title)
                if date_match:
                    legal_text_obj['date'] = date_match.group(1)
                else:
                    legal_text_obj['date'] = 'date unknown'   


                # extracting  subtitle information, which are NOR, ELI, jorf and the text number 
                ref_order_num = ''
                euro_legislation_id = ''
                jorf = ''
                jorf_link = ''
                jorf_text_num = ''
            
                for line in page.select('.top-page-jo span'):
                    try:
                        if 'NOR' in line.text.split(' ')[0]:
                            ref_order_num = line.text.strip().replace('NOR : ', '')
                    
                        elif 'ELI' in line.text.split(' ')[0]:
                            euro_legislation_id = line.text.strip().replace('ELI : ', '')
                    
                        elif 'JORF' in line.text.split(' ')[0]:
                            jorf = line.text.strip() 
                            jorf_link = base_url + line.find('a').get('href')

                        elif 'Texte' in line.text.split(' ')[0]:
                            jorf_text_num = line.text.strip()
                    except:
                        pass
                    
                legal_text_obj['NOR'] = ref_order_num
                legal_text_obj['ELI'] = euro_legislation_id
                legal_text_obj['jorf'] = jorf
                legal_text_obj['jorf_link'] = jorf_link
                legal_text_obj['jorf_text_num'] = jorf_text_num
                # print("ref_order_num  ", ref_order_num)
                # print("euro_legislation_id  ", euro_legislation_id)
                # print("jorf  ", jorf)
                # print("jorf_link  ", jorf_link)
                # print("jorf_text_num  ", jorf_text_num)
                        
                        

                # extract the summary preface i.e the text before the summary list of the articles    
                preface = ''
                if(page.select_one('div.summary-preface>p')):
                    preface = page.select_one('div.summary-preface>p').text.strip()
                legal_text_obj['preface'] = preface

                # print("preface ", preface)

                #extract the articles, iterating over each article and get information about it
                articles = []
                if (page.select('.list-article-consommation')):
                    summary_list = page.select('.list-article-consommation')
                    for article_html in summary_list:
                        article_title = article_html.select_one("p.name-article").text.strip()
                        
                        if(len(article_html.select('div.content p') ) > 1    ) :
                            article_text = '\n'.join([article.text.strip() for article in article_html.select('div.content p')])
                        else :    
                            article_text = article_html.select_one('div.content > p').text.strip()
                        
                        article_link = base_url + article_html.select_one("p.name-article > a").get('href')
                        
                        article = {}
                        article['title'] = article_title
                        article['text'] = article_text
                        article['link'] = article_link
                        article['tables'] = get_tables(article_html)

                        articles.append(article)
                    
                legal_text_obj['articles'] = articles
                # print("len of articles ", len(articles))

                
                # extract the information in the annexe section, get the tables in html if they exist there
                if(page.select_one('article.summary-preface div.content')):
                    annexe_element = page.select_one('article.summary-preface div.content')
                    legal_text_obj['annexe'] = annexe_element.text.strip() 
                    legal_text_obj['annexe_tables'] = get_tables(annexe_element)
                else :
                    legal_text_obj['annexe'] = ''   
                    legal_text_obj['annexe_tables'] = ''

                # extract the text that is after the annexe
                annexe_summary = ''
                if (page.select_one('div.summary-annexe')):
                    annexe_summary = page.select_one('div.summary-annexe')
                    annexe_summary = ' '.join(annexe_summary.get_text(separator='\n').split())
                legal_text_obj['annexe_summary'] = annexe_summary
                # print("annexe_summary: ", annexe_summary)

                # extract the pdf link to the official journal related to the legal text
                jorf_pdf_link = ''
                if(page.select_one('a.doc-download')):
                    jorf_pdf_link = base_url + page.select_one('a.doc-download').get('href')
                legal_text_obj['jorf_pdf'] = jorf_pdf_link
                # print("pdf", jorf_pdf_link)

                # append the object created i.e the legal text information
                legal_texts.append(legal_text_obj)
            
        print("finished scraping")          
    except Exception as e:
        tb = traceback.format_exc()
        logging.error(f"An error occurred: {e}. Traceback: {tb}")
        print('an error has occured, closing the chrome driver...')
        raise
    finally:
        driver.quit()

    # make the result into a dataframe
    try :
        # create an empty DataFrame
        df = pd.DataFrame(columns=["title", "nature", "date", "NOR", "ELI", "jorf", "jorf_link", "jorf_text_num", "preface", "article_title", "article_text", "article_link", "article_tables", "annexe", "annexe_tables", "annexe_summary", "jorf_pdf"])

        # add rows to the df
        for legal_text in legal_texts:
            for article in legal_text['articles']:
                new_row = pd.DataFrame ( {
                        "title": legal_text['title'],
                        "nature": legal_text['nature'],
                        "date": legal_text['date'],
                        "NOR" : legal_text['NOR'],
                        "ELI" : legal_text['ELI'],
                        "jorf" : legal_text['jorf'],
                        "jorf_link" : legal_text['jorf_link'],
                        "jorf_text_num" : legal_text['jorf_text_num'],
                        "preface" : legal_text['preface'],
                        "article_title" : article['title'], 
                        "article_text" : article['text'], 
                        "article_link" : article['link'], 
                        "article_tables" : article['tables'],
                        "annexe" : legal_text['annexe'],
                        "annexe_tables" : legal_text['annexe_tables'],
                        "annexe_summary" : legal_text['annexe_summary'], 
                        "jorf_pdf" : legal_text['jorf_pdf'], 
                        
                    }, index=[0] )
                df = pd.concat([df, new_row], ignore_index=True)
        # create a csv file and put the content there
        df.to_csv('/csv_files/legal_texts.csv', sep ='|', index=False)
    except :
        print("couldn't save to csv file, verify the values")
