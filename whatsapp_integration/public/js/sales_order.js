// frappe.ui.form.on('Sales Order', {
//     refresh: function(frm) {
//         frm.add_custom_button(__('Send WhatsApp'), function() {
//             const fullPhoneNumber = "+917265806735"; // Hardcoding for testing, replace with dynamic retrieval
//             // Example of dynamically getting phone number (uncomment and use if needed)
//             // if (!frm.doc.contact_person) {
//             //     frappe.msgprint("Please select a Contact Person for this Sales Order.");
//             //     return;
//             // }
//             // frappe.db.get_value("Contact", { name: frm.doc.contact_person }, "mobile_no")
//             //     .then(r => {
//             //         const mobileNo = r.message ? r.message.mobile_no : null;
//             //         if (!mobileNo) {
//             //             frappe.msgprint("Mobile number not found for the selected Contact Person.");
//             //             return;
//             //         }
//             //         sendWhatsAppMessage(frm, `+91${mobileNo}`); // Assuming Indian numbers, adjust country code
//             //     });
            
//             // For now, using the hardcoded number
//             sendWhatsAppMessage(frm, fullPhoneNumber);

//         }, __('WhatsApp Actions')); // Group the button under "WhatsApp Actions"

//         // You can also add more buttons here if needed
//     }
// });

// function sendWhatsAppMessage(frm, fullPhoneNumber) {
//     // Ensure the phone number is in the correct format (e.g., "+91XXXXXXXXXX")
//     if (!fullPhoneNumber) {
//         frappe.msgprint("Recipient phone number is missing.");
//         return;
//     }

//     // You can dynamically get these values from the Sales Order document (frm.doc)
//     // based on your Interakt template requirements.
//     const customerName = frm.doc.customer_name || "Customer";
//     const salesOrderId = frm.doc.name;
//     // const grandTotal = frappe.format(frm.doc.grand_total, frm.meta.get_field("grand_total")) || "N/A";

//     const bodyValues = [
//         customerName,  // Corresponds to {{1}} in your template's body
//         salesOrderId   // Corresponds to {{2}} in your template's body
//         // Add more if your template has more body variables
//     ];

//     const buttonValues = {
//         // Example for a Call-to-Action URL button at index 0 ({{1}})
//         // Assumes your template has a button with a dynamic URL like `https://yourdomain.com/vieworder?id={{1}}`
//         "0": [`your_dynamic_url_value`]
//         // Add more entries if your template has more dynamic buttons
//     };
//     frappe.call({
//         method: "whatsapp_integration.api.whatsapp.send_interakt_whatsapp_template",
//         args: {
//             "full_phone_number": fullPhoneNumber,
//             "template_name": "test_template", // Replace with your actual Interakt template name
//             "body_values": bodyValues,
//             "header_values": [], // Empty array if no header variables
//             "button_values": buttonValues // Empty object {} if no dynamic buttons, or if passing directly to server script
//         },
//         callback: function(response) {
//             if (response.message) {
//                 frappe.msgprint("WhatsApp message sent successfully!");
//                 console.log("Interakt API Response:", response.message);
//             } else if (response.exc) {
//                 frappe.msgprint(`Error sending WhatsApp message: ${response.exc}`);
//                 console.error("Interakt API Error:", response.exc);
//             }
//         }
//     });
// }
