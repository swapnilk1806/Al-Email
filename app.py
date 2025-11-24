from flask import Flask, redirect, url_for, session, request, render_template, send_file
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import google.oauth2.credentials
from datetime import datetime
from email.utils import parsedate_to_datetime
import io, csv, time, json, base64, os

# Local imports
from config import CLIENT_SECRET_FILE, SCOPES, REDIRECT_URI, EMAIL_TYPES
from utils.gmail_utils import get_email_body, fetch_messages, parse_email_meta
from utils.classifier import batch_detect_email_types
from utils.helpers import clean_html, quote_plus_safe

app = Flask(__name__)
app.secret_key = "replace_with_secure_key"
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GLOBAL_GMAIL_EMAILS = []


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login")
def login():
    flow = Flow.from_client_secrets_file(CLIENT_SECRET_FILE, scopes=SCOPES)
    flow.redirect_uri = REDIRECT_URI
    auth_url, state = flow.authorization_url(access_type="offline", include_granted_scopes="true")

    session["state"] = state
    return redirect(auth_url)


@app.route("/callback")
def callback():
    state = session.get("state")

    flow = Flow.from_client_secrets_file(CLIENT_SECRET_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = REDIRECT_URI
    flow.fetch_token(authorization_response=request.url)

    creds = flow.credentials
    session["credentials"] = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes,
    }

    return redirect("/date_filter")


@app.route("/date_filter")
def date_filter():
    return render_template("date_filter.html")


@app.route("/emails", methods=["GET", "POST"])
def emails():

    if "credentials" not in session:
        return redirect("/")

    if request.method == "POST":
        session["start_date"] = request.form["start"]
        session["end_date"] = request.form["end"]

    start_str = session.get("start_date")
    end_str = session.get("end_date")
    if not start_str or not end_str:
        return redirect("/date_filter")

    start_dt = datetime.strptime(start_str, "%Y-%m-%d")
    end_dt = datetime.strptime(end_str, "%Y-%m-%d")

    creds = google.oauth2.credentials.Credentials(**session["credentials"])
    service = build("gmail", "v1", credentials=creds)

    # Fetch emails
    messages, next_page = fetch_messages(service, request.args.get("page_token"))

    to_classify_texts = []
    to_classify_ids = []
    display_items = []

    for m in messages:
        msg_detail = service.users().messages().get(userId="me", id=m["id"], format="full").execute()

        sender, receiver, date_text = parse_email_meta(msg_detail)
        try:
            email_dt = parsedate_to_datetime(date_text).replace(tzinfo=None)
        except:
            continue

        if not (start_dt <= email_dt <= end_dt):
            continue

        body = get_email_body(msg_detail.get("payload", {}))
        plain_text = clean_html(body)

        existing = next((e for e in GLOBAL_GMAIL_EMAILS if e["id"] == m["id"]), None)
        if existing:
            existing.update({"sender": sender, "receiver": receiver, "date": date_text, "message": plain_text})
            display_items.append(existing)
        else:
            item = {
                "id": m["id"],
                "sender": sender,
                "receiver": receiver,
                "date": date_text,
                "message": plain_text,
                "type": "Unknown",
            }
            GLOBAL_GMAIL_EMAILS.append(item)
            display_items.append(item)
            to_classify_ids.append(m["id"])
            to_classify_texts.append(plain_text)

    # Categorize unread emails
    if to_classify_texts:
        types = batch_detect_email_types(to_classify_texts)
        for mid, typ in zip(to_classify_ids, types):
            email = next(e for e in GLOBAL_GMAIL_EMAILS if e["id"] == mid)
            email["type"] = typ

    return render_template(
        "emails.html",
        emails=display_items,
        start_date=start_str,
        end_date=end_str,
        next_page=quote_plus_safe(next_page) if next_page else None,
        selected_type=request.args.get("filter_type", "All"),
        TYPES=EMAIL_TYPES,
    )


@app.route("/download")
def download():
    start = request.args.get("start_date", "")
    end = request.args.get("end_date", "")
    typ = request.args.get("type", "")

    sdt = datetime.strptime(start, "%Y-%m-%d")
    edt = datetime.strptime(end, "%Y-%m-%d")

    rows = [e for e in GLOBAL_GMAIL_EMAILS if sdt <= parsedate_to_datetime(e["date"]).replace(tzinfo=None) <= edt]

    if typ and typ != "All":
        rows = [e for e in rows if e["type"] == typ]

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["sender", "receiver", "date", "message", "type"])
    for r in rows:
        writer.writerow([r["sender"], r["receiver"], r["date"], r["message"], r["type"]])

    mem = io.BytesIO(output.getvalue().encode("utf-8"))
    mem.seek(0)
    return send_file(mem, mimetype="text/csv", as_attachment=True, download_name="gmail_export.csv")


if __name__ == "__main__":
    app.run(debug=True)
