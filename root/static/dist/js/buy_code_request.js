$(document).ready(function() {
    $('.buy-btn-code-request').on('click', function() {

        var productId = $(this).data('id')
        var productName = $(this).data('name')
        var productPrice = parseFloat($(this).data('price'))
        var redirectUrl = $(this).data('redirect-url')

        // Remplir le modal
        $('#buyCodeRequestModal #product_id').val(productId)
        $('#buyCodeRequestModal #productName').text(productName)
        $('#buyCodeRequestModal #productPrice').text(productPrice)
        $('#buyCodeRequestModal #quantity').val(1)
        $('#buyCodeRequestModal #totalPrice').text(productPrice.toFixed(2))

        // Calcul automatique du total
        $('#buyCodeRequestModal #quantity').off('input').on('input', function() {
            let quantity = parseInt($(this).val()) || 1

            if (quantity < 1) quantity = 1

            $(this).val(quantity)
            $('#buyCodeRequestModal #totalPrice').text((productPrice * quantity).toFixed(2))
        })

        // Ouvrir le modal
        $('#buyCodeRequestModal').modal('show')
    })



    // AJAX pour envoyer la requête du modal
    $('#buyCodeRequestModal #buyForm').on('submit', function(e) {
        e.preventDefault()
        var form = $(this)
        var redirectUrl = $('#buyCodeRequestModal #redirectUrl').val() // <--- ici aussi

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




