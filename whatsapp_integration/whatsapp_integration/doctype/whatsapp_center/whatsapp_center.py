import frappe
import requests
import re
from frappe.utils import now_datetime

from frappe.model.document import Document

class WhatsAppCenter(Document):
    pass  # or your actual logic


def log_whatsapp_message(doc, phone_number, payload, response, status):
    try:
        # Fields
        message_type = "Template" if doc.use_template else "Text"
        template_name = doc.template if doc.use_template else ""
        message_body = (
                            doc.message.replace("_*{{1}}*_", doc.body_text) if doc.use_template else doc.body_text
                        )
        sent_on = now_datetime()
        response_json = frappe.as_json(response)
        reference_doctype = doc.doctype
        reference_name = doc.name

        # Generate a unique name for the log (like Frappe normally does)
        log_name = frappe.model.naming.make_autoname('WL-.YYYY.MM.DD.-.####')

        # Insert manually using SQL
        frappe.db.sql("""
            INSERT INTO `tabWhatsApp Logs` 
            (name, status, phone_number, message_type, template_name, message_body, sent_on, response, reference_doctype, reference_name, creation, modified)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        """, (
            log_name, status, phone_number, message_type, template_name,
            message_body, sent_on, response_json,
            reference_doctype, reference_name
        ))

        frappe.db.commit()
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Failed to insert WhatsApp Log via SQL")


@frappe.whitelist()
def send_whatsapp_message(docname):
    payload = {}
    doc = frappe.get_doc("WhatsApp Center", docname)

    api_key = frappe.db.get_single_value("WhatsApp Settings NBL", "api_key")

    headers = {
        "Authorization": f"Basic {api_key}",
        "Content-Type": "application/json"
    }

    # Clean the number
    raw_mobile = doc.mobile_number.strip()
    cleaned_mobile = re.sub(r'^\+?91', '', raw_mobile)
    full_phone_number = f"+91{cleaned_mobile}"

    try:
        # Build payload
        if doc.use_template:
            if not doc.template:
                frappe.throw("Template is required when using template message.")

            payload = {
                "fullPhoneNumber": full_phone_number,
                "type": "Template",
                "callbackData": "whatsapp_center_callback",
                "template": {
                    "name": doc.template,
                    "languageCode": "en",
                    "headerValues": [],
                    "bodyValues": [doc.body_text or ""],
                    "buttonValues": {
                        "0": ["your_dynamic_url_value"]
                    }
                }
            }
        else:
            if not doc.body_text:
                frappe.throw("Message Body is required when not using template.")

            payload = {
                "userId": "",
                "fullPhoneNumber": full_phone_number,
                "callbackData": "whatsapp_center_callback",
                "type": "Text",
                "data": {
                    "message": doc.body_text
                }
            }

        # Send message
        response = requests.post(
            url="https://api.interakt.ai/v1/public/message/",
            headers=headers,
            json=payload
        )
        res_json = response.json()

        status = "Success" if res_json.get("result") else "Failed"
        
        log_whatsapp_message(doc, full_phone_number, payload, res_json, status)

        if not res_json.get("result"):
            frappe.throw(f"Error sending message: {res_json.get('message')}")
            log_whatsapp_message(doc, full_phone_number, payload, res_json, status)

        return res_json

    except Exception as e:
        # log_whatsapp_message(doc, full_phone_number, payload, {"error": str(e)}, "Failed")
        frappe.throw(f"Exception while sending WhatsApp message: {e}")





