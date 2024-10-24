import re
import difflib


async def search_word_in_text(text, word, case_sensitive=True):
    sentence_endings = re.compile(r'(?<=[.!?])\s*')
    sentences = sentence_endings.split(text)
    result = []

    if not case_sensitive:
        word = word.lower()

    for sentence in sentences:
        if not case_sensitive:
            sentence_check = sentence.lower()
        else:
            sentence_check = sentence

        if re.search(rf'\b{re.escape(word)}\b', sentence_check, re.IGNORECASE):
            result.append(sentence_check.strip())

    return result


async def fuzzy_search(text, word, case_sensitive=True):
    sentence_endings = re.compile(r'(?<=[.!?])\s*')
    sentences = sentence_endings.split(text)
    result = []

    if not case_sensitive:
        word = word.lower()

    for sentence in sentences:
        if not case_sensitive:
            sentence_check = sentence.lower()
        else:
            sentence_check = sentence

        words_in_sentence = sentence_check.split()
        for w in words_in_sentence:
            w = re.sub(r'[^\w\s]', '', w)
            similarity = difflib.SequenceMatcher(None, w, word).ratio()
            if similarity >= 0.7 and (1 - similarity) * len(w) + abs(len(w) - len(word)) <= 3.99999999999:
                result.append(sentence.strip())
                break

    return result
