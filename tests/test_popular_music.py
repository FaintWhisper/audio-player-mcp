#!/usr/bin/env python3
"""
Test script for popular music search scenarios
Tests the audio player with popular songs, artists, and genres that most people would recognize
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from audio_player_mcp.player import (_get_audio_files, _enhanced_metadata_search,
                                        _get_all_genres, _search_by_genre)
    import time

    def test_popular_music_scenarios():
        print("🎵 Popular Music Search Test")
        print("=" * 45)
        print("Testing with popular artists, songs, and scenarios")
        print("that most people would recognize and search for.")
        print("")
        
        # Get all files
        files = _get_audio_files()
        print(f"📁 Found {len(files)} audio files to search through")
        print("")
        
        # Popular artist searches
        print("🎤 Testing Popular Artist Searches")
        print("-" * 35)
        popular_artists = [
            "Taylor Swift",
            "Drake", 
            "Ariana Grande",
            "Post Malone",
            "Billie Eilish",
            "The Weeknd",
            "Ed Sheeran",
            "Dua Lipa",
            "Justin Bieber",
            "Olivia Rodrigo"
        ]
        
        artist_results = {}
        for artist in popular_artists:
            results = _enhanced_metadata_search(files, artist, limit=3)
            artist_results[artist] = len(results)
            if results:
                print(f"✅ {artist}: Found {len(results)} songs")
                for result in results[:2]:  # Show top 2
                    display_name = f"{result['artist']} - {result['title']}" if result['artist'] and result['title'] else result['filename']
                    print(f"   📀 {display_name} (Score: {result['score']:.1f})")
            else:
                print(f"❌ {artist}: No songs found")
        
        print()
        
        # Popular song searches
        print("🎵 Testing Popular Song Title Searches")
        print("-" * 40)
        popular_songs = [
            "Blinding Lights",  # The Weeknd
            "Shape of You",     # Ed Sheeran
            "Bad Guy",          # Billie Eilish
            "Thank U Next",     # Ariana Grande
            "Circles",          # Post Malone
            "Levitating",       # Dua Lipa
            "Anti-Hero",        # Taylor Swift
            "As It Was",        # Harry Styles
            "Good 4 U",         # Olivia Rodrigo
            "Stay"              # The Kid LAROI & Justin Bieber
        ]
        
        song_results = {}
        for song in popular_songs:
            results = _enhanced_metadata_search(files, song, limit=3)
            song_results[song] = len(results)
            if results:
                print(f"✅ '{song}': Found {len(results)} matches")
                best_match = results[0]
                display_name = f"{best_match['artist']} - {best_match['title']}" if best_match['artist'] and best_match['title'] else best_match['filename']
                print(f"   🎯 Best: {display_name} (Score: {best_match['score']:.1f})")
            else:
                print(f"❌ '{song}': No matches found")
        
        print()
        
        # Popular genre searches
        print("🎼 Testing Popular Genre Searches")
        print("-" * 35)
        
        # Get all genres first
        all_genres = _get_all_genres()
        popular_genres = ["Pop", "Hip Hop", "Rock", "Electronic", "Dance", "R&B", "Country", "Alternative", "Rap"]
        
        genre_results = {}
        for genre in popular_genres:
            # Find matching genres (case insensitive)
            matching_genres = [g for g in all_genres.keys() if genre.lower() in g.lower()]
            
            if matching_genres:
                # Use the most common matching genre
                best_genre = max(matching_genres, key=lambda g: all_genres[g])
                results = _search_by_genre(best_genre, limit=3)
                genre_results[genre] = len(results)
                print(f"✅ {genre} (as '{best_genre}'): Found {len(results)} songs")
                for result in results[:2]:  # Show top 2
                    print(f"   📀 {result['name']} (Genre: {result['genre']})")
            else:
                genre_results[genre] = 0
                print(f"❌ {genre}: No matching genre found")
        
        print()
        
        # Summary statistics
        print("📊 Search Results Summary")
        print("-" * 25)
        
        total_artists_found = sum(1 for count in artist_results.values() if count > 0)
        total_songs_found = sum(1 for count in song_results.values() if count > 0)
        total_genres_found = sum(1 for count in genre_results.values() if count > 0)
        
        print(f"Popular Artists Found: {total_artists_found}/{len(popular_artists)} ({total_artists_found/len(popular_artists)*100:.1f}%)")
        print(f"Popular Songs Found: {total_songs_found}/{len(popular_songs)} ({total_songs_found/len(popular_songs)*100:.1f}%)")
        print(f"Popular Genres Found: {total_genres_found}/{len(popular_genres)} ({total_genres_found/len(popular_genres)*100:.1f}%)")
        
        print()
        
        # Recommendations
        if total_artists_found == 0 and total_songs_found == 0:
            print("💡 Recommendations:")
            print("   - The music library may not contain mainstream pop music")
            print("   - Try adding popular songs from Billboard Hot 100 or Spotify Top 50")
            print("   - Consider adding music from streaming platforms' popular playlists")
        elif total_artists_found < len(popular_artists) // 2:
            print("💡 The music library contains some popular music but could benefit from:")
            print("   - More contemporary pop artists")
            print("   - Recent chart-toppers")
            print("   - Mainstream streaming hits")
        else:
            print("🎉 Great! The music library contains many popular artists and songs!")
            print("   The search functionality works well with mainstream music.")
        
        print("\n✅ Popular music search test completed!")

    if __name__ == "__main__":
        test_popular_music_scenarios()

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure to install dependencies:")
    print("   pip install mutagen fuzzywuzzy")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
