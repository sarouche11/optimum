document.getElementById('copyCodesBtn').addEventListener('click', function() {
    // Récupère tous les codes dans le tableau
    const codeCells = document.querySelectorAll('#codesTable .activation-code');
    
    if (codeCells.length === 0) return;

    // Crée le texte à copier
    const codes = Array.from(codeCells)
                       .map(td => td.textContent.trim())
                       .join('\n');

    // Crée une zone temporaire pour la sélection
    const textarea = document.createElement('textarea');
    textarea.value = codes;
    document.body.appendChild(textarea);

    textarea.select();
    textarea.setSelectionRange(0, 99999); // pour mobile
    document.execCommand('copy'); // copie dans le presse-papiers

    // Supprime la zone temporaire
    document.body.removeChild(textarea);

    // Met en surbrillance les codes pour montrer la copie
    codeCells.forEach(td => {
        td.style.backgroundColor = '#d1ffd1'; // vert clair
    });

    // Remet la couleur normale après 1.5s
    setTimeout(() => {
        codeCells.forEach(td => {
            td.style.backgroundColor = '';
        });
    }, 1500);
});