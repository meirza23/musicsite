from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Response
from pymongo import MongoClient
from ytmusicapi import YTMusic
from yt_dlp import YoutubeDL
import os
import datetime
import requests
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId

app = Flask(__name__)
app.secret_key = os.urandom(24)

# MongoDB Bağlantısı
client = MongoClient('mongodb://localhost:27017/')
db = client['mei_music']

# Admin kullanıcı oluşturma
def create_admin_user():
    if not db.users.find_one({'email': 'admin@gmail.com'}):
        hashed_pw = generate_password_hash('admin123')
        db.users.insert_one({
            'name': 'Admin',
            'surname': 'User',
            'email': 'admin@gmail.com',
            'password': hashed_pw,
            'is_admin': True
        })
        print("Admin kullanıcısı oluşturuldu.")

create_admin_user()

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Kullanıcının playlist'lerini çek
    playlists = list(db.playlists.find({'user_id': ObjectId(session['user_id'])}))
    
    ytmusic = YTMusic()
    search_results = ytmusic.search('pop', filter='songs', limit=6)
    
    processed_songs = []
    for song in search_results:
        processed_songs.append({
            'title': song.get('title', 'Bilinmeyen Şarkı'),
            'artist': song.get('artists', [{}])[0].get('name', 'Bilinmeyen Sanatçı'),
            'thumbnail': song.get('thumbnails', [{}])[0].get('url', ''),
            'videoId': song.get('videoId', '')
        })
    
    return render_template('home_page.html', 
                         songs=processed_songs, 
                         playlists=playlists)  # playlists değişkenini ekle

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/api/create_playlist', methods=['POST'])
def create_playlist():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    playlist_name = data.get('name')
    
    if not playlist_name:
        return jsonify({'error': 'Playlist name required'}), 400
    
    db.playlists.insert_one({
        'user_id': ObjectId(session['user_id']),
        'name': playlist_name,
        'songs': [],
        'created_at': datetime.datetime.utcnow()
    })
    
    return jsonify({'status': 'success'})

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user = db.users.find_one({'email': request.form['email']})
        if user and check_password_hash(user['password'], request.form['password']):
            session['user_id'] = str(user['_id'])
            session['is_admin'] = user.get('is_admin', False)
            
            # Admin kontrolü ekle
            if user.get('is_admin'):
                return redirect(url_for('admin_panel'))  # Admin ise panele yönlendir
            
            return redirect(url_for('home'))  # Normal kullanıcılar için
        error = 'Geçersiz e-posta veya şifre'
    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        existing_user = db.users.find_one({'email': request.form['email']})
        if existing_user:
            return render_template('register.html', error='Bu e-posta zaten kayıtlı')
        
        hashed_pw = generate_password_hash(request.form['password'])
        db.users.insert_one({
            'name': request.form['name'],
            'surname': request.form['surname'],
            'email': request.form['email'],
            'password': hashed_pw,
            'is_admin': False
        })
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/api/search')
def search():
    query = request.args.get('q')
    ytmusic = YTMusic()
    results = ytmusic.search(query, filter='songs', limit=5)
    return jsonify(results)

@app.route('/library')
def library():
    playlists = list(db.playlists.find({'user_id': ObjectId(session['user_id'])}))
    return render_template('library.html', playlists=playlists)

@app.route('/admin')
def admin_panel():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    users = list(db.users.find({}))
    return render_template('admin.html', users=users)

@app.route('/player/<video_id>')
def player(video_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    ytmusic = YTMusic()
    try:
        song_data = ytmusic.get_song(video_id)
        video_details = song_data.get('videoDetails', {})

        return render_template(
            'player.html',
            video_id=video_id,
            thumbnail=video_details.get('thumbnail', {}).get('thumbnails', [{}])[0].get('url', ''),
            title=video_details.get('title', 'Bilinmeyen Şarkı'),
            artist=video_details.get('author', 'Bilinmeyen Sanatçı'),
            playlists=list(db.playlists.find({'user_id': ObjectId(session['user_id'])}))
        )
    except Exception as e:
        print(f"Player error: {str(e)}")
        return redirect(url_for('home'))
    
@app.route('/stream/<video_id>')
def stream_audio(video_id):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f'https://www.youtube.com/watch?v={video_id}', download=False)
            audio_url = info['url']
            response = requests.get(audio_url, stream=True)
            return Response(response.iter_content(chunk_size=1024), content_type=response.headers['Content-Type'])
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/api/add_to_playlist', methods=['POST'])
def add_to_playlist():
    data = request.json
    db.playlists.update_one(
        {'_id': ObjectId(data['playlistId'])},
        {'$addToSet': {'songs': data['videoId']}}
    )
    return jsonify({'status': 'success'})

@app.route('/playlist/<playlist_id>')
def playlist_detail(playlist_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    playlist = db.playlists.find_one({
        '_id': ObjectId(playlist_id),
        'user_id': ObjectId(session['user_id'])
    })
    
    if not playlist:
        return "Playlist bulunamadı", 404
    
    ytmusic = YTMusic()
    songs = []
    for video_id in playlist['songs']:
        try:
            song_data = ytmusic.get_song(video_id)
            video_details = song_data.get('videoDetails', {})
            songs.append({
                'title': video_details.get('title', 'Bilinmeyen Şarkı'),
                'artist': video_details.get('author', 'Bilinmeyen Sanatçı'),
                'thumbnail': video_details.get('thumbnail', {}).get('thumbnails', [{}])[0].get('url', ''),
                'videoId': video_id
            })
        except:
            continue
    
    return render_template('playlist_detail.html', 
                         playlist=playlist,
                         songs=songs,
                         playlists=list(db.playlists.find({'user_id': ObjectId(session['user_id'])})))

# Kullanıcı Silme
@app.route('/admin/delete/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    if not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    db.users.delete_one({'_id': ObjectId(user_id)})
    return jsonify({'status': 'success'})

@app.route('/admin/update/<user_id>', methods=['PUT'])
def update_user(user_id):
    if not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    
    # E-posta çakışması kontrolü
    existing_user = db.users.find_one({
        'email': data['email'],
        '_id': {'$ne': ObjectId(user_id)}
    })
    if existing_user:
        return jsonify({'error': 'Bu e-posta zaten kullanılıyor'}), 400

    # Veritabanını güncelle
    result = db.users.update_one(
        {'_id': ObjectId(user_id)},
        {'$set': {
            'name': data['name'],
            'surname': data['surname'],
            'email': data['email']
        }}
    )

    if result.modified_count == 0:
        return jsonify({'error': 'Değişiklik yapılmadı'}), 400

    return jsonify({'status': 'success'})

@app.route('/admin/get/<user_id>')
def get_user(user_id):
    if not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        user = db.users.find_one({'_id': ObjectId(user_id)})
        if not user:
            return jsonify({'error': 'Kullanıcı bulunamadı'}), 404
        
        return jsonify({
            'name': user['name'],
            'surname': user['surname'],
            'email': user['email']
        })
    except Exception as e:
        return jsonify({'error': 'Geçersiz kullanıcı ID'}), 400
    
# app.py'ye bu yeni route'u ekleyin
@app.route('/api/get_user_playlists')
def get_user_playlists():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    playlists = list(db.playlists.find(
        {'user_id': ObjectId(session['user_id'])},
        {'_id': 1, 'name': 1}
    ))
    
    # ObjectId'yi string'e çevir
    processed = [{
        '_id': str(playlist['_id']),
        'name': playlist['name']
    } for playlist in playlists]
    
    return jsonify(processed)

if __name__ == '__main__':
    app.run(debug=True)