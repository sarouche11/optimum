
console.log(" Le Fichier JS est bien chargé !");


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener("DOMContentLoaded", function () {
    const notifDropdown = document.getElementById("notificationDropdown");
    const notifIcon = document.querySelector(".notif-dot");

    if (notifDropdown) {
        const notifUrl = notifDropdown.dataset.url;
        const csrfToken = getCookie('csrftoken');  // récupère le token depuis cookie

        notifDropdown.addEventListener("click", function () {
            console.log("Avant déclenchement"); 
            fetch(notifUrl, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken,
                    "X-Requested-With": "XMLHttpRequest"
                }
            }).then(response => {
                if (response.ok && notifIcon) {
                    notifIcon.style.display = "none";
                    console.log("Après déclenchement");
                }
            });
        });
    }
});
