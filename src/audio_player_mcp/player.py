# MUST be at the very top of the file, before any other imports
import os
import sys

# Redirect stdout to stderr for anything that bypasses our controls
real_stdout = sys.stdout
sys.stdout = sys.stderr

# Now safe to import other modules
import logging
from mcp.server.fastmcp import FastMCP, Context
import vlc
import json
from pathlib import Path
import time
import threading
from fuzzywuzzy import fuzz, process
from mutagen import File as MutagenFile

# Configure logging to stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger("audio-player")

# Restore stdout for MCP protocol messages only
sys.stdout = real_stdout
sys.stdout.reconfigure(line_buffering=True)

# Initialize MCP server
mcp = FastMCP("audio-player")

# Update in player.py - handle both Windows and WSL paths
def _get_music_directory():
    """Get the correct music directory path for both Windows and WSL"""
    if 'AUDIO_PLAYER_DIR' in os.environ:
        return Path(os.environ['AUDIO_PLAYER_DIR'])
    
    # Check if we're running in WSL
    if os.path.exists('/mnt/c/Users'):
        # We're in WSL, use the Windows path via /mnt/c
        return Path('/mnt/c/Users/Amit/Music')
    else:
        # We're on Windows or other system, use standard paths
        windows_path = Path('C:/Users/Amit/Music')
        if windows_path.exists():
            return windows_path
        else:
            return Path(os.path.expanduser('~/Music'))

AUDIO_DIR = _get_music_directory()
logger.info(f"Using audio directory: {AUDIO_DIR}")

# Supported audio formats
# Note: pygame.mixer natively supports MP3, WAV, OGG
# FLAC, OPUS, M4A, AAC support depends on system codecs
SUPPORTED_FORMATS = {'.mp3', '.wav', '.ogg', '.flac', '.opus', '.m4a', '.aac'}

# Verify directory exists
if not AUDIO_DIR.exists():
    logger.warning(f"Audio directory does not exist: {AUDIO_DIR}")
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Created audio directory: {AUDIO_DIR}")

# Simple state management
class AudioState:
    def __init__(self):
        self.volume = 3
        self.playing = None
        self.paused = False
        self.playlist = []
        self.current_index = -1
        self.position = 0.0  # Track position in seconds
        self.vlc_instance = None
        self.media_player = None
        self._position_lock = threading.Lock()

    def init_vlc(self):
        """Initialize VLC if not already done"""
        if self.vlc_instance is None:
            # More robust VLC initialization for server environments
            vlc_args = [
                '--intf', 'dummy',  # No interface
                '--no-video',       # Audio only
                '--verbose', '1',   # Some logging for debugging
                '--aout', 'directsound',  # Windows audio output
                '--no-metadata-network-access',  # Don't try to fetch metadata
                '--no-lua',         # Disable lua
                '--no-stats',       # No statistics
                '--no-osd',         # No on-screen display
            ]
            
            try:
                self.vlc_instance = vlc.Instance(vlc_args)
                self.media_player = self.vlc_instance.media_player_new()
                self.media_player.audio_set_volume(int(self.volume * 10))  # VLC uses 0-100 scale
                logger.info("VLC initialized successfully for server environment")
            except Exception as e:
                logger.error(f"Failed to initialize VLC: {e}")
                # Fallback to minimal VLC instance
                try:
                    self.vlc_instance = vlc.Instance('--intf', 'dummy')
                    self.media_player = self.vlc_instance.media_player_new()
                    self.media_player.audio_set_volume(int(self.volume * 10))
                    logger.info("VLC initialized with fallback configuration")
                except Exception as e2:
                    logger.error(f"VLC fallback initialization also failed: {e2}")
                    raise e2

state = AudioState()

@mcp.resource("audio://files")
def audio_files_resource() -> str:
    """List available audio files from all subdirectories"""
    try:
        files = [
            {"name": filepath, "display_name": Path(filepath).name, "folder": str(Path(filepath).parent) if Path(filepath).parent != Path('.') else "root"}
            for filepath in _get_audio_files()
        ]
        logger.info(f"Found {len(files)} audio files across all subdirectories")
        return json.dumps({"files": files})
    except Exception as e:
        logger.error(f"Error listing audio files: {e}")
        raise


@mcp.tool()
async def list_audio_files(ctx: Context) -> dict:
    """List all available audio files in the audio directory"""
    logger.info("Listing audio files via tool")
    try:
        files = _get_audio_files()
        
        # Create detailed file information
        file_details = []
        for filepath in files:
            path_obj = Path(filepath)
            file_details.append({
                "path": filepath,
                "name": path_obj.name,
                "folder": str(path_obj.parent) if path_obj.parent != Path('.') else "root",
                "extension": path_obj.suffix.lower()
            })
        
        # Log the results
        logger.info(f"Found {len(files)} audio files across all subdirectories")
        ctx.info(f"Retrieved {len(files)} audio files from all folders")
        
        return {
            "status": "success",
            "files": file_details,
            "count": len(files),
            "base_directory": str(AUDIO_DIR)
        }
        
    except Exception as e:
        error_msg = f"Error listing audio files: {str(e)}"
        logger.error(error_msg)
        ctx.error(error_msg)
        raise

