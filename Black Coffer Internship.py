import gdown
import pandas as pd
import csv
import requests
from bs4 import BeautifulSoup
import os
from nltk.tokenize import word_tokenize,sent_tokenize
import string
import re

#Input File Download
file_id = 'https://docs.google.com/spreadsheets/d/1D7QkDHxUSKnQhR--q0BAwKMxQlUyoJTQ/edit?usp=drive_link&ouid=111828069938540720970&rtpof=true&sd=true'
list = file_id.split('/')
file_id = list[5]
output_file = 'input.xlsx'
if not os.path.exists(output_file):
    gdown.download(f'https://drive.google.com/uc?id={file_id}',output_file)

input = pd.read_excel('input.xlsx')

uri_id = input.iloc[:,0]
uri = input.iloc[:,1]

#Web Scraping Articles
folder_path='Text_Article'
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

error_id = []
for i in range(len(uri_id)):
    url = uri[i]
    url_id = uri_id[i]
    response = requests.get(url)
    title_text = ''
    body_text = ''

    if response.status_code == 200:
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')

        title = soup.find_all('h1', class_='entry-title')
        title_text = "\n".join([p.get_text() for p in title])

        body = soup.find_all('div', class_='td-post-content tagdiv-type')
        body_text = "\n".join([p.get_text() for p in body])
    else:
        error_id.append(url_id)
        print(f"Failed to retrieve the page {url_id}. Status code: {response.status_code}")

    article = title_text+"\n"+body_text
    filename=f'{url_id}.txt'
    file_path = os.path.join(folder_path, filename)
    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(article)

#Stop Words Download
stop_words_uri = ['https://drive.google.com/file/d/1mBOuggD8AVNFjr9sprLoD2_6mVWAgRGE/view?usp=drive_link','https://drive.google.com/file/d/1K-6MjPq5AQg4ICYY6PDfapB7JECUnryD/view?usp=drive_link', 'https://drive.google.com/file/d/13LXnH6vaJhvY4s2ai_2oW2qwongU_iAI/view?usp=drive_link', 'https://drive.google.com/file/d/1tTDfLXNPxNuUGZXHQkQhW6wPf4Xnivwr/view?usp=drive_link', 'https://drive.google.com/file/d/1PnZhcsfjBVxnzwa4N6MrLWf6Kuhhjpdk/view?usp=drive_link', 'https://drive.google.com/file/d/1RKxMOHzBdLrGuYb7MCJRTKKPwDG9Agbe/view?usp=drive_link', 'https://drive.google.com/file/d/1aWxyJI0d9MOk59OZ_unfBY5E-Nvg_ezW/view?usp=drive_link']
folder_path='Stop_words'
if not os.path.exists(folder_path):
    os.makedirs(folder_path)
n=[]
for i in range(len(stop_words_uri)):
    list = stop_words_uri[i].split('/')
    file_id = list[5]
    output_file = f'Stop_words\{i+1}.txt'
    if not os.path.exists(output_file):
        gdown.download(f'https://drive.google.com/uc?id={file_id}',output_file)

stop_token = []
for i in range(len(stop_words_uri)):
    stop_file = f'Stop_words/{i+1}.txt'
    with open(stop_file, 'r', encoding='latin-1') as file:
        text = file.read()
        text_token = word_tokenize(text)
        stop_token.append(text_token)
stop_word_list = [item for sublist in stop_token for item in sublist]
for i in string.punctuation:
    stop_word_list.append(i)

#Postive, Negative words Download
master_dict = ["https://drive.google.com/file/d/1seAj8G42SmfgUUx8lqVDJofm4Tuh2TOT/view?usp=drive_link","https://drive.google.com/file/d/1qqMwc_-ayS38HEOB97osO_nkIxRkbnvh/view?usp=drive_link"]
filename = ['Positive_words','Negative_words']
def file_download(list,filename):
    for i in range(len(list)):
        url = list[i].split('/')
        file_id = url[5]
        output_file = f'{filename[i]}.txt'
        if not os.path.exists(output_file):
            gdown.download(f'https://drive.google.com/uc?id={file_id}',output_file)
