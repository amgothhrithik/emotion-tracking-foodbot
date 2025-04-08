import re
import  random
def extract_session_id(session_str:str):
    match=re.search(r"/sessions/(.*?)/contexts/",session_str)
    if match:
        return match.group(1)
    return ""


def into_str(inprogress_orders,session_id):
    order_parts = []
    for item, qty in inprogress_orders[session_id].items():
        name = item if qty == 1 else item + "s"
        order_parts.append(f"{int(qty)} {name}")

    if len(order_parts) == 2:
        order_summary = " and ".join(order_parts)
    elif len(order_parts) == 1:
        order_summary = order_parts[0]
    else:
        order_summary = ", ".join(order_parts[:-1]) + " and " + order_parts[-1]
    return  order_summary
