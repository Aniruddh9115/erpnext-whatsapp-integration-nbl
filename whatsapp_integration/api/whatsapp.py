# your_app_name/your_module_name/interakt_integration.py

import frappe
import requests
import json

@frappe.whitelist()
def send_interakt_whatsapp_template(full_phone_number, template_name, body_values=[], header_values=[], button_values={}):
    """
    Sends a WhatsApp template message via the Interakt API using the configured WhatsApp Settings.

    :param full_phone_number: The recipient's full phone number with country code (e.g., "+919106862506").
    :param template_name: The name of the Interakt template to use.
    :param body_values: A list of values for the template's body variables.
    :param header_values: A list of values for the template's header variables (if any).
    :param button_values: A dictionary of values for dynamic URL buttons. 
                         Keys are button indices (starting from 0), values are lists of strings.
                         e.g., {"0": ["your_dynamic_url_value"]}
    """

    try:
        # Get WhatsApp Settings NBL document
        whatsapp_settings = frappe.get_doc("WhatsApp Settings NBL")

        # Extract API URL and API Key from the settings
        api_url = whatsapp_settings.api_url
        
        api_key_param = next((p.value for p in whatsapp_settings.parameters if p.parameter == "apikey"), None)
        
        if not api_url or not api_key_param:
            frappe.throw("WhatsApp API URL or API Key is not configured in 'WhatsApp Settings NBL'.")

        # Interakt's API expects the Authorization header to be "Basic <API_KEY>"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {api_key_param}"
        }
        # frappe.throw(str(body_values))
        
        # Prepare the request payload as per Interakt's documentation
        payload = {
            "fullPhoneNumber": full_phone_number,
            "type": "Template",
            "callbackData": "test_callback_data",  # You can customize this
            "template": {
                "name": template_name,
                "languageCode": "en",  # Assuming English, adjust as needed
                "headerValues": [],
                "bodyValues": ["Aniruddh"],
                "buttonValues": {
                                "0": ["your_dynamic_url_value"] 
                                }
            }
        }
        # Send the POST request to Interakt API
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)

        frappe.msgprint("WhatsApp template message sent successfully!")
        return response.json()

    except requests.exceptions.RequestException as e:
        frappe.throw(f"Error sending WhatsApp message: {e}")
    except Exception as e:
        frappe.throw(f"An unexpected error occurred: {e}")


