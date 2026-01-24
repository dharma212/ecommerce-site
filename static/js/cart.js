$(document).ready(function () {

    /* ================= ADD TO CART ================= */
    $(document).on("click", ".add-to-cart-btn", function (e) {
        e.preventDefault();
        e.stopImmediatePropagation();

        if (!IS_LOGGED_IN) {
            $("#loginModal").fadeIn();
            return false;
        }

        let btn = $(this);
        let productId = btn.data("product-id");

        $.ajax({
            url: "/cart/add/ajax/",
            type: "POST",
            headers: { "X-CSRFToken": CSRF_TOKEN },
            data: { product_id: productId },
            success: function (response) {
                if (response.success) {
                    btn.text("Added")
                       .removeClass("btn-primary")
                       .addClass("btn-success")
                       .prop("disabled", true);
                }
            }
        });
    });


    /* ================= WISHLIST ================= */
    $(document).on("click", ".wishlist-btn", function (e) {
        e.preventDefault();
        e.stopImmediatePropagation();

        if (!IS_LOGGED_IN) {
            $("#loginModal").fadeIn();
            return false;
        }

        let btn = $(this);
        btn.toggleClass("active");
        btn.find("i").toggleClass("fa-regular fa-solid");
    });


    /* ================= POPUP CLOSE ================= */
    $(document).on("click", ".login-cancel, .close-modal", function () {
        $("#loginModal").fadeOut();
    });

    $(document).on("click", "#loginModal", function (e) {
        if (e.target.id === "loginModal") {
            $(this).fadeOut();
        }
    });

});
