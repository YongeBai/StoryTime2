import argparse
import os
from chapter_split import extract_chapters

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--book_path", type=str, required=True)
    args = parser.parse_args()

    book_path = args.book_path
    extract_chapters(book_path)

    book_name_ext = os.path.basename(book_path)
    book_name = os.path.splitext(book_name_ext)[0]

if __name__ == "__main__":
    main()