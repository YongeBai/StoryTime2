import argparse
import os
import re

import music_tag
import torch
import torchaudio
from TTS.api import TTS

cuda = torch.cuda.is_available()
device = torch.device("cuda" if cuda else "cpu")
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=cuda)
# tts.to(device)


def clean_text(text: str, target_len: int = 200, max_len: int = 300) -> list[str]:
    # remove double new line, redundant whitespace, convert non-ascii quotes to ascii quotes
    text = re.sub(r"\n\n+", r"\n", text)
    text = re.sub(r"\s+", r" ", text)
    text = re.sub(r"[“”]", '"', text)

    # split text into sentences, keep quotes together
    sentences = re.split(r'(?<=[.!?])\s+(?=(?:[^"]*"[^"]*")*[^"]*$)', text)

    # recombine sentences into chunks of desired length
    chunks = []
    chunk = ""
    for sentence in sentences:
        if len(chunk) + len(sentence) > target_len:
            chunks.append(chunk)
            chunk = ""
        chunk += sentence + " "
        if len(chunk) > max_len:
            chunks.append(chunk)
            chunk = ""
    if chunk:
        chunks.append(chunk)

    # clean up chunks, remove leading/trailing whitespace, remove empty/unless chunks
    chunks = [s.strip() for s in chunks]
    chunks = [s for s in chunks if s and not re.match(r"^[\s\.,;:!?]*$", s)]

    return chunks


def process_metadata(file_path: str, book_title: str, chapter_no: int, author: str):
    audio = music_tag.load_file(file_path)

    audio["album"] = book_title
    audio["tracknumber"] = chapter_no
    # audio["artist"] = author
    audio["title"] = file_path[:-4]

    audio.save()


def main(voice_prompt_file: str):
    chapter_num = 1
    files = os.listdir(PATH_TO_TXT_FILES)
    files.sort(
        key=lambda file_name: os.path.getmtime(
            os.path.join(PATH_TO_TXT_FILES, file_name)
        )
    )

    for file in files[:1]:
        text_path = os.path.join(PATH_TO_TXT_FILES, file)
        audio_path = os.path.join(PATH_TO_AUDIO_FILES, file)

        # read chapter
        with open(text_path, "r", encoding="utf-8") as f:
            text = " ".join([l for l in f.readlines()])
            # cleaned_text = clean_text(text)
            #decide between using ur clean text or pySDB's with split=True

            tts.tts_to_file(
                text=text,
                file_path=audio_path,
                speaker_wav=voice_prompt_file,
                language="en",
                split_sentences=True,
            )

        # rvc

        # process metadata
        # process_metadata(full_path, BOOK_TITLE, chapter_num, AUTHOR)
        # chapter_num += 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", type=str, required=True, default=None)
    # parser.add_argument("--author", type=str, default=None)
    parser.add_argument("--voice", type=str, default="lex_fridman")

    args = parser.parse_args()

    BOOK_TITLE = args.title
    # AUTHOR = args.author
    VOICE = args.narrator

    PATH_TO_TXT_FILES = os.path.join(os.getcwd(), "books", BOOK_TITLE, "chapters_text")
    PATH_TO_AUDIO_FILES = os.path.join(
        os.getcwd(), "books", BOOK_TITLE, "chapters_audio"
    )
    PATH_TO_VOICES = os.path.join(os.getcwd(), "voices")
    voice_prompt_file = os.path.join(PATH_TO_VOICES, f"{VOICE}.wav")

    main(voice_prompt_file)
