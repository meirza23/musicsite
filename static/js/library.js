

// Filtre seçeneklerini yönet
document.querySelectorAll('.filter-option').forEach(option => {
    option.addEventListener('click', function() {
        document.querySelector('.filter-option.active').classList.remove('active');
        this.classList.add('active');
    });
});

// Playlist kartlarına tıklama
document.querySelectorAll('.playlist-card').forEach(card => {
    card.addEventListener('click', function(e) {
        if(!e.target.closest('.play-overlay')) {
            // Playlist detay sayfasına yönlendirme
            console.log('Playlist seçildi');
        }
    });
});