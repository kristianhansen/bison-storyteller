# 🦬 Bruno the Storytelling Bison
### Morning Star Elementary — Voice AI Demo
<img width="960" height="808" alt="Screenshot 2026-03-10 at 12 02 15 AM" src="https://github.com/user-attachments/assets/67d917e3-72af-4a31-916c-ae33eda33c3e" />

<img width="800" height="802" alt="Screenshot 2026-03-10 at 12 30 24 AM" src="https://github.com/user-attachments/assets/d8746e29-0bf4-426d-bb8c-5c5f806b1a30" />


Kids give Bruno the Bison 4 story ingredients by speaking or typing. He thinks for a few seconds, then tells a short funny story (~45 seconds) read aloud in the browser. Run multiple rounds and watch the stories change every time.

**Fully local. No internet required after setup. No API keys. No paid software.**

---

## How It Works

```
Browser (index.html)
    │
    ├─ Voice input → MediaRecorder → POST /api/transcribe
    └─ Story request → POST /api/story
                              ▼
              Python server (server.py) :5001
                    │
                    ├─ /api/transcribe → whisper-cli (local speech-to-text)
                    └─ /api/story      → Ollama (local LLM)
                                                │
                                        Browser reads story aloud
                                        via built-in macOS TTS
```

---

## Requirements

- **macOS** with Apple Silicon (M1/M2/M3/M4 recommended)
- **Python 3** — comes pre-installed on macOS
- **Homebrew** — macOS package manager
- **Google Chrome** — for microphone and TTS support

---

## One-Time Setup

### 1. Install Homebrew (if not already installed)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Install Ollama
```bash
brew install ollama
```
Or download the Mac app directly from [ollama.com](https://ollama.com).

### 3. Pull a language model
```bash
ollama pull llama3.2
```
`llama3.2` (3B parameters) is fast and works great for short funny stories on Apple Silicon. You can also use `llama3.1` (8B) for slightly more creative output at the cost of a few extra seconds per story.

### 4. Install whisper-cli and ffmpeg (for offline voice input)
```bash
brew install whisper-cpp ffmpeg
```
Note: Homebrew installs the speech-to-text binary as `whisper-cli`.

### 5. Download the Whisper speech model (~140MB, one-time)
```bash
mkdir -p ~/.whisper
curl -L https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin \
     -o ~/.whisper/ggml-base.en.bin
```

### 6. Clone this repo
```bash
git clone https://github.com/kristianhansen/bison-storyteller.git
cd bison-storyteller
```

---

## Running the Demo

### Terminal 1 — Start Ollama
```bash
ollama serve
```
If you see `address already in use`, Ollama is already running in the background — skip this step.

### Terminal 2 — Start the server
```bash
cd bison-storyteller
python3 server.py
```

You should see:
```
🦬  Bruno the Storytelling Bison — Backend Server
==================================================
   Model  : llama3.2
   Ollama : http://localhost:11434/api/chat
   Port   : 5001
==================================================

🌐 Open your browser: http://localhost:5001
```

### Open Chrome and go to:
```
http://localhost:5001
```

---

## Demo Flow (for the classroom)

1. **Introduce Bruno** — "This is Bruno, Morning Star's storytelling bison. He needs YOUR help to make a story!"
2. **Step through 4 ingredients** — call on different kids for each one:
   - 🦸 A main character
   - 🌍 A place
   - ⚡ A problem or challenge
   - ✨ Something magical (optional)
3. **Speak or type** — hit the red **Speak Answer** button, the kid says their answer, it transcribes in the big display box
4. **Watch Bruno think** — he bounces around while the story generates (5–10 seconds)
5. **Settle the class, then press Play** — the navy ▶️ button reads the story aloud
6. **Run it again** — refresh the page (`Cmd+R`) for a fresh round with new ingredients

---

## Configuration

All settings are at the top of `server.py`:

| Setting | Default | Description |
|---|---|---|
| `OLLAMA_MODEL` | `llama3.2` | Swap to any model you've pulled with `ollama pull` |
| `PORT` | `5001` | Change if the port is already in use |
| `SYSTEM_PROMPT` | (see file) | Controls story tone, length, and style |

To change story length or tone, edit `SYSTEM_PROMPT` in `server.py`. For example, you could make Bruno tell science facts, rhyming poems, or spooky Halloween stories.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `Cannot reach Ollama` | Run `ollama serve` in a terminal |
| `Address already in use` on port 5001 | Change `PORT` in `server.py` to `5002` |
| Mic button not working | Allow microphone access in Chrome (click the lock icon in the address bar) |
| `whisper-cli not found` | Run `brew install whisper-cpp` — binary installs as `whisper-cli` |
| Whisper model not found | Run the `mkdir` + `curl` commands in Step 5 above |
| Story generates slowly | Make sure you're using `llama3.2` not a larger model |
| No audio on Play | Click anywhere on the page first, then press Play (browser autoplay policy) |

---

## Project Structure

```
bison-storyteller/
├── index.html    # Frontend — step-by-step ingredient UI, voice recording, TTS playback
├── server.py     # Backend — Python HTTP server, Ollama + Whisper integration
└── README.md     # This file
```

No pip installs required. Uses only Python's standard library plus Ollama, whisper-cli, and ffmpeg.