@mcp.tool()
async def list_folders(ctx: Context) -> dict:
    """List all folders containing audio files with file counts"""
    logger.info("Listing audio folders and file counts")
    
    try:
        files = _get_audio_files()
        
        # Group files by folder
        folder_stats = {}
        for filepath in files:
            folder = str(Path(filepath).parent) if Path(filepath).parent != Path('.') else "root"
            if folder not in folder_stats:
                folder_stats[folder] = {"count": 0, "files": []}
            folder_stats[folder]["count"] += 1
            folder_stats[folder]["files"].append(Path(filepath).name)
        
        # Create summary
        folder_list = []
        for folder, stats in folder_stats.items():
            folder_list.append({
                "folder": folder,
                "file_count": stats["count"],
                "sample_files": stats["files"][:3]  # Show first 3 files as examples
            })
        
        # Sort by folder name
        folder_list.sort(key=lambda x: x["folder"])
        
        logger.info(f"Found {len(folder_list)} folders with audio files")
        ctx.info(f"Found {len(folder_list)} folders containing audio files")
        
        return {
            "status": "success",
            "folders": folder_list,
            "total_folders": len(folder_list),
            "total_files": len(files),
            "base_directory": str(AUDIO_DIR)
        }
        
    except Exception as e:
        error_msg = f"Error listing folders: {str(e)}"
        logger.error(error_msg)
        ctx.error(error_msg)
        raise

def _normalize_music_terms(text: str) -> str:
    """Normalize common music terminology for better matching"""
    # Convert to lowercase for processing
    text = text.lower()
    
    # Music terminology normalization
    replacements = {
        r'\bfeat\b': 'featuring',  # feat -> featuring
        r'\bft\b': 'featuring',    # ft -> featuring  
        r'\bw/\b': 'with',         # w/ -> with
        r'\bvs\b': 'versus',       # vs -> versus
        r'\bfeaturing\b': 'featuring',  # normalize case
        r'\bremix\b': 'remix',     # normalize case
        r'\bedit\b': 'edit',       # normalize case
        r'\bmix\b': 'mix',         # normalize case
        r'\boriginal\b': 'original', # normalize case
        r'\bextended\b': 'extended', # normalize case
        r'\bofficial\b': 'official', # normalize case
    }
    
    import re
    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text)
    
    return text

def _preprocess_music_query(query: str) -> str:
    """Preprocess search query for better music matching"""
    # Normalize the query using the same rules as file names
    normalized = _normalize_music_terms(query)
    
    # Handle common search patterns
    normalized = normalized.strip()
    
    return normalized

def _create_search_data_for_file(file_path: str) -> dict:
    """Create comprehensive search data for a file including metadata and filename"""
    try:
        # Convert relative path to absolute path for metadata extraction
        absolute_path = AUDIO_DIR / file_path
        
        # Extract metadata
        title, artist = _extract_title_and_artist(str(absolute_path))
        
        # Get filename without extension
        filename_stem = Path(file_path).stem
        
        # Create searchable text combinations
        search_texts = []
        
        # 1. Title and Artist from metadata (highest priority)
        if title and artist:
            search_texts.append(f"{artist} - {title}")
            search_texts.append(f"{title} {artist}")
            search_texts.append(title)
            search_texts.append(artist)
        elif title:
            search_texts.append(title)
        elif artist:
            search_texts.append(artist)
        
        # 2. Filename (cleaned and normalized)
        clean_filename = filename_stem.replace('_', ' ').replace('-', ' ').replace('.', ' ')
        normalized_filename = _normalize_music_terms(clean_filename)
        search_texts.append(normalized_filename)
        search_texts.append(clean_filename)
        
        # 3. Raw filename stem
        search_texts.append(filename_stem)
        
        return {
            "file_path": file_path,
            "title": title,
            "artist": artist,
            "filename": filename_stem,
            "search_texts": search_texts
        }
        
    except Exception as e:
        logger.debug(f"Error creating search data for {file_path}: {e}")
        # Fallback to filename only
        filename_stem = Path(file_path).stem
        clean_filename = filename_stem.replace('_', ' ').replace('-', ' ').replace('.', ' ')
        return {
            "file_path": file_path,
            "title": "",
            "artist": "",
            "filename": filename_stem,
            "search_texts": [clean_filename, filename_stem]
        }

def _enhanced_metadata_search(files: list, query: str, limit: int = 10) -> list:
    """Enhanced search that considers title, artist metadata and filename"""
    if not query.strip():
        return []
    
    logger.info(f"Performing enhanced metadata search for: '{query}'")
    
    # Create search data for all files
    search_data = []
    for file_path in files:
        search_data.append(_create_search_data_for_file(file_path))
    
    query_lower = query.lower().strip()
    normalized_query = _preprocess_music_query(query)
    
    # Score matches with different priorities
    scored_matches = []
    
    for data in search_data:
        max_score = 0
        best_match_text = ""
        match_type = ""
        
        # Check each search text for this file
        for i, search_text in enumerate(data["search_texts"]):
            search_text_lower = search_text.lower()
            
            # Priority weights (metadata gets higher priority than filename)
            if i == 0 and data["title"] and data["artist"]:  # "Artist - Title"
                weight = 1.0
                match_type = "artist_title"
            elif i <= 3 and (data["title"] or data["artist"]):  # Other metadata combinations
                weight = 0.9
                match_type = "metadata"
            else:  # Filename-based
                weight = 0.7
                match_type = "filename"
            
            # Exact match (highest priority)
            if query_lower == search_text_lower:
                score = 100 * weight
            # Exact phrase match
            elif query_lower in search_text_lower:
                score = 95 * weight
            # Fuzzy match
            else:
                # Use token sort ratio for better matching of reordered words
                fuzzy_score = fuzz.token_sort_ratio(normalized_query, search_text)
                score = fuzzy_score * weight
            
            if score > max_score:
                max_score = score
                best_match_text = search_text
                if score >= 95:  # Keep the high-priority match type for exact/phrase matches
                    match_type = match_type
                else:
                    match_type = f"{match_type}_fuzzy"
        
        if max_score >= 30:  # Minimum threshold
            scored_matches.append({
                "file_path": data["file_path"],
                "score": max_score,
                "match_text": best_match_text,
                "match_type": match_type,
                "title": data["title"],
                "artist": data["artist"],
                "filename": data["filename"]
            })
    
    # Sort by score (descending) and return top matches
    scored_matches.sort(key=lambda x: x["score"], reverse=True)
    return scored_matches[:limit]

