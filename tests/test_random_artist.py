#!/usr/bin/env python3

"""
Test script for the new play_random_song_by_artist function
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from audio_player_mcp.player import AUDIO_DIR, _get_audio_files
import asyncio

# Mock the Context class for testing
class MockContext:
    def info(self, message):
        print(f"INFO: {message}")
    
    def error(self, message):
        print(f"ERROR: {message}")

async def test_random_artist_function():
    """Test the play_random_song_by_artist function"""
    print("Testing play_random_song_by_artist function...")
    print(f"Audio directory: {AUDIO_DIR}")
    
    # Import the function after the path is set
    from audio_player_mcp.player import play_random_song_by_artist, search_songs
    
    # Test popular artists
    popular_artists = [
        "Taylor Swift",
        "Drake", 
        "Ed Sheeran",
        "Ariana Grande",
        "The Weeknd"
    ]
    
    ctx = MockContext()
    
    for artist in popular_artists:
        print(f"\n--- Testing artist: {artist} ---")
        
        try:
            # First check if we have any songs by this artist
            search_result = await search_songs(artist, ctx, limit=10)
            
            if search_result["status"] == "success" and search_result["matches"]:
                print(f"Found {len(search_result['matches'])} potential matches for {artist}")
                
                # Now test the random function
                result = await play_random_song_by_artist(artist, ctx)
                
                if result["status"] == "success":
                    print(f"✅ Successfully would play random {artist} song:")
                    print(f"   File: {result.get('filename', 'N/A')}")
                    print(f"   Selected from: {result.get('selected_from', 'N/A')}")
                    print(f"   Match score: {result.get('match_score', 'N/A')}")
                    if result.get('artist_metadata'):
                        print(f"   Artist metadata: {result['artist_metadata']}")
                    if result.get('title_metadata'):
                        print(f"   Title metadata: {result['title_metadata']}")
                elif result["status"] == "no_matches":
                    print(f"❌ No songs found for {artist}")
                else:
                    print(f"❓ Unexpected result: {result}")
            else:
                print(f"❌ No songs found for {artist} in search")
                
        except Exception as e:
            print(f"❌ Error testing {artist}: {e}")
    
    print("\n--- Testing function behavior ---")
    
    # Test with invalid artist
    try:
        result = await play_random_song_by_artist("NonExistentArtist12345", ctx)
        print(f"Invalid artist test result: {result['status']}")
    except Exception as e:
        print(f"Error with invalid artist: {e}")

if __name__ == "__main__":
    print("Audio Player MCP - Random Artist Function Test")
    print("=" * 50)
    
    # Check if audio directory exists
    if not os.path.exists(AUDIO_DIR):
        print(f"❌ Audio directory not found: {AUDIO_DIR}")
        print("Please ensure AUDIO_PLAYER_DIR is set correctly or music files exist in the default location")
        sys.exit(1)
    
    # Check for audio files
    try:
        audio_files = _get_audio_files()
        print(f"Found {len(audio_files)} audio files in directory")
        
        if len(audio_files) == 0:
            print("❌ No audio files found. Please add some music files to test.")
            sys.exit(1)
        
        # Show some sample files
        print("\nSample audio files:")
        for i, file in enumerate(audio_files[:5]):
            print(f"  {i+1}. {os.path.basename(file)}")
        if len(audio_files) > 5:
            print(f"  ... and {len(audio_files) - 5} more")
            
    except Exception as e:
        print(f"❌ Error accessing audio files: {e}")
        sys.exit(1)
    
    # Run the test
    asyncio.run(test_random_artist_function())
    
    print("\n" + "=" * 50)
    print("Test completed!")
