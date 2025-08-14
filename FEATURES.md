# Audio Player MCP - Feature Implementation

## Implemented Features

### Core Playback Controls
- **Resume Playback** (`resume_playback`): Resume playback after it has been paused
- **Pause Playback** (`pause_playback`): Pause current playback
- **Next Song** (`next_song`): Play the next song in the playlist
- **Previous Song** (`previous_song`): Play the previous song in the playlist

### Skip Controls
- **Skip Forward** (`skip_forward`): Skip forward by specified seconds (default: 30s) - **Now fully functional with VLC!**
- **Skip Backward** (`skip_backward`): Skip backward by specified seconds (default: 10s) - **Now fully functional with VLC!**
- **Seek to Position** (`seek_to_position`): Jump to a specific time position in the track - **New VLC feature!**

### Additional Features
- **Set Volume** (`set_volume`): Set playback volume (0-10 scale)
- **Get Playback Status** (`get_playback_status`): Get current playback status including:
  - Current playing status (playing/paused/stopped)
  - Current file
  - Volume level
  - Playlist size
  - Current position in playlist
****  - Time position in current track
- **Search Songs** (`search_songs`): Fuzzy search for songs by name, artist, or partial matches across all subfolders
- **Search and Play** (`search_and_play`): Search for a song and automatically play the best match
- **List Folders** (`list_folders`): Show folder structure and file counts
- **Diagnose Audio System** (`diagnose_audio_system`): Check VLC capabilities and audio system status

### Enhanced State Management
- **Playlist Management**: Automatically maintains a playlist of all available audio files
- **Position Tracking**: Tracks current position in the playlist for next/previous functionality
- **Pause/Resume State**: Properly manages pause/resume state

## MCP Tools Available

1. `list_audio_files` - List available audio files
2. `play_audio` - Play a specific audio file
3. `stop_playback` - Stop playback
4. `pause_playback` - Pause current playback
5. `resume_playback` - Resume paused playback
6. `next_song` - Play next song in playlist
7. `previous_song` - Play previous song in playlist
8. `skip_forward` - Skip forward (default 30s, now with real seeking!)
9. `skip_backward` - Skip backward (default 10s, now with real seeking!)
10. `set_volume` - Set volume (0-10)
11. `get_playback_status` - Get current status
12. `search_songs` - Fuzzy search for songs by name/artist (across all subfolders)
13. `search_and_play` - Search and play best match
14. `list_folders` - Show folder structure and file counts  
15. `diagnose_audio_system` - Check VLC and audio system status
12. `seek_to_position` - Seek to specific time position

## Usage Examples

```python
# Basic playback
await play_audio("song.mp3", ctx)
await pause_playback(ctx)
await resume_playback(ctx)

# Playlist navigation
await next_song(ctx)
await previous_song(ctx)

# Skip controls
await skip_forward(ctx, 30)  # Skip 30 seconds forward
await skip_backward(ctx, 10)  # Skip 10 seconds backward

# Volume control
await set_volume(7, ctx)  # Set volume to 7/10

# Search functionality
await search_songs("calvin harris", ctx, 5)  # Find up to 5 matches across all folders
await search_and_play("outside ellie", ctx)  # Search and play best match

# Folder management
await list_folders(ctx)  # Show all folders with file counts

# Status check
status = await get_playback_status(ctx)

# Audio system diagnostics
diagnosis = await diagnose_audio_system(ctx)

# Seek to specific position
await seek_to_position(120, ctx)  # Jump to 2 minutes (120 seconds)
```

## Technical Notes

- Uses VLC media player for robust audio playback (upgraded from pygame.mixer)
- Full seeking support with skip forward/backward functionality
- **Fuzzy search**: Intelligent song searching using fuzzywuzzy library with multiple algorithms
- **Recursive folder scanning**: Searches through all subfolders automatically
- Automatically scans for multiple audio formats: MP3, WAV, OGG, FLAC, OPUS, M4A, AAC
- VLC provides excellent format compatibility and codec support
- Real-time playback position tracking
- Maintains playlist state across operations
- Proper error handling and logging
- MCP-compliant tool interface

## Limitations

- Requires VLC media player to be installed on the system
- Threading may be required for some advanced features in future versions
