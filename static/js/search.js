$(document).ready(function () {
  const $input = $("#searchInput");
  const $resultsBox = $("#searchResults");

  if (!$input.length || !$resultsBox.length) return;

  $input.on("keyup", function () {
    const query = $.trim($(this).val());

    if (query === "") {
      $resultsBox.empty().hide();
      return;
    }

    $.ajax({
      url: "/user/ajax/product-search/",
      type: "GET",
      data: { q: query },
      dataType: "json",
      success: function (data) {
        $resultsBox.empty().show(); 

        if (!data.results || data.results.length === 0) {
          $resultsBox.append('<div class="no-result">No product found</div>');
          return;
        }

        $.each(data.results, function (index, product) {
          const $link = $("<a></a>", {
            href: "/product/view-product/" + product.id + "/",
            class: "search-item",
            text: product.name
          });
          $resultsBox.append($link);
        });
      },
      error: function () {
        $resultsBox.hide();
      }
    });
  });

  // Hide results when clicking outside
  $(document).on("click", function (e) {
    if (!$(e.target).closest(".search").length) {
      $resultsBox.hide();
    }
  });
});