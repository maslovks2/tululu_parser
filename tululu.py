import bs4
import requests
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def get_book_page_url(id):
    return f"http://tululu.org/b{id}"


def get_book_file_url(id):
    return f"http://tululu.org/txt.php?id={id}"


def get_html(url, params=None):
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.text


def save(output_path, response):
    dirname = os.path.dirname(output_path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(output_path, "wb") as file:
        file.write(response.content)


def get_author_and_title(soup):
    content_div = soup.find("div", {"id": "content"})
    if not content_div:
        raise requests.exceptions.HTTPError("Books not found")
    title, _, author = (
        content_div
        .find("h1")
        .text
        .split("\xa0")
    )
    return author.strip(), title.strip()


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError(
            f"Error. Request ({response.history[0].url}) was redirected."
        )


def compose_filename(id, filename, ext=".txt"):
    return f"{id}. {filename}{ext}"


def download_txt(url, filename, folder):
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


def download_books(ids, output_dir):
    for id in ids:
        try:
            html = get_html(get_book_page_url(id))
            soup = bs4.BeautifulSoup(html, "lxml")
            author, title = get_author_and_title(soup)
            download_txt(
                url=get_book_file_url(id),
                filename=compose_filename(id, title),
                folder=output_dir
            )
        except requests.HTTPError as e:
            print(e)


if __name__ == "__main__":
    # Примеры использования
    download_books(range(1, 11), "books/")
