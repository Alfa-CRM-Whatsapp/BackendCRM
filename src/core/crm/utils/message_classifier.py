from typing import Tuple, Optional
import logging
import re
import unicodedata

from rapidfuzz import fuzz
from rapidfuzz.distance import Levenshtein

logger = logging.getLogger(__name__)

AUTO_LEARNING_ENABLED = True
AUTO_LEARNING_THRESHOLD = 0.75

MAX_EXAMPLES_PER_CATEGORY = 350

DUPLICATE_SIMILARITY_THRESHOLD = 93
MIN_LENGTH = 2

WORD_WEIGHT = 0.4
FULL_WEIGHT = 0.6

KEYWORD_BOOST = 20

def normalize(text: str) -> str:
    text = text.lower().strip()

    text = unicodedata.normalize('NFKD', text)
    text = ''.join(c for c in text if not unicodedata.combining(c))

    text = re.sub(r'[^a-z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text)

    return text

def similarity(a: str, b: str) -> float:
    return max(
        fuzz.ratio(a, b),
        fuzz.partial_ratio(a, b),
        fuzz.token_set_ratio(a, b)
    )


def typo_bonus(a: str, b: str) -> int:
    dist = Levenshtein.distance(a, b)

    if dist == 1:
        return 12
    elif dist == 2:
        return 6

    return 0


def final_score(a: str, b: str) -> float:
    return similarity(a, b) + typo_bonus(a, b)

def word_score(message_text: str, example_text: str) -> float:
    message_words = message_text.split()
    example_words = example_text.split()

    if not message_words or not example_words:
        return 0

    total = 0

    for w1 in message_words:
        best_word_score = 0

        for w2 in example_words:
            score = similarity(w1, w2)
            score += typo_bonus(w1, w2)

            if score >= 85:
                score += KEYWORD_BOOST

            if score > best_word_score:
                best_word_score = score

        total += best_word_score

    return total / len(message_words)

def combined_score(message_text: str, example_text: str) -> float:
    full = final_score(message_text, example_text)
    word = word_score(message_text, example_text)

    return (full * FULL_WEIGHT) + (word * WORD_WEIGHT)

def is_duplicate(category, text: str) -> bool:
    from core.crm.models import CategoryExample

    if CategoryExample.objects.filter(
        category=category,
        text__iexact=text
    ).exists():
        return True

    examples = CategoryExample.objects.filter(category=category)

    for ex in examples:
        ex_text = normalize(ex.text)

        score = similarity(text, ex_text)

        if score >= DUPLICATE_SIMILARITY_THRESHOLD:
            return True

    return False

def auto_learn(category, message_text: str):
    from core.crm.models import CategoryExample

    try:
        text = normalize(message_text)

        print(f"🧠 Tentando aprender: '{text}'")

        if len(text) < MIN_LENGTH:
            print("❌ Muito curto")
            return

        total = CategoryExample.objects.filter(category=category).count()

        if total >= MAX_EXAMPLES_PER_CATEGORY:
            print("❌ Limite atingido")
            return

        if is_duplicate(category, text):
            print("❌ Duplicado")
            return

        CategoryExample.objects.create(
            category=category,
            text=text,
            is_positive=True
        )

        print(f"✅ Auto-learning salvo -> {category.name}")

    except Exception as e:
        logger.error(f"❌ Erro auto-learning: {e}")

def classify_message(
    message_text: str,
    whatsapp_number_id: str,
    similarity_threshold: float = 65
) -> Tuple[Optional[object], float]:

    if not message_text or not message_text.strip():
        return None, 0.0

    from core.crm.models import WhatsappNumber, MessageCategory

    message_text = normalize(message_text)

    try:
        whatsapp_number = WhatsappNumber.objects.get(
            phone_number_id=whatsapp_number_id
        )
    except Exception as e:
        logger.error(f"❌ Error retrieving WhatsApp number: {e}")
        return None, 0.0

    categories = MessageCategory.objects.filter(
        whatsapp_number=whatsapp_number,
        is_active=True
    ).prefetch_related("examples")

    if not categories.exists():
        return None, 0.0

    best_category = None
    best_score = 0

    for category in categories:
        try:
            examples = category.examples.filter(is_positive=True)

            for ex in examples:
                example_text = normalize(ex.text)

                if message_text == example_text:
                    print(f"⚡ Match exato -> {category.name}")
                    return category, 1.0

                score = combined_score(message_text, example_text)

                if score > best_score:
                    best_score = score
                    best_category = category

        except Exception as e:
            logger.error(f"❌ Error in category {category.name}: {e}")

    if best_category and best_score >= similarity_threshold:
        confidence = min(best_score / 100, 1.0)

        print(f"🏷️ Classificado: {best_category.name} ({confidence:.2f})")

        if AUTO_LEARNING_ENABLED and AUTO_LEARNING_THRESHOLD <= confidence <= 0.97:
            auto_learn(best_category, message_text)

        return best_category, confidence

    print(f"⚠️ Sem match ({best_score})")
    return None, best_score / 100