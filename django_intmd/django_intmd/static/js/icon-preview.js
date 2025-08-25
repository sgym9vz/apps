document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.querySelector('.icon-input');
    if (!fileInput) return;
    
    const previewContainer = document.createElement('div');
    previewContainer.className = 'icon-preview-container';
    previewContainer.style.marginTop = '10px';
    previewContainer.style.display = 'none';
    
    const previewImg = document.createElement('img');
    previewImg.className = 'icon-preview-image';
    previewImg.style.width = '100px';
    previewImg.style.height = '100px';
    previewImg.style.objectFit = 'cover';
    previewImg.style.borderRadius = '50%';
    previewImg.style.border = '3px solid #f0f0f0';
    
    previewContainer.appendChild(previewImg);
    
    fileInput.parentNode.insertBefore(previewContainer, fileInput.nextSibling);
    
    fileInput.addEventListener('change', function() {
        if (this.files && this.files[0]) {
            const reader = new FileReader();
            
            reader.onload = function(e) {
                previewImg.src = e.target.result;
                previewContainer.style.display = 'block';
            };
            
            reader.readAsDataURL(this.files[0]);
        } else {
            previewContainer.style.display = 'none';
        }
    });
    
    const clearCheckbox = document.getElementById('icon-clear_id');
    if (clearCheckbox) {
        clearCheckbox.addEventListener('change', function() {
            if (this.checked) {
                const currentIconPreview = document.querySelector('.current-icon-preview');
                if (currentIconPreview) {
                    currentIconPreview.style.opacity = '0.3';
                }
            } else {
                const currentIconPreview = document.querySelector('.current-icon-preview');
                if (currentIconPreview) {
                    currentIconPreview.style.opacity = '1';
                }
            }
        });
    }
});
