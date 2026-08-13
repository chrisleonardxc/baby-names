VOWELS = "aeiouy"


def estimate_syllables(name: str) -> int:
    lowered = name.lower()
    count = 0
    prev_was_vowel = False
    for ch in lowered:
        is_vowel = ch in VOWELS
        if is_vowel and not prev_was_vowel:
            count += 1
        prev_was_vowel = is_vowel
    if lowered.endswith("e") and count > 1:
        count -= 1
    return max(count, 1)
