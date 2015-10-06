import json

import plamee.utils as utils
import plamee.utils.html

from plamee.cakestory import *
from plamee.fb.ogdbg import *

import plamee.log as log

# Errors handling

errors = []

def log_error(message):
    errors.append(message)
    log.error(message, False)

def raise_errors():
    if(len(errors)):
        raise RuntimeError("Some errors occurred:\n" + "\n".join(errors))

# Load defs
defs = Client(NetworkType.DEVICE).defs.data

if "payments" in defs:
    defs = defs["payments"]
else:
    raise RuntimeError("Payments are not found in defs.")

# Init OpenGraph debugger
debugger = OpenGraphDebugger("a.strelkov@plamee.com", "0119643")

payment_names = sorted(defs.keys())

for i in range(len(payment_names)):
    payment_name = payment_names[i]

    # Get payment config
    payment = defs[payment_name]

    if "store" in payment:
        payment = payment["store"]
    else:
        continue

    if "FB" in payment:
        payment = payment["FB"]
    else:
        continue

    log.debug("[%d%%] Checking tier %s..." % (round(100.0 * i / len(payment_names)), payment_name))

    # Load the Scrawler's response
    try:
        result = debugger.check_url(urlparse.urljoin("http://%s" % Net.get_host(), payment["id"]))
    except:
        log_error("Error occurred for %s during attempt to get scraped data." % payment_name)
        continue

    if result["status"]["response-code"] != 200:
        log_error("The Scrawler's response code is invalid: %d." % result["status"]["response-code"])
        continue

    # Parse prices
    temp_prices = None

    if not result["contents"].has_key("product:price"):
        log_error("Prices are not found in FB response for %s." % payment_name)
        continue
    else:
        temp_prices = utils.html.get_tags(result["contents"]["product:price"], "pre")
        for i in range(len(temp_prices)):
            temp_prices[i] = utils.html.get_tag_data(temp_prices[i])
            temp_prices[i] = utils.html.unescape(temp_prices[i])

    temp_prices = json.loads("[" + ", ".join(temp_prices) + "]")

    fb_prices = {}
    for temp_price in temp_prices:
        fb_prices[temp_price["currency"]] = temp_price["amount"]

    sv_prices = payment["price"]

    # Compare prices
    if len(fb_prices.keys()) != len(sv_prices.keys()):
        log_error("FB has different number of prices for %s: %d in defs against %d in FB." % (payment_name, len(sv_prices.keys()), len(fb_prices.keys())))
        continue

    for key in fb_prices.keys():
        if not sv_prices.has_key(key):
            log_error("Price in %s is not found in %s" % (key, payment_name))
            continue
        if fb_prices[key] != sv_prices[key]:
            log_error("Price in %s is different for %s: %f in defs against %f in FB." % (key, payment_name, sv_prices[key], fb_prices[key]))
            continue

log.debug("[100%] All tiers are checked.")
raise_errors()