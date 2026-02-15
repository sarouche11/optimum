document.addEventListener("DOMContentLoaded", function() {

    let form = document.getElementById('buyForm');
    if (!form) return; // sécurité

    form.addEventListener('submit', function(e) {
        e.preventDefault();

        fetch(form.action, {
            method: "POST",
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: new FormData(form)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                let container = document.getElementById("codesContainer");
                container.innerHTML = "";
                data.codes.forEach(code => {
                    container.innerHTML += `
                        <div class="list-group-item text-center fw-bold text-success code-item">
                            ${code}
                        </div>
                    `;
                });

                // Cacher le modal d'achat
                let buyModalEl = document.getElementById('buyModal');
                let buyModal = bootstrap.Modal.getInstance(buyModalEl);
                if (buyModal) buyModal.hide();

                // Ouvrir le modal résultat
                let resultModalEl = document.getElementById('resultBuyModal');
                let resultModal = new bootstrap.Modal(resultModalEl);
                resultModal.show();

                // 🔥 Forcer le reload quand on clique sur n'importe quel bouton de fermeture
                resultModalEl.querySelectorAll('[data-bs-dismiss="modal"]').forEach(btn => {
                    btn.addEventListener('click', function() {
                        location.reload();
                    });
                });

            } else {
                alert(data.error);
            }
        });
    });

});
