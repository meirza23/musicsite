document.addEventListener('DOMContentLoaded', () => {
    // Kapatma butonu ve overlay
    const closeBtn = document.querySelector('.close-btn');
    const overlay = document.querySelector('.modal-overlay');

    const closeModal = () => {
        window.location.href = 'home_page.html'; // Ana sayfaya yönlendir
    };

    closeBtn.addEventListener('click', closeModal);

    // Overlay'e tıklanınca kapat
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) closeModal();
    });

    // ESC tuşu ile kapat
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeModal();
    });
});