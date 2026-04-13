from typing import Tuple, Optional
import logging
from rapidfuzz import fuzz

logger = logging.getLogger(__name__)

AUTO_LEARNING_ENABLED = True
AUTO_LEARNING_THRESHOLD = 0.70  
MAX_EXAMPLES_PER_CATEGORY = 350
DUPLICATE_SIMILARITY_THRESHOLD = 90 

def normalize(text: str) -> str:
    return text.lower().strip()

def is_duplicate(category, text: str) -> bool:
    from core.crm.models import CategoryExample

    if CategoryExample.objects.filter(
        category=category,
        text__iexact=text
    ).exists():
        return True

    examples = CategoryExample.objects.filter(category=category)

    for ex in examples:
        score = fuzz.token_set_ratio(text, normalize(ex.text))
        if score >= DUPLICATE_SIMILARITY_THRESHOLD:
            return True

    return False


def auto_learn(category, message_text: str):
    from core.crm.models import CategoryExample

    try:
        text = normalize(message_text)

        if len(text) < 5:
            return

        total = CategoryExample.objects.filter(
            category=category
        ).count()

        if total >= MAX_EXAMPLES_PER_CATEGORY:
            return

        if is_duplicate(category, text):
            return

        CategoryExample.objects.create(
            category=category,
            text=text,
            is_positive=True
        )

        print(f"🧠 Auto-learning: exemplo salvo -> {category.name}")

    except Exception as e:
        logger.error(f"❌ Erro auto-learning: {e}")


def classify_message(
    message_text: str,
    whatsapp_number_id: str,
    similarity_threshold: float = 60  
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

                score = fuzz.token_set_ratio(message_text, example_text)

                if score > best_score:
                    best_score = score
                    best_category = category

        except Exception as e:
            logger.error(f"❌ Error in category {category.name}: {e}")

    if best_category and best_score >= similarity_threshold:
        confidence = best_score / 100

        print(f"🏷️ Classificado: {best_category.name} ({confidence:.2f})")

        if AUTO_LEARNING_ENABLED and confidence >= AUTO_LEARNING_THRESHOLD:
            auto_learn(best_category, message_text)

        return best_category, confidence

    print(f"⚠️ Sem match ({best_score})")
    return None, best_score / 100