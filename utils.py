import os
import re
import sys

import music_tag
import torch
import torchaudio


def process_metadata(file_path: str, book_title: str, chapter_no: int, author: str):
    audio = music_tag.load_file(file_path)

    audio["album"] = book_title
    audio["tracknumber"] = chapter_no
    audio["artist"] = author
    audio["title"] = file_path[:-4]

    audio.save()