def _enhanced_music_search(candidates: list, query: str, limit: int = 10) -> list:
    """Enhanced search specifically designed for music files"""
    normalized_query = _preprocess_music_query(query)
    
    # Try exact word matching first for music terms
    music_terms = ['featuring', 'feat', 'remix', 'edit', 'mix', 'original', 'extended', 'official']
    query_lower = query.lower().strip()
    
    exact_matches = []
    partial_matches = []
    
    # If query is a music term, prioritize exact matches
    if query_lower in music_terms or any(term in query_lower for term in music_terms):
        for i, candidate in enumerate(candidates):
            candidate_lower = candidate.lower()
            # Exact word boundary match gets highest priority
            if query_lower in candidate_lower:
                # Check if it's a word boundary match
                import re
                if re.search(rf'\b{re.escape(query_lower)}\b', candidate_lower):
                    exact_matches.append((candidate, 95, i))
                else:
                    partial_matches.append((candidate, 85, i))
    
    # Regular fuzzy matching for remaining candidates
    remaining_candidates = [c for i, c in enumerate(candidates) 
                          if i not in [match[2] for match in exact_matches + partial_matches]]
    
    if remaining_candidates:
        fuzzy_matches = process.extract(normalized_query, remaining_candidates, 
                                      scorer=fuzz.token_sort_ratio, limit=limit)
        fuzzy_results = [(match, score, candidates.index(match)) for match, score in fuzzy_matches]
    else:
        fuzzy_results = []
    
    # Combine all matches and sort by score
    all_matches = exact_matches + partial_matches + fuzzy_results
    all_matches.sort(key=lambda x: x[1], reverse=True)
    
    return all_matches[:limit]

def _extract_title_and_artist(file_path: str) -> tuple[str, str]:
    """Extract title and artist information from audio file metadata"""
    try:
        audio_file = MutagenFile(file_path)
        if audio_file is None:
            return "", ""
        
        title = ""
        artist = ""
        
        # Try different approaches based on file type
        if hasattr(audio_file, 'tags') and audio_file.tags:
            tags = audio_file.tags
            
            # For MP3 files with ID3 tags
            if hasattr(tags, 'get'):
                # Try various ID3 title tag formats
                for title_key in ['TIT2', 'TITLE', 'Title']:
                    if title_key in tags:
                        title_value = tags[title_key]
                        if hasattr(title_value, 'text') and title_value.text:
                            title = str(title_value.text[0])
                            break
                        elif isinstance(title_value, list) and len(title_value) > 0:
                            title = str(title_value[0])
                            break
                
                # Try various ID3 artist tag formats
                for artist_key in ['TPE1', 'ARTIST', 'Artist']:
                    if artist_key in tags:
                        artist_value = tags[artist_key]
                        if hasattr(artist_value, 'text') and artist_value.text:
                            artist = str(artist_value.text[0])
                            break
                        elif isinstance(artist_value, list) and len(artist_value) > 0:
                            artist = str(artist_value[0])
                            break
        
        # For FLAC, OGG, and other formats - try common field names
        if not title and hasattr(audio_file, 'get'):
            for title_key in ['TITLE', 'title', 'Title']:
                if title_key in audio_file:
                    title_value = audio_file[title_key]
                    if isinstance(title_value, list) and len(title_value) > 0:
                        title = str(title_value[0])
                        break
                    elif isinstance(title_value, str):
                        title = title_value
                        break
        
        if not artist and hasattr(audio_file, 'get'):
            for artist_key in ['ARTIST', 'artist', 'Artist']:
                if artist_key in audio_file:
                    artist_value = audio_file[artist_key]
                    if isinstance(artist_value, list) and len(artist_value) > 0:
                        artist = str(artist_value[0])
                        break
                    elif isinstance(artist_value, str):
                        artist = artist_value
                        break
        
        # Alternative approach: direct dictionary access
        if not title:
            for title_key in ['TITLE', 'title', 'Title', 'TIT2']:
                try:
                    if title_key in audio_file:
                        title_value = audio_file[title_key]
                        if isinstance(title_value, list) and len(title_value) > 0:
                            title = str(title_value[0])
                            break
                        elif isinstance(title_value, str):
                            title = title_value
                            break
                except Exception:
                    continue
        
        if not artist:
            for artist_key in ['ARTIST', 'artist', 'Artist', 'TPE1']:
                try:
                    if artist_key in audio_file:
                        artist_value = audio_file[artist_key]
                        if isinstance(artist_value, list) and len(artist_value) > 0:
                            artist = str(artist_value[0])
                            break
                        elif isinstance(artist_value, str):
                            artist = artist_value
                            break
                except Exception:
                    continue
        
        # Clean up the strings
        if title:
            title = title.strip()
        if artist:
            artist = artist.strip()
        
        return title, artist
        
    except Exception as e:
        logger.debug(f"Could not extract title/artist from {file_path}: {e}")
        return "", ""

