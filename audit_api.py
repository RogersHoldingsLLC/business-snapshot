import os

from flask import Flask, jsonify, request

from report import run_audit


app = Flask(__name__)


@app.get("/health")
def health():
    return jsonify({"ok": True, "service": "Website Audit Tool API"})


@app.post("/audit")
def audit():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"success": False, "error": "Request body must be valid JSON"}), 400

    company = str(payload.get("company", "")).strip()
    website = str(payload.get("website", "")).strip()
    city = str(payload.get("city", "")).strip()
    missing_fields = [
        field
        for field, value in (
            ("company", company),
            ("website", website),
            ("city", city),
        )
        if not value
    ]

    if missing_fields:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Missing required fields: " + ", ".join(missing_fields),
                }
            ),
            400,
        )

    try:
        result = run_audit(company, website, city)
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 500

    return jsonify(
        {
            "success": True,
            "company": result["company"],
            "website": result["website"],
            "auditScore": result["auditScore"],
            "auditOutcome": result["auditOutcome"],
            "priorityTier": result["priorityTier"],
            "offerService": result["offerService"],
            "notes": result["notes"],
            "summary": result["summary"],
            "reportPath": result["reportPath"],
        }
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", os.environ.get("WEBSITE_AUDIT_PORT", 8080)))
    host = os.environ.get("WEBSITE_AUDIT_HOST", "127.0.0.1")
    app.run(host=host, port=port)
