$(document).ready(function() {
    $('.buy-btn').on('click', function() {
        var productId = $(this).data('id')
        var productName = $(this).data('name')
        var productPrice = parseFloat($(this).data('price'))
        var productStock = parseInt($(this).data('stock'))

        // Remplir le modal
        $('#product_id').val(productId)
        $('#productName').text(productName)
        $('#productPrice').text(productPrice)
        $('#productStock').text(productStock)
        $('#quantity').val(1)
        $('#quantity').attr('max', productStock)
        $('#totalPrice').text(productPrice.toFixed(2))

        // Calcul automatique du total
        $('#quantity').off('input').on('input', function() {
            let quantity = parseInt($(this).val()) || 1
            if (quantity > productStock) quantity = productStock
            else if (quantity < 1) quantity = 1
            $(this).val(quantity)
            $('#totalPrice').text((productPrice * quantity).toFixed(2))
        })

        // Ouvrir le modal manuellement
        $('#buyModal').modal('show')
    })
})
