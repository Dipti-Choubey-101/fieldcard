# Field Card

Tell it where you are and how long you have. A local open-weight model writes a one-page,
printable outing: what to bring, things to find, and a rule for the phone. Print it, put the
screen away, go. Everything runs on your laptop through Ollama: no account, no API key, no
internet needed after setup.

## Run (Windows)
1. Install [Python 3.11+](https://python.org) (tick **Add python.exe to PATH**).
2. Install [Ollama](https://ollama.com/download), then in PowerShell: `ollama pull gemma3:4b`
3. Double-click `run.bat`. Your browser opens at http://localhost:5001.

## Change it
- `MODEL` at the top of `app.py`: any model you have pulled with Ollama.
- `build_prompt()` in `app.py`: how the card is written.
- `CARD_SCHEMA` in `app.py`: the sections on the card.
