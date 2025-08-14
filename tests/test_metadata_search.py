#!/usr/bin/env python3
"""
Test script for enhanced metadata search functionality
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from audio_player_mcp.player import (_get_audio_files, _extract_title_and_artist, 
                                        _enhanced_metadata_search, _create_search_data_for_file,
                                        AUDIO_DIR)
    import time

    def test_metadata_search():
        print("🎵 Enhanced Metadata Search Test")
        print("=" * 45)
        
        # Get some files to test
        files = _get_audio_files()
        print(f"📁 Found {len(files)} audio files")
        
        if len(files) == 0:
            print("❌ No audio files found!")
            return
        
        # Test metadata extraction on first 5 files
        print(f"\n🔍 Testing metadata extraction on first 5 files:")
        for i, file_path in enumerate(files[:5], 1):
            absolute_path = AUDIO_DIR / file_path
            title, artist = _extract_title_and_artist(str(absolute_path))
            filename = Path(file_path).name
            print(f"  {i}. {filename[:40]}{'...' if len(filename) > 40 else ''}")
            print(f"     Title: {title if title else 'N/A'}")
            print(f"     Artist: {artist if artist else 'N/A'}")
            print()
        
        # Test search data creation
        print(f"🔧 Testing search data creation for first file...")
        if files:
            search_data = _create_search_data_for_file(files[0])
            print(f"File: {search_data['file_path']}")
            print(f"Title: {search_data['title']}")
            print(f"Artist: {search_data['artist']}")
            print(f"Search texts: {search_data['search_texts']}")
            print()
        
        # Test various search queries with popular songs and artists
        test_queries = [
            "Taylor Swift",  # Popular artist
            "Blinding Lights",  # Hit song by The Weeknd
            "Drake",  # Popular rapper
            "Bad Guy",  # Hit song by Billie Eilish
            "Ed Sheeran",  # Popular singer-songwriter
            "Shape of You",  # Hit song by Ed Sheeran
            "Ariana Grande",  # Popular pop artist
            "Thank U Next",  # Hit song by Ariana Grande
            "Post Malone",  # Popular artist
            "Circles",  # Hit song by Post Malone
            "Dua Lipa",  # Popular pop artist
            "Levitating",  # Hit song by Dua Lipa
        ]
        
        print(f"🔍 Testing enhanced metadata search with various queries:")
        print("-" * 50)
        
        for query in test_queries:
            print(f"\n🔎 Searching for: '{query}'")
            
            start_time = time.time()
            # Test with a subset of files for reasonable performance
            test_files = files[:min(100, len(files))]
            results = _enhanced_metadata_search(test_files, query, limit=3)
            end_time = time.time()
            
            print(f"⏱️  Search completed in {end_time - start_time:.3f} seconds")
            print(f"Found {len(results)} results:")
            
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result['filename'][:40]}{'...' if len(result['filename']) > 40 else ''}")
                if result['title'] and result['artist']:
                    print(f"     🎵 {result['artist']} - {result['title']}")
                elif result['title']:
                    print(f"     🎵 {result['title']}")
                elif result['artist']:
                    print(f"     🎵 {result['artist']}")
                print(f"     📊 Score: {result['score']:.1f} | Match: {result['match_type']}")
                print(f"     🎯 Matched: '{result['match_text']}'")
                print()
        
        print("✅ Enhanced metadata search test completed!")

    if __name__ == "__main__":
        test_metadata_search()

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure to install dependencies:")
    print("   pip install mutagen fuzzywuzzy")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