def _extract_genre_from_file(file_path: str) -> str:
    """Extract genre information from audio file metadata"""
    try:
        audio_file = MutagenFile(file_path)
        if audio_file is None:
            return "Unknown"
        
        # Debug: Let's see what tags are available
        # logger.debug(f"Available tags for {file_path}: {list(audio_file.keys())}")
        
        genre = None
        
        # Try different approaches based on file type
        if hasattr(audio_file, 'tags') and audio_file.tags:
            tags = audio_file.tags
            
            # For MP3 files with ID3 tags
            if hasattr(tags, 'get'):
                # Try various ID3 genre tag formats
                for genre_key in ['TCON', 'TCO', 'TIT1']:  # TCON is standard, TCO is old format
                    if genre_key in tags:
                        genre_value = tags[genre_key]
                        if hasattr(genre_value, 'text') and genre_value.text:
                            genre = str(genre_value.text[0])
                            break
                        elif isinstance(genre_value, list) and len(genre_value) > 0:
                            genre = str(genre_value[0])
                            break
        
        # For FLAC, OGG, and other formats - try common genre field names
        if not genre and hasattr(audio_file, 'get'):
            for genre_key in ['GENRE', 'genre', 'Genre']:
                if genre_key in audio_file:
                    genre_value = audio_file[genre_key]
                    if isinstance(genre_value, list) and len(genre_value) > 0:
                        genre = str(genre_value[0])
                        break
                    elif isinstance(genre_value, str):
                        genre = genre_value
                        break
        
        # Alternative approach: direct dictionary access
        if not genre:
            # Try direct access to the audio file as dict
            for genre_key in ['GENRE', 'genre', 'Genre', 'TCON']:
                try:
                    if genre_key in audio_file:
                        genre_value = audio_file[genre_key]
                        if isinstance(genre_value, list) and len(genre_value) > 0:
                            genre = str(genre_value[0])
                            break
                        elif isinstance(genre_value, str):
                            genre = genre_value
                            break
                except Exception:
                    continue
        
        # Clean up the genre string
        if genre:
            genre = genre.strip()
            # Remove ID3v1 genre numbers (e.g., "(13)" or "(13)Pop")
            import re
            genre = re.sub(r'^\(\d+\)', '', genre).strip()
            if genre.startswith('(') and genre.endswith(')'):
                genre = genre[1:-1]
            # Capitalize properly
            if genre:
                genre = genre.title()
                return genre if genre else "Unknown"
        
        return "Unknown"
        
    except Exception as e:
        logger.debug(f"Could not extract genre from {file_path}: {e}")
        return "Unknown"

def _get_all_genres() -> dict:
    """Get all unique genres from the music collection with file counts"""
    files = _get_audio_files()
    genre_counts = {}
    
    logger.info(f"Extracting genres from {len(files)} files...")
    
    for file_path in files:
        # Convert relative path to absolute path
        absolute_path = AUDIO_DIR / file_path
        genre = _extract_genre_from_file(str(absolute_path))
        if genre in genre_counts:
            genre_counts[genre] += 1
        else:
            genre_counts[genre] = 1
    
    return genre_counts

def _search_by_genre(genre_query: str, limit: int = 20) -> list:
    """Search for songs by genre"""
    files = _get_audio_files()
    matching_files = []
    
    genre_query_lower = genre_query.lower().strip()
    
    for file_path in files:
        # Convert relative path to absolute path
        absolute_path = AUDIO_DIR / file_path
        file_genre = _extract_genre_from_file(str(absolute_path))
        if file_genre.lower() == genre_query_lower or genre_query_lower in file_genre.lower():
            matching_files.append({
                "file": file_path,
                "name": Path(file_path).name,
                "folder": str(Path(file_path).parent) if Path(file_path).parent != Path('.') else "root",
                "genre": file_genre
            })
            
            if len(matching_files) >= limit:
                break
    
    return matching_files

@mcp.tool()
async def search_songs(query: str, ctx: Context, limit: int = 10) -> dict:
    """Search for songs using fuzzy matching"""
    logger.info(f"Searching for songs with query: '{query}'")
    
    try:
        # Get all available audio files
        files = _get_audio_files()
        
        if not files:
            return {
                "status": "no_files",
                "message": "No audio files found in directory",
                "matches": []
            }
        
        # Perform fuzzy search
        if not query.strip():
            # If empty query, return first 'limit' files
            matches = [
                {
                    "file": f, 
                    "name": Path(f).name,
                    "folder": str(Path(f).parent) if Path(f).parent != Path('.') else "root",
                    "score": 100, 
                    "match_type": "all"
                } for f in files[:limit]
            ]
        else:
            # Use enhanced metadata search that considers title, artist and filename
            search_results = _enhanced_metadata_search(files, query, limit)
            
            # Convert results to our format
            matches = []
            for result in search_results:
                # Create display info with metadata when available
                display_name = Path(result["file_path"]).name
                if result["title"] and result["artist"]:
                    display_info = f"{result['artist']} - {result['title']}"
                elif result["title"]:
                    display_info = result["title"]
                elif result["artist"]:
                    display_info = result["artist"]
                else:
                    display_info = display_name
                
                matches.append({
                    "file": result["file_path"],
                    "name": display_name,
                    "folder": str(Path(result["file_path"]).parent) if Path(result["file_path"]).parent != Path('.') else "root",
                    "score": round(result["score"], 1),
                    "match_type": result["match_type"],
                    "matched_text": result["match_text"],
                    "display_info": display_info,
                    "title": result["title"],
                    "artist": result["artist"]
                })
        
        logger.info(f"Found {len(matches)} matches for query '{query}'")
        ctx.info(f"Found {len(matches)} matching songs")
        
        return {
            "status": "success",
            "query": query,
            "matches": matches,
            "total_files_searched": len(files)
        }
        
    except Exception as e:
        error_msg = f"Error searching songs: {str(e)}"
        logger.error(error_msg)
        ctx.error(error_msg)
        raise

