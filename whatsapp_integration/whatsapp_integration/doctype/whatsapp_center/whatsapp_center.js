frappe.ui.form.on('WhatsApp Center', {
    refresh(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button('Send WhatsApp', () => {
                frappe.call({
                    method: 'whatsapp_integration.whatsapp_integration.doctype.whatsapp_center.whatsapp_center.send_whatsapp_message',
                    args: {
                        docname: frm.doc.name
                    },
                    callback: function(r) {
                        if (r.message) {
                            frappe.msgprint("Message sent successfully!");
                        }
                    }
                });
            });
        }
    },
    use_template(frm) {
        if (!frm.doc.use_template) {
            frm.set_value('template', '');
        }
    },
    person: function(frm) {
        const mobileFieldMap = {
            "Customer": "mobile_no",
            "Lead": "mobile_no",
            "Employee": "cell_number",
            "Supplier": "mobile_no"
        };

        const doctype = frm.doc.person_type;
        const name = frm.doc.person;
        const mobile_field = mobileFieldMap[doctype];

        if (doctype && name && mobile_field) {
            frappe.db.get_value(doctype, name, mobile_field)
                .then(r => {
                    if (r.message && r.message[mobile_field]) {
                        frm.set_value('mobile_number', r.message[mobile_field]);
                    } else {
                        frappe.msgprint(__('Mobile number not found for selected {0}', [doctype]));
                        frm.set_value('mobile_number', '');
                    }
                });
        }
    }
});

