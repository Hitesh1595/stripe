from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.integrations.utils import create_request_log
from erpnext.shopping_cart.cart import get_party
import stripe

def create_stripe_subscription(gateway_controller, data):
	stripe_settings = frappe.get_doc("Stripe Setting", gateway_controller)
	stripe_settings.data = frappe._dict(data)

	stripe.api_key = stripe_settings.get_password(fieldname="secret_key", raise_exception=False)
	stripe.default_http_client = stripe.http_client.RequestsClient()

	try:
		stripe_settings.integration_request = create_request_log(stripe_settings.data, "Host", "Stripe")
		stripe_settings.payment_plans = frappe.get_doc("Payment Request", stripe_settings.data.reference_docname).subscription_plans
		return create_subscription_on_stripe(stripe_settings)

	except Exception:
		frappe.log_error(frappe.get_traceback())
		return{
			"redirect_to": frappe.redirect_to_message(_('Server Error'), _("It seems that there is an issue with the server's stripe configuration. In case of failure, the amount will get refunded to your account.")),
			"status": 401
		}


def create_subscription_on_stripe(stripe_settings):
		items = []
		for payment_plan in stripe_settings.payment_plans:
			plan = frappe.db.get_value("Subscription Plan", payment_plan.plan, "payment_plan_id")
			items.append({"plan": plan, "quantity": payment_plan.qty})
	
		try:
			customer = stripe.Customer.create(description=stripe_settings.data.payer_name, email=stripe_settings.data.payer_email, source=stripe_settings.data.stripe_token_id)
			subscription = stripe.Subscription.create(customer=customer, items=items)

			print("value of subscription +++++++++++++++",subscription["id"])
			if subscription.status == "active":
           
				stripe_settings.integration_request.db_set('status', 'Completed', update_modified=False)
				stripe_settings.flags.status_changed_to = "Completed"
				customer = get_party()
				
				doc = frappe.get_doc('Customer',customer.name)
				doc.db_set("subscription_id",subscription["id"], update_modified=False)

			else:
				stripe_settings.integration_request.db_set('status', 'Failed', update_modified=False)
				frappe.log_error('Subscription N°: ' + subscription.id, 'Stripe Payment not completed')

		except Exception:
			stripe_settings.integration_request.db_set('status', 'Failed', update_modified=False)
			frappe.log_error(frappe.get_traceback())

		return stripe_settings.finalize_request()






def cancel_subscription():
    try:
        # Cancel the subscription by deleting it
        deletedSubscription = stripe.Subscription.delete(data['subscriptionId'])
        return {"subscription":deletedSubscription}
    except Exception as e:
        pass




def list_subscriptions():
  
    customer_id = frappe.session.user

    try:
        # Cancel the subscription by deleting it
        subscriptions = stripe.Subscription.list(
            customer=customer_id,
            status='all',
            expand=['data.default_payment_method']
        )
        return {"subscriptions":subscriptions}
    except Exception as e:
        pass
       

# def update_subscription():
 
#     try:
#         subscription = stripe.Subscription.retrieve(data['subscriptionId'])

#         update_subscription = stripe.Subscription.modify(
#             data['subscriptionId'],
#             items=[{
#                 'id': subscription['items']['data'][0].id,
#                 'price': os.getenv(data['newPriceLookupKey'].upper()),
#             }]
#         )
#         return update_subscription
#     except Exception as e:
#         pass
        