@mcp.tool()
async def search_and_play(query: str, ctx: Context) -> dict:
    """Search for a song and play the best match"""
    logger.info(f"Searching and playing best match for: '{query}'")
    
    try:
        # First, search for songs
        search_result = await search_songs(query, ctx, limit=1)
        
        if search_result["status"] != "success" or not search_result["matches"]:
            return {
                "status": "no_matches",
                "message": f"No songs found matching '{query}'",
                "query": query
            }
        
        # Get the best match
        best_match = search_result["matches"][0]
        filename = best_match["file"]
        score = best_match["score"]
        
        # Play the best match
        play_result = await play_audio(filename, ctx)
        
        # Combine results
        return {
            "status": "search_and_play_success",
            "query": query,
            "matched_file": filename,
            "match_score": score,
            "match_type": best_match["match_type"],
            "play_result": play_result
        }
        
    except Exception as e:
        error_msg = f"Error in search and play: {str(e)}"
        logger.error(error_msg)
        ctx.error(error_msg)
        raise

@mcp.tool()
async def play_audio(filename: str, ctx: Context) -> dict:
    """Play an audio file"""
    logger.info(f"Attempting to play: {filename}")
    
    # Handle both relative paths (from subdirectories) and just filenames
    if "/" in filename or "\\" in filename or Path(filename).is_absolute():
        # This looks like a path (relative or absolute)
        file_path = AUDIO_DIR / filename
    else:
        # This is just a filename, try to find it in the directory tree
        all_files = _get_audio_files()
        matching_files = [f for f in all_files if Path(f).name == filename]
        
        if not matching_files:
            raise FileNotFoundError(f"Audio file not found: {filename}")
        elif len(matching_files) > 1:
            # Multiple files with same name, use the first one but warn
            logger.warning(f"Multiple files named '{filename}' found, using: {matching_files[0]}")
            ctx.info(f"Multiple files found, playing: {matching_files[0]}")
        
        file_path = AUDIO_DIR / matching_files[0]
    
    try:
        # Validate file exists and is within audio directory
        if not file_path.exists():
            raise FileNotFoundError(f"Audio file not found: {filename}")
        if not str(file_path.resolve()).startswith(str(AUDIO_DIR.resolve())):
            raise ValueError("File must be in the audio directory")
        
        # Initialize VLC if needed
        state.init_vlc()
        logger.info("VLC audio system ready")
        ctx.info("VLC audio system ready")
        
        # Stop any current playback
        if state.playing and state.media_player.is_playing():
            state.media_player.stop()
            ctx.info("Stopped previous playback")
        
        # Load and play
        ctx.info(f"Loading audio file: {filename}")
        try:
            media = state.vlc_instance.media_new(str(file_path))
            state.media_player.set_media(media)
            logger.info(f"Media loaded successfully: {file_path}")
        except Exception as e:
            raise Exception(f"Failed to load audio file: {e}")
        
        # Set volume and play
        state.media_player.audio_set_volume(int(state.volume * 10))  # VLC uses 0-100 scale
        logger.info(f"Volume set to {int(state.volume * 10)}/100")
        
        # Start playback
        play_result = state.media_player.play()
        logger.info(f"VLC play() returned: {play_result}")
        
        # Wait a moment for playback to start and verify
        time.sleep(0.5)
        
        # Check if playback actually started
        is_playing = state.media_player.is_playing()
        player_state = state.media_player.get_state()
        logger.info(f"Is playing: {is_playing}, Player state: {player_state}")
        
        if not is_playing and player_state not in [vlc.State.Playing, vlc.State.Opening]:
            # Try to get more detailed error information
            error_msg = f"VLC failed to start playback. State: {player_state}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        # Update state
        state.playing = filename
        state.paused = False
        _update_playlist()  # Update playlist and current index
        
        logger.info(f"Playing {filename} at volume {state.volume}/10")
        ctx.info(f"Started playback: {filename}")
        
        return {
            "status": "playing",
            "file": filename,
            "volume": state.volume,
            "vlc_state": str(player_state),
            "is_playing": is_playing
        }
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Playback error: {error_msg}")
        ctx.error(error_msg)
        raise

@mcp.tool()
def stop_playback(ctx: Context) -> dict:
    """Stop playback"""
    try:
        if state.media_player is None:
            msg = "Audio system not initialized"
            logger.warning(msg)
            return {"status": "not_initialized", "message": msg}
        
        try:
            state.media_player.stop()
        except Exception as e:
            raise Exception(f"Failed to stop playback: {e}")
        
        state.playing = None
        state.paused = False
        
        msg = "Playback stopped"
        logger.info(msg)
        ctx.info(msg)
        return {"status": "stopped"}
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Stop error: {error_msg}")
        ctx.error(error_msg)
        raise

