"""
FAQ Matching Engine
TF-IDF vectorisation + cosine similarity (scikit-learn).
Lightweight built-in preprocessing — no external downloads, no network calls,
so the app starts instantly every time.
"""
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

THRESHOLD_NONE   = 0.12
THRESHOLD_MEDIUM = 0.30
THRESHOLD_HIGH   = 0.45

# Compact, FAQ-relevant stopword list — no NLTK download needed.
STOP_WORDS = {
    "a","an","the","is","are","was","were","be","been","being","i","you","he","she",
    "it","we","they","my","your","his","her","its","our","their","this","that","these",
    "those","do","does","did","doing","have","has","had","having","will","would","can",
    "could","should","may","might","must","shall","to","of","in","on","at","for","with",
    "about","into","through","during","before","after","above","below","from","up",
    "down","out","off","over","under","again","further","then","once","here","there",
    "when","where","why","how","all","any","both","each","few","more","most","other",
    "some","such","no","nor","not","only","own","same","so","than","too","very","just",
    "and","or","but","if","because","as","until","while","what","which","who","whom",
}

_WORD_RE = re.compile(r"[a-z0-9]+")

# Minimal suffix-stripping — captures the common plural/verb-form cases that
# matter for FAQ matching (orders→order, tracking→track) without a full
# Porter-stemmer dependency.
def _light_stem(word: str) -> str:
    if len(word) > 5 and word.endswith("ing"):
        return word[:-3]
    if len(word) > 4 and word.endswith("ed"):
        return word[:-2]
    if len(word) > 4 and word.endswith("ies"):
        return word[:-3] + "y"
    if len(word) > 3 and word.endswith("es"):
        return word[:-2]
    if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def preprocess(text: str) -> str:
    words = _WORD_RE.findall(text.lower())
    tokens = [_light_stem(w) for w in words if w not in STOP_WORDS]
    return " ".join(tokens)


class FAQEngine:
    def __init__(self, faq_data: list):
        self.data       = faq_data
        self.categories = sorted(set(d["category"] for d in faq_data))

        corpus = [
            preprocess(item["question"] + " " + " ".join(item.get("keywords", [])))
            for item in faq_data
        ]

        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
        self.matrix     = self.vectorizer.fit_transform(corpus)

    # ── public ────────────────────────────────────────────────────────────────
    def query(self, user_input: str, category: str = "All"):
        processed = preprocess(user_input)
        if not processed.strip():
            return self._miss([], "Please type a question.")

        indices = list(range(len(self.data)))
        if category and category not in ("All", "All Categories"):
            indices = [i for i, d in enumerate(self.data) if d["category"] == category]
            if not indices:
                indices = list(range(len(self.data)))

        qvec = self.vectorizer.transform([processed])

        scores     = cosine_similarity(qvec, self.matrix[indices]).flatten()
        best_local = int(np.argmax(scores))
        best_score = float(scores[best_local])
        best_idx   = indices[best_local]

        if best_score < THRESHOLD_NONE:
            all_scores = cosine_similarity(qvec, self.matrix).flatten()
            top  = np.argsort(all_scores)[::-1][:3]
            sugg = [self.data[i]["question"] for i in top if all_scores[i] > 0.05]
            return self._miss(sugg)

        conf = "high" if best_score >= THRESHOLD_HIGH else \
               "medium" if best_score >= THRESHOLD_MEDIUM else "low"

        item = self.data[best_idx]
        return {
            "found"      : True,
            "answer"     : item["answer"],
            "question"   : item["question"],
            "category"   : item["category"],
            "confidence" : round(best_score, 3),
            "conf_label" : conf,
            "suggestions": [],
        }

    def sample_questions(self, category: str = "All", n: int = 4) -> list:
        pool = self.data if category in ("All", "All Categories") else \
               [d for d in self.data if d["category"] == category]
        return [d["question"] for d in pool[:n]]

    # ── private ───────────────────────────────────────────────────────────────
    def _miss(self, suggestions, msg=None):
        return {
            "found"      : False,
            "answer"     : None,
            "question"   : None,
            "category"   : None,
            "confidence" : 0.0,
            "conf_label" : "none",
            "suggestions": suggestions,
            "miss_msg"   : msg,
        }
