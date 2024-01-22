# StoryTime: Ebooks to Audiobooks
Turn epub files into audiobooks.

### note: only works with linux and an nvidia GPU

# Setup
1. download rmvpe.pt from https://huggingface.co/lj1995/VoiceConversionWebUI/blob/main/rmvpe.pt 
2. download hubert_base.pt from https://huggingface.co/lj1995/VoiceConversionWebUI/blob/main/hubert_base.pt
3. add you .epub so that your files structure looks like this:
    
```
StoryTime2
└───voices
│   │   lex_fridman.pth
│   │   lex_fridman.wav
|   
│   README.md
|   epub_to_text.py
|   hubert_base.pt
|   YOUR_BOOK.epub
|   requirements.txt
|   rmvpe.pt
|   run.sh
|   text_to_audiobook.py
```

4. in the terminal run `chmod +x run.sh`
5. run `./run.sh YOUR_BOOK`

If it is your first time running you'll get a message from coqui asking you to accept terms and conditions

6. You'll get both a zipfile of all the chapters and the chapters themselves. I like to upload them to youtube music so I can listen on my phone offline, the metadata has been edited so that it keeps its ordering.