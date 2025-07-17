#!/usr/bin/env python3
"""
Example usage of the enhanced YouTube streaming functionality in SongHub.
This demonstrates how to integrate the new streaming features into applications.
"""

import requests
import json
from app import get_youtube_stream_url

def example_basic_streaming():
    """Example: Basic audio streaming"""
    print("=== Basic Audio Streaming Example ===")
    
    # Example video IDs
    video_ids = [
        "dQw4w9WgXcQ",  # Rick Astley - Never Gonna Give You Up
        "9bZkp7q19f0",  # PSY - Gangnam Style
        "kJQP7kiw5Fk"   # Luis Fonsi - Despacito
    ]
    
    for video_id in video_ids:
        print(f"\nTesting video: {video_id}")
        
        # Get audio stream
        result = get_youtube_stream_url(video_id, audio_only=True)
        
        if result['status'] == 'success':
            print(f"✅ Success: {result['video_info']['title']}")
            print(f"   Duration: {result['video_info']['duration']} seconds")
            print(f"   Format: {result['format_info']['ext']}")
            print(f"   Audio Codec: {result['format_info']['acodec']}")
            print(f"   Bitrate: {result['format_info']['abr']} kbps")
            print(f"   Stream URL: {result['stream_url'][:80]}...")
        else:
            print(f"❌ Failed: {result['message']}")

def example_format_discovery():
    """Example: Discover available formats"""
    print("\n=== Format Discovery Example ===")
    
    video_id = "dQw4w9WgXcQ"
    base_url = "http://127.0.0.1:8002"
    
    try:
        # Get all available formats
        response = requests.get(f"{base_url}/get_formats/{video_id}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\nVideo: {data['video_info']['title']}")
            print(f"Duration: {data['video_info']['duration']} seconds")
            print(f"Views: {data['video_info']['view_count']}")
            
            # Show audio formats
            audio_formats = data['formats']['audio_only']
            print(f"\nAvailable Audio Formats ({len(audio_formats)}):")
            for fmt in audio_formats[:5]:  # Show top 5
                print(f"  - {fmt['format_id']}: {fmt['ext']} | "
                      f"{fmt['acodec']} | {fmt['abr']}kbps")
            
            # Show video formats
            video_formats = data['formats']['video_only']
            print(f"\nAvailable Video Formats ({len(video_formats)}):")
            for fmt in video_formats[:5]:  # Show top 5
                print(f"  - {fmt['format_id']}: {fmt['ext']} | "
                      f"{fmt['vcodec']} | {fmt['width']}x{fmt['height']}")
            
            # Show recommended formats
            recommended = data['recommended']
            print("\nRecommended Formats:")
            if recommended['best_audio']:
                ba = recommended['best_audio']
                print(f"  Best Audio: {ba['format_id']} ({ba['abr']}kbps {ba['ext']})")
            if recommended['best_video']:
                bv = recommended['best_video']
                print(f"  Best Video: {bv['format_id']} ({bv['width']}x{bv['height']} {bv['ext']})")
            
        else:
            print(f"❌ API request failed: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Start with: python3 app.py")

def example_specific_format_streaming():
    """Example: Stream specific format"""
    print("\n=== Specific Format Streaming Example ===")
    
    video_id = "dQw4w9WgXcQ"
    base_url = "http://127.0.0.1:8002"
    
    try:
        # First, get available formats
        response = requests.get(f"{base_url}/get_formats/{video_id}")
        
        if response.status_code == 200:
            data = response.json()
            audio_formats = data['formats']['audio_only']
            
            if audio_formats:
                # Choose the best audio format
                best_format = audio_formats[0]
                format_id = best_format['format_id']
                
                print(f"Selected format: {format_id} ({best_format['abr']}kbps {best_format['ext']})")
                
                # Get stream URL for this specific format
                stream_response = requests.get(f"{base_url}/stream/{video_id}/{format_id}")
                
                if stream_response.status_code == 200:
                    stream_data = stream_response.json()
                    print(f"✅ Stream URL obtained: {stream_data['stream_url'][:80]}...")
                    print(f"   Format info: {stream_data['format_info']}")
                else:
                    print(f"❌ Failed to get stream URL: {stream_response.status_code}")
            else:
                print("❌ No audio formats available")
        else:
            print(f"❌ Failed to get formats: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Start with: python3 app.py")

