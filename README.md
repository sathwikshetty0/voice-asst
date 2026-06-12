# Voice Assistant (VAI)

A browser-based voice assistant that lets you have natural spoken conversations with an AI. You speak into your mic, the AI thinks and responds in text, then reads the response back to you out loud.

## How It Works

1. **Speech-to-Text** — Uses the browser's built-in Web Speech API to capture your voice and convert it to text.
2. **AI Response** — Sends your message to NVIDIA's hosted Llama 3.3 70B model via streaming API for fast, natural replies.
3. **Text-to-Speech** — Speaks the AI's response back using the browser's Speech Synthesis API with sentence-level chunking to avoid Chrome's silent-failure bug.

All processing happens client-side except for the LLM call, which is proxied through a lightweight Python server to avoid CORS issues.

## Features

- 🎙️ **Voice Input** — Click-to-talk with real-time transcription feedback
- ⚡ **Streaming Responses** — Tokens appear live as the model generates them
- 🔊 **Voice Output** — AI reads responses aloud with sentence-level chunking (no silent failures)
- 💬 **Conversation Memory** — Keeps context of the last 20 messages
- 🎨 **Dark UI** — Clean, modern dark interface with smooth animations
- ⚙️ **Settings Panel** — Save your API key in localStorage (no server storage)
- 🚀 **Zero Dependencies** — No npm, no build step, no frameworks — just Python + a browser

## AI Model

| Property | Details |
|----------|---------|
| **Model** | Meta Llama 3.3 70B Instruct |
| **Provider** | NVIDIA AI (NIM) |
| **Endpoint** | `https://integrate.api.nvidia.com/v1/chat/completions` |
| **Parameters** | temperature: 0.8, top_p: 0.9, max_tokens: 512 |
| **Streaming** | Yes — Server-Sent Events (SSE) for real-time token delivery |
| **Context** | Maintains last 20 messages for conversational memory |

### Why Llama 3.3 70B?

- High-quality conversational responses with natural tone
- Fast inference via NVIDIA's hosted NIM infrastructure
- Supports streaming for low-latency feel (tokens arrive as they're generated)
- Free tier available on NVIDIA's platform for development

### System Prompt

The model is configured as a warm, emotionally intelligent voice companion:
- Speaks naturally like a real human (not robotic)
- Keeps responses to 2-4 sentences (ideal for voice)
- Matches the user's emotional tone
- Avoids bullet points unless explicitly asked
- Prioritizes natural spoken language

## Tech Stack

- **Frontend**: Vanilla HTML/CSS/JavaScript (no build step, no frameworks)
- **Backend**: Python 3 standard library only (`http.server`, `urllib.request`)
- **LLM**: Meta Llama 3.3 70B Instruct via NVIDIA NIM API (streaming SSE)
- **Speech-to-Text**: Web Speech API (`SpeechRecognition` / `webkitSpeechRecognition`)
- **Text-to-Speech**: Web Speech API (`SpeechSynthesis`) with sentence chunking
- **Proxy**: Python `http.server` forwards requests to NVIDIA to bypass browser CORS restrictions

## Prerequisites

- **Python 3.7+** installed on your machine
- **Chrome or Edge** browser (required for Web Speech API support)
- **NVIDIA API Key** from [NVIDIA AI](https://build.nvidia.com/)

## Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/YOUR_USERNAME/vai.git
   cd vai
   ```

2. **Add your NVIDIA API key**

   You can either:
   - Edit the `NVIDIA_API_KEY` constant directly in `index.html`
   - Or enter it in the Settings panel (gear icon) once the app is running — it saves to localStorage

3. **Start the server**

   ```bash
   python server.py
   ```

   The server starts at `http://127.0.0.1:3000` by default.

4. **Open in browser**

   Navigate to [http://127.0.0.1:3000](http://127.0.0.1:3000) in Chrome or Edge.

## Usage

1. Click the microphone button (or wait for "Ready" status)
2. Speak naturally — you'll see a live transcript as you talk
3. Pause when done — the assistant will process your message
4. The AI response streams in live, then is spoken aloud
5. Once speaking finishes, you can click the mic again for the next turn

## Configuration

| Option | Location | Description |
|--------|----------|-------------|
| `PORT` | Environment variable | Server port (default: `3000`) |
| NVIDIA API Key | Settings panel or `index.html` | Required for AI responses |

To change the port:

```bash
set PORT=8080
python server.py
```

## Project Structure

```
vai/
├── index.html    # Complete frontend (HTML + CSS + JS in one file)
├── server.py     # Python proxy server (serves static files + proxies NVIDIA API)
└── README.md     # This file
```

## Architecture

```
Browser (Chrome/Edge)
  ├── SpeechRecognition API → captures voice → text
  ├── fetch() POST /api/nvidia → streams AI response
  └── SpeechSynthesis API → reads response aloud

Python Server (server.py)
  ├── GET / → serves index.html
  └── POST /api/nvidia → proxies to NVIDIA API (avoids CORS)
```

## Browser Compatibility

| Browser | Speech Input | Speech Output | Status |
|---------|-------------|---------------|--------|
| Chrome (Desktop) | ✅ | ✅ | Fully supported |
| Edge (Desktop) | ✅ | ✅ | Fully supported |
| Firefox | ❌ | ✅ | No speech input |
| Safari | ⚠️ | ✅ | Partial support |

## Troubleshooting

- **"Microphone permission denied"** — Allow mic access when the browser prompts, or check site permissions in browser settings.
- **Stuck on "Thinking"** — Check your NVIDIA API key is valid. Open browser DevTools (F12) → Console for error details.
- **No voice output** — Make sure your system volume is up and no other app has exclusive audio. Try refreshing the page.
- **CORS errors** — Make sure you're accessing via `http://127.0.0.1:3000`, not by opening the HTML file directly.

## License

MIT