file_download(master_dict,filename)

with open('Positive_words.txt', 'r', encoding='latin-1') as file:
    pos_words = file.read()
with open('Negative_words.txt', 'r', encoding='latin-1') as file:
    neg_words = file.read()

#Function to calculate syllables
def count_syllables(word):
    word = word.lower()

    if word.endswith("es") or word.endswith("ed"):
        return 0

    vowels = ['a','e','i','o','u']
    count = 0
    prev_char_is_vowel = False

    for char in word:
        if char in vowels:
            if not prev_char_is_vowel:
                count += 1
            prev_char_is_vowel = True
        else:
            prev_char_is_vowel = False

    return count

#Functions to calculate Pronouns
def count_personal_pronouns(text):
    pronoun_pattern = re.compile(r'\b(?:I|we|my|ours|us)\b', re.IGNORECASE)
    country_pattern = re.compile(r'\bUS\b', re.IGNORECASE)
    pronoun_matches = [word for word in text if pronoun_pattern.match(word)]
    valid_pronoun_matches = [match for match in pronoun_matches if not (country_pattern.match(match) or match.lower() == 'i.e')]
    return len(valid_pronoun_matches)


#Sensitivity Analysis
output_list = [['URL_ID','URL','POSITIVE SCORE ','NEGATIVE SCORE ','POLARITY SCORE ','SUBJECTIVITY SCORE ','AVG SENTENCE LENGTH ','PERCENTAGE OF COMPLEX WORDS ','FOG INDEX ','AVG NUMBER OF WORDS PER SENTENCE ','COMPLEX WORD COUNT ','WORD COUNT ','SYLLABLE PER WORD ','PERSONAL PRONOUNS ','AVG WORD LENGTH ']]
for i in range(len(uri_id)):
    if uri_id[i] not in error_id:
        filename = f'Text_Article/{uri_id[i]}.txt'
        with open(filename, 'r', encoding='utf-8') as file:
            text = file.read()
            sent_token = sent_tokenize(text)
            sent_len = len(sent_token)
            word_token_before = [word_tokenize(sentence) for sentence in sent_token]
            word_token_before = [item for sublist in word_token_before for item in sublist]
            word_len_bef = len(word_token_before)
            word_token = [word for word in word_token_before if word.lower() not in stop_word_list]
            word_token_len = len(word_token)
            char_len = sum(len(word) for word in word_token)
            pos = 0
            pos_score = sum(1 for word in word_token if word.lower() in pos_words)
            pos = 0
            neg_score = sum(1 for word in word_token if word.lower() in neg_words)
            syllable_counts = [count_syllables(word) for word in word_token]
            complex_counts = sum(1 for i in syllable_counts if i>2)
            syllable_counts = sum(i for i in syllable_counts)
            try:
                avg_syllable = syllable_counts/word_token_len
            except ZeroDivisionError:
                avg_syllable = 0
            pronoun_count = count_personal_pronouns(word_token_before)
            pol_score = (pos_score-neg_score)/((pos_score+neg_score)+0.000001)
            sub_score = (pos_score+neg_score)/((word_token_len)+0.000001)
            try:
                avg_words = word_token_len/sent_len
            except ZeroDivisionError:
                avg_words = 0
            try:
                comp_words = complex_counts/word_token_len
            except ZeroDivisionError:
                comp_words = 0
            fog_index = 0.4*(avg_words+comp_words)
            try:
                avg_word_len = char_len/word_token_len
            except ZeroDivisionError:
                avg_word_len = 0
            output = [uri_id[i],uri[i],pos_score,neg_score,pol_score,sub_score,avg_words,comp_words,fog_index,avg_words,complex_counts,word_token_len,avg_syllable,pronoun_count,avg_word_len]
            output_list.append(output)
    else:
        output = [uri_id[i],uri[i],'error','error','error','error','error','error','error','error','error','error','error','error','error']
        output_list.append(output)
#Saving Output
file_path = "Output Data Structure.csv"

with open(file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(output_list)