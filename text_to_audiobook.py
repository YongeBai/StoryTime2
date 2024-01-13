import argparse
import os
import re

import music_tag
import scipy
import numpy as np
import torch
import pydub
from TTS.api import TTS

cuda = torch.cuda.is_available()
device = torch.device("cuda" if cuda else "cpu")
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=cuda)
# tts.to(device)


def clean_text(text: str, target_len: int = 200) -> list[str]:
    # remove double new line, redundant whitespace, convert non-ascii quotes to ascii quotes
    text = re.sub(r"\n\n+", r"\n", text)
    text = re.sub(r"\s+", r" ", text)
    text = re.sub(r"[“”]", '"', text)

    # split text into sentences, keep quotes together
    # sentences = re.split(r'(?<=[.!?;:—])\s+(?=(?:[^"]*"[^"]*")*[^"]*$)', text)
    sentences = re.split(r"(?<=[.!?;:—])", text)

    # recombine sentences into chunks of desired length
    chunks = []
    chunk = ""
    for sentence in sentences:
        if len(chunk) + len(sentence) > target_len:
            chunks.append(chunk)
            chunk = ""
        chunk += sentence + " "

    if chunk:
        chunks.append(chunk)

    # clean up chunks, remove leading/trailing whitespace, remove empty/only punctucation chunks
    chunks = [s.strip() for s in chunks]
    chunks = [s for s in chunks if s and not re.match(r"^[\s\.,;:!?]*$", s)]

    return chunks


def read_chapter(text_path: str, audio_path: str, voice_prompt_file: str):
    with open(text_path, "r", encoding="utf-8") as f:
        text = " ".join([l for l in f.readlines()])

        cleaned_text = clean_text(text)

        all_audio = []
        for i, text in enumerate(cleaned_text[:2]):
            # no clue how to combine the raw ints into one file properly, its making the voice higher pitch when im just using scipy to combine them    
            # hacky solution is to save each chunk as a separate file and then combine them
            tts.tts_to_file(
                text=text,
                language="en",
                speaker_wav=voice_prompt_file,
                split_sentences=False,
                file_path=f"{i}.wav",
            )
            all_audio.append(pydub.AudioSegment.from_wav(f"{i}.wav"))

    combined_audio = all_audio[0]
    for audio in all_audio[1:]:
        combined_audio += audio

    combined_audio.export(audio_path, format="wav")

    for i in range(len(all_audio)):
        os.remove(f"{i}.wav")


def process_metadata(audio_path: str, book_title: str, chapter_no: int):
    audio = music_tag.load_file(audio_path)

    audio["album"] = book_title
    audio["tracknumber"] = chapter_no
    # audio["artist"] = author
    audio["title"] = audio_path[:-4]

    audio.save()


def main(book_title: str, path_to_text_files: str, path_to_audio_files, voice_prompt_file: str):
    chapter_num = 1
    files = os.listdir(path_to_text_files)
    files.sort(
        key=lambda file_name: os.path.getmtime(
            os.path.join(path_to_text_files, file_name)
        )
    )

    for file in files[:3]:
        chapter_name_ext = os.path.basename(file)
        chapter_name = os.path.splitext(chapter_name_ext)[0]

        text_path = os.path.join(path_to_text_files, f"{chapter_name}.txt")
        audio_path = os.path.join(path_to_audio_files, f"{chapter_name}.wav")

        # read chapter
        read_chapter(text_path, audio_path, voice_prompt_file)

        # rvc

        # process metadata
        process_metadata(audio_path, book_title, chapter_num)

        print(f"Done Processing Chapter {chapter_name}")
        chapter_num += 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", type=str, required=True, default=None)
    # parser.add_argument("--author", type=str, default=None)
    parser.add_argument("--voice", type=str, default="lex_fridman")

    args = parser.parse_args()

    book_title = args.title
    # AUTHOR = args.author
    voice = args.voice

    path_to_text_files = os.path.join(os.getcwd(), "books", book_title, "chapters_text")
    path_to_audio_files = os.path.join(
        os.getcwd(), "books", book_title, "chapters_audio"
    )
    if not os.path.exists(path_to_audio_files):
        os.makedirs(path_to_audio_files)

    path_to_voices = os.path.join(os.getcwd(), "voices")
    voice_prompt_file = os.path.join(path_to_voices, f"{voice}.wav")

    main(book_title, path_to_text_files, path_to_audio_files, voice_prompt_file)
