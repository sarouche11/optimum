// static/dist/js/btn_copy.js
function copyAllCodes() {
    const codeElements = document.querySelectorAll('.code-item');

    if (codeElements.length === 0) return;

    // Récupère le texte de tous les codes
    const codes = Array.from(codeElements)
                       .map(el => el.innerText.trim())
                       .join("\n");

    // Copie dans le presse-papiers
    navigator.clipboard.writeText(codes)
        .then(() => {
            // Met en surbrillance pour montrer que c'est copié
            codeElements.forEach(el => el.style.backgroundColor = '#d1ffd1');

            // Remet la couleur normale après 1.5s
            setTimeout(() => {
                codeElements.forEach(el => el.style.backgroundColor = '');
            }, 1500);
        })
        .catch(() => {
            // Si la copie échoue, rien ne se passe
        });
}
