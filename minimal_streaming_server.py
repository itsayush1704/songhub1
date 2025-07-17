#!/usr/bin/env python3
"""
Minimal streaming server to test functionality
"""

from flask import Flask, jsonify, request
import yt_dlp

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

@app.route('/stream/<video_id>')
def get_stream(video_id):
    """Test streaming endpoint"""
    try:
        audio_only = request.args.get('audio_only', 'true').lower() == 'true'
        result = get_stream_url_simple(video_id, audio_only)
        return jsonify(result)
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Server error: {str(e)}'}), 500

@app.route('/test')
def test():
    return jsonify({'status': 'ok', 'message': 'Server is running'})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8003, debug=True)