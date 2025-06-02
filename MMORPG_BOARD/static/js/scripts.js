document.addEventListener('DOMContentLoaded', function() {
    // Подтверждение удаления
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Вы уверены, что хотите удалить?')) {
                e.preventDefault();
            }
        });
    });

    // Валидация форм
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const textareas = form.querySelectorAll('textarea');
            let isValid = true;

            textareas.forEach(textarea => {
                if (textarea.value.trim() === '') {
                    textarea.classList.add('error');
                    isValid = false;
                } else {
                    textarea.classList.remove('error');
                }
            });

            if (!isValid) {
                e.preventDefault();
                alert('Пожалуйста, заполните все обязательные поля');
            }
        });
    });

    // Предпросмотр изображений перед загрузкой
    const imageInputs = document.querySelectorAll('input[type="file"][accept="image/*"]');
    imageInputs.forEach(input => {
        input.addEventListener('change', function() {
            const preview = this.nextElementSibling;
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    preview.src = e.target.result;
                    preview.style.display = 'block';
                }
                reader.readAsDataURL(this.files[0]);
            }
        });
    });
});

// Функция для фильтрации откликов
function filterResponses(adId) {
    const url = new URL(window.location.href);
    if (adId) {
        url.searchParams.set('ad_filter', adId);
    } else {
        url.searchParams.delete('ad_filter');
    }
    window.location.href = url.toString();
}