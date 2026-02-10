$(document).ready(function () {

    /* ================= INIT CART COUNT ================= */
    updateCartCount();

    /* ========== INIT CART & WISHLIST ON PAGE LOAD ========== */
    if (IS_LOGGED_IN) {
        $.ajax({
            url: "/cart/ajax/get_items/",
            type: "GET",
            success: function (response) {

                // Cart buttons
                response.cart.forEach(productId => {
                    let btn = $('.add-to-cart-btn[data-product-id="' + productId + '"]');
                    btn.text("Added")
                        .removeClass("btn-primary")
                        .addClass("btn-success")
                        .prop("disabled", true);
                });

                // Wishlist buttons
                response.wishlist.forEach(productId => {
                    let btn = $('.wishlist-button[data-product-id="' + productId + '"]');
                    btn.addClass("active");
                    btn.find("i")
                        .removeClass("fa-regular")
                        .addClass("fa-solid")
                        .css("color", "red");
                });
            }
        });
    }

    /* ================= CLOSE LOGIN MODAL ================= */
    $(document).on("click", ".close-modal", function () {
        $("#loginModal").fadeOut();
    });

    $(document).on("click", "#loginModal", function (e) {
        if (e.target.id === "loginModal") {
            $(this).fadeOut();
        }
    });

    /* ================= ADD TO CART ================= */
    $(document).on("click", ".add-to-cart-btn", function (e) {
        e.preventDefault();
        e.stopImmediatePropagation();

        if (!IS_LOGGED_IN) {
            $("#loginModal").fadeIn();
            return;
        }

        let btn = $(this);
        let productId = btn.data("product-id");

        btn.text("Added")
            .removeClass("btn-primary")
            .addClass("btn-success")
            .prop("disabled", true);

        $.ajax({
            url: "/cart/ajax/add/",
            type: "POST",
            headers: { "X-CSRFToken": CSRF_TOKEN },
            data: { product_id: productId },

            success: function () {
                updateCartCount(); // ✅ MAIN FIX
            },

            error: function () {
                btn.text("Add to Cart")
                    .removeClass("btn-success")
                    .addClass("btn-primary")
                    .prop("disabled", false);
            }
        });
    });

    /* ================= REMOVE FROM CART ================= */
    $(document).on("click", ".remove-from-cart-btn", function (e) {
        e.preventDefault();

        let itemId = $(this).data("item-id");
        let cartItem = $(this).closest(".cart-item");

        $.ajax({
            url: "/cart/ajax/remove/",
            type: "POST",
            headers: { "X-CSRFToken": CSRF_TOKEN },
            data: { item_id: itemId },

            success: function (response) {
                if (response.success) {
                    cartItem.remove();
                    updateCartCount();
                }
            }
        });
    });

   /* ================= UPDATE QUANTITY ================= */
$(document).on("click", ".update-qty", function (e) {
    e.preventDefault();

    let btn = $(this);
    let itemId = btn.data("item-id");
    let action = btn.data("action");

    let qtySpan = $("#qty-" + itemId);
    let cartItem = btn.closest(".cart-item");

    let minusBtn = cartItem.find('[data-action="minus"]');
    let plusBtn = cartItem.find('[data-action="plus"]');

    $.ajax({
        url: "/cart/ajax/update-qty/",
        type: "POST",
        headers: { "X-CSRFToken": CSRF_TOKEN },
        data: {
            item_id: itemId,
            action: action
        },

        success: function (response) {
            if (response.success) {

                let qty = response.quantity;
                qtySpan.text(qty);

                /* 🔽 MINUS BUTTON LOGIC */
                if (qty <= 1) {
                    minusBtn.prop("disabled", true);
                } else {
                    minusBtn.prop("disabled", false);
                }

                /* 🔼 PLUS BUTTON LOGIC */
                if (response.stock_reached) {
                    plusBtn.prop("disabled", true);
                } else {
                    plusBtn.prop("disabled", false);
                }

                /* 💰 UPDATE TOTALS */
                $(".total-price-val").text("₹" + response.total_price);
                $("#grand-total").text("₹" + response.total_price);

                updateCartCount();
            }
        }
    });
});


    /* ================= WISHLIST TOGGLE ================= */
    $(document).on("click", ".wishlist-button", function (e) {
        e.preventDefault();

        if (!IS_LOGGED_IN) {
            $("#loginModal").fadeIn();
            return;
        }

        let btn = $(this);
        let productId = btn.data("product-id");
        let icon = btn.find("i");

        $.ajax({
            url: "/cart/wishlist/ajax/toggle/",
            type: "POST",
            headers: { "X-CSRFToken": CSRF_TOKEN },
            data: { product_id: productId },

            success: function (response) {
                if (response.status === "added") {
                    btn.addClass("active");
                    icon.removeClass("fa-regular")
                        .addClass("fa-solid")
                        .css("color", "red");
                } else {
                    btn.removeClass("active");
                    icon.removeClass("fa-solid")
                        .addClass("fa-regular")
                        .css("color", "");
                }
            }
        });
    });

});

/* ================= CART COUNT ================= */
function updateCartCount() {
    if (!IS_LOGGED_IN) {
        $("#cart-count").text(0).hide();
        return;
    }

    $.ajax({
        url: CART_COUNT_URL,
        type: "GET",
        success: function (response) {
            const badge = $("#cart-count");

            badge.text(response.count);
            response.count > 0 ? badge.show() : badge.hide();

            $(".total-price-val").text("₹" + response.total);
            $("#grand-total").text("₹" + response.total);
        }
    });
}

