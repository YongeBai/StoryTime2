#!/bin/bash

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e git+https://github.com/JarodMica/rvc.git#egg=rvc
pip install -e git+https://github.com/JarodMica/rvc-tts-pipeline.git#egg=rvc_tts_pipe

title="$1"
# author="$2"

# if [ -z "$author" ]; then
#     author="No Author"
# fi

# voice="$3"

python3 epub_to_text.py --title "$title"
python3 text_to_audiobook.py --title "$title"
# python3 text_to_audiobook.py --title "$title" --author "$author" --voice "$voice"

deactivate
