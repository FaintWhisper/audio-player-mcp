
# Audio Player MCP Server

A Model Context Protocol (MCP) server that allows Claude to control audio playback on your computer.

## Features

- Play MP3, WAV, and OGG audio files.
- List available audio files in your music directory.
- Stop audio playback.
- Secure file access with directory isolation.

## Requirements

- Python 3.10 or higher.
- [Claude Desktop](https://claude.ai/download) (latest version).

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Here-and-Tomorrow-LLC/audio-player-mcp.git
   ```

2. Navigate to the repository directory:
   ```bash
   cd audio-player-mcp
   ```

3. Install the package in editable mode:
   ```bash
   pip install -e .
   ```

## Setup with Claude Desktop

1. Open Claude Desktop settings and navigate to:  
   `Developer > Edit Config`

2. Locate your configuration file:  
   - **Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

3. Add the following configuration based on your operating system:

   **Mac/Linux:**
   ```json
   {
     "mcpServers": {
       "audio-player": {
         "command": "/path/to/your/venv/bin/python",
         "args": [
           "/path/to/your/audio-player-mcp/src/audio_player_mcp/player.py"
         ],
         "env": {
           "AUDIO_PLAYER_DIR": "/path/to/your/audio/files"
         }
       }
     }
   }
   ```

   **Windows:**
   ```json
   {
     "mcpServers": {
       "audio-player": {
         "command": "C:\path\to\your\venv\Scripts\python.exe",
         "args": [
           "C:\path\to\your\audio-player-mcp\src\audio_player_mcp\player.py"
         ],
         "env": {
           "AUDIO_PLAYER_DIR": "C:\path\to\your\audio\files"
         }
       }
     }
   }
   ```

   **Note:** If `AUDIO_PLAYER_DIR` is not set, the server will default to using the `Music` folder in your home directory.

4. Restart Claude Desktop.

## Usage

You can now control audio playback by asking Claude:

- "What audio files do I have?"
- "Play song.mp3."
- "Stop the music."

## Troubleshooting

If something isn't working, check Claude's logs:

- **Mac:**
  ```bash
  tail -f ~/Library/Logs/Claude/mcp*.log
  ```

- **Windows:**
  ```bash
  type "%APPDATA%\Claude\logs\mcp*.log"
  ```

## Development

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/audio-player-mcp.git
   ```

2. Navigate to the repository directory:
   ```bash
   cd audio-player-mcp
   ```

3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

4. Run the MCP server in development mode:
   ```bash
   mcp dev src/audio_player_mcp/player.py
   ```

## License

This project is licensed under the [MIT License](LICENSE).
