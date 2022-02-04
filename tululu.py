import argparse
import requests
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin


TULULU_BASE_URL = "http://tululu.org"


def save(output_path, response):
    dirname = os.path.dirname(output_path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(output_path, "wb") as file:
        file.write(response.content)


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError(
            f"Error. Request ({response.history[0].url}) was redirected."
        )


def download_file(url, filename, folder):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    response = requests.get(url)
    check_for_redirect(response)
    sanitized_filename = sanitize_filename(filename)
    output_path = os.path.join(folder, sanitized_filename)
    save(output_path, response)
    return output_path


def download_txt(url, filename):
    output_folder = "books/"
    return download_file(url, filename, output_folder)


def download_image(url, filename):
    ouput_folder = 'images/'
    return download_file(url, filename, ouput_folder)


def compose_filename(id, filename='', ext=".txt"):
    if filename:
        composed_filename = f"{id}. {filename}{ext}"
    else:
        composed_filename = f"{id}{ext}"
    return composed_filename


def get_book_page_url(id):
    book_page_location = f"b{id}"
    return urljoin(TULULU_BASE_URL, book_page_location)


def add_meta(id, book_page):
    title = book_page["title"]
    book_page['book_url'] = urljoin(TULULU_BASE_URL, f"/txt.php?id={id}")
    book_page['book_filename'] = compose_filename(id, title)
    book_cover_location = book_page['book_cover_location']
    _, book_cover_extension = os.path.splitext(book_cover_location)
    book_page['cover_url'] = urljoin(TULULU_BASE_URL, book_cover_location)
    book_page['cover_filename'] = compose_filename(id, ext=book_cover_extension)


def parse_book_page(html):
    soup = BeautifulSoup(html, "lxml")
    content_div = soup.find("div", {"id": "content"})
    if not content_div:
        raise requests.exceptions.HTTPError("Books page found")
    title, _, author = (
        content_div
        .find("h1")
        .text
        .split("\xa0")
    )
    book_cover_location = (
        content_div.find("div", class_="bookimage").find("img")['src']
    )
    comments = [
        comment_div.find(class_="black").text
        for comment_div in soup.find_all("div", class_="texts")
    ]
    genres = [
        anchor_tag.text
        for anchor_tag in (
            content_div
            .find('span', class_='d_book')
            .find_all('a')
        )
    ]
    return {
        'author': author.strip(),
        'title': title.strip(),
        'book_cover_location': book_cover_location.strip(),
        'comments': comments,
        'genres': genres
    }


def get_html(url, params=None):
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.text


def download_books(ids):
    for id in ids:
        try:
            html = get_html(get_book_page_url(id))
            book_page = parse_book_page(html)
            add_meta(id, book_page)

            download_txt(book_page['book_url'], book_page['book_filename'])
            download_image(book_page['cover_url'], book_page['cover_filename'])
        except requests.HTTPError as e:
            print(f'Error occured while parsing id:{id}({e})')


def create_parser():
    parser = argparse.ArgumentParser(description="Script for parsing tululu.org book pages")
    parser.add_argument("start_id", type=int, default=1)
    parser.add_argument("end_id", type=int, default=10)
    return parser


def parse_args():
    parser = create_parser()
    args = parser.parse_args()
    assert args.end_id > args.start_id, "--end_id must be more than --start_id"
    return args


if __name__ == "__main__":
    arguments = parse_args()
    download_books(range(arguments.start_id, arguments.end_id + 1))
