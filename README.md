
# Audio Player MCP Server

A comprehensive Model Context Protocol (MCP) server that allows Claude to control audio playback with advanced search, metadata extraction, and playback features.

## 🎵 Features

### Core Playback
- **Play Audio Files**: Supports MP3, FLAC, WAV, OGG formats
- **Advanced Playback Controls**: Play, pause, resume, stop, next, previous
- **Volume Control**: Set volume levels (0-10 scale)
- **Seek Controls**: Skip forward/backward by seconds, seek to specific positions
- **Playlist Management**: Automatic playlist creation and position tracking

### Enhanced Search
- **Metadata-Aware Search**: Search by artist name, song title, or filename
- **Fuzzy Search**: Find songs with partial matches and typos
- **Genre Search**: Browse music by genre with metadata extraction
- **Random Artist Selection**: Play random songs by specific artists
- **Popular Music Support**: Optimized for mainstream artists and songs
- **Priority Matching**: Metadata matches prioritized over filename matches

### Smart Features
- **Folder Navigation**: Browse music directory structure with file counts
- **Playback Status**: Real-time status including current position and track info
- **Audio System Diagnostics**: VLC capability checking and troubleshooting
- **Secure File Access**: Directory isolation for security

## 🎯 Supported Formats

- **MP3** - ID3 tag support for metadata
- **FLAC** - Native metadata support
- **WAV** - Basic playback support
- **OGG** - Vorbis comment support

## 📋 Requirements

- **Python 3.10+**
- **Claude Desktop** (latest version)
- **VLC Media Player** (for advanced playback features)
- **Audio Libraries**: `mutagen`, `python-vlc`, `fuzzywuzzy`

## 🚀 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Here-and-Tomorrow-LLC/audio-player-mcp.git
   cd audio-player-mcp
   ```

2. **Install the package:**
   ```bash
   pip install -e .
   ```

3. **Install VLC Media Player** (if not already installed):
   - **Windows**: Download from [VideoLAN](https://www.videolan.org/vlc/)
   - **Mac**: `brew install vlc` or download from VideoLAN
   - **Linux**: `sudo apt install vlc` (Ubuntu/Debian)

## ⚙️ Configuration

### Claude Desktop Setup

1. **Open Claude Desktop settings**: Navigate to `Developer > Edit Config`

2. **Locate configuration file**:
   - **Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

3. **Add configuration**:

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
           "AUDIO_PLAYER_DIR": "/path/to/your/music/directory"
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
         "command": "C:\\path\\to\\your\\venv\\Scripts\\python.exe",
         "args": [
           "C:\\path\\to\\your\\audio-player-mcp\\src\\audio_player_mcp\\player.py"
         ],
         "env": {
           "AUDIO_PLAYER_DIR": "C:\\path\\to\\your\\music\\directory"
         }
       }
     }
   }
   ```

4. **Restart Claude Desktop**

> **Note**: If `AUDIO_PLAYER_DIR` is not set, the server defaults to your system's Music folder.

## 🎼 Usage Examples

### Basic Playback
```
"Play some music"
"What songs do I have?"
"Stop the music"
"Pause playback"
"Resume playback"
"Next song"
"Previous song"
```

### Advanced Search
```
### Advanced Search

```
"Play Taylor Swift"               # Search by artist
"Play Blinding Lights"           # Search by song title
"Find songs by Drake"            # Artist search
"Play some pop music"            # Genre search
"Search for Shape of You"        # Title search
"Play a random Taylor Swift song" # Random song by artist
```
```

### Playback Controls
```
"Skip forward 30 seconds"
"Skip back 10 seconds"
"Set volume to 7"
"Seek to 2 minutes"
"What's playing?"
"Show playback status"
```

### Music Discovery
```
"Show me my folders"
"What genres do I have?"
"Browse my music collection"
"Diagnose audio system"
```

## 🛠️ Available MCP Tools

| Tool | Description |
|------|-------------|
| `list_audio_files` | List available audio files |
| `play_audio` | Play a specific audio file |
| `stop_playback` | Stop current playback |
| `pause_playback` | Pause current playback |
| `resume_playback` | Resume paused playback |
| `next_song` | Play next song in playlist |
| `previous_song` | Play previous song in playlist |
| `skip_forward` | Skip forward by specified seconds |
| `skip_backward` | Skip backward by specified seconds |
| `seek_to_position` | Seek to specific time position |
| `set_volume` | Set volume (0-10 scale) |
| `get_playback_status` | Get current playback status |
| `search_songs` | Search for songs by metadata/filename |
| `search_and_play` | Search and automatically play best match |
| `play_random_song_by_artist` | Play a random song by specified artist |
| `list_folders` | Show folder structure and file counts |
| `diagnose_audio_system` | Check VLC and audio system status |

