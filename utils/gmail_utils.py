import base64

def get_email_body(payload):
    if "parts" in payload:
        for part in payload["parts"]:
            res = get_email_body(part)
            if res:
                return res

    data = payload.get("body", {}).get("data")
    if data:
        try:
            return base64.urlsafe_b64decode(data).decode(errors="ignore")
        except:
            return ""
    return ""


def fetch_messages(service, page_token=None):
    results = service.users().messages().list(
        userId="me", maxResults=20, pageToken=page_token
    ).execute()

    return results.get("messages", []), results.get("nextPageToken")


def parse_email_meta(msg):
    sender = receiver = date = "(unknown)"
    for header in msg.get("payload", {}).get("headers", []):
        if header["name"] == "From":
            sender = header["value"]
        if header["name"] == "To":
            receiver = header["value"]
        if header["name"] == "Date":
            date = header["value"]
    return sender, receiver, date
