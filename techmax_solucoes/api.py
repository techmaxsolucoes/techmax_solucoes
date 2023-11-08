import frappe
from frappe.utils import today
import json


from frappe.utils import cint, fmt_money

from payments.payment_gateways.doctype.stripe_settings.stripe_settings import (
    get_gateway_controller,
)

@frappe.whitelist(allow_guest=True)
def get_api_key(reference_doctype, reference_docname):
    print(reference_doctype, reference_docname)
    gateway_controller = get_gateway_controller(reference_doctype, reference_docname)
    publishable_key = frappe.db.get_value(
        "Stripe Settings", gateway_controller, "publishable_key"
    )
    if cint(frappe.form_dict.get("use_sandbox")):
        publishable_key = frappe.conf.sandbox_publishable_key

    print(publishable_key)
    return publishable_key

@frappe.whitelist()
def subscribe(customer, plan):
    from erpnext.accounts.doctype.subscription.subscription import get_subscription_updates
    from erpnext.accounts.doctype.payment_request.payment_request import make_payment_request

    subscription = None
    if not (subscription := frappe.db.get_value('Subscription', [
            ['Subscription', 'party_type', '=', 'Customer'],
            ['Subscription', 'party', '=', customer],
            ['Subscription', 'start_date', '<=', today()],
            ['Subscription', 'status', '=', 'Unpaid'],
            ['Subscription Plan Detail', 'plan', '=', plan]
        ], 'name')): 

        doc = frappe.new_doc('Subscription').update({
            'party_type': 'Customer',
            'party': customer,
            'start_date': today(),
            'generate_invoice_at_period_start': True,
        })

        doc.append('plans', {
            'plan': plan,
            'qty': 1
        })

        doc.save()

        get_subscription_updates(doc.name)
        
        doc = frappe.get_doc('Subscription', doc.name);

        payment_request = frappe.get_doc("Payment Request", make_payment_request(
            dt=doc.invoices[-1].document_type,
            dn=doc.invoices[-1].invoice
        )['name'])

        payment_request.is_a_subscription = False
        payment_request.flags.mute_email = True
        payment_request.save()
        payment_request.submit()

        doc.update({
            'payment': payment_request.name
        })

        doc.save()
    else:
        doc = frappe.get_doc('Subscription', subscription);
        payment_request = frappe.get_doc('Payment Request', doc.payment)
        
    payment_url = payment_request.get_payment_url()
    print(payment_request.name)
    return {
        'payment_url': payment_url,
        'payment_test': f'/checkout?subscription={doc.name}&payment={payment_request.name}'
    }

    #frappe.local.response["type"] = "redirect"
    #frappe.local.response["location"] = payment_url