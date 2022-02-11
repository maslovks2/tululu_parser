import argparse
import requests
import os
import enum
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlencode, urlparse, urlunparse


TULULU_BASE_URL = "http://tululu.org"


class FileType(enum.Enum):
    BOOK = (2, "books/")
    IMAGE = (1, "images/")

    def __init__(self, id_, ouput_folder):
        self.id = id_
        self.output_folder = ouput_folder


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError(
            f"Error. Request ({response.history[0].url}) was redirected."
        )


def download_file(url, filename, file_type, url_params=None):
    response = requests.get(url, params=url_params)
    check_for_redirect(response)
    output_path = os.path.join(
        file_type.output_folder, 
        sanitize_filename(filename)
    )
    dirname = os.path.dirname(output_path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    if file_type == FileType.BOOK:
        with open(output_path, "w", encoding=response.encoding) as file:
            file.write(response.text)
    else:
        with open(output_path, "wb") as file:
            file.write(response.content)
    return output_path


def compose_filename(id_, filename='', ext=".txt"):
    return  f"{id_}. {filename}{ext}" if filename else f"{id_}{ext}"


def add_urls_and_filenames(book_id, book_page):
    title = book_page["title"]
    book_page['book_url'] = (
        urlunparse(
            urlparse(TULULU_BASE_URL)
            ._replace(
                path='txt.php',
                query=urlencode({'id': book_id})
            )
        )
    )
    book_page['book_filename'] = compose_filename(book_id, title)
    book_cover_location = book_page['book_cover_location']
    _, book_cover_extension = os.path.splitext(book_cover_location)
    book_page['cover_url'] = urljoin(TULULU_BASE_URL, book_cover_location)
    book_page['cover_filename'] = compose_filename(book_id, ext=book_cover_extension)


def parse_book_page(html):
    soup = BeautifulSoup(html, "lxml")
    content_div = soup.find("div", {"id": "content"})
    if not content_div:
        raise requests.exceptions.HTTPError("Books page not found")
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


def download_books(books_ids):
    for book_id in books_ids:
        try:
            book_page_url = urljoin(TULULU_BASE_URL, f"b{book_id}")
            response = requests.get(url)
            response.raise_for_status()
            html = response.text
            book_page = parse_book_page(html)
            add_urls_and_filenames(book_id, book_page)

            download_file(book_page['book_url'], book_page['book_filename'], file_type=FileType.BOOK)
            download_file(book_page['cover_url'], book_page['cover_filename'], file_type=FileType.IMAGE)
        except requests.HTTPError as e:
            print(f'Error occured while parsing id:{book_id}({e})')


def create_parser():
    parser = argparse.ArgumentParser(description="Script for parsing tululu.org book pages")
    parser.add_argument("start_id", type=int, default=1)
    parser.add_argument("end_id", type=int, default=10)
    return parser


def parse_args():
    parser = create_parser()
    args = parser.parse_args()
    assert args.end_id >= args.start_id, "--end_id must be more or equal than --start_id"
    return args


if __name__ == "__main__":
    arguments = parse_args()
    download_books(range(arguments.start_id, arguments.end_id + 1))
