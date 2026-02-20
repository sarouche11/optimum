$(document).ready(function() {
    $('.buy-btn-request').on('click', function() {
        var productId = $(this).data('id')
        var productName = $(this).data('name')
        var productPrice = parseFloat($(this).data('price'))
        var redirectUrl = $(this).data('redirect-url')

        // Remplir le modal
        $('#buy-requestModal #product_id').val(productId)
        $('#buy-requestModal #productName').text(productName)
        $('#buy-requestModal #productPrice').text(productPrice)
        $('#buy-requestModal #quantity').val(1)
        $('#buy-requestModal #totalPrice').text(productPrice.toFixed(2))

        // Calcul automatique du total
        $('#buy-requestModal #quantity').off('input').on('input', function() {
            var qty = parseInt($(this).val()) || 1
            $('#buy-requestModal #totalPrice').text((productPrice * qty).toFixed(2))
        })

        // Ouvrir le modal
        $('#buy-requestModal').modal('show')
    })

    // AJAX pour envoyer la requête du modal
    $('#buy-requestModal #buyForm').on('submit', function(e) {
        e.preventDefault()
        var form = $(this)
        var redirectUrl = $('#buy-requestModal #redirectUrl').val() // <--- ici aussi

        $.ajax({
            type: form.attr('method'),
            url: form.attr('action'),
            data: form.serialize(),
            success: function(response) {
                if (response.success) {
                    // Redirection vers list_achat après succès
                    
                    window.location.href = redirectUrl;
                } else {
                    // Afficher une erreur
                    alert('Erreur : ' + response.error)
                }
            },
            error: function(xhr, status, error) {
                alert('Erreur serveur : ' + error)
            }
        })
    })
})