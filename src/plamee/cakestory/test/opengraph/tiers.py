import plamee.utils as utils
import plamee.utils.html

from plamee.cakestory import *
from plamee.utils.fb.ogdbg import *

# Load defs
defs = Net.send(Commands.ServerCommand("/defs?group=default", None, Net.RequestMethod.GET)).response

if "payments" in defs:
    defs = defs["payments"]
else:
    raise RuntimeError("Payments are not found in defs.")

# Init OpenGraph debugger
debugger = OpenGraphDebugger("a.p.strelkov@gmail.com", "stre1a")

for payment_name in defs:
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

    # Load the Scrawler's response
    result = debugger.check_url("http://cakestory.plamee.com" + payment["id"])

    status_checked = False
    for status_field in result["status"]:
        if status_field[0].strip().lower() == "response code":
            match = re.search(r"\d+", status_field[1])
            if match is None or int(match.group(0)) != 200:
                raise RuntimeError("The Scrawler returned invalid response code.")
            else:
                status_checked = True
            break

    if not status_checked:
        raise RuntimeError("The Scrawler's response code is not found.")

    # Parse prices
    temp_prices = None

    for content_field in result["contents"]:
        if content_field[0].strip().lower() == "product:price":
            temp_prices = utils.html.get_tags(content_field[1], "pre")
            for i in range(len(temp_prices)):
                temp_prices[i] = utils.html.unescape(temp_prices[i])
                temp_prices[i] = utils.html.get_tag_data(temp_prices[i])
            break

    if temp_prices is None:
        raise RuntimeError("Prices are not found in FB response.")

    temp_prices = json.loads("[" + ", ".join(temp_prices) + "]")

    fb_prices = {}
    for temp_price in temp_prices:
        fb_prices[temp_price["currency"]] = temp_price["amount"]

    sv_prices = payment["price"]

    # Compare prices
    if len(fb_prices.keys()) != len(sv_prices.keys()):
        raise RuntimeError("FB has different number of prices for %s: %d in defs against %d in FB." % (payment_name, len(sv_prices.keys()), len(fb_prices.keys())))

    for key in fb_prices.keys():
        if not sv_prices.has_key(key):
            raise RuntimeError("Price in %s is not found in %s" % (key, payment_name))
        if fb_prices[key] != sv_prices[key]:
            raise RuntimeError("Price in %s is different for %s: %f in defs against %f in FB." % (key, payment_name, sv_prices[key], fb_prices[key]))

