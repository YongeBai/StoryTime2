import os
import torch

from utils import process_metadata


BOOK_TITLE = "Example"
AUTHOR = "Example"
PATH_TO_TXT_FILES = os.path.join(os.getcwd(), "books", BOOK_TITLE, "chapters_text")


def main():
    chapter_num = 1
    files = os.listdir(PATH_TO_TXT_FILES)
    files.sort(
        key=lambda file_name: os.path.getmtime(
            os.path.join(PATH_TO_TXT_FILES, file_name)
        )
    )

    for file in files:
        full_path = os.path.join(PATH_TO_TXT_FILES, file)

        # read chapter

        # rvc

        # process metadata
        process_metadata(full_path, BOOK_TITLE, chapter_num, AUTHOR)
        chapter_num += 1


if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    main()
