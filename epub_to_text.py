import argparse
import os
import re
import shutil

import ebooklib
from bs4 import BeautifulSoup
from ebooklib import epub


def get_book_dir(path: str) -> str:
    return os.path.dirname(path)


def get_epub_navigation(path: str) -> str:
    book = ebooklib.epub.read_epub(path)
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_NAVIGATION:
            return item.get_content().decode("utf-8")


def parse_navigation(nav: str) -> list:
    soup = BeautifulSoup(nav, "xml")
    nav_points = soup.find_all("navPoint")
    chapters_title_and_content = []
    for nav in nav_points:
        chapter_name_html = nav.find("text")
        chapter_name = re.search(r">(.*)<", str(chapter_name_html)).group(1)

        chapters_title_and_content.append(
            (chapter_name, nav.find("content").get("src"))
        )

    return chapters_title_and_content


def extract_chapter_html(chapter_xhtml: str, book: epub.EpubBook) -> str:
    href, fragment = chapter_xhtml.split("#")
    chapter_item = book.get_item_with_href(href)

    chapter_content = chapter_item.get_content().decode("utf-8")
    soup = BeautifulSoup(chapter_content, "xml")

    title = soup.find(id=fragment)
    paragraphs = title.find_next_siblings("p")

    text = " ".join([p.get_text() for p in paragraphs])
    return text


def extract_chapters(path: str):
    book = ebooklib.epub.read_epub(path)
    nav = get_epub_navigation(path)
    chapters = parse_navigation(nav)
    book_dir = os.path.dirname(path)

    for chapter_name, chapter_content_xhtml in chapters:
        text = extract_chapter_html(chapter_content_xhtml, book)

        os.makedirs(f"{book_dir}/chapters_text", exist_ok=True)
        file_name = f"{book_dir}/chapters_text/{chapter_name}.txt"

        with open(file_name, "w") as f:
            f.write(chapter_name + "\n")
            f.write(text)

    print("Done")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", type=str, required=True)
    args = parser.parse_args()

    book_title = args.title
    book_file = f"{book_title}.epub"
    book_path_folder = os.path.join(
        os.getcwd(),
        "books",
        book_title,
    )

    if not os.path.exists(book_path_folder):
        os.makedirs(book_path_folder)
    
    book_path = os.path.join(book_path_folder, book_file)
    shutil.move(book_file, book_path)
    
    extract_chapters(book_path)


if __name__ == "__main__":
    main()