def example_error_handling():
    """Example: Error handling"""
    print("\n=== Error Handling Example ===")
    
    # Test with invalid video ID
    invalid_video_id = "invalid_id_123"
    print(f"\nTesting with invalid video ID: {invalid_video_id}")
    
    result = get_youtube_stream_url(invalid_video_id, audio_only=True)
    
    if result['status'] == 'error':
        print(f"✅ Error properly handled: {result['message']}")
    else:
        print("❌ Expected error but got success")
    
    # Test with private/unavailable video
    private_video_id = "xxxxxxxxxx"
    print(f"\nTesting with potentially unavailable video ID: {private_video_id}")
    
    result = get_youtube_stream_url(private_video_id, audio_only=True)
    
    if result['status'] == 'error':
        print(f"✅ Error properly handled: {result['message']}")
    else:
        print(f"✅ Unexpected success: {result['video_info']['title']}")

def example_integration_patterns():
    """Example: Common integration patterns"""
    print("\n=== Integration Patterns Example ===")
    
    video_id = "dQw4w9WgXcQ"
    
    # Pattern 1: Simple audio player
    print("\n1. Simple Audio Player Pattern:")
    result = get_youtube_stream_url(video_id, audio_only=True)
    if result['status'] == 'success':
        print(f"   Title: {result['video_info']['title']}")
        print(f"   Stream URL ready for HTML5 audio element")
        print(f"   <audio src='{result['stream_url']}' controls></audio>")
    
    # Pattern 2: Quality selection
    print("\n2. Quality Selection Pattern:")
    base_url = "http://127.0.0.1:8002"
    
    try:
        response = requests.get(f"{base_url}/get_formats/{video_id}")
        if response.status_code == 200:
            data = response.json()
            audio_formats = data['formats']['audio_only']
            
            print("   Available qualities:")
            for i, fmt in enumerate(audio_formats[:3]):
                quality_label = f"{fmt['abr']}kbps {fmt['ext']}"
                print(f"   [{i+1}] {quality_label} (format_id: {fmt['format_id']})")
            
            # Simulate user selection
            selected_format = audio_formats[0] if audio_formats else None
            if selected_format:
                print(f"   User selected: {selected_format['abr']}kbps {selected_format['ext']}")
                
    except requests.exceptions.ConnectionError:
        print("   (Server not running - simulated)")
    
    # Pattern 3: Metadata extraction
    print("\n3. Metadata Extraction Pattern:")
    result = get_youtube_stream_url(video_id, audio_only=True)
    if result['status'] == 'success':
        video_info = result['video_info']
        format_info = result['format_info']
        
        print(f"   Title: {video_info['title']}")
        print(f"   Uploader: {video_info['uploader']}")
        print(f"   Duration: {video_info['duration']}s")
        print(f"   Views: {video_info['view_count']}")
        print(f"   Audio Quality: {format_info['abr']}kbps {format_info['acodec']}")

def main():
    """Run all examples"""
    print("YouTube Streaming Functionality Examples")
    print("========================================")
    
    # Run examples
    example_basic_streaming()
    example_format_discovery()
    example_specific_format_streaming()
    example_error_handling()
    example_integration_patterns()
    
    print("\n=== Summary ===")
    print("These examples demonstrate:")
    print("✅ Basic audio stream extraction")
    print("✅ Format discovery and selection")
    print("✅ Specific format streaming")
    print("✅ Error handling")
    print("✅ Common integration patterns")
    print("\nFor more details, see STREAMING_FEATURES.md")

if __name__ == "__main__":
    main()