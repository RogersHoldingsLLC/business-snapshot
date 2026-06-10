import re
import sys
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup


def fetch_website(website):
    try:
        return requests.get(website, timeout=10)
    except requests.RequestException:
        return None


def analyze_website(website):
    response = fetch_website(website)

    results = {
        "reachable": "No",
        "https": "Yes" if website.startswith("https://") else "No",
        "title": "Not Found",
        "meta_description": "Not Found",
        "phone_found": "No",
        "email_found": "No",
        "contact_language": "No",
        "service_language": "No",
    }

    if response is None:
        return results

    results["reachable"] = "Yes"

    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text(" ", strip=True).lower()

    if soup.title and soup.title.string:
        results["title"] = soup.title.string.strip()

    meta = soup.find("meta", attrs={"name": "description"})
    if meta and meta.get("content"):
        results["meta_description"] = meta.get("content").strip()

    if re.search(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", response.text):
        results["phone_found"] = "Yes"

    if re.search(r"[\w\.-]+@[\w\.-]+\.\w+", response.text):
        results["email_found"] = "Yes"

    if any(word in text for word in ["contact", "call", "schedule", "quote", "appointment"]):
        results["contact_language"] = "Yes"

    if any(word in text for word in ["services", "service", "what we do", "solutions"]):
        results["service_language"] = "Yes"

    return results


def calculate_score(results):
    score = 0

    if results["reachable"] == "Yes":
        score += 20
    if results["https"] == "Yes":
        score += 15
    if results["title"] != "Not Found":
        score += 15
    if results["meta_description"] != "Not Found":
        score += 15
    if results["phone_found"] == "Yes":
        score += 10
    if results["email_found"] == "Yes":
        score += 10
    if results["contact_language"] == "Yes":
        score += 10
    if results["service_language"] == "Yes":
        score += 5

    return score


def score_rating(score):
    if score >= 90:
        return "Excellent"
    if score >= 75:
        return "Strong"
    if score >= 60:
        return "Average"
    if score >= 40:
        return "Needs Improvement"
    return "Critical"


def opportunity_rating(score):
    if score >= 90:
        return "LOW OPPORTUNITY"
    if score >= 75:
        return "MODERATE OPPORTUNITY"
    if score >= 60:
        return "GOOD OPPORTUNITY"
    return "HIGH OPPORTUNITY"


def generate_recommendations(results):
    recommendations = []

    if results["reachable"] == "No":
        recommendations.append("Confirm the website is live and loading correctly.")
    if results["https"] == "No":
        recommendations.append("Add HTTPS/SSL security to improve trust.")
    if results["title"] == "Not Found":
        recommendations.append("Add a clear page title with the business name and main service.")
    if results["meta_description"] == "Not Found":
        recommendations.append("Add a meta description for better search visibility.")
    if results["phone_found"] == "No":
        recommendations.append("Make the phone number easy to find.")
    if results["email_found"] == "No":
        recommendations.append("Add a visible email address or contact form.")
    if results["contact_language"] == "No":
        recommendations.append("Add clear calls-to-action like Call, Schedule, or Request a Quote.")
    if results["service_language"] == "No":
        recommendations.append("Clearly list the services offered.")

    if not recommendations:
        recommendations.append("Website fundamentals look strong. Review design, speed, conversion flow, and Google Business Profile next.")

    return recommendations


def generate_sales_talking_points(results, score, opportunity):
    points = []

    if results["meta_description"] == "Not Found":
        points.append("Website is missing a meta description.")
    if results["email_found"] == "No":
        points.append("No visible email address was detected.")
    if results["phone_found"] == "No":
        points.append("A phone number was not detected.")
    if results["contact_language"] == "No":
        points.append("Calls-to-action could be improved.")
    if results["service_language"] == "No":
        points.append("Services are not clearly communicated.")
    if score < 60:
        points.append("This business may be a strong Rogers Holdings prospect.")
    if score >= 75:
        points.append("Website has solid fundamentals, but conversion and local visibility may still be improved.")

    points.append(f"Opportunity rating: {opportunity}")

    return points


def create_report(business, website, location):
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)

    safe_name = "".join(c for c in business if c.isalnum() or c in (" ", "_")).replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = reports_dir / f"{safe_name}_Report_{timestamp}.txt"

    website_results = analyze_website(website)
    score = calculate_score(website_results)
    rating = score_rating(score)
    opportunity = opportunity_rating(score)

    recommendations = generate_recommendations(website_results)
    sales_points = generate_sales_talking_points(website_results, score, opportunity)

    recommendation_text = "\n".join(f"{i + 1}. {item}" for i, item in enumerate(recommendations))
    sales_points_text = "\n".join(f"• {item}" for item in sales_points)

    report = f"""
==================================================
ROGERS HOLDINGS LLC
LOCAL BUSINESS DIGITAL OPTIMIZATION REPORT
==================================================

BUSINESS INFORMATION
--------------------------------------------------
Business Name : {business}
Website       : {website}
Location      : {location}
Generated     : {datetime.now().strftime("%B %d, %Y %I:%M %p")}

==================================================
WEBSITE OPTIMIZATION SCORE
==================================================
Score       : {score}/100
Rating      : {rating}
Opportunity : {opportunity}

==================================================
AUTOMATED WEBSITE CHECKS
==================================================
Website Reachable        : {website_results["reachable"]}
HTTPS Enabled            : {website_results["https"]}
Page Title               : {website_results["title"]}
Meta Description         : {website_results["meta_description"]}
Phone Number Found       : {website_results["phone_found"]}
Email Address Found      : {website_results["email_found"]}
Contact Language Found   : {website_results["contact_language"]}
Service Language Found   : {website_results["service_language"]}

==================================================
INTELLIGENT RECOMMENDATIONS
==================================================
{recommendation_text}

==================================================
SALES TALKING POINTS
==================================================
{sales_points_text}

==================================================
MANUAL WEBSITE AUDIT
==================================================
[ ] Mobile Friendly
[ ] Clear Call-To-Action
[ ] Contact Information Easy To Find
[ ] Services Clearly Listed
[ ] Trust Signals Present
[ ] Fast Load Speed
[ ] Strong Homepage Message

==================================================
GOOGLE BUSINESS PROFILE REVIEW
==================================================
[ ] Reviews Reviewed
[ ] Photos Reviewed
[ ] Categories Reviewed
[ ] Hours Verified
[ ] Services Verified

==================================================
ROGERS HOLDINGS LLC SUMMARY
==================================================
This report was generated by Rogers Holdings LLC to identify
digital optimization opportunities for local businesses.

A higher score means stronger digital fundamentals.
A lower score means there may be clearer opportunities to improve visibility,
trust, and customer conversion.
==================================================
"""

    with open(file_path, "w") as file:
        file.write(report)

    print("\n✅ Report successfully created:")
    print(file_path)
    print(f"\nWebsite Optimization Score: {score}/100 - {rating}")
    print(f"Opportunity Rating: {opportunity}")


if len(sys.argv) != 4:
    print('\nUsage: python3 report.py "Business Name" "Website URL" "City, State"\n')
    sys.exit(1)


create_report(sys.argv[1], sys.argv[2], sys.argv[3])