frappe.ui.form.on('WhatsApp Template', {
    refresh(frm) {
        if (frm.doc.docstatus === 1) {  // Only show if document is saved
            frm.add_custom_button('Create on Interakt', () => {
                frappe.call({
                    method: "whatsapp_integration.whatsapp_integration.doctype.whatsapp_template.whatsapp_template.create_interakt_template",
                    args: {
                        template_name: frm.doc.name
                    },
                    callback: (r) => {
                        frappe.msgprint(r.message);
                    }
                });
            });
        }
    }
});
