import os, json, time

try:
    import google.generativeai as genai
    from dotenv import load_dotenv
    load_dotenv()

    key = os.getenv("GEMINI_API_KEY")
    if key:
        genai.configure(api_key=key)
        MODEL = genai.GenerativeModel("models/gemini-2.5-flash")
    else:
        MODEL = None
except:
    MODEL = None


def batch_detect_email_types(msgs):
    if not MODEL:
        return ["Unknown"] * len(msgs)

    prompt = "Classify emails into categories. Return a pure JSON array.\n"

    for i, msg in enumerate(msgs, 1):
        prompt += f"\nEmail {i}: {msg[:800]}"

    try:
        resp = MODEL.generate_content(prompt)
        text = resp.text
    except:
        return ["Unknown"] * len(msgs)

    try:
        start = text.index("[")
        end = text.rindex("]") + 1
        arr = json.loads(text[start:end])
    except:
        return ["Unknown"] * len(msgs)

    out = ["Unknown"] * len(msgs)

    for item in arr:
        idx = item.get("index", 0) - 1
        typ = item.get("type", "Unknown")
        if 0 <= idx < len(msgs):
            out[idx] = typ

    return out
