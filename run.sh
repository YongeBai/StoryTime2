#!/bin/bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

title="$1"

author="$2"
if [ -z "$author" ]; then
    author="No Author"
fi

voice="$3"

python3 epub_to_text.py "$title"
python3 text_to_audio.py "$title" "$author" "$voice"

deactivate
