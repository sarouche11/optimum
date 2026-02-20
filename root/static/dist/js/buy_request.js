$(document).ready(function() {
    $('.buy-btn-request').on('click', function() {
        var productId = $(this).data('id')
        var productName = $(this).data('name')
        var productPrice = parseFloat($(this).data('price'))

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

        // Ouvrir le modal manuellement
        $('#buy-requestModal').modal('show')
    })
})
