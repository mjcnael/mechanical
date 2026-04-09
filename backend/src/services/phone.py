import re


def normalize_phone_number(phone_number: str) -> str:
    cleaned = (
        phone_number.strip()
        .replace(" ", "")
        .replace("-", "")
        .replace("(", "")
        .replace(")", "")
    )
    if len(cleaned) == 11 and cleaned.startswith("8"):
        return f"+7{cleaned[1:]}"
    if len(cleaned) == 11 and cleaned.startswith("7"):
        return f"+{cleaned}"
    return cleaned


def is_valid_phone_number(phone_number: str) -> bool:
    return re.fullmatch(r"\+7\d{10}", normalize_phone_number(phone_number)) is not None


def phone_number_variants(phone_number: str) -> list[str]:
    normalized = normalize_phone_number(phone_number)
    variants = [normalized]
    if normalized.startswith("+7") and len(normalized) == 12:
        variants.append(f"8{normalized[2:]}")
    return variants
