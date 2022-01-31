import requests
from bs4 import BeautifulSoup


def get_html(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def get_post_title(soup):
    title_tag = soup.find('main').find('header').find('h1')
    title_text = title_tag.text
    return title_text


def get_img_url(soup):
    return soup.find('img', class_='attachment-post-image')['src']


def get_post_text(soup):
    post_content = soup.find('div', class_="entry-content")
    elements_texts = []
    for html_element in post_content.find_all(['p', 'h3'], recursive=True):
        elements_texts.append(html_element.text)
    return '\n'.join(elements_texts)


if __name__ == '__main__':
    post_url = 'https://www.franksonnenbergonline.com/blog/are-you-grateful/'
    html = get_html(post_url)

    soup = BeautifulSoup(html, 'lxml')

    title_text = get_post_title(soup)
    img_url = get_img_url(soup)
    post_text = get_post_text(soup)

    print(title_text)
    print(img_url, end='\n\n')
    print(post_text)
