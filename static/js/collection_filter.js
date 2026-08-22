document.addEventListener("DOMContentLoaded", () => {
    const filter = document.getElementById("size-filter");

    const cards = Array.from(
        document.querySelectorAll(".product-grid .product-card")
    );

    if (!filter || !cards.length) {
        return;
    }


    // Collect all available sizes from the products
    const sizes = [
        ...new Set(
            cards
                .map((card) => {
                    const sizeData = card.querySelector(".product-size-data");

                    return sizeData
                        ? sizeData.dataset.size
                        : null;
                })
                .filter(Boolean)
        )
    ];


    // Put common clothing sizes into a sensible order
    const sizeRank = (value) => {
        const size = value.trim().toUpperCase();

        const namedSizes = {
            "XXS": 10,

            "XS": 20,

            "S": 30,
            "SMALL": 30,

            "M": 40,
            "MEDIUM": 40,

            "L": 50,
            "LARGE": 50,

            "XL": 60,
            "X-LARGE": 60,

            "XXL": 70,
            "2XL": 70,

            "XXXL": 80,
            "3XL": 80,

            "ONE SIZE": 900,
            "ONE SIZE FITS ALL": 900
        };


        if (
            Object.prototype.hasOwnProperty.call(
                namedSizes,
                size
            )
        ) {
            return namedSizes[size];
        }


        // Handles numerical sizes such as UK 8, 10, 12, 14 etc.
        const numericSize = parseFloat(
            size.replace(/[^\d.]/g, "")
        );

        if (!Number.isNaN(numericSize)) {
            return 100 + numericSize;
        }


        return 500;
    };


    // Sort the filter choices
    sizes.sort((a, b) => {
        return sizeRank(a) - sizeRank(b);
    });


    // Add each available size to the dropdown
    sizes.forEach((size) => {
        const option = document.createElement("option");

        option.value = size;
        option.textContent = size;

        filter.appendChild(option);
    });


    // Hide the filter if this collection has no size data
    if (!sizes.length) {
        const tools = filter.closest(".collection-tools");

        if (tools) {
            tools.hidden = true;
        }

        return;
    }


    // Filter the cards when the customer chooses a size
    filter.addEventListener("change", () => {
        const selectedSize = filter.value;

        cards.forEach((card) => {
            const sizeData = card.querySelector(
                ".product-size-data"
            );

            const productSize = sizeData
                ? sizeData.dataset.size
                : null;

            const shouldShow =
                selectedSize === "all" ||
                productSize === selectedSize;

            if (shouldShow) {
                card.hidden = false;
                card.style.display = "";
            } else {
                card.hidden = true;
                card.style.display = "none";
            }
        });
    });
});