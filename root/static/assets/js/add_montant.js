document.addEventListener('DOMContentLoaded', function() {

    // Tous les boutons "Ajouter" du tableau
    const addButtons = document.querySelectorAll('.btn-add-montant');

    // Le formulaire dans le modal
    const form = document.getElementById('addMontantForm');

    // L'input hidden pour l'ID du profil
    const profilInput = document.getElementById('profil_id_input');

    addButtons.forEach(button => {
        button.addEventListener('click', () => {

            // Récupérer l'ID du profil depuis le data-attribute
            const profilId = button.getAttribute('data-profil');

            // Remplir le champ hidden du formulaire
            profilInput.value = profilId;

            // (Optionnel) Mettre à jour l'action si besoin dynamique
            // form.action = `/root/add_montant/${profilId}/`;

            console.log("Profil ID injecté dans le formulaire =", profilId);
        });
    });

});
