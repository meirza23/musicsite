function togglePassword(btn) {
    const input = btn.previousElementSibling;
    const isVisible = input.type === 'text';
    
    input.type = isVisible ? 'password' : 'text';
    btn.textContent = isVisible ? '👁️' : '🔓';
    btn.style.color = isVisible ? '#B3B3B3' : '#FFD700';
}

function deleteUser(btn) {
    const row = btn.closest('tr');
    if(confirm('Bu kullanıcıyı silmek istediğinize emin misiniz?')) {
        row.remove();
    }
}

function openAddModal() {
    document.getElementById('addModal').style.display = 'block';
}

function closeAddModal() {
    document.getElementById('addModal').style.display = 'none';
}

function addUser(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    
    const name = formData.get('name').trim();
    const surname = formData.get('surname').trim();
    const email = formData.get('email').trim();
    const password = formData.get('password').trim();

    if(!name || !surname || !email || !password) {
        alert('Lütfen tüm alanları doldurun!');
        return;
    }

    const newRow = document.createElement('tr');
    newRow.innerHTML = `
        <td>${name}</td>
        <td>${surname}</td>
        <td>${email}</td>
        <td>
            <div class="password-field">
                <input type="password" value="${password}" class="pwd-input">
                <button class="toggle-pwd" onclick="togglePassword(this)">👁️</button>
            </div>
        </td>
        <td>
            <button class="btn btn-edit" onclick="editUser(this)">Düzenle</button>
            <button class="btn btn-delete" onclick="deleteUser(this)">Sil</button>
        </td>
    `;

    document.querySelector('.user-table tbody').appendChild(newRow);
    e.target.reset();
    closeAddModal();
}

function editUser(btn) {
    const row = btn.closest('tr');
    const cells = Array.from(row.querySelectorAll('td')).slice(0, 4);
    const isEditing = row.classList.contains('editing');

    if (!isEditing) {
        cells.forEach((cell, index) => {
            let value;
            if (index === 3) { // Şifre hücresi
                const input = cell.querySelector('.pwd-input');
                value = input ? input.value : '';
            } else {
                value = cell.textContent;
            }
            const inputType = index === 2 ? 'email' : 'text';
            cell.innerHTML = `<input type="${inputType}" value="${value}" style="width:${cell.offsetWidth}px">`;
        });
        row.classList.add('editing');
        btn.textContent = 'Kaydet';
        btn.classList.replace('btn-edit', 'btn-add');
    } else {
        cells.forEach((cell, index) => {
            const input = cell.querySelector('input');
            const value = input.value;
            if (index === 3) { // Şifre hücresini yeniden oluştur
                cell.innerHTML = `
                    <div class="password-field">
                        <input type="password" value="${value}" class="pwd-input">
                        <button class="toggle-pwd" onclick="togglePassword(this)">👁️</button>
                    </div>
                `;
            } else {
                cell.textContent = value;
            }
        });
        row.classList.remove('editing');
        btn.textContent = 'Düzenle';
        btn.classList.replace('btn-add', 'btn-edit');
    }
}

window.onclick = function(event) {
    const modal = document.getElementById('addModal');
    if(event.target == modal) {
        closeAddModal();
    }
};