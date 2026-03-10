# 🦬 Bruno the Storytelling Bison
### Morning Star Elementary — Voice AI Demo

A fully local, kid-friendly voice AI demo where children give Bruno the Bison story ingredients and he creates a short 1-minute story, read aloud in the browser.

**No internet required after setup. No paid software. No API keys.**

---

## What It Does

1. Kids speak or type 3–4 story ingredients (a character, a place, a problem, something magical)
2. Bruno "thinks" with a bouncing animation
3. A short ~150-word story appears, tailored to their ingredients
4. Teacher presses **▶️ Play Story Aloud** when the class is ready
5. The browser reads the story in a natural voice

---

## Requirements

- macOS (M-series Mac recommended, M4 Pro is perfect)
- [Ollama](https://ollama.com) — already installed ✅
- Python 3 (comes with macOS)
- A modern browser (Chrome works best for voice input)

---

## Setup (One Time)

### 1. Make sure Ollama has the model

```bash
# You already have these — pick one:
ollama pull llama3.2      # recommended (faster, great for short stories)
# or
ollama pull llama3.1
```

If you want to change the model, edit line 16 of `server.py`:
```python
OLLAMA_MODEL = "llama3.2"   # change to "llama3.1" if preferred
```

### 2. (Optional) Install Whisper for microphone fallback

The app uses Chrome's built-in speech recognition by default — no install needed.

If you ever want the more accurate Whisper backend:
```bash
brew install whisper-cpp ffmpeg
mkdir -p ~/.whisper
# Download the small English model (~150MB):
curl -L https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin \
     -o ~/.whisper/ggml-base.en.bin
```

---

## Running the Demo

### Step 1 — Start Ollama
```bash
ollama serve
```
(Leave this terminal open, or it may already be running in the background)

### Step 2 — Start Bruno's server
Open a new terminal window, navigate to this folder, then:

```bash
cd /path/to/bison-storyteller
python3 server.py
```

You'll see:
```
🦬  Bruno the Storytelling Bison — Backend Server
==================================================
   Model  : llama3.2
   Ollama : http://localhost:11434/api/chat
   Port   : 5000
==================================================

🌐 Open your browser: http://localhost:5000
```

### Step 3 — Open the app
Go to **http://localhost:5000** in Chrome.

That's it! The app is fully self-contained.

---

## Demo Script (for the classroom)

1. **Introduce Bruno** — "This is Bruno, Morning Star's storytelling bison. He needs YOUR help!"
2. **Collect ingredients** — Call on 3-4 kids to give an ingredient each. They can click 🎤 to speak, or a helper can type.
3. **Hit the button** — "Bruno, Tell Us a Story!"
4. **Watch Bruno think** — He bounces around while the AI generates (usually 5-10 seconds)
5. **Press Play** — When the class settles, press the navy ▶️ Play Story Aloud button
6. **Listen** — The browser reads the story aloud

---

## Troubleshooting

| Problem | Fix |
|---|---|
| "Cannot reach Ollama" | Run `ollama serve` in a terminal |
| Voice input not working | Use Chrome; Safari doesn't support Web Speech API well |
| Story takes too long | Switch model to `llama3.2` (faster than 3.1 for short outputs) |
| No audio on Play | Check system volume; click elsewhere on page first (browser autoplay policy) |

---

## Customization

**Change the story style** — Edit the `SYSTEM_PROMPT` in `server.py`. You can make Bruno tell science facts, math adventures, history stories, etc.

**Change the model** — Edit `OLLAMA_MODEL` in `server.py`.

**School colors** — Currently set to navy (`#1a2e5a`) and gold (`#f5a800`). Edit the CSS variables at the top of `index.html` to match your exact brand colors.

**Add more ingredient fields** — Copy any `.ingredient-card` block in `index.html` and add a new `input5` field, then include it in the `generateStory()` JS function.

---

## Architecture

```
Browser (index.html)
    │
    │  POST /api/story  { ingredients: "..." }
    ▼
Python server (server.py) — http://localhost:5000
    │
    │  POST http://localhost:11434/api/chat
    ▼
Ollama (llama3.2) — fully local LLM
    │
    └─ Returns story text → browser TTS reads it aloud
```

Voice input uses the browser's built-in Web Speech API (Chrome).
A Whisper fallback endpoint (`/api/transcribe`) is included for future use.
