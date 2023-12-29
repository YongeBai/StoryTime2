import ebooklib
import os
from bs4 import BeautifulSoup
from ebooklib import epub
import re


# def epub2html(path: str) -> list:
#     book = ebooklib.epub.read_epub(path)
#     chapters = []
#     nav = None
#     for item in book.get_items():
#         if item.get_type() == ebooklib.ITEM_DOCUMENT:
#             chapters.append(item.get_content())
#         if item.get_type() == ebooklib.ITEM_NAVIGATION:
#             nav = item.get_content()

#     return nav


# def html2text(html: str) -> str:
#     soup = BeautifulSoup(html, "html.parser")
#     return soup.get_text()


def get_book_dir(path: str) -> str:
    return os.path.dirname(path)


# def extract_chapters(path: str) -> list:
#     chapters = epub2html(path)
#     book_dir = get_book_dir(path)

#     for i, chapter in enumerate(chapters):
#         chapter = html2text(chapter)

#         file_name = f'{book_dir}/chapter_{i}.txt'
#         with open(file_name, 'w') as f:
#             f.write(chapter)


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
