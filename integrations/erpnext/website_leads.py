"""Install beside the e2e Website Leads controller as website_api.py (Frappe 14+)."""
import re

import frappe
import requests
from frappe.rate_limiter import rate_limit

ORIGINS = {"https://e2erecycling.com", "https://www.e2erecycling.com"}
HOSTNAMES = {"e2erecycling.com", "www.e2erecycling.com"}
FIELDS = {
    "contact_name": ("contact_name", 120),
    "company": ("company", 140),
    "work_email": ("work_email", 140),
    "phone": ("phone", 40),
    "city_locations": ("citylocation", 140),
    "asset_types_volume": ("asset_typesapproximate_volume", 1000),
    "requirement_details": ("requirement_details", 2000),
}


def failure(code, message, status=400):
    frappe.local.response["http_status_code"] = status
    return {"ok": False, "code": code, "message": message}


def clean_fields(payload):
    values = {}
    for source, (target, maximum) in FIELDS.items():
        value = payload.get(source)
        if not isinstance(value, str):
            raise ValueError("Complete every required field.")
        value = value.strip()
        if not value or len(value) > maximum:
            raise ValueError("Complete every required field within its character limit.")
        if re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f<>]", value):
            raise ValueError("Please use plain text without HTML or control characters.")
        values[target] = value
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", values["work_email"]):
        raise ValueError("Enter a valid work email address.")
    if not re.fullmatch(r"[+\d() .\-]{7,40}", values["phone"]) or len(re.sub(r"\D", "", values["phone"])) < 7:
        raise ValueError("Enter a valid contact phone number.")
    return values


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=5, seconds=600, methods=["POST"])
def submit(**payload):
    """Accept only CAPTCHA-verified website enquiries, never arbitrary doctypes."""
    if frappe.get_request_header("Origin") not in ORIGINS:
        return failure("origin", "Please submit through the e2e Recycling website.", 403)
    if frappe.request.content_length and frappe.request.content_length > 24000:
        return failure("size", "Your enquiry is too long.", 413)
    if set(payload) - set(FIELDS) - {"cmd", "recaptcha_response", "website"}:
        return failure("fields", "The form contains unsupported fields.")
    if payload.get("website"):
        return failure("verification", "We could not verify this enquiry.")
    try:
        values = clean_fields(payload)
    except ValueError as error:
        return failure("validation", str(error))
    token = payload.get("recaptcha_response")
    if not isinstance(token, str) or not 20 <= len(token) <= 8192:
        return failure("captcha", "Complete the reCAPTCHA check and try again.")
    secret = frappe.conf.get("e2e_recaptcha_secret")
    if not secret:
        return failure("unavailable", "Online enquiries are temporarily unavailable. Please email info@e2erecycling.com.", 503)
    try:
        response = requests.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={"secret": secret, "response": token},
            timeout=(3, 7), allow_redirects=False,
        )
        response.raise_for_status()
        result = response.json()
        if not isinstance(result, dict):
            raise ValueError("Invalid verification response")
    except (requests.RequestException, ValueError):
        return failure("unavailable", "Verification is temporarily unavailable. Please try again or email info@e2erecycling.com.", 503)
    if result.get("success") is not True or result.get("hostname") not in HOSTNAMES:
        return failure("captcha", "The reCAPTCHA check expired or failed. Please complete it again.")
    try:
        lead = frappe.get_doc({
            "doctype": "e2e Website Leads",
            "naming_series": "e2e-WEB-LEAD-.YYYY.-",
            **values,
        })
        lead.insert(ignore_permissions=True)
    except Exception as error:
        frappe.db.rollback()
        # Never log form contents, CAPTCHA tokens, or secrets.
        frappe.logger("e2e_website").error("Lead insert failed: %s", type(error).__name__)
        return failure("unavailable", "We could not save your enquiry. Please try again or email info@e2erecycling.com.", 503)
    # Frappe commits successful POSTs and dispatches its native after_insert webhook.
    return {"ok": True, "message": "Thank you. Your enquiry has reached the e2e team."}


def configure():
    """Run with bench execute, never HTTP. Secret input is hidden and not logged."""
    import getpass
    import json
    import os
    import shutil
    from pathlib import Path

    path = Path(frappe.get_site_path("site_config.json"))
    config = json.loads(path.read_text())
    secret = getpass.getpass("Paste the Google reCAPTCHA SECRET key (hidden), then Enter: ").strip()
    if len(secret) < 30 or secret == "6LcpwAQuAAAAAL0Bcj0j0uDE3AyqYDmOQnEaZ3Lb":
        raise ValueError("A valid secret key is required; the public site key cannot be used.")
    current = config.get("allow_cors", [])
    if isinstance(current, str):
        current = [current]
    if not isinstance(current, list) or "*" in current:
        raise ValueError("Review the existing CORS configuration before setup; no changes were made.")
    backup = path.with_name("site_config.before-e2e-contact.json")
    if not backup.exists():
        shutil.copy2(path, backup)
        backup.chmod(0o600)
    config["e2e_recaptcha_secret"] = secret
    config["allow_cors"] = sorted(set(current) | ORIGINS)
    temporary = path.with_name("site_config.e2e-contact.tmp")
    descriptor = os.open(str(temporary), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w") as handle:
        json.dump(config, handle, indent=2)
        handle.write("\n")
    os.replace(temporary, path)
    print("e2e CAPTCHA secret saved privately; website origins added. CSRF settings unchanged.")
