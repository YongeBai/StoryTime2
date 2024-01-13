import os
import torch
from TTS.api import TTS
from argparse import ArgumentParser

# from utils import process_metadata


cuda = torch.cuda.is_available()
device = torch.device("cuda" if cuda else "cpu")
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=cuda)
# tts.to(device)


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
    parser = ArgumentParser()
    parser.add_argument("--title", type=str, required=True, default=None)
    # parser.add_argument("--author", type=str, default=None)
    parser.add_argument("--voice", type=str, default="lex_fridman")
    
    args = parser.parse_args()

    BOOK_TITLE = args.title
    # AUTHOR = args.author
    VOICE = args.narrator

    PATH_TO_TXT_FILES = os.path.join(os.getcwd(), "books", BOOK_TITLE, "chapters_text")
    PATH_TO_AUDIO_FILES = os.path.join(os.getcwd(), "books", BOOK_TITLE, "chapters_audio")
    PATH_TO_VOICES = os.path.join(os.getcwd(), "voices")
    voice_prompt_file = os.path.join(PATH_TO_VOICES, f"{VOICE}.wav")

    main(voice_prompt_file)
