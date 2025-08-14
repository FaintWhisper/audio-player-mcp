#!/usr/bin/env python3
"""
Test script for fuzzy search functionality
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from fuzzywuzzy import process
    from audio_player_mcp.player import (_get_audio_files, AUDIO_DIR, 
                                        _normalize_music_terms, _enhanced_music_search)
    
    print("🔍 Fuzzy Search Test")
    print("=" * 40)
    
    # Test audio directory
    print(f"📁 Audio directory: {AUDIO_DIR}")
    
    # Get available files
    files = _get_audio_files()
    print(f"🎵 Found {len(files)} audio files")
    
    if not files:
        print("❌ No audio files found!")
        sys.exit(1)
    
    # Show some example files
    print("\n📋 Example files:")
    for i, file in enumerate(files[:5]):
        folder = str(Path(file).parent) if Path(file).parent != Path('.') else "root"
        print(f"  {i+1}. {Path(file).name} (in {folder})")
    if len(files) > 5:
        print(f"  ... and {len(files) - 5} more")
    
    # Show folder distribution
    folders = {}
    for file in files:
        folder = str(Path(file).parent) if Path(file).parent != Path('.') else "root"
        folders[folder] = folders.get(folder, 0) + 1
    
    print("\n📁 Folder distribution:")
    for folder, count in sorted(folders.items()):
        print(f"  {folder}: {count} files")
    
    # Test searches
    test_queries = [
        "calvin harris",
        "outside",
        "ellie goulding", 
        "harris calvin",  # reversed order
        "outsde",  # typo
        "featuring",  # should find songs with "featuring" 
        "feat",  # should find songs with "feat" or "featuring"
        "ft",  # another abbreviation
        "remix",  # music term
        "original mix"  # compound music term
    ]
    
    print("\n🔎 Testing fuzzy search:")
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        
        # Prepare file names for search
        file_names_for_search = []
        for file in files:
            name_without_ext = Path(file).stem
            clean_name = name_without_ext.replace('_', ' ').replace('-', ' ').replace('.', ' ')
            file_names_for_search.append(clean_name)
        
        # Find matches
        matches = process.extract(query, file_names_for_search, limit=3)
        
        for i, (match, score) in enumerate(matches, 1):
            idx = file_names_for_search.index(match)
            original_file = files[idx]
            print(f"  {i}. {original_file} (score: {score})")
            
        if not matches or matches[0][1] < 30:
            print("  ❌ No good matches found")
    
    # Test enhanced music search
    print("\n=== Testing Enhanced Music Search ===")
    test_queries = ["feat", "featuring", "remix", "live", "acoustic"]
    
    for query in test_queries:
        print(f"\nTesting query: '{query}'")
        # Normalize the query
        normalized_query = _normalize_music_terms(query)
        print(f"Normalized query: '{normalized_query}'")
        
        # Test enhanced search
        enhanced_results = _enhanced_music_search(files, query, limit=5)
        print(f"Enhanced search results for '{query}':")
        for result in enhanced_results:
            print(f"  {result}")
    
    # Test specific "feat" case
    print("\n=== Specific 'feat' Test ===")
    feat_results = _enhanced_music_search(files, "feat", limit=10)
    print(f"Found {len(feat_results)} results for 'feat':")
    for result in feat_results[:10]:
        print(f"  {result}")
    
    print("\n✅ Fuzzy search test completed!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure to install dependencies:")
    print("   pip install fuzzywuzzy python-Levenshtein")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