@mcp.tool()
async def pause_playback(ctx: Context) -> dict:
    """Pause current playback"""
    try:
        if state.media_player is None:
            msg = "Audio system not initialized"
            logger.warning(msg)
            return {"status": "not_initialized", "message": msg}
        
        if not state.playing:
            msg = "No audio currently playing"
            logger.info(msg)
            return {"status": "not_playing", "message": msg}
        
        if state.paused:
            msg = "Audio already paused"
            logger.info(msg)
            return {"status": "already_paused", "message": msg}
        
        state.media_player.pause()
        state.paused = True
        
        msg = "Playback paused"
        logger.info(msg)
        ctx.info(msg)
        return {"status": "paused", "file": state.playing}
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Pause error: {error_msg}")
        ctx.error(error_msg)
        raise

@mcp.tool()
async def resume_playback(ctx: Context) -> dict:
    """Resume paused playback"""
    try:
        if state.media_player is None:
            msg = "Audio system not initialized"
            logger.warning(msg)
            return {"status": "not_initialized", "message": msg}
        
        if not state.playing:
            msg = "No audio to resume"
            logger.info(msg)
            return {"status": "no_audio", "message": msg}
        
        if not state.paused:
            msg = "Audio is not paused"
            logger.info(msg)
            return {"status": "not_paused", "message": msg}
        
        state.media_player.play()
        state.paused = False
        
        msg = f"Resumed playback: {state.playing}"
        logger.info(msg)
        ctx.info(msg)
        return {"status": "resumed", "file": state.playing}
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Resume error: {error_msg}")
        ctx.error(error_msg)
        raise

def _get_audio_files() -> list:
    """Helper function to get available audio files recursively from all subfolders"""
    audio_files = []
    
    def scan_directory(directory: Path, base_path: Path):
        """Recursively scan directory for audio files"""
        try:
            for item in directory.iterdir():
                if item.is_file() and item.suffix.lower() in SUPPORTED_FORMATS:
                    # Store relative path from base audio directory for better organization
                    relative_path = item.relative_to(base_path)
                    audio_files.append(str(relative_path))
                elif item.is_dir():
                    # Recursively scan subdirectories
                    scan_directory(item, base_path)
        except PermissionError:
            # Skip directories we don't have permission to read
            logger.warning(f"Permission denied accessing directory: {directory}")
        except Exception as e:
            logger.warning(f"Error scanning directory {directory}: {e}")
    
    try:
        scan_directory(AUDIO_DIR, AUDIO_DIR)
        logger.info(f"Found {len(audio_files)} audio files across all subdirectories")
    except Exception as e:
        logger.error(f"Error scanning audio directory: {e}")
    
    return audio_files

def _update_playlist():
    """Update the playlist with all available audio files"""
    state.playlist = _get_audio_files()
    if state.playing and state.playing in state.playlist:
        state.current_index = state.playlist.index(state.playing)
    else:
        state.current_index = -1

@mcp.tool()
async def next_song(ctx: Context) -> dict:
    """Play the next song in the playlist"""
    try:
        _update_playlist()
        
        if not state.playlist:
            msg = "No audio files available"
            logger.info(msg)
            return {"status": "no_files", "message": msg}
        
        if state.current_index == -1:
            # Start from the beginning if no current song
            next_index = 0
        else:
            next_index = (state.current_index + 1) % len(state.playlist)
        
        next_filename = state.playlist[next_index]
        
        # Use the existing play_audio function
        await play_audio(next_filename, ctx)
        state.current_index = next_index
        
        msg = f"Playing next song: {next_filename}"
        logger.info(msg)
        ctx.info(msg)
        return {
            "status": "next_song",
            "file": next_filename,
            "position": f"{next_index + 1}/{len(state.playlist)}"
        }
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Next song error: {error_msg}")
        ctx.error(error_msg)
        raise

@mcp.tool()
async def previous_song(ctx: Context) -> dict:
    """Play the previous song in the playlist"""
    try:
        _update_playlist()
        
        if not state.playlist:
            msg = "No audio files available"
            logger.info(msg)
            return {"status": "no_files", "message": msg}
        
        if state.current_index == -1:
            # Start from the end if no current song
            prev_index = len(state.playlist) - 1
        else:
            prev_index = (state.current_index - 1) % len(state.playlist)
        
        prev_filename = state.playlist[prev_index]
        
        # Use the existing play_audio function
        await play_audio(prev_filename, ctx)
        state.current_index = prev_index
        
        msg = f"Playing previous song: {prev_filename}"
        logger.info(msg)
        ctx.info(msg)
        return {
            "status": "previous_song",
            "file": prev_filename,
            "position": f"{prev_index + 1}/{len(state.playlist)}"
        }
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Previous song error: {error_msg}")
        ctx.error(error_msg)
        raise