## 🔍 Enhanced Search Features

### Metadata Extraction
- **Artist Information**: Extracts from TPE1, ARTIST, Artist tags
- **Title Information**: Extracts from TIT2, TITLE, Title tags
- **Genre Information**: Comprehensive genre detection
- **Multiple Formats**: Supports ID3, FLAC, OGG Vorbis metadata

### Search Algorithm
- **Priority Matching**: Metadata matches score higher than filename matches
- **Multiple Combinations**: Creates searchable text from "Artist - Title", "Title Artist", etc.
- **Fuzzy Matching**: Handles typos and partial matches
- **Score Weighting**: Returns best matches first

### Match Types
- `artist_title`: Exact "Artist - Title" match
- `metadata`: Title or artist metadata match
- `filename`: Filename match
- `*_fuzzy`: Fuzzy variants of above

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
./run_tests.sh

# Run specific test categories
python tests/test_popular_music.py      # Popular music search tests
python tests/test_metadata_search.py    # Metadata extraction tests
python tests/test_fuzzy_search.py       # Fuzzy search tests
python tests/test_genre_search.py       # Genre detection tests
python tests/test_vlc_playback.py       # VLC integration tests
```

### Test Results
The system demonstrates excellent performance:
- **Popular Artists**: 100% match rate
- **Popular Songs**: 100% match rate  
- **Popular Genres**: 88.9% match rate

## 🎤 Popular Music Support

The system is optimized for mainstream music and popular artists:

**Tested Artists**: Taylor Swift, Drake, Ariana Grande, Post Malone, Billie Eilish, The Weeknd, Ed Sheeran, Dua Lipa, Justin Bieber, Olivia Rodrigo

**Tested Songs**: "Blinding Lights", "Shape of You", "Bad Guy", "Thank U Next", "Circles", "Levitating", "Anti-Hero", and more

**Tested Genres**: Pop, Hip Hop/Rap, Rock, Electronic, Dance, R&B, Alternative, Country

## 🐛 Troubleshooting

### Check Claude Logs
- **Mac**: `tail -f ~/Library/Logs/Claude/mcp*.log`
- **Windows**: `type "%APPDATA%\Claude\logs\mcp*.log"`

### Common Issues

**VLC Not Found**:
```bash
# Install VLC
# Windows: Download from videolan.org
# Mac: brew install vlc
# Linux: sudo apt install vlc
```

**No Audio Files Found**:
- Check `AUDIO_PLAYER_DIR` path in configuration
- Ensure directory contains supported audio formats
- Verify file permissions

**Search Not Working**:
- Check metadata extraction with `diagnose_audio_system`
- Verify audio files have embedded metadata
- Try filename-based searches as fallback

## 🔧 Development

### Setup Development Environment
```bash
git clone https://github.com/Here-and-Tomorrow-LLC/audio-player-mcp.git
cd audio-player-mcp
pip install -e ".[dev]"
```

### Run in Development Mode
```bash
mcp dev src/audio_player_mcp/player.py
```

### Project Structure
```
audio-player-mcp/
├── src/audio_player_mcp/
│   ├── __init__.py
│   └── player.py              # Main MCP server
├── tests/                     # Comprehensive test suite
│   ├── test_popular_music.py  # Popular music tests
│   ├── test_metadata_search.py # Metadata extraction tests
│   ├── test_fuzzy_search.py   # Fuzzy search tests
│   ├── test_genre_search.py   # Genre detection tests
│   ├── test_vlc_playback.py   # VLC integration tests
│   ├── test_mcp_vlc.py        # MCP protocol tests
│   └── test_full_integration.py # Full integration tests
├── run_tests.sh              # Test automation script
├── pyproject.toml            # Project configuration
└── README.md                 # This file
```

## 📝 License

This project is licensed under the [MIT License](LICENSE).

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 🎼 Acknowledgments

- Based on the original [audio-player-mcp](https://github.com/Here-and-Tomorrow-LLC/audio-player-mcp) by Here-and-Tomorrow-LLC
- Built with the [Model Context Protocol (MCP)](https://github.com/modelcontextprotocol)
- Audio processing powered by [Mutagen](https://github.com/quodlibet/mutagen)
- Playback engine using [VLC Media Player](https://www.videolan.org/vlc/)
- Fuzzy search provided by [FuzzyWuzzy](https://github.com/seatgeek/fuzzywuzzy)
