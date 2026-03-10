"""
Bruno the Storytelling Bison — Local Backend
Handles story generation via Ollama, and optional Whisper transcription.
Run with: python server.py
"""

import json
import subprocess
import tempfile
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import urlopen, Request
from urllib.error import URLError

# ─── Configuration ────────────────────────────────────────────────────────────

OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "llama3.2"   # Change to "llama3.1" if preferred

SYSTEM_PROMPT = """You are Bruno the Bison, the beloved mascot of Morning Star Elementary School.
You are a hilarious, over-the-top storyteller who makes kids burst out laughing.

When given story ingredients, you craft a SHORT, FUNNY story that:
- Is exactly 100-120 words long (about 45 seconds when read aloud at a normal pace)
- Is genuinely funny — use silly sound effects, ridiculous situations, unexpected twists, and goofy details
- Has a clear beginning, middle, and punchline-style ending that gets a laugh
- Uses simple language that kids ages 5-11 can follow and enjoy
- Incorporates ALL the ingredients the kids provided in the most absurd, creative way possible
- Avoids any scary, violent, or inappropriate content
- Ends with something surprising or ridiculous that will make the whole class groan and giggle

Respond with ONLY the story itself — no title, no preamble, no "Here's your story:" intro.
Start with a punchy, funny opening line that grabs attention immediately."""

PORT = 5001

# ─── Request Handler ──────────────────────────────────────────────────────────

class BrunoHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        print(f"  [{self.address_string()}] {format % args}")

    def send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self):
        """Serve the frontend."""
        if self.path in ("/", "/index.html"):
            self._serve_file("index.html", "text/html")
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        if self.path == "/api/story":
            self._handle_story(body)
        elif self.path == "/api/transcribe":
            self._handle_transcribe(body)
        else:
            self.send_response(404)
            self.end_headers()

    # ── Story Generation ──────────────────────────────────────────────

    def _handle_story(self, body):
        try:
            data = json.loads(body)
            ingredients = data.get("ingredients", "").strip()
            if not ingredients:
                self._send_json({"error": "No ingredients provided"}, 400)
                return

            print(f"\n🦬 Generating story for ingredients:\n{ingredients}\n")

            user_message = (
                f"Please create a fun adventure story using these ingredients that kids gave me:\n\n"
                f"{ingredients}\n\n"
                f"Remember: about 150-200 words, exciting, age-appropriate, and ends happily!"
            )

            payload = json.dumps({
                "model": OLLAMA_MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": user_message}
                ],
                "stream": False,
                "options": {
                    "temperature": 0.85,
                    "top_p": 0.9,
                    "num_predict": 400
                }
            }).encode()

            req = Request(OLLAMA_URL, data=payload,
                          headers={"Content-Type": "application/json"})

            try:
                with urlopen(req, timeout=60) as resp:
                    result = json.loads(resp.read())
            except URLError as e:
                print(f"❌ Ollama connection error: {e}")
                self._send_json({
                    "error": "Cannot reach Ollama. Is it running? Try: ollama serve"
                }, 503)
                return

            story = result.get("message", {}).get("content", "").strip()
            print(f"✅ Story generated ({len(story.split())} words)")
            self._send_json({"story": story})

        except Exception as e:
            print(f"❌ Story error: {e}")
            self._send_json({"error": str(e)}, 500)

    # ── Whisper Transcription (optional, for future use) ───────────────

    def _handle_transcribe(self, body):
        """
        Accepts raw audio bytes (webm) from the browser MediaRecorder,
        converts to 16kHz mono WAV with ffmpeg, then transcribes with
        the Homebrew whisper-cpp CLI. Fully offline — no internet needed.
        """
        tmp_path = None
        wav_path = None
        try:
            # Save incoming audio (webm from MediaRecorder)
            with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as f:
                f.write(body)
                tmp_path = f.name

            wav_path = tmp_path.replace(".webm", ".wav")

            # Convert to 16kHz mono WAV (required by whisper)
            ffmpeg = self._find_bin("ffmpeg")
            subprocess.run(
                [ffmpeg, "-y", "-i", tmp_path, "-ar", "16000", "-ac", "1", wav_path],
                capture_output=True, check=True
            )

            # Run whisper-cpp (Homebrew installs as 'whisper-cli')
            whisper = self._find_bin("whisper-cli")
            model   = os.path.expanduser("~/.whisper/ggml-base.en.bin")
            result  = subprocess.run(
                [whisper, "-m", model, "-f", wav_path, "-nt"],
                capture_output=True, text=True, timeout=30
            )

            # whisper-cpp prints transcript to stdout; strip timestamps/noise
            lines = [l.strip() for l in result.stdout.splitlines()
                     if l.strip() and not l.strip().startswith('[')]
            transcript = ' '.join(lines).strip()

            if not transcript:
                # fallback: try stderr (some builds print there)
                lines = [l.strip() for l in result.stderr.splitlines()
                         if l.strip() and not l.strip().startswith('[')
                         and not l.startswith('whisper')]
                transcript = ' '.join(lines).strip()

            print(f"🎤 Transcribed: {transcript!r}")
            self._send_json({"transcript": transcript})

        except FileNotFoundError as e:
            print(f"❌ Binary not found: {e}")
            self._send_json({
                "error": "whisper-cpp or ffmpeg not found. Run: brew install whisper-cpp ffmpeg"
            }, 503)
        except subprocess.CalledProcessError as e:
            print(f"❌ ffmpeg/whisper error: {e.stderr}")
            self._send_json({"error": "Audio conversion failed: " + str(e)}, 500)
        except Exception as e:
            print(f"❌ Transcribe error: {e}")
            self._send_json({"error": str(e)}, 500)
        finally:
            for p in [tmp_path, wav_path]:
                if p:
                    try: os.unlink(p)
                    except Exception: pass

    def _find_bin(self, name):
        """Find a binary, checking Homebrew paths on macOS."""
        import shutil
        path = shutil.which(name)
        if path:
            return path
        # Common Homebrew locations
        for prefix in ["/opt/homebrew/bin", "/usr/local/bin"]:
            candidate = os.path.join(prefix, name)
            if os.path.isfile(candidate):
                return candidate
        raise FileNotFoundError(f"{name} not found in PATH or Homebrew")

    # ── Helpers ───────────────────────────────────────────────────────

    def _serve_file(self, filename, content_type):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(script_dir, filename)
        try:
            with open(filepath, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type + "; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()

    def _send_json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(body)


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("🦬  Bruno the Storytelling Bison — Backend Server")
    print("=" * 50)
    print(f"   Model  : {OLLAMA_MODEL}")
    print(f"   Ollama : {OLLAMA_URL}")
    print(f"   Port   : {PORT}")
    print("=" * 50)
    print(f"\n🌐 Open your browser: http://localhost:{PORT}")
    print("   Press Ctrl+C to stop\n")

    server = HTTPServer(("localhost", PORT), BrunoHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Bruno is heading back to the prairie. Goodbye!")
