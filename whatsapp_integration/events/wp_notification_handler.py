import frappe
from frappe.exceptions import ValidationError
import re

# @frappe.whitelist()
# def on_submit_sales_order(doc, method):
#     try:
#         # Get mobile number from Customer
#         customer = frappe.get_doc("Customer", doc.customer)
#         mobile_number = customer.mobile_no

#         if not mobile_number:
#             frappe.log_error(f"Customer {doc.customer} has no mobile number", "WhatsApp Auto Msg")
#             return

#         # Clean and format mobile number
#         mobile_number = re.sub(r'\D', '', mobile_number)  # Remove all non-digit characters
#         if not mobile_number.startswith('91'):
#             mobile_number = '91' + mobile_number
#         mobile_number = '+' + mobile_number

#         # Create WhatsApp Center document
#         whatsapp_doc = frappe.new_doc("WhatsApp Center")
#         whatsapp_doc.person_type = "Customer"
#         whatsapp_doc.person = doc.customer
#         whatsapp_doc.mobile_number = mobile_number
#         whatsapp_doc.use_template = 1  # or 0 if you want plain text
#         whatsapp_doc.template = "cls_sales_order_submitted_z1"  # Replace with your actual template name
#         whatsapp_doc.body_text = doc.name  # Or dynamic value for template
#         whatsapp_doc.insert(ignore_permissions=True)

#         # Send the message
#         from whatsapp_integration.whatsapp_integration.doctype.whatsapp_center.whatsapp_center import send_whatsapp_message
#         send_whatsapp_message(whatsapp_doc.name)

#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "Failed to auto-send WhatsApp on Sales Order Submit")


@frappe.whitelist()
def wp_notification_handler(doc, method):
    try:
        # Map Frappe method to 'send_alert_on' value
        event_map = {
            "on_update": "Save",
            "on_submit": "Submit",
            "after_insert": "New",
            "on_cancel": "Cancel"
        }

        event = event_map.get(method)
        if not event:
            return

        # ✅ Only process if doc.doctype is configured in WP Notification
        enabled_doctypes = frappe.get_all("WP Notification", distinct=True, pluck="document_type")
        if doc.doctype not in enabled_doctypes:
            return  # 🔕 Skip if this doctype is not configured

        # Find matching WP Notification
        wp_notification = frappe.get_all(
            "WP Notification",
            filters={
                "document_type": doc.doctype,
                "send_alert_on": event
            },
            fields=["template", "massage"],
            limit=1
        )

        if not wp_notification:
            return  # No notification configured for this event

        template = wp_notification[0].template
        raw_message = wp_notification[0].massage or ""

        # Extract customer (if available)
        customer = None
        if hasattr(doc, 'customer'):
            customer = doc.customer
        elif hasattr(doc, 'party_type') and doc.party_type == "Customer":
            customer = doc.party

        if not customer:
            frappe.log_error(f"Customer not found in {doc.doctype} {doc.name}", "WP Notification Error")
            return

        customer_doc = frappe.get_doc("Customer", customer)
        mobile_number = customer_doc.mobile_no

        if not mobile_number:
            frappe.log_error(f"Mobile number missing for customer {customer}", "WP Notification Error")
            return

        # Format mobile number
        mobile_number = re.sub(r'\D', '', mobile_number)
        if not mobile_number.startswith('91'):
            mobile_number = '91' + mobile_number
        mobile_number = '+' + mobile_number

        # Replace placeholders {{1}}, {{2}}, etc.
        message_body = raw_message
        matches = re.findall(r"{{(\d+)}}", raw_message)

        doc_values = list(doc.as_dict().values())
        for match in matches:
            index = int(match) - 1
            value = doc_values[index] if index < len(doc_values) else ""
            message_body = message_body.replace(f"{{{{{match}}}}}", str(value))

        # Create WhatsApp Center doc
        whatsapp_doc = frappe.new_doc("WhatsApp Center")
        whatsapp_doc.person_type = "Customer"
        whatsapp_doc.person = customer
        whatsapp_doc.mobile_number = mobile_number
        # whatsapp_doc.mobile_number = "+919106862506"
        whatsapp_doc.use_template = 1
        whatsapp_doc.template = template
        whatsapp_doc.body_text = doc.name
        whatsapp_doc.message = raw_message
        whatsapp_doc.message_body = message_body
        whatsapp_doc.insert(ignore_permissions=True)

        # Send the message
        from whatsapp_integration.whatsapp_integration.doctype.whatsapp_center.whatsapp_center import send_whatsapp_message
        send_whatsapp_message(whatsapp_doc.name)

    except Exception:
        frappe.log_error(frappe.get_traceback(), "WP Notification Handler Error")
