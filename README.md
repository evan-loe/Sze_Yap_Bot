# Sze_Yap_bot

Sze Yap Bot is a dictionary bot which searches Stephen Li's Taishanese Dictionary and Gene Chin's Hoisanva English dictionary! 

Sze Yap Bot is feature rich with advanced searching for both english and chinese words and phrases. 
You can also join a voice channel to listen to audio from Stephen Li's dictionary and listen to taishanese words being read!

Features:

* Search english and chinese words in both Stephen Li and Gene Chin's dictionaries
* Intuitive and easy to use search navigation system
* Chinese character to pinyin
* Pronounciation audio
* Customizable welcome message with optional chinese title!

Sze Yap Bot is actively being developed so expect more features to come!

## Local run

To run the bot on your machine without using the production `/mnt` path, use the local runner and point it at a dev data directory:

```bash
python src/run_bot.py --data-dir ./dev-data
```

That will store `cogs/`, `synonyms/`, `orig_audio/`, `tones_audio/`, and `temp/` under `./dev-data` instead of `/mnt/data/szeyap-bot-files`.
