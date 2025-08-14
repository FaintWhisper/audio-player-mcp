#!/usr/bin/env python3
"""
Test script to debug VLC issues in MCP server environment
This simulates the MCP server environment more closely
"""

import sys
import os
import time
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import the player module
from audio_player_mcp.player import state

def test_mcp_vlc_environment():
    """Test VLC in an environment similar to MCP server"""
    
    print("🔍 Testing VLC in MCP-like environment...")
    
    # Set up environment similar to MCP server
    test_file = r"C:\Users\Amit\Music\MP3\Outside (feat. Ellie Goulding) - Calvin Harris.flac"
    
    if not Path(test_file).exists():
        print(f"❌ Test file not found: {test_file}")
        return False
    
    try:
        # Test VLC initialization (like the MCP server would)
        print("🔧 Initializing VLC instance...")
        state.init_vlc()
        
        if state.vlc_instance is None:
            print("❌ Failed to create VLC instance")
            return False
        
        print("✅ VLC instance created")
        
        if state.media_player is None:
            print("❌ Failed to create media player")
            return False
            
        print("✅ Media player created")
        
        # Test media loading
        print("📀 Loading media...")
        media = state.vlc_instance.media_new(test_file)
        state.media_player.set_media(media)
        print("✅ Media loaded")
        
        # Set volume
        state.media_player.audio_set_volume(30)  # 30%
        print("🔊 Volume set to 30%")
        
        # Test playback
        print("▶️ Starting playback...")
        play_result = state.media_player.play()
        print(f"Play result: {play_result}")
        
        # Wait and check status
        time.sleep(1)
        
        is_playing = state.media_player.is_playing()
        player_state = state.media_player.get_state()
        
        print(f"Is playing: {is_playing}")
        print(f"Player state: {player_state}")
        
        if is_playing:
            print("✅ Playback started successfully!")
            
            # Let it play for a few seconds
            for i in range(3):
                time.sleep(1)
                current_time = state.media_player.get_time() // 1000
                length = state.media_player.get_length() // 1000
                print(f"   ⏱️ Time: {current_time}s / {length}s")
            
            # Stop playback
            print("⏹️ Stopping playback...")
            state.media_player.stop()
            
            return True
        else:
            print(f"❌ Playback failed to start. State: {player_state}")
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_audio_outputs():
    """Test available audio outputs"""
    print("\n🔊 Testing audio outputs...")
    
    try:
        import vlc
        
        # Create a simple VLC instance
        instance = vlc.Instance()
        
        # Try to enumerate audio outputs
        try:
            outputs = instance.audio_output_enumerate()
            if outputs:
                print("Available audio outputs:")
                for output in outputs:
                    name = output.name.decode('utf-8') if output.name else "unknown"
                    desc = output.description.decode('utf-8') if output.description else "unknown"
                    print(f"  - {name}: {desc}")
            else:
                print("No audio outputs found")
        except Exception as e:
            print(f"Failed to enumerate audio outputs: {e}")
            
    except Exception as e:
        print(f"Error testing audio outputs: {e}")

if __name__ == "__main__":
    print("🧪 VLC MCP Environment Test")
    print("=" * 40)
    
    # Test audio outputs first
    test_audio_outputs()
    
    # Test VLC in MCP-like environment
    success = test_mcp_vlc_environment()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 VLC MCP test PASSED!")
    else:
        print("💥 VLC MCP test FAILED!")
        print("\n📝 Debugging tips:")
        print("1. Check if VLC media player is installed on Windows")
        print("2. Verify audio drivers are working")
        print("3. Try running as administrator")
        print("4. Check Windows audio settings")
