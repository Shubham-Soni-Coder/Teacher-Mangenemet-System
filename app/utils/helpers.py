def initials(name: str):
    parts = name.strip().split()
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0][0].upper()
    return parts[0][0].upper() + parts[-1][0].upper()


def normalize(name: str) -> str:
    return " ".join(name.strip().split())
