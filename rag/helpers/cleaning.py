import json 
import re
import html
import emoji
import unicodedata
from bs4 import BeautifulSoup

def json_parse(json_str, lang_code: str = "en") -> str:
    """
    Parses a multilingual JSON string and extracts the value for the specified language code.

    Args:
        json_str: A JSON-formatted string containing language keys (e.g., '{"en": "value"}', '{"id": "nilai"}').
        lang_code: The preferred language code to extract (default is "en").

    Returns:
        The value corresponding to the specified language code.
        If not found, returns the first available value.
        Returns an empty string if parsing fails or no valid value is found.
    """
    try:
        data = json.loads(json_str)

        if lang_code in data:
            return data[lang_code]

        if isinstance(data, dict):
            return next(iter(data.values()), "")
        
        return ""
    except (json.JSONDecodeError, TypeError):
        return ""

def clean_html(html_str: str) -> str:
    """
    Cleans an HTML string by removing tags and extracting readable text.

    Args:
        html_str: A string containing HTML content.

    Returns:
        A plain text string with all HTML tags removed. Text from separate tags is joined by newlines.
    """
    data = BeautifulSoup(html_str, "html.parser")
    return data.get_text(separator="\n", strip=True)

def normalize_whitespace(text: str) -> str :
    """
    Normalizes whitespace in a string by collapsing tabs, newlines, and multiple spaces.

    Args:
        text: The input string to normalize.

    Returns:
        A cleaned string with all tabs/newlines replaced by a single space, 
        multiple spaces reduced to one, and leading/trailing spaces removed.
    """ 
    text = re.sub(r"[\t\r]+", " ", text)
    
    text = re.sub(r" {2,}", " ", text)
    
    return text.strip()

def normalize_punctuation(text: str) -> str:
    """
    Cleans and normalizes punctuation spacing and repetition in a string.

    Args:
        text: The input string containing text with potentially inconsistent punctuation.

    Returns:
        A cleaned string with:
        - No extra space before punctuation
        - Single space after punctuation if followed by a word
        - Repeated punctuation collapsed into a single mark
    """
    text = re.sub(r"\s+([.,!?;:])", r"\1", text)

    # Only add space after punctuation if NOT followed by another digit (to avoid breaking numbers)
    text = re.sub(r"([.,!?;:])(?=[^\d\s])", r"\1 ", text)

    text = re.sub(r"([.,!?])\1+", r"\1", text)

    return text.strip()

def decode_html_entities(text: str) -> str:
    """
    Decodes HTML entities in a string into their corresponding characters.

    Args:
        text: A string that may contain HTML character entities (e.g., &amp;, &nbsp;).

    Returns:
        A string with all HTML entities converted to their literal characters.
    """
    return html.unescape(text)


def remove_non_informative(text: str) -> str:
    """
    Removes common non-informative marketing or filler phrases from text.

    Args:
        text: A string that may contain repetitive or unhelpful phrases (e.g., promotional language).

    Returns:
        A cleaned string with specified non-informative patterns removed.
    """
    NON_INFORMATIVE_PATTERNS = [
        r"click here",                
        r"cek katalog.*",           
        r"klik.*di sini",
        r"silakan tanyakan.*",
        r"jangan lewatkan.*",    
        r"segera miliki.*",           
    ]
    
    for pattern in NON_INFORMATIVE_PATTERNS:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    return text.strip()

def remove_emoji(text: str) -> str:
    """
    Removes all emojis from the input text.

    Args:
        text: A string that may contain emojis.

    Returns:
        A string with all emojis removed.
    """
    return emoji.replace_emoji(text, replace='')

def remove_special_symbols(text: str) -> str:
    """
    Removes or replaces specific special characters from the input text.
    - Removes symbols: ~ @ # $ ^ _ \
    - Replaces epecific brackets {}, [] to ()

    Args:
        text: A string that may contain special symbols.

    Returns:
        A string with selected special symbols removed or replaced.
    """
    text = re.sub(r"[~@#\$^_\\]", "", text)

    text = re.sub(r"[{\[]", "(", text)

    text = re.sub(r"[}\]]", ")", text)


    return text

def remove_accents(text: str) -> str:
    """
    Removes accented characters from text and converts them to their ASCII equivalents.

    Args:
        text: A string that may contain accented Unicode characters (e.g., 'résumé').

    Returns:
        A string with accents removed (e.g., 'resume').
    """
    return ''.join(
        c for c in unicodedata.normalize('NFKD', text)
        if not unicodedata.combining(c)
    )