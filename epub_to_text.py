import argparse
import os
import re
import shutil

import ebooklib
from bs4 import BeautifulSoup
from ebooklib import epub


def get_epub_content(path: str) -> list[str]:
    book = ebooklib.epub.read_epub(path)
    items = []
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            items.append(item.get_content())

    return items


def extract_chapters(book_path_folder, book_path):
    # create folder for chapters text
    if not os.path.exists(f"{book_path_folder}/chapters_text"):
        os.makedirs(f"{book_path_folder}/chapters_text")
        items = get_epub_content(book_path)

        for item in items:
            soup = BeautifulSoup(item, "xml")

            chapter_div = soup.find("div", {"class": "chapter"})
            if not chapter_div:
                continue

            h2_tag = chapter_div.find("h2")
            if not h2_tag:
                continue

            chapter_name = h2_tag.get_text().strip(".")

            file_name = os.path.join(
                book_path_folder, "chapters_text", f"{chapter_name}.txt"
            )

            text = [para.get_text() for para in soup.find_all("p")]
            text = "\n".join(text)

            with open(file_name, "w", encoding="utf-8") as f:
                f.write(chapter_name + ",\n")
                f.write(text)

        print("Done Extracting Chapters")
    else:
        print("Chapters already extracted")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", type=str, required=True)
    args = parser.parse_args()

    book_title = args.title
    epub_path = f"{book_title}.epub"

    book_path_folder = os.path.join(
        os.getcwd(),
        "books",
        book_title,
    )
    if not os.path.exists(book_path_folder):
        os.makedirs(book_path_folder)
        shutil.move(epub_path, book_path_folder)

    book_path = os.path.join(book_path_folder, epub_path)

    extract_chapters(book_path_folder, book_path)


if __name__ == "__main__":
    main()