@mcp.tool()
async def skip_forward(ctx: Context, seconds: int = 30) -> dict:
    """Skip forward by specified seconds (default 30)"""
    try:
        if state.media_player is None:
            msg = "Audio system not initialized"
            logger.warning(msg)
            return {"status": "not_initialized", "message": msg}
        
        if not state.playing:
            msg = "No audio currently playing"
            logger.info(msg)
            return {"status": "not_playing", "message": msg}
        
        # VLC supports proper seeking
        current_time = state.media_player.get_time()  # Get current time in milliseconds
        new_time = current_time + (seconds * 1000)  # Convert seconds to milliseconds
        
        # Get the total length to avoid seeking beyond the end
        length = state.media_player.get_length()
        if length > 0 and new_time > length:
            new_time = length - 1000  # Stay 1 second before the end
        
        state.media_player.set_time(new_time)
        
        msg = f"Skipped forward {seconds} seconds"
        logger.info(msg)
        ctx.info(msg)
        
        return {
            "status": "skip_forward",
            "seconds": seconds,
            "current_time": new_time // 1000,  # Convert back to seconds for display
            "file": state.playing
        }
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Skip forward error: {error_msg}")
        ctx.error(error_msg)
        raise

@mcp.tool()
async def skip_backward(ctx: Context, seconds: int = 10) -> dict:
    """Skip backward by specified seconds (default 10)"""
    try:
        if state.media_player is None:
            msg = "Audio system not initialized"
            logger.warning(msg)
            return {"status": "not_initialized", "message": msg}
        
        if not state.playing:
            msg = "No audio currently playing"
            logger.info(msg)
            return {"status": "not_playing", "message": msg}
        
        # VLC supports proper seeking
        current_time = state.media_player.get_time()  # Get current time in milliseconds
        new_time = current_time - (seconds * 1000)  # Convert seconds to milliseconds
        
        # Don't seek before the beginning
        if new_time < 0:
            new_time = 0
        
        state.media_player.set_time(new_time)
        
        msg = f"Skipped backward {seconds} seconds"
        logger.info(msg)
        ctx.info(msg)
        
        return {
            "status": "skip_backward",
            "seconds": seconds,
            "current_time": new_time // 1000,  # Convert back to seconds for display
            "file": state.playing
        }
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Skip backward error: {error_msg}")
        ctx.error(error_msg)
        raise

@mcp.tool()
async def get_playback_status(ctx: Context) -> dict:
    """Get current playback status"""
    try:
        _update_playlist()
        
        is_playing = False
        current_time = 0
        total_time = 0
        
        if state.media_player is not None:
            is_playing = state.media_player.is_playing()
            current_time = state.media_player.get_time() // 1000  # Convert to seconds
            total_time = state.media_player.get_length() // 1000  # Convert to seconds
        
        return {
            "status": "playing" if is_playing and not state.paused else "paused" if state.paused else "stopped",
            "current_file": state.playing,
            "paused": state.paused,
            "volume": state.volume,
            "playlist_size": len(state.playlist),
            "current_position": f"{state.current_index + 1}/{len(state.playlist)}" if state.current_index >= 0 else "0/0",
            "time_position": f"{current_time}s / {total_time}s" if total_time > 0 else "0s / 0s"
        }
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Status error: {error_msg}")
        ctx.error(error_msg)
        raise

@mcp.tool()
async def diagnose_audio_system(ctx: Context) -> dict:
    """Diagnose the audio system and VLC capabilities"""
    try:
        diagnosis = {
            "vlc_available": False,
            "vlc_version": "unknown",
            "audio_outputs": [],
            "vlc_instance_created": False,
            "media_player_created": False,
            "error_details": []
        }
        
        # Check if VLC is available
        try:
            diagnosis["vlc_version"] = vlc.libvlc_get_version().decode('utf-8')
            diagnosis["vlc_available"] = True
            logger.info(f"VLC version: {diagnosis['vlc_version']}")
        except Exception as e:
            diagnosis["error_details"].append(f"VLC not available: {e}")
            logger.error(f"VLC not available: {e}")
        
        # Try to create VLC instance
        if diagnosis["vlc_available"]:
            try:
                state.init_vlc()
                diagnosis["vlc_instance_created"] = state.vlc_instance is not None
                diagnosis["media_player_created"] = state.media_player is not None
                
                if state.media_player:
                    # Get audio output modules
                    try:
                        audio_outputs = state.vlc_instance.audio_output_enumerate()
                        if audio_outputs:
                            for output in audio_outputs:
                                diagnosis["audio_outputs"].append({
                                    "name": output.name.decode('utf-8') if output.name else "unknown",
                                    "description": output.description.decode('utf-8') if output.description else "unknown"
                                })
                    except Exception as e:
                        diagnosis["error_details"].append(f"Failed to enumerate audio outputs: {e}")
                        
            except Exception as e:
                diagnosis["error_details"].append(f"Failed to initialize VLC: {e}")
                logger.error(f"Failed to initialize VLC: {e}")
        
        ctx.info("Audio system diagnosis completed")
        return diagnosis
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Diagnosis error: {error_msg}")
        ctx.error(error_msg)
        return {"error": error_msg}

@mcp.tool()
async def set_volume(volume: int, ctx: Context) -> dict:
    """Set playback volume (0-10)"""
    try:
        if volume < 0 or volume > 10:
            raise ValueError("Volume must be between 0 and 10")
        
        state.volume = volume
        
        if state.media_player is not None:
            state.media_player.audio_set_volume(int(volume * 10))  # VLC uses 0-100 scale
        
        msg = f"Volume set to {volume}/10"
        logger.info(msg)
        ctx.info(msg)
        
        return {
            "status": "volume_changed",
            "volume": volume,
            "file": state.playing
        }
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Volume error: {error_msg}")
        ctx.error(error_msg)
        raise

