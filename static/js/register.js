document.addEventListener('DOMContentLoaded', () => {
    const registerForm = document.querySelector('.login-form');
    
    registerForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        // Form verilerini topla
        const firstName = registerForm.querySelector('input[placeholder="Ad"]').value;
        const lastName = registerForm.querySelector('input[placeholder="Soyad"]').value;
        const email = registerForm.querySelector('input[type="email"]').value;
        const password = registerForm.querySelector('input[type="password"]').value;
        
        // API simülasyonu
        console.log('Kayıt bilgileri:', { firstName, lastName, email, password });
        
        // Başarılı kayıt sonrası yönlendirme
        alert('Kayıt başarılı! Giriş sayfasına yönlendiriliyorsunuz...');
        window.location.href = '/login';
    });
});