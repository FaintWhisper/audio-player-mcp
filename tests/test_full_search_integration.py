#!/usr/bin/env python3
"""
Test the full search integration with metadata
"""

import sys
import os
import asyncio
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from audio_player_mcp.player import search_songs
    from mcp.server.fastmcp import Context
    
    class MockContext:
        def info(self, message):
            print(f"ℹ️  {message}")
        
        def error(self, message):
            print(f"❌ {message}")
    
    async def test_full_search():
        print("🔍 Full Search Integration Test")
        print("=" * 40)
        
        ctx = MockContext()
        
        test_queries = [
            "Taylor Swift",  # Popular artist
            "Blinding Lights",  # The Weeknd hit
            "Drake",  # Popular rapper  
            "Bad Guy",  # Billie Eilish hit
            "Ed Sheeran",  # Popular singer-songwriter
            "Shape of You",  # Ed Sheeran hit
            "Ariana Grande",  # Popular pop star
            "Thank U Next",  # Ariana Grande hit
            "Post Malone",  # Popular artist
            "Circles"  # Post Malone hit
        ]
        
        for query in test_queries:
            print(f"\n🔎 Testing full search for: '{query}'")
            print("-" * 30)
            
            result = await search_songs(query, ctx, limit=3)
            
            if result["status"] == "success":
                print(f"✅ Found {len(result['matches'])} matches")
                for i, match in enumerate(result["matches"], 1):
                    print(f"  {i}. {match['name']}")
                    if 'display_info' in match:
                        print(f"     🎵 {match['display_info']}")
                    if 'title' in match and 'artist' in match:
                        if match['title'] and match['artist']:
                            print(f"     📝 Metadata: {match['artist']} - {match['title']}")
                    print(f"     📊 Score: {match['score']} | Type: {match['match_type']}")
                    if 'matched_text' in match:
                        print(f"     🎯 Matched: '{match['matched_text']}'")
            else:
                print(f"❌ Search failed: {result.get('message', 'Unknown error')}")
    
    if __name__ == "__main__":
        asyncio.run(test_full_search())

except ImportError as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
