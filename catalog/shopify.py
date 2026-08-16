import os

import requests


SHOPIFY_STORE_DOMAIN = os.getenv("SHOPIFY_STORE_DOMAIN")
SHOPIFY_STOREFRONT_TOKEN = os.getenv("SHOPIFY_STOREFRONT_TOKEN")
SHOPIFY_API_VERSION = os.getenv("SHOPIFY_API_VERSION", "2026-07")


def shopify_query(query, variables=None):
    """
    Send a GraphQL request to the Shopify Storefront API.
    """

    if not SHOPIFY_STORE_DOMAIN or not SHOPIFY_STOREFRONT_TOKEN:
        raise RuntimeError(
            "Shopify environment variables are not configured."
        )

    url = (
        f"https://{SHOPIFY_STORE_DOMAIN}"
        f"/api/{SHOPIFY_API_VERSION}/graphql.json"
    )

    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Storefront-Access-Token": SHOPIFY_STOREFRONT_TOKEN,
    }

    response = requests.post(
        url,
        headers=headers,
        json={
            "query": query,
            "variables": variables or {},
        },
        timeout=10,
    )

    response.raise_for_status()

    payload = response.json()

    if payload.get("errors"):
        raise RuntimeError(payload["errors"])

    return payload["data"]


PRODUCT_FIELDS = """
    id
    title
    handle
    description
    descriptionHtml
    availableForSale

    featuredImage {
        url
        altText
    }

    images(first: 20) {
        nodes {
            url
            altText
        }
    }

    selectedOrFirstAvailableVariant {
        id
        sku
        title
        availableForSale

        price {
            amount
            currencyCode
        }
    }
"""


def get_products():
    """
    Return products available through the Shopify storefront.
    """

    query = f"""
    query GetProducts {{
      products(first: 50) {{
        nodes {{
          {PRODUCT_FIELDS}
        }}
      }}
    }}
    """

    data = shopify_query(query)

    return data["products"]["nodes"]


def get_product_by_handle(handle):
    """
    Return a single Shopify product using its handle.
    """

    query = f"""
    query GetProduct($handle: String!) {{
      product(handle: $handle) {{
        {PRODUCT_FIELDS}
      }}
    }}
    """

    data = shopify_query(
        query,
        {
            "handle": handle,
        },
    )

    return data["product"]


def get_collection_by_handle(handle):
    """
    Return a Shopify collection and the products within it.
    """

    query = f"""
    query GetCollection($handle: String!) {{
      collection(handle: $handle) {{
        id
        title
        handle
        description

        products(first: 50) {{
          nodes {{
            {PRODUCT_FIELDS}
          }}
        }}
      }}
    }}
    """

    data = shopify_query(
        query,
        {
            "handle": handle,
        },
    )

    return data["collection"]


def create_cart(variant_id, quantity=1):
    """
    Create a new Shopify cart containing a product variant.
    """

    query = """
    mutation CartCreate($lines: [CartLineInput!]) {
      cartCreate(
        input: {
          lines: $lines
        }
      ) {
        cart {
          id
          checkoutUrl
          totalQuantity

          lines(first: 20) {
            nodes {
              id
              quantity

              merchandise {
                ... on ProductVariant {
                  id
                  title

                  product {
                    title
                    handle
                  }

                  price {
                    amount
                    currencyCode
                  }
                }
              }
            }
          }
        }

        userErrors {
          field
          message
        }
      }
    }
    """

    data = shopify_query(
        query,
        {
            "lines": [
                {
                    "merchandiseId": variant_id,
                    "quantity": quantity,
                }
            ]
        },
    )

    result = data["cartCreate"]

    if result["userErrors"]:
        raise RuntimeError(result["userErrors"])

    return result["cart"]


def add_cart_line(cart_id, variant_id, quantity=1):
    """
    Add another product variant to an existing Shopify cart.
    """

    query = """
    mutation CartLinesAdd(
      $cartId: ID!,
      $lines: [CartLineInput!]!
    ) {
      cartLinesAdd(
        cartId: $cartId,
        lines: $lines
      ) {
        cart {
          id
          checkoutUrl
          totalQuantity

          lines(first: 20) {
            nodes {
              id
              quantity

              merchandise {
                ... on ProductVariant {
                  id
                  title

                  product {
                    title
                    handle
                  }

                  price {
                    amount
                    currencyCode
                  }
                }
              }
            }
          }
        }

        userErrors {
          field
          message
        }
      }
    }
    """

    data = shopify_query(
        query,
        {
            "cartId": cart_id,
            "lines": [
                {
                    "merchandiseId": variant_id,
                    "quantity": quantity,
                }
            ],
        },
    )

    result = data["cartLinesAdd"]

    if result["userErrors"]:
        raise RuntimeError(result["userErrors"])

    return result["cart"]

    def get_cart(cart_id):
        query = """
    query GetCart($cartId: ID!) {
      cart(id: $cartId) {
        id
        checkoutUrl
        totalQuantity

        cost {
          subtotalAmount {
            amount
            currencyCode
          }

          totalAmount {
            amount
            currencyCode
          }
        }

        lines(first: 50) {
          nodes {
            id
            quantity

            merchandise {
              ... on ProductVariant {
                id
                title

                price {
                  amount
                  currencyCode
                }

                product {
                  title
                  handle

                  featuredImage {
                    url
                    altText
                  }
                }
              }
            }
          }
        }
      }
    }
    """

    data = shopify_query(
        query,
        {
            "cartId": cart_id,
        },
    )

    return data["cart"]


def remove_cart_line(cart_id, line_id):
    query = """
    mutation CartLinesRemove(
      $cartId: ID!,
      $lineIds: [ID!]!
    ) {
      cartLinesRemove(
        cartId: $cartId,
        lineIds: $lineIds
      ) {
        cart {
          id
          checkoutUrl
          totalQuantity

          cost {
            subtotalAmount {
              amount
              currencyCode
            }

            totalAmount {
              amount
              currencyCode
            }
          }

          lines(first: 50) {
            nodes {
              id
              quantity

              merchandise {
                ... on ProductVariant {
                  id
                  title

                  price {
                    amount
                    currencyCode
                  }

                  product {
                    title
                    handle

                    featuredImage {
                      url
                      altText
                    }
                  }
                }
              }
            }
          }
        }

        userErrors {
          field
          message
        }
      }
    }
    """

    data = shopify_query(
        query,
        {
            "cartId": cart_id,
            "lineIds": [line_id],
        },
    )

    result = data["cartLinesRemove"]

    if result["userErrors"]:
        raise RuntimeError(result["userErrors"])

    return result["cart"]