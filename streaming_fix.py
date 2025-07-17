#!/usr/bin/env python3
"""
Fixed streaming implementation for SongHub
"""

import yt_dlp
from flask import Flask, jsonify, request

app = Flask(__name__)

def get_stream_url_simple(video_id, audio_only=True):
    """Simple, reliable streaming URL extraction"""
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'bestaudio[ext=m4a]/bestaudio' if audio_only else 'best[ext=mp4]/best'
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if info and 'url' in info:
                return {
                    'status': 'success',
                    'stream_url': info['url'],
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0)
                }
            
            # Try formats if direct URL not available
            formats = info.get('formats', []) if info else []
            for fmt in formats:
                if 'url' in fmt:
                    return {
                        'status': 'success',
                        'stream_url': fmt['url'],
                        'title': info.get('title', 'Unknown') if info else 'Unknown',
                        'duration': info.get('duration', 0) if info else 0
                    }
            
            return {'status': 'error', 'message': 'No stream URL found'}
            
    except Exception as e:
        return {'status': 'error', 'message': f'Error: {str(e)}'}

@app.route('/test_stream/<video_id>')
def test_stream(video_id):
    """Test streaming endpoint"""
    audio_only = request.args.get('audio_only', 'true').lower() == 'true'
    result = get_stream_url_simple(video_id, audio_only)
    return jsonify(result)

if __name__ == '__main__':
    # Test the function directly
    result = get_stream_url_simple('dQw4w9WgXcQ', True)
    print("Test result:")
    print(result)
    
    if result.get('status') == 'success':
        print("\n✅ Streaming function works!")
        print(f"Stream URL: {result['stream_url'][:100]}...")
    else:
        print("\n❌ Streaming function failed")
        print(f"Error: {result.get('message', 'Unknown error')}")