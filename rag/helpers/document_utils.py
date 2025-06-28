from langchain.schema import Document
import helpers.cleaning as c
import json
import locale

def generate_product_documents(products:list[dict], attributes_data : dict) -> list[Document]:
    return [Document(page_content=product_page_content(product=product, attributes_data=attributes_data), 
                     metadata={
                         "id": product["id"],
                         "product_type" : product["product_type"],
                         "brand_name" : format_brand(product["brand_name"]),  
                         "category_name" : format_category(product["category_name"]),
                         "sub_category_name" : format_category(product["sub_category_name"]),
                         "seller_id" : product["seller_id"],
                         "price" : product["price"], 
                         "discount" : product["discount"], 
                         "shipping_fee" : product["shipping_fee"], 
                         "weight" : product["weight"]
                     }) for product in products]

def product_page_content(product:dict, attributes_data : dict) -> str :
    format = f"""\
**Product Name** : {product["name"]}

**Description** : {c.clean_html(product["description"])}

Product "{product["name"]}" falls under the {format_category(product["category_name"])} > {format_category(product["sub_category_name"])} category, from the brand {format_brand(product["brand_name"])}. It comes with {product.get("warranty_policy") or "no warranty specified"}. {format_product_status(product=product)}

**Key features and specifications include**:
{format_attributes(product["attributes_value"], attributes_data=attributes_data)}
Weight: {product["weight"]} KG
Variants available: {product["variant_product"]} option(s)
Minimum purchase quantity: {product.get("minimum_purchase_qty" or 1)}
Maximum purchase quantity: {product.get("maximum_purchase_qty")}

**Price**: {format_currency(product["price"])}
Discount: {format_currency(product.get("discount") or 0)}
Shipping Fee: {format_currency(product["shipping_fee"])}
Shipping is available to {format_shipping_country(product["shipping_country"])}."""
    return clean_page_content(format)
    
def format_brand(brand_name: str) -> str:
    if not brand_name :
        return "Unbranded"

    brand = c.json_parse(brand_name)
    return brand if brand.lower() != "other" else "Unbranded"

def format_category(category_name: str) -> str : 
    if not category_name :
        return "Uncategorized"
    
    category = c.json_parse(category_name)
    return category if category.lower() != "kategori lainnya" else "Uncategorized"

def format_product_status(product: dict) -> str :
    status_sentences = []
    if product["top_status"] == 2:
        status_sentences.append("This product is a top product.")
    if product["featured_status"] == 2:
        status_sentences.append("It is featured product on our platform.")
    if product["best_selling_item_status"] == 2:
        status_sentences.append("It is among our best-selling items.")
    if product["is_suggested"] == 1:
        status_sentences.append("This product is also recommended for buyers.")
    
    return " ".join(status_sentences) if len(status_sentences) > 0 else ""

def format_attributes(attributes : str, attributes_data : dict) -> str :
    try:
        attributes = json.loads(attributes)
        parts = []
        for item in attributes:
            attr_id = item.get("attribute_id", "")
            values = item.get("values", [])
            value_str = ", ".join(values).replace("-", " ")
            parts.append(f"- **{attributes_data.get(int(attr_id))}**: {value_str}")
        return "\n".join(parts)
    except Exception as e:
        return ""

def format_shipping_country(country_str: str) -> str:
    if not country_str :
        return "Shipping information is currently unavailable."
    try:
        countries = json.loads(country_str)
        shipping_countries = ", ".join(countries)
        return f"Shipping is available to {shipping_countries}" if isinstance(countries, list) else "Shipping information is currently unavailable."
    except json.JSONDecodeError:
        return "Shipping information is currently unavailable."

def format_currency(price) -> str:
    locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')
    formatted_price = locale.currency(price, symbol=True, grouping=True)
    return formatted_price

def clean_page_content(page_content: str) -> str :
    cleaned_whitespace = c.normalize_whitespace(page_content)
    cleaned_punctuation = c.normalize_punctuation(cleaned_whitespace)
    cleaned_html_entities = c.decode_html_entities(cleaned_punctuation)
    cleaned_non_informative_patterns = c.remove_non_informative(cleaned_html_entities)
    cleaned_emoji = c.remove_emoji(cleaned_non_informative_patterns)
    cleaned_special_symbols = c.remove_special_symbols(cleaned_emoji)
    cleaned_text = c.remove_accents(cleaned_special_symbols)
    
    return cleaned_text