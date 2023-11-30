import os
import re

from bs4 import BeautifulSoup
import requests
from psycopg2 import sql

from db_conn import cursor, conn

values =[]

url = "https://scholar.google.com/scholar?start=0&q=электрозарядные+станции&hl=ru&as_sdt=0,5"

page = requests.get(url)

soup = BeautifulSoup(page.text, "html.parser")

pages = soup.find_all('a', class_='gs_nma')
print('Google')
for page in pages:
    url = f"https://scholar.google.com/scholar?start={int(page.text)*10-10}&q=электрозарядные+станции&hl=ru&as_sdt=0,5"

    page_soap = requests.get(url)

    soup = BeautifulSoup(page_soap.text, "html.parser")
    status = int(page.text)*10-10 < len(pages)/2
    for article in soup.find_all('div', class_='gs_ri'):
        info = BeautifulSoup(article.text, "html.parser")
        # print(article)
        author_block = article.find('div', class_='gs_a')
        author = (author_block.text[:author_block.text.find("-")])[:author_block.text.find("…")]
        title_block = article.find('a')
        title = title_block.text[:title_block.text.find("…")]
        # print(title)
        print(title_block.get('href'))
        # if title_block.get('href').find('https://cyberleninka.ru/')>=0:
        #     elibrary_req = requests.get(title_block.get('href'))
        #     elibrary_soup = BeautifulSoup(elibrary_req.text, "html.parser")
        #     print(elibrary_soup.text)
        values.append((title,
                       author,
                       title_block.get('href'),
                       '',
                       '',
                       status))

habr = 'https://habr.com/ru/search/?q=ЭЗС&target_type=posts&order=relevance'

page_habr = requests.get(habr)

# Самое время воспользоваться BeautifulSoup4 и скормить ему наш page,
# указав в кавычках как он нам поможет 'html.parcer':
soup_habr = BeautifulSoup(page_habr.text, "html.parser")

# пегинация
pages_habr= soup_habr.find_all('a', class_="tm-pagination__page")
new_pages_habr = [1]
print('HABR')
for page_habr in pages_habr:
    new_pages_habr.append(int(page_habr.text))
page_mid=int((new_pages_habr[len(new_pages_habr)-2]+1)/2)
for page_habr in new_pages_habr:
    new_link = f"https://habr.com/ru/search/page{page_habr}/?q=ЭЗС&target_type=posts"
    new_page_habr = requests.get(new_link)
    new_soup_habr = BeautifulSoup(new_page_habr.text, "html.parser")
    # Теперь воспользуемся функцией поиска в BeautifulSoup4:
    # Список всех статей из поиска
    for link in new_soup_habr.find_all('a', attrs={'href': re.compile(r"news\/[0-9]+\/$")}):
        page_url = 'https://habr.com' + link.get('href')
        page_article = requests.get(page_url)
        page_soup = BeautifulSoup(page_article.text, "html.parser")

        # Автор
        author = page_soup.find('a', class_='tm-user-info__username').text
        # Заголовок
        title = page_soup.find('h1', class_='tm-title tm-title_h1').text
        print(title)
        # Текст
        text = page_soup.find('div', class_='article-formatted-body').text
        # Теги
        tags = ''
        status = page_habr <= page_mid
        tags_soup = page_soup.findAll('a', class_='tm-tags-list__link')
        for tag_soup in tags_soup:
            tags = tags + ' ' + tag_soup.text
        values.append( (title,
                        author,
                       '',
                    text,
                    tags,
                        status))

vc = 'https://vc.ru/search/v2/content/new?query=ЭЗС'
page_vc = requests.get(vc)
soup_vc = BeautifulSoup(page_vc.text, "html.parser")
pages = soup_vc.find_all('div', class_='content-feed')
page_mid = int(len(pages)/2)
print('VC',int(len(pages)/2) )
i = 0
for page in pages:
    title = page.find('div', class_='content-title').text
    print(title)
    tags = page.find('div', class_='content-header-author__name').text
    try:
        author = page.find('a', class_='content-header-author__name').text
    except:
        author = ''
    link = page.find('a', class_='content-link')
    article_req = requests.get(link['href'])
    article_soap = BeautifulSoup(article_req.text, "html.parser")
    anotation = ''
    text = ''
    status = i < page_mid
    print(status)
    i = i+1
    texts_block = article_soap.findAll('div', class_='l-island-a')
    for text_bloc in texts_block:
        if text_bloc.find('p') is not None:
            if anotation == '':
                anotation = text_bloc.find('p').text
            else:
                text = text + text_bloc.find('p').text
    values.append((re.sub(r"( +){2,}", '', title),
                   re.sub(r"( +){2,}", '', author),
                   re.sub(r"( +){2,}", '', anotation),
                   re.sub(r"( +){2,}", '', text),
                   re.sub(r"( +){2,}", '', tags),
                   status))
with conn.cursor() as cursor:
    conn.autocommit = True

    insert = sql.SQL('insert into articles (title, authors, anatation, text, tags, status) VALUES {}').format(
        sql.SQL(',').join(map(sql.Literal, values)))
    cursor.execute(insert)
