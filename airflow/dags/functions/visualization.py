from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
from wordcloud import WordCloud

client = MongoClient("mongodb://root:root@mongodb:27017/")
db = client["legisFrance"]
collection = db["legalText"]
df = pd.DataFrame(list(collection.find())).drop("_id", axis=1)

# a function to plot the number of legal text by their natures over time
def plot_nature_over_time():
    # Group data by 'nature' and 'date', and count the number of occurrences
    grouped_data = df.groupby(['nature', pd.Grouper(key='date', freq='D')])['NOR'].count().reset_index()
    grouped_data['cumulative_count'] = grouped_data.groupby('nature')['NOR'].cumsum()
    sns.set_style('darkgrid')

    fig, axs = plt.subplots(nrows=2, ncols=1, figsize=(16, 12))
    
    #the first graph, number of legal text by nature over time
    sns.lineplot(x='date', y='NOR', hue='nature', data=grouped_data, marker='o', ax=axs[0])
    axs[0].set_title('Number of Legal Texts by Nature per Day')
    axs[0].set_xticks(df['date'])
    axs[0].tick_params(axis='x', rotation=90, labelsize=9)
    axs[0].set_xlabel('Date')
    axs[0].set_ylabel('Count')

    #the second graph, cumulative number of legal text by nature over time
    sns.lineplot(x='date', y='cumulative_count', hue='nature', data=grouped_data, marker='o', ax=axs[1])
    axs[1].set_title('Cumulative Number of Legal Texts by Nature over time')
    axs[1].set_xticks(df['date'])
    axs[1].tick_params(axis='x', rotation=90, labelsize=9)
    axs[1].set_xlabel('Date')
    axs[1].set_ylabel('Cumulative Count')

    # Adjust spacing between subplots
    fig.subplots_adjust(hspace=0.5)

    # Save the visualization
    plt.savefig('/usr/local/airflow/visualizations/legal_text_by_nature_over_time.png', bbox_inches='tight')



def plot_wordcloud():
    
    # get the stop words list and put it in a set    
    with open("/usr/local/airflow/visualizations/stopwords.txt", "r") as f:
        stopwords = {line.strip() for line in f}
    
    # Get titles texts 
    titles_text = ' '.join(list(df['title']))
    
    # Get articles texts
    all_articles_texts = ''
    for article_list in df['articles']:
        for article in article_list :
            all_articles_texts += article['article_text'] + ' '


    # Create a figure with two subplots
    fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(16, 8))

    # Generate title word cloud
    title_wordcloud = WordCloud(stopwords=stopwords, background_color='white', width=800, height=400).generate(titles_text)
    axs[0].imshow(title_wordcloud, interpolation='bilinear')
    axs[0].set_title('Title Word Cloud', fontsize=16)
    axs[0].axis('off')

    # Generate the article word cloud
    article_wordcloud = WordCloud(stopwords=stopwords, background_color='white', width=800, height=400).generate(all_articles_texts)
    axs[1].imshow(article_wordcloud, interpolation='bilinear')
    axs[1].set_title('Article Word Cloud', fontsize=16)
    axs[1].axis('off')

    # Save the visualization
    plt.savefig('/usr/local/airflow/visualizations/wordcloud.png', bbox_inches='tight')

def plot_avg_articles():

    # Calculate the average number of articles by nature
    avg_by_nature = df.groupby('nature')['articles'].apply(lambda x: sum(len(articles) for articles in x) / len(x)).reset_index(name='avg_num_articles')

    
    # plot the average number of articles by nature using a bar chart
    sns.set_style('darkgrid')
    sns.barplot(x=avg_by_nature['nature'], y=avg_by_nature['avg_num_articles'])
    plt.title('Average Number of Articles by Nature')
    plt.xlabel('Nature of Legal Text')
    plt.ylabel('Average Number of Articles')
    # Save the visualization
    plt.savefig('/usr/local/airflow/visualizations/avg_articles.png', bbox_inches='tight')


def create_visualizations():
    plot_nature_over_time()
    plot_wordcloud()  
    plot_avg_articles()

