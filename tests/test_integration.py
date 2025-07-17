import pytest
import json
import time
from unittest.mock import patch, MagicMock
from app import app


class TestIntegration:
    """Integration tests for SongHub application workflows"""
    
    @pytest.fixture
    def client(self):
        """Create a test client with session support"""
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_client() as client:
            with app.app_context():
                yield client
    
    @pytest.fixture
    def mock_ytmusic(self):
        """Mock YTMusic API for consistent testing"""
        with patch('app.ytmusic') as mock:
            # Mock search results
            mock.search.return_value = [
                {
                    'videoId': 'test123',
                    'title': 'Test Song 1',
                    'artists': [{'name': 'Test Artist 1'}],
                    'thumbnails': [{'url': 'http://test.com/thumb1.jpg'}],
                    'duration': '3:30',
                    'album': {'name': 'Test Album 1'}
                },
                {
                    'videoId': 'test456',
                    'title': 'Test Song 2',
                    'artists': [{'name': 'Test Artist 2'}],
                    'thumbnails': [{'url': 'http://test.com/thumb2.jpg'}],
                    'duration': '4:15',
                    'album': {'name': 'Test Album 2'}
                }
            ]
            
            # Mock charts
            mock.get_charts.return_value = {
                'tracks': [
                    {
                        'videoId': 'chart1',
                        'title': 'Chart Song 1',
                        'artists': [{'name': 'Chart Artist 1'}],
                        'thumbnails': [{'url': 'http://test.com/chart1.jpg'}],
                        'views': '1M views'
                    }
                ]
            }
            
            yield mock
    
    def test_complete_user_workflow(self, client, mock_ytmusic):
        """Test a complete user workflow from search to playlist creation"""
        # Step 1: User visits homepage
        response = client.get('/')
        assert response.status_code == 200
        
        # Step 2: User searches for songs
        response = client.get('/search?q=test')
        assert response.status_code == 200
        search_data = json.loads(response.data)
        assert search_data['status'] == 'success'
        assert len(search_data['results']) > 0
        
        # Step 3: User creates a playlist
        playlist_data = {
            'name': 'My Integration Test Playlist',
            'description': 'Created during integration testing'
        }
        response = client.post('/playlists',
                             data=json.dumps(playlist_data),
                             content_type='application/json')
        assert response.status_code == 200
        playlist_response = json.loads(response.data)
        assert playlist_response['status'] == 'success'
        playlist_id = playlist_response['playlist_id']
        
        # Step 4: User adds songs to playlist
        song_data = {
            'videoId': 'test123',
            'title': 'Test Song 1',
            'artist': 'Test Artist 1',
            'thumbnail': 'http://test.com/thumb1.jpg'
        }
        response = client.post(f'/playlists/{playlist_id}/songs',
                             data=json.dumps(song_data),
                             content_type='application/json')
        assert response.status_code == 200
        add_response = json.loads(response.data)
        assert add_response['status'] == 'success'
        
        # Step 5: User retrieves playlist to verify
        response = client.get(f'/playlists/{playlist_id}/songs')
        assert response.status_code == 200
        songs_data = json.loads(response.data)
        assert songs_data['status'] == 'success'
        assert len(songs_data['songs']) == 1
        assert songs_data['songs'][0]['videoId'] == 'test123'
        
        # Step 6: User gets recommendations
        response = client.get('/recommendations')
        assert response.status_code == 200
        rec_data = json.loads(response.data)
        assert rec_data['status'] == 'success'
    
    def test_music_streaming_workflow(self, client):
        """Test the music streaming workflow"""
        # Test getting stream URL
        with patch('app.yt_dlp.YoutubeDL') as mock_ydl:
            mock_instance = MagicMock()
            mock_instance.extract_info.return_value = {
                'formats': [{
                    'url': 'http://test.com/stream.mp4',
                    'format_id': 'test_format',
                    'ext': 'mp4',
                    'acodec': 'mp4a'
                }],
                'title': 'Test Song',
                'uploader': 'Test Artist'
            }
            mock_ydl.return_value.__enter__.return_value = mock_instance
            
            response = client.get('/get_stream_url/test123?audio_only=true')
            assert response.status_code == 200
            stream_data = json.loads(response.data)
            assert stream_data['status'] == 'success'
            assert 'stream_url' in stream_data
    
    def test_recommendation_system_workflow(self, client, mock_ytmusic):
        """Test the recommendation system workflow"""
        # Simulate user listening history by making multiple requests
        songs = [
            {'videoId': 'song1', 'title': 'Song 1', 'artist': 'Artist A'},
            {'videoId': 'song2', 'title': 'Song 2', 'artist': 'Artist A'},
            {'videoId': 'song3', 'title': 'Song 3', 'artist': 'Artist B'}
        ]
        
        # Simulate playing songs (this would update user preferences)
        for song in songs:
            response = client.get(f'/get_stream_url/{song["videoId"]}')
            # The endpoint should handle the request even if streaming fails
            assert response.status_code == 200
        
        # Get recommendations based on listening history
        response = client.get('/recommendations')
        assert response.status_code == 200
        rec_data = json.loads(response.data)
        assert rec_data['status'] == 'success'
        assert 'recommendations' in rec_data
    
    def test_playlist_management_workflow(self, client):
        """Test complete playlist management workflow"""
        # Create multiple playlists
        playlists = []
        for i in range(3):
            playlist_data = {
                'name': f'Test Playlist {i+1}',
                'description': f'Description for playlist {i+1}'
            }
            response = client.post('/playlists',
                                 data=json.dumps(playlist_data),
                                 content_type='application/json')
            assert response.status_code == 200
            playlist_response = json.loads(response.data)
            playlists.append(playlist_response['playlist_id'])
        
        # Add songs to each playlist
        for i, playlist_id in enumerate(playlists):
            song_data = {
                'videoId': f'song{i+1}',
                'title': f'Song {i+1}',
                'artist': f'Artist {i+1}'
            }
            response = client.post(f'/playlists/{playlist_id}/songs',
                                 data=json.dumps(song_data),
                                 content_type='application/json')
            assert response.status_code == 200
        
        # Retrieve all playlists
        response = client.get('/playlists')
        assert response.status_code == 200
        all_playlists = json.loads(response.data)
        assert all_playlists['status'] == 'success'
        assert len(all_playlists['playlists']) >= 3
        
        # Remove a song from a playlist
        response = client.delete(f'/playlists/{playlists[0]}/songs',
                               data=json.dumps({'videoId': 'song1'}),
                               content_type='application/json')
        assert response.status_code == 200
        
        # Verify song was removed
        response = client.get(f'/playlists/{playlists[0]}/songs')
        assert response.status_code == 200
        songs_data = json.loads(response.data)
        assert len(songs_data['songs']) == 0
    
    def test_error_recovery_workflow(self, client):
        """Test error recovery and fallback mechanisms"""
        # Test with invalid playlist ID
        response = client.get('/playlists/invalid_id/songs')
        assert response.status_code == 404
        
        # Test adding song to non-existent playlist
        song_data = {'videoId': 'test', 'title': 'Test', 'artist': 'Test'}
        response = client.post('/playlists/invalid_id/songs',
                             data=json.dumps(song_data),
                             content_type='application/json')
        assert response.status_code == 404
        
        # Test search with empty query
        response = client.get('/search?q=')
        assert response.status_code == 400
        
        # Test stream URL with invalid video ID (should fallback)
        response = client.get('/get_stream_url/invalid_video_id')
        assert response.status_code == 200
        stream_data = json.loads(response.data)
        # Should contain fallback YouTube URL
        assert 'youtube.com' in stream_data.get('stream_url', '')
    
    def test_concurrent_user_simulation(self, client, mock_ytmusic):
        """Simulate multiple users using the application concurrently"""
        # Simulate different user sessions
        user_actions = [
            lambda: client.get('/search?q=pop'),
            lambda: client.get('/recommendations'),
            lambda: client.get('/trending'),
            lambda: client.post('/playlists', 
                              data=json.dumps({'name': 'Concurrent Test'}),
                              content_type='application/json')
        ]
        
        # Execute actions rapidly to simulate concurrent usage
        results = []
        for action in user_actions:
            response = action()
            results.append(response.status_code)
            time.sleep(0.1)  # Small delay to simulate real usage
        
        # All actions should succeed
        assert all(status in [200, 201] for status in results)
    
    def test_data_persistence_workflow(self, client):
        """Test that data persists correctly across requests"""
        # Create a playlist
        playlist_data = {'name': 'Persistence Test Playlist'}
        response = client.post('/playlists',
                             data=json.dumps(playlist_data),
                             content_type='application/json')
        playlist_id = json.loads(response.data)['playlist_id']
        
        # Add a song
        song_data = {
            'videoId': 'persist_test',
            'title': 'Persistence Test Song',
            'artist': 'Test Artist'
        }
        client.post(f'/playlists/{playlist_id}/songs',
                   data=json.dumps(song_data),
                   content_type='application/json')
        
        # Verify data persists in subsequent requests
        response = client.get('/playlists')
        playlists_data = json.loads(response.data)
        assert playlist_id in playlists_data['playlists']
        
        response = client.get(f'/playlists/{playlist_id}/songs')
        songs_data = json.loads(response.data)
        assert len(songs_data['songs']) == 1
        assert songs_data['songs'][0]['videoId'] == 'persist_test'


if __name__ == '__main__':
    pytest.main([__file__])