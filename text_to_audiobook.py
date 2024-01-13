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


def clean_text(text: str, target_len: int = 200, max_len: int = 250) -> list[str]:
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


def read_chapter(text_path: str, audio_path: str, voice_prompt_file: str) -> str:
    with open(text_path, "r", encoding="utf-8") as f:
        text = " ".join([l for l in f.readlines()][:100])

        cleaned_text = clean_text(text)

        all_audio = []
        for text in cleaned_text:
            audio = tts.tts(
                text=text,
                language="en",
                speaker_wav=voice_prompt_file,
                split_sentences=False,
            )
            all_audio.append(audio)

        full_audio = torch.cat(all_audio, dim=-1)
        torchaudio.save(f"{audio_path}.wav", full_audio)


def process_metadata(file_path: str, book_title: str, chapter_no: int):
    audio = music_tag.load_file(file_path)

    audio["album"] = book_title
    audio["tracknumber"] = chapter_no
    # audio["artist"] = author
    audio["title"] = file_path[:-4]

    audio.save()


def main(voice_prompt_file: str):
    chapter_num = 1
    files = os.listdir(path_to_text_files)
    files.sort(
        key=lambda file_name: os.path.getmtime(
            os.path.join(path_to_text_files, file_name)
        )
    )

    for file in files[:1]:
        text_path = os.path.join(path_to_text_files, file)
        audio_path = os.path.join(path_to_audio_files, file)

        # read chapter
        read_chapter(text_path, audio_path, voice_prompt_file)

        # rvc

        # process metadata
        # process_metadata(full_path, BOOK_TITLE, chapter_num)
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
    path_to_voices = os.path.join(os.getcwd(), "voices")
    voice_prompt_file = os.path.join(path_to_voices, f"{voice}.wav")

    main(voice_prompt_file)