/* ================= SAFE PAYMENT BUTTON ================= */
document.addEventListener("DOMContentLoaded", function () {
    const btn = document.querySelector(".btn-orange");
    if (btn) {
        btn.addEventListener("click", function (e) {
            e.preventDefault();
            showPayment();
        });
    }
});

function showPayment() {
    const address = document.getElementById("address-section");
    const payment = document.getElementById("payment-section");
    if (!address || !payment) return;

    address.style.opacity = "0.6";
    address.style.pointerEvents = "none";
    payment.classList.remove("d-none");

    window.scrollTo({
        top: payment.offsetTop - 100,
        behavior: "smooth"
    });
}
$(document).ready(function () {

    /* ================= INIT ================= */
    if (IS_LOGGED_IN) {
        updateCartCount();

        $.get("/cart/ajax/get_items/", function (response) {

            // cart buttons
            response.cart.forEach(id => {
                $('.add-to-cart-btn[data-product-id="' + id + '"]')
                    .text("Added")
                    .removeClass("btn-primary")
                    .addClass("btn-success")
                    .prop("disabled", true);
            });

            // wishlist buttons
            response.wishlist.forEach(id => {
                let btn = $('.wishlist-button[data-product-id="' + id + '"]');
                btn.addClass("active");
                btn.find("i").removeClass("fa-regular").addClass("fa-solid").css("color", "red");
            });
        });
    }

    /* ================= ADD TO CART ================= */
    $(document).on("click", ".add-to-cart-btn", function (e) {
        e.preventDefault();

        if (!IS_LOGGED_IN) {
            $("#loginModal").fadeIn();
            return;
        }

        let btn = $(this);
        let productId = btn.data("product-id");

        btn.text("Added").removeClass("btn-primary").addClass("btn-success").prop("disabled", true);

        $.ajax({
            url: "/cart/ajax/add/",
            type: "POST",
            headers: { "X-CSRFToken": CSRF_TOKEN },
            data: { product_id: productId },
            success: updateCartCount,
            error: function () {
                btn.text("Add to Cart").removeClass("btn-success").addClass("btn-primary").prop("disabled", false);
            }
        });
    });

    /* ================= REMOVE FROM CART ================= */
    $(document).on("click", ".remove-from-cart-btn", function (e) {
        e.preventDefault();

        let btn = $(this);
        let itemId = btn.data("item-id");
        let cartItem = btn.closest(".cart-item");

        $.ajax({
            url: "/cart/ajax/remove/",
            type: "POST",
            headers: { "X-CSRFToken": CSRF_TOKEN },
            data: { item_id: itemId },
            success: function () {
                cartItem.fadeOut(300, function () {
                    $(this).remove();
                    updateCartCount();
                });
            }
        });
    });

    /* ================= WISHLIST TOGGLE ================= */
    $(document).on("click", ".wishlist-button", function (e) {
        e.preventDefault();

        if (!IS_LOGGED_IN) {
            $("#loginModal").fadeIn();
            return;
        }

        let btn = $(this);
        let productId = btn.data("product-id");
        let icon = btn.find("i");

        $.ajax({
            url: "/cart/wishlist/ajax/toggle/",
            type: "POST",
            headers: { "X-CSRFToken": CSRF_TOKEN },
            data: { product_id: productId },
            success: function (res) {
                if (res.status === "added") {
                    btn.addClass("active");
                    icon.removeClass("fa-regular").addClass("fa-solid").css("color", "red");
                } else {
                    btn.removeClass("active");
                    icon.removeClass("fa-solid").addClass("fa-regular").css("color", "");
                }
            }
        });
    });

    /* ================= REMOVE FROM WISHLIST ================= */
    $(document).on("click", ".remove-from-wishlist-btn", function (e) {
        e.preventDefault();

        let btn = $(this);
        let itemId = btn.data("item-id");
        let card = btn.closest(".wishlist-card");

        $.ajax({
            url: "/cart/ajax/wishlist/remove/",
            type: "POST",
            headers: { "X-CSRFToken": CSRF_TOKEN },
            data: { item_id: itemId },
            success: function (res) {
                if (res.success) {
                    card.fadeOut(300, () => card.remove());
                    $(".wishlist-title").text("My Wishlist (" + res.wishlist_count + ")");
                }
            }
        });
    });

    /* ================= MOVE WISHLIST → CART ================= */
    $(document).on("click", ".move-to-cart-btn", function () {

        let btn = $(this);
        let itemId = btn.data("item-id");
        let url = btn.data("url");
        let card = btn.closest(".wishlist-card");

        $.ajax({
            url: url,
            type: "POST",
            headers: { "X-CSRFToken": CSRF_TOKEN },
            data: { item_id: itemId },
            success: function (res) {
                if (res.success) {
                    card.fadeOut(300, () => card.remove());
                    updateCartCount();
                }
            }
        });
    });

});


/* ================= CART COUNT ================= */
function updateCartCount() {
    if (!IS_LOGGED_IN) {
        $("#cart-count").hide();
        return;
    }

    $.get(CART_COUNT_URL, function (res) {
        let badge = $("#cart-count");

        badge.text(res.count);
        res.count > 0 ? badge.show() : badge.hide();

        $(".total-price-val").text("₹" + res.total);
        $("#grand-total").text("₹" + res.total);
    });
}
