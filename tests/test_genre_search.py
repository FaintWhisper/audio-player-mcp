#!/usr/bin/env python3
"""
Test script for genre search functionality
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from audio_player_mcp.player import (_get_audio_files, _extract_genre_from_file, 
                                        _get_all_genres, _search_by_genre, AUDIO_DIR)
    import time

    def test_genre_functionality():
        print("🎵 Genre Search Test - Popular Music Genres")
        print("=" * 50)
        print("This test searches for popular music genres like:")
        print("Pop, Rock, Hip Hop, Electronic, R&B, Country, etc.")
        print("")
        
        # Get some files to test
        files = _get_audio_files()
        print(f"📁 Found {len(files)} audio files")
        
        if len(files) == 0:
            print("❌ No audio files found!")
            return
        
        # Test genre extraction on first 10 files
        print(f"\n🔍 Testing genre extraction on first 10 files:")
        for i, file_path in enumerate(files[:10], 1):
            # Convert relative path to absolute path for genre extraction
            absolute_path = AUDIO_DIR / file_path
            genre = _extract_genre_from_file(str(absolute_path))
            filename = Path(file_path).name
            print(f"  {i}. {filename[:50]}{'...' if len(filename) > 50 else ''}")
            print(f"     Genre: {genre}")
        
        # Get all genres (this might take a while)
        print(f"\n📊 Analyzing genres across all {len(files)} files...")
        print("⏳ This may take a moment...")
        
        start_time = time.time()
        genre_counts = _get_all_genres()
        end_time = time.time()
        
        print(f"✅ Genre analysis completed in {end_time - start_time:.2f} seconds")
        print(f"🎼 Found {len(genre_counts)} unique genres")
        
        # Show top 10 genres
        sorted_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)
        print(f"\n🏆 Top 10 genres by count:")
        for i, (genre, count) in enumerate(sorted_genres[:10], 1):
            print(f"  {i}. {genre}: {count} songs")
        
        # Test searching by popular genres
        popular_genres_to_test = ["Pop", "Rock", "Hip Hop", "Electronic", "Dance", "R&B", "Alternative"]
        
        print(f"\n🎯 Testing search for popular genres:")
        for genre in popular_genres_to_test:
            if any(genre.lower() in found_genre.lower() for found_genre, _ in sorted_genres):
                print(f"\n🔎 Searching for genre '{genre}':")
                genre_results = _search_by_genre(genre, limit=3)
                if genre_results:
                    print(f"  ✅ Found {len(genre_results)} songs:")
                    for i, result in enumerate(genre_results, 1):
                        print(f"    {i}. {result['name']}")
                        print(f"       Genre: {result['genre']}")
                else:
                    print(f"  ❌ No songs found for '{genre}'")
            else:
                print(f"  ⏭️  Genre '{genre}' not found in music library")
        
        # Test searching by most common genre
        if sorted_genres:
            top_genre = sorted_genres[0][0]
            print(f"\n🔎 Testing search for most common genre '{top_genre}':")
            
            genre_results = _search_by_genre(top_genre, limit=5)
            print(f"Found {len(genre_results)} songs:")
            for i, result in enumerate(genre_results, 1):
                print(f"  {i}. {result['name']}")
                print(f"     Folder: {result['folder']}")
                print(f"     Genre: {result['genre']}")
        
        print(f"\n✅ Genre search test completed!")

    if __name__ == "__main__":
        test_genre_functionality()

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure to install dependencies:")
    print("   pip install mutagen")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
