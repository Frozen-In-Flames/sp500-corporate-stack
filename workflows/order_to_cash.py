"""Order-to-cash across four S&P 500 vendors on the shared shelf.

PayPal takes the payment, FedEx quotes the shipment, QuickBooks books the
invoice, Webex notifies the sales room. Four vendors, one workflow, no
vendor owns the shelf.
"""

WORKFLOW = {
    "name": "Order to cash",
    "description": ("Take payment, quote shipping, book the invoice, "
                    "notify sales."),
    "steps": [
        {"step": 1, "adapter": "PYPL",
         "action": "create checkout order (payment)"},
        {"step": 2, "adapter": "FDX",
         "action": "quote shipping rate"},
        {"step": 3, "adapter": "INTU",
         "action": "book invoice in accounting"},
        {"step": 4, "adapter": "CSCO",
         "action": "notify sales room"},
    ],
}
