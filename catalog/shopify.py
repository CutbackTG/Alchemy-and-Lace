import os

import requests


SHOPIFY_STORE_DOMAIN = os.getenv("SHOPIFY_STORE_DOMAIN")
SHOPIFY_STOREFRONT_TOKEN = os.getenv("SHOPIFY_STOREFRONT_TOKEN")
SHOPIFY_API_VERSION = os.getenv("SHOPIFY_API_VERSION", "2026-07")


def shopify_query(query, variables=None):
    if not SHOPIFY_STORE_DOMAIN or not SHOPIFY_STOREFRONT_TOKEN:
        raise RuntimeError("Shopify environment variables are not configured.")

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