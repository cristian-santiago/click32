// qr_code.js - Preview do QR Code
function updateQRCodePreview() {
    const img = document.getElementById('qrCodePreview');
    if (img) {
        img.src = img.src.split('?')[0] + '?t=' + Date.now();
    }
}

// Inicializa se a imagem existir
document.addEventListener('DOMContentLoaded', function() {
    const qrImg = document.getElementById('qrCodePreview');
    if (qrImg) {
        // Garante carregamento fresco
        qrImg.src = qrImg.src.split('?')[0] + '?t=' + Date.now();
    }
});