# 🛍️ ShopAssist — FAQ Chatbot

**CodeAlpha AI Internship · Task 2: Chatbot for FAQs**

A production-grade NLP-powered FAQ chatbot for e-commerce support. Built with TF-IDF matching, confidence scoring, Gmail OTP email verification, session analytics, and a fully custom Streamlit UI.

---

## Live Demo

```bash
git clone https://github.com/Rushithaborra/CodeAlpha_ChatbotForFAQs.git
cd CodeAlpha_ChatbotForFAQs
pip install -r requirements.txt
streamlit run app.py
```

Opens at `http://localhost:8501`

---

## Features

### 💬 Chat
- Matches questions against a 73-entry FAQ database using **TF-IDF + cosine similarity**
- Every answer is labelled **High / Medium / Low** confidence
- Smart fallback — suggests related questions when no match is found
- Category pills to filter by topic
- Welcome message with sample questions on first load

### 📊 Dashboard
- Total questions asked vs. answered
- Category breakdown bar chart
- List of unanswered questions from the session

### 🕑 History
- Full conversation history with category tags and confidence badges
- Filter by category
- Clear history button

### 👤 Account
- Profile card with avatar initials, name, email, and member badge
- Edit display name — saves immediately on click
- **Change email with Gmail OTP verification** — a 6-digit code is emailed to the new address; the change only takes effect after entering the correct code
- 10-minute code expiry with a live countdown
- Resend button (available after 60 seconds)
- Auth error checklist with direct links to Google App Passwords setup
- Account details panel (account type, store, language, notifications)

### 🗂️ Sidebar
- Compact account card showing current name and email
- Quick edit profile expander (same OTP flow)
- Category filter dropdown
- Session stats (questions asked, answered, FAQ count)
- Clear conversation button

---

## Project Structure

```
CodeAlpha_ChatbotForFAQs/
│
├── app.py                  # Streamlit UI — all tabs, sidebar, session state, email logic
├── faq_engine.py           # NLP matching engine (TF-IDF + cosine similarity)
├── faq_data.py             # 73 FAQ entries across 10 categories
├── requirements.txt        # Python dependencies
├── .streamlit/
│   └── secrets.toml        # Gmail credentials (not committed — see setup below)
└── README.md
```

---

## Tech Stack

| Layer        | Technology                                      |
|--------------|-------------------------------------------------|
| UI           | Streamlit 1.40+                                 |
| NLP Matching | scikit-learn — TF-IDF vectoriser, cosine similarity |
| Email / OTP  | Python `smtplib` + Gmail SMTP (SSL + TLS)       |
| Language     | Python 3.9+                                     |
| Fonts        | Google Fonts — Cormorant Garamond, Inter        |

---

## How the Matching Engine Works

```
User Input
    │
    ▼
Preprocessing
 • Lowercase + punctuation removal
 • Stopword filtering (compact built-in list, no NLTK download)
 • Lightweight suffix stripping (orders→order, tracking→track)
    │
    ▼
TF-IDF Vectorisation  (bigrams, min_df=1)
 • Corpus = FAQ question + keyword synonyms
 • Query vector computed at runtime
    │
    ▼
Cosine Similarity
 • Scored against all FAQs (or category-filtered subset)
    │
    ▼
Confidence Thresholding
 • ≥ 0.45  →  High
 • ≥ 0.30  →  Medium
 • ≥ 0.12  →  Low
 • < 0.12  →  No match — top-3 suggestions returned
    │
    ▼
Answer + confidence badge rendered in chat
```

> No NLTK, no network downloads, instant cold start.

---

## FAQ Database

| Category              | Entries |
|-----------------------|---------|
| Orders                | 10      |
| Payments              | 9       |
| Shipping & Delivery   | 8       |
| Returns & Refunds     | 8       |
| Account & Profile     | 8       |
| Discounts & Offers    | 7       |
| Products              | 8       |
| Gift Cards            | 5       |
| Technical Support     | 5       |
| Privacy & Security    | 5       |
| **Total**             | **73**  |

---

## Gmail OTP Setup

Email verification uses your Gmail account via App Passwords (OAuth is not required).

**1. Enable 2-Step Verification**
Go to [myaccount.google.com/security](https://myaccount.google.com/security) and enable 2-Step Verification.

**2. Generate an App Password**
Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords), create a new app password, and copy the 16-character code.

**3. Create `.streamlit/secrets.toml`**
```toml
[gmail]
sender       = "yourname@gmail.com"
app_password = "abcd efgh ijkl mnop"
```

**4. Restart the app**

> `secrets.toml` is in `.gitignore` and will never be committed.
> If credentials are missing or incorrect, the app falls back to showing the OTP on screen (demo mode) so the flow can still be tested.

---

## Sample Interactions

| User query | Matched FAQ | Confidence |
|---|---|---|
| "how do I track my order" | How do I track my order? | High |
| "payment not going through" | Why was my payment declined? | High |
| "when will my package arrive" | How long does delivery take? | High |
| "can I swap my product" | Can I exchange a product? | High |
| "do you have discount codes" | How do I apply a coupon code? | Medium |
| "gift card balance" | How do I check my gift card balance? | High |
| "website not loading" | The website or app is not loading | High |
| "my data privacy" | How do you protect my personal data? | Medium |

---

## Future Scope

| Area | Planned Enhancement |
|---|---|
| **AI** | Replace TF-IDF with an LLM (Claude/GPT) for natural, generative answers |
| **Multi-turn** | Conversation context so the bot remembers previous messages |
| **Live agent** | Escalate to human support when confidence is low |
| **Real auth** | JWT-based login with persistent accounts in a database |
| **Admin panel** | Manage FAQs through a UI without editing code |
| **Feedback** | Thumbs up/down on answers to improve ranking |
| **Multilingual** | Auto-detect and respond in the user's language |
| **Integrations** | Connect to real order management to look up live order status |
| **Widget** | Embed the chatbot in any website via a JS snippet |
| **Mobile** | Native mobile app using the same backend |

---

## Installation

```bash
# Python 3.9+ required
pip install -r requirements.txt
streamlit run app.py
```

If `python3` on your machine points to a newer Python without the packages, use:
```bash
/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3 -m streamlit run app.py
# or
/Users/<you>/Library/Python/3.9/bin/streamlit run app.py
```

---

## Author

**Rushitha Borra**
GitHub: [github.com/Rushithaborra](https://github.com/Rushithaborra)

---

## Acknowledgements

- [CodeAlpha](https://www.codealpha.tech/) — Internship programme
- [scikit-learn](https://scikit-learn.org/) — TF-IDF & cosine similarity
- [Streamlit](https://streamlit.io/) — UI framework
