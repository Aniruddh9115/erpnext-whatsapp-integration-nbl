import frappe
import requests
import json
from frappe.model.document import Document


class WhatsAppTemplate(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from whatsapp_integration.whatsapp_integration.doctype.body_variable.body_variable import BodyVariable

		amended_from: DF.Link | None
		approval_status: DF.Data | None
		body_text: DF.SmallText | None
		body_variable: DF.Table[BodyVariable]
		category: DF.Data | None
		created_at_utc: DF.Datetime | None
		display_name: DF.Data | None
		footer: DF.Data | None
		id: DF.Data | None
		language: DF.Data | None
		template_name: DF.Data | None
		template_type: DF.Literal["Text", "Media", "Document"]
		variable_count: DF.Int
	# end: auto-generated types
	pass


@frappe.whitelist()
def sync_interakt_templates():
	import requests
	import json

	api_token = frappe.db.get_single_value("WhatsApp Settings NBL", "api_key")

	headers = {
		"Authorization": f"Basic {api_token}",
		"Content-Type": "application/json"
	}

	url = "https://api.interakt.ai/v1/public/track/organization/templates"
	response = requests.get(url, headers=headers)

	if response.status_code != 200:
		frappe.throw(f"Failed to fetch templates: {response.text}")

	data = response.json()
	templates = data.get("results", {}).get("templates", [])

	if not templates:
		frappe.throw("No templates found in API response.")

	synced_count = 0

	for t in templates:
		print(t)
		template_name = t.get("name")
		language = t.get("language")
		body_text = t.get("body")
		footer = t.get("footer")
		category = t.get("category")
		id = t.get('id')
		approval_status = t.get("approval_status")
		display_name = t.get("display_name")

		body_variable = []
		import re
		matches = re.findall(r"\{\{(\d+)\}\}", body_text or "")
		for match in sorted(set(matches), key=int):
			body_variable.append(f"{{{{{match}}}}}")

		existing = frappe.get_all("WhatsApp Template", filters={"template_name": template_name}, limit=1)

		if existing:
			doc = frappe.get_doc("WhatsApp Template", existing[0].name)
			doc.template_type = "Text"
			doc.language = language
			doc.body_text = body_text,
			doc.footer = footer
			doc.category = category
			doc.id = id
			doc.approval_status = approval_status
			doc.display_name = display_name
			doc.save()
		else:
			frappe.get_doc({
					"doctype": "WhatsApp Template",
					"template_name": template_name,
					"template_type": "Text",
					"language": language,
					"body_text": body_text,
					"footer": footer,
					"category": category,
					"id" : id,
					"approval_status" : approval_status,
					"display_name" : display_name,
			}).insert()

		synced_count += 1

	return f"Successfully synced {synced_count} templates."



@frappe.whitelist()
def create_interakt_template(template_name):
	import requests
	import json
	import re

	# Get the WhatsApp Template document
	doc = frappe.get_doc("WhatsApp Template", template_name)

	# Get API Key from settings
	api_token = frappe.db.get_single_value("WhatsApp Settings NBL", "api_key")
	headers = {
		"Authorization": f"Basic {api_token}",
		"Content-Type": "application/json"
	}

	# Prepare body variables
	body_variables = []
	matches = re.findall(r"\{\{(\d+)\}\}", doc.body_text or "")
	for match in sorted(set(matches), key=int):
		body_variables.append(f"{{{{{match}}}}}")

	# Construct payload
	payload = {
		"name": doc.template_name,
		"category": doc.category or "UTILITY",
		"language": doc.language or "en",
		"body": doc.body_text,
		"footer": doc.footer,
		"display_name": doc.display_name
	}

	# Optionally add footer to components (if Interakt API expects it separately)
	# if doc.footer:
	# 	payload["components"]["footer"] = {
	# 		"text": doc.footer
	# 	}

	# Debug (optional)
	# frappe.throw(str(payload))

	# Send request to Interakt
	url = "https://api.interakt.ai/v1/public/track/templates/"
	response = requests.post(url, headers=headers, data=json.dumps(payload))

	if response.status_code != 200:
		frappe.throw(f"Failed to create template: {response.text}")

	return f"Template '{doc.template_name}' created successfully on Interakt."