@mcp.tool()
async def seek_to_position(position_seconds: int, ctx: Context) -> dict:
    """Seek to a specific position in the current track (in seconds)"""
    try:
        if state.media_player is None:
            msg = "Audio system not initialized"
            logger.warning(msg)
            return {"status": "not_initialized", "message": msg}
        
        if not state.playing:
            msg = "No audio currently playing"
            logger.info(msg)
            return {"status": "not_playing", "message": msg}
        
        # Convert seconds to milliseconds for VLC
        position_ms = position_seconds * 1000
        
        # Get the total length to validate the position
        length = state.media_player.get_length()
        if length > 0 and position_ms > length:
            position_ms = length - 1000  # Stay 1 second before the end
        
        if position_ms < 0:
            position_ms = 0
        
        state.media_player.set_time(position_ms)
        
        msg = f"Seeked to position: {position_seconds} seconds"
        logger.info(msg)
        ctx.info(msg)
        
        return {
            "status": "seeked",
            "position_seconds": position_seconds,
            "file": state.playing
        }
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Seek error: {error_msg}")
        ctx.error(error_msg)
        raise

@mcp.tool()
async def list_genres(ctx: Context) -> dict:
    """List all available genres in the music collection with counts"""
    logger.info("Listing all genres in music collection")
    
    try:
        genre_counts = _get_all_genres()
        
        # Sort genres by count (most common first)
        sorted_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)
        
        total_files = sum(genre_counts.values())
        unique_genres = len(genre_counts)
        
        ctx.info(f"Found {unique_genres} unique genres across {total_files} files")
        
        return {
            "status": "success",
            "total_files": total_files,
            "unique_genres": unique_genres,
            "genres": [
                {"genre": genre, "count": count} 
                for genre, count in sorted_genres
            ]
        }
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"List genres error: {error_msg}")
        ctx.error(error_msg)
        raise

@mcp.tool()
async def search_by_genre(genre: str, ctx: Context, limit: int = 20) -> dict:
    """Search for songs by genre"""
    logger.info(f"Searching for songs in genre: '{genre}'")
    
    try:
        matching_files = _search_by_genre(genre, limit)
        
        ctx.info(f"Found {len(matching_files)} songs in genre '{genre}'")
        
        return {
            "status": "success",
            "genre": genre,
            "matches": matching_files,
            "count": len(matching_files)
        }
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Search by genre error: {error_msg}")
        ctx.error(error_msg)
        raise

@mcp.tool()
async def play_random_song_by_artist(artist: str, ctx: Context) -> dict:
    """Play a random song by the specified artist"""
    logger.info(f"Playing random song by artist: '{artist}'")
    
    try:
        import random
        
        # Search for songs by the artist
        search_result = await search_songs(artist, ctx, limit=100)  # Get more options for randomness
        
        if search_result["status"] != "success" or not search_result["matches"]:
            return {
                "status": "no_matches",
                "message": f"No songs found by artist '{artist}'"
            }
        
        # Filter results to prioritize artist matches over filename matches
        artist_matches = []
        other_matches = []
        
        for match in search_result["matches"]:
            # Check if the match is likely an artist match
            if (match.get("artist") and 
                fuzz.partial_ratio(artist.lower(), match["artist"].lower()) >= 80):
                artist_matches.append(match)
            elif (match.get("display_info") and 
                  fuzz.partial_ratio(artist.lower(), match["display_info"].lower()) >= 80):
                artist_matches.append(match)
            elif match.get("match_type") == "metadata":
                artist_matches.append(match)
            else:
                other_matches.append(match)
        
        # Prefer artist matches, but fall back to other matches if needed
        available_songs = artist_matches if artist_matches else other_matches
        
        if not available_songs:
            return {
                "status": "no_matches",
                "message": f"No songs found by artist '{artist}'"
            }
        
        # Pick a random song from the available options
        random_song = random.choice(available_songs)
        
        # Play the selected song
        play_result = await play_audio(random_song["file"], ctx)
        
        # Add artist info to the result
        if play_result.get("status") == "success":
            play_result["artist_searched"] = artist
            play_result["selected_from"] = f"{len(available_songs)} songs by '{artist}'"
            play_result["match_score"] = random_song.get("score", 0)
            play_result["match_type"] = random_song.get("match_type", "unknown")
            if random_song.get("artist"):
                play_result["artist_metadata"] = random_song["artist"]
            if random_song.get("title"):
                play_result["title_metadata"] = random_song["title"]
        
        return play_result
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Play random song by artist error: {error_msg}")
        ctx.error(error_msg)
        raise

@mcp.tool()
async def play_random_from_genre(genre: str, ctx: Context) -> dict:
    """Play a random song from the specified genre"""
    logger.info(f"Playing random song from genre: '{genre}'")
    
    try:
        import random
        
        matching_files = _search_by_genre(genre, limit=100)  # Get more options for randomness
        
        if not matching_files:
            return {
                "status": "no_matches",
                "message": f"No songs found in genre '{genre}'"
            }
        
        # Pick a random song
        random_song = random.choice(matching_files)
        
        # Play the selected song
        play_result = await play_audio(random_song["file"], ctx)
        
        # Add genre info to the result
        if play_result.get("status") == "success":
            play_result["genre"] = random_song["genre"]
            play_result["selected_from"] = f"{len(matching_files)} songs in genre '{genre}'"
        
        return play_result
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Play random from genre error: {error_msg}")
        ctx.error(error_msg)
        raise

if __name__ == "__main__":
    logger.info(f"Starting audio player MCP server with directory: {AUDIO_DIR}")
    mcp.run()