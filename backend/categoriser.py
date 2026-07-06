import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ── Category seed vocabulary ──────────────────────────────────────────────────
# Each category is seeded with vendor keywords typical of that category.
# The TF-IDF vectorizer builds a category centroid from these seeds, then
# classifies new vendors by cosine similarity to the nearest centroid.
# Zero API calls, zero model downloads, runs in microseconds.

CATEGORY_SEEDS: dict[str, list[str]] = {
    "Software & SaaS": [
        "microsoft", "adobe", "slack", "notion", "github", "atlassian",
        "salesforce", "zoom", "dropbox", "aws", "google workspace", "xero",
        "myob", "quickbooks", "figma", "linear", "jira", "confluence",
        "datadog", "twilio", "sendgrid", "cloudflare", "vercel", "netlify",
    ],
    "Travel & Transport": [
        "uber", "lyft", "qantas", "virgin australia", "jetstar", "airbnb",
        "booking", "expedia", "taxi", "translink", "myki", "tollway",
        "parking", "budget car", "hertz", "avis", "enterprise rent",
        "rex airlines", "tigerair", "skyscanner",
    ],
    "Food & Dining": [
        "mcdonald", "kfc", "hungry jacks", "subway", "dominos", "pizza hut",
        "cafe", "restaurant", "bar", "uber eats", "menulog", "doordash",
        "woolworths", "coles", "aldi", "iga", "harris farm", "7eleven",
        "starbucks", "gloria jeans", "grill'd", "nandos", "sushi",
    ],
    "Office Supplies": [
        "officeworks", "staples", "ikea", "bunnings", "harvey norman",
        "jb hifi", "amazon", "amzn", "kmart", "target", "big w",
        "cartridge world", "officeworks", "ryman", "warehouse stationery",
    ],
    "Utilities & Bills": [
        "agl", "origin energy", "energyaustralia", "optus", "telstra",
        "vodafone", "tpg", "aussie broadband", "internode", "council rates",
        "strata levy", "water board", "ausgrid", "endeavour energy",
    ],
    "Advertising & Marketing": [
        "meta", "facebook ads", "google ads", "linkedin", "mailchimp",
        "canva", "hootsuite", "hubspot", "semrush", "ahrefs", "buffer",
        "klaviyo", "brevo", "convertkit", "activecampaign",
    ],
    "Professional Services": [
        "accountant", "lawyer", "solicitor", "consulting", "upwork",
        "freelancer", "fiverr", "99designs", "airtasker", "seek",
        "deloitte", "pwc", "kpmg", "ey consulting",
    ],
    "Banking & Finance": [
        "anz", "commonwealth bank", "westpac", "nab", "bendigo bank",
        "macquarie", "paypal", "stripe", "afterpay", "zip pay",
        "visa", "mastercard", "american express", "bpay", "osko",
        "sq square", "square payments", "tyro",
    ],
    "Subscriptions & Entertainment": [
        "spotify", "netflix", "stan", "disney plus", "apple music",
        "amazon prime", "audible", "binge", "kayo", "foxtel",
        "youtube premium", "twitch", "steam", "xbox gamepass",
    ],
    "Healthcare & Wellbeing": [
        "pharmacy", "chemist warehouse", "priceline", "doctor", "dentist",
        "medibank", "bupa", "hcf", "nib health", "physiotherapy",
        "gym", "fitness first", "anytime fitness", "yoga",
    ],
}


class TransactionCategoriser:
    """
    TF-IDF cosine similarity categoriser.

    Builds a centroid vector for each category from its seed keywords,
    then classifies an unseen vendor by nearest-centroid lookup.

    No training data required. Explainable: confidence score = cosine similarity.
    Extensible: add seeds to CATEGORY_SEEDS to improve coverage.
    """

    def __init__(self) -> None:
        categories = list(CATEGORY_SEEDS.keys())
        seed_docs = [" ".join(CATEGORY_SEEDS[c]) for c in categories]

        self.categories = categories
        self.vectorizer = TfidfVectorizer(
            analyzer="word",
            ngram_range=(1, 2),   # unigrams + bigrams catch "UBER EATS"
            sublinear_tf=True,
        )
        seed_matrix = self.vectorizer.fit_transform(seed_docs)
        # Each row is the centroid of a category
        self.centroids = seed_matrix.toarray()

    def categorise(self, vendor: str) -> dict:
        """Return best-matching category and a confidence score (0–1)."""
        if not vendor or vendor == "UNKNOWN":
            return {"category": "Uncategorised", "confidence": 0.0}

        vec = self.vectorizer.transform([vendor.lower()]).toarray()
        similarities = cosine_similarity(vec, self.centroids)[0]

        best_idx = int(np.argmax(similarities))
        best_score = float(similarities[best_idx])

        # If no seed keyword overlaps at all, flag as uncategorised
        if best_score < 0.05:
            return {"category": "Uncategorised", "confidence": round(best_score, 3)}

        return {
            "category": self.categories[best_idx],
            "confidence": round(best_score, 3),
        }


# Module-level singleton — instantiated once at import, reused across requests
categoriser = TransactionCategoriser()
