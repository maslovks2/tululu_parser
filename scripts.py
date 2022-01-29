import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import os


def save_file(url, output_path):
    response = requests.get(url)
    response.raise_for_status()

    with open(output_path, 'wb') as file:
        file.write(response.content)


def save_requests_log():
    img_url = "https://dvmn.org/media/Requests_Python_Logo.png"
    output_path = 'dvmb.svg'
    save_file(img_url, output_path)


def save_mars_book():
    book_url = "http://tululu.org/txt.php?id=32168"
    output_path = "mars_book.txt"
    save_file(book_url, output_path)


def disable_waringins():
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def download_books_from_tululu(ids):
    base_url = "http://tululu.org/txt.php"
    for id in ids:
        response = requests.get(base_url, params={'id': id})
        output_dir = 'books'
        os.makedirs(output_dir, exist_ok=True)

        file_path = os.path.join(output_dir, f'id_{id}')
        with open(file_path, 'wb') as file:
            file.write(response.content)


if __name__ == '__main__':
    disable_waringins()
    save_requests_log()
    save_mars_book()
    download_books_from_tululu(range(1, 11))
