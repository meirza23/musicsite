from pymongo import MongoClient
from werkzeug.security import generate_password_hash

client = MongoClient('mongodb://localhost:27017/')
db = client['mei_music']

# Koleksiyonları Oluştur
db.create_collection('users')
db.users.create_index('email', unique=True)

db.create_collection('playlists')
db.create_collection('likes')

# Admin Kullanıcısı Ekle
admin_pw = generate_password_hash('admin123')
db.users.insert_one({
    'name': 'Admin',
    'email': 'admin@meimusic.com',
    'password': admin_pw,
    'is_admin': True
})