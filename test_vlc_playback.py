#!/usr/bin/env python3
"""
Simple test script to verify VLC playback functionality
Usage: python test_vlc_playback.py "path/to/audio/file.flac"
"""

import sys
import time
import vlc
from pathlib import Path

def test_vlc_playback(file_path):
    """Test VLC playback with the given audio file"""
    
    # Convert to Path object and check if file exists
    audio_file = Path(file_path)
    if not audio_file.exists():
        print(f"❌ Error: File not found: {file_path}")
        return False
    
    print(f"🎵 Testing VLC playback with: {audio_file.name}")
    print(f"📁 Full path: {audio_file}")
    
    try:
        # Create VLC instance
        print("🔧 Creating VLC instance...")
        vlc_instance = vlc.Instance('--intf', 'dummy', '--verbose', '0')
        
        # Create media player
        print("🎛️ Creating media player...")
        media_player = vlc_instance.media_player_new()
        
        # Create media from file
        print("📀 Loading media file...")
        media = vlc_instance.media_new(str(audio_file))
        media_player.set_media(media)
        
        # Set volume to 50%
        media_player.audio_set_volume(50)
        
        # Start playback
        print("▶️ Starting playback...")
        media_player.play()
        
        # Wait for playback to start
        time.sleep(1)
        
        # Check if playing
        if media_player.is_playing():
            print("✅ Playback started successfully!")
            
            # Get media info
            length = media_player.get_length() // 1000  # Convert to seconds
            print(f"⏱️ Track length: {length} seconds")
            
            # Play for 5 seconds then stop
            print("🎧 Playing for 5 seconds...")
            for i in range(5):
                if media_player.is_playing():
                    current_time = media_player.get_time() // 1000
                    print(f"   Time: {current_time}s / {length}s")
                    time.sleep(1)
                else:
                    print("❌ Playback stopped unexpectedly")
                    break
            
            # Stop playback
            print("⏹️ Stopping playback...")
            media_player.stop()
            print("✅ Test completed successfully!")
            return True
            
        else:
            print("❌ Failed to start playback")
            return False
            
    except Exception as e:
        print(f"❌ Error during playback test: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_vlc_playback.py \"path/to/audio/file\"")
        print("Example: python test_vlc_playback.py \"C:\\Users\\Amit\\Music\\MP3\\Outside (feat. Ellie Goulding) - Calvin Harris.flac\"")
        sys.exit(1)
    
    file_path = sys.argv[1]
    success = test_vlc_playback(file_path)
    
    if success:
        print("\n🎉 VLC playback test PASSED!")
    else:
        print("\n💥 VLC playback test FAILED!")
        sys.exit(1)
