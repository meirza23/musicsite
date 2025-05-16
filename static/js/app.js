// Menü Toggle
document.querySelector('.menu-icon').addEventListener('click', () => {
    document.querySelector('.sidebar').classList.toggle('active');
});

// Profil Menüsü
document.querySelector('.profile-icon').addEventListener('click', () => {
    document.querySelector('.profile-menu').classList.toggle('show');
});

// Arama Fonksiyonu
document.getElementById('searchInput')?.addEventListener('input', async (e) => {
    const response = await fetch(`/api/search?q=${encodeURIComponent(e.target.value)}`);
    const results = await response.json();
    
    const musicGrid = document.querySelector('.music-grid');
    if (musicGrid) {
        musicGrid.innerHTML = results.map(song => `
            <div class="music-card" onclick="window.location.href='/player/${song.videoId}'">
                <div class="album-art">
                    <img src="${song.thumbnails[0].url}">
                    <div class="play-overlay">
                        <i class="fas fa-play"></i>
                    </div>
                </div>
                <h4>${song.title}</h4>
                <p>${song.artists[0]?.name || 'Bilinmeyen Sanatçı'}</p>
            </div>
        `).join('');
    }
});

// Playlist'e Ekleme
function addToPlaylist(videoId) {
    const playlistId = document.getElementById('playlistSelect').value;
    if (playlistId) {
        fetch('/api/add_to_playlist', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ playlistId, videoId })
        }).then(response => {
            if (response.ok) alert('Şarkı eklendi!');
            else alert('Hata oluştu!');
        });
    }
}