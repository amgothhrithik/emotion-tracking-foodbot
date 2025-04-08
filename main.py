import db_connector
from emotion_model import predict_emotion
from db_connector import get_order_status, get_next_order_id
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import random
import helper
app = FastAPI()
inprogress_orders={}
ANGER_EMOTIONS = {"anger", "annoyance", "disappointment", "frustration", "disapproval", "disgust"}

DELAY_KEYWORDS = {
    "taking too long", "so long", "still waiting", "forever", "late", "delay", "delayed", "delays",
    "delaying", "waiting for so long", "still hasn’t arrived", "how much longer", "still not here",
    "longer than usual", "while ago", "delivered yet", "still says preparing", "saying still preparing",
    "order status still the same", "no update on my order", "says still in preparation", "is my order even coming"
}


@app.post("/webhook")
async def webhook(request: Request):
    req = await request.json()
    user_message = req['queryResult']['queryText']
    intent_name = req['queryResult']['intent']['displayName']
    parameters=req['queryResult']['parameters']
    output_contexts=req['queryResult']['outputContexts']
    session_id = helper.extract_session_id(output_contexts[0]["name"])
    print(f"Intent Detected: {intent_name}")

    intent_handler_dict={
        "add_order_context-ongoing_order": add_to_order,
        "remove.order-context:ongoing_order":remove_from_order,
        "track_order_no_context-ongoing_order":track_order_no,
        "order_complete-context:ongoing_order":complete_order,
        "Tracking.Order": tracking_order

    }
    if intent_name=="Tracking.Order":
        return intent_handler_dict[intent_name](parameters,user_message)
    else:
        return intent_handler_dict[intent_name](parameters,session_id)

def remove_from_order(parameters: dict, session_id: str):
    if session_id not in inprogress_orders:
        return JSONResponse(content={
            "fulfillmentText": '''We're sorry, but we’re having trouble finding your order.
                Could you please place a new one? We sincerely apologize for the inconvenience.'''
        })
    else:


        current_order = inprogress_orders[session_id]
        food_items = parameters["food_items"]
        quantities = parameters["number"]

        if len(food_items) != len(quantities):
            return JSONResponse(content={
                "fulfillmentText": '''Sorry I didn't understand.
                Can you please specify food items with their respective quantities.'''
            })

        not_list = []
        more_quantity = []

        for item, qty in zip(food_items, quantities):
            if item in current_order:
                if qty <= current_order[item]:
                    current_order[item] -= qty
                    if current_order[item] == 0:
                        del current_order[item]
                else:
                    more_quantity.append(item)
                    del current_order[item]
            else:
                not_list.append(item)

        not_present_items = ""
        if len(not_list) == 1:
            not_present_items = f"Food item {not_list[0]} was not present in the order. "
        elif len(not_list) > 1:
            not_present_items = f"Food items {', '.join(not_list)} were not present in the order. "

        more_in_quantities = ""
        if len(more_quantity) == 1:
            more_in_quantities = f"And quantity of food item {more_quantity[0]} was more than present in the order. So removed it completely. "
        elif len(more_quantity) > 1:
            more_in_quantities = f"And quantities of food items {', '.join(more_quantity)} were more than present in the order. So removed them completely. "

        if current_order:
            updated_order = f"After processing your remove request, your current order is: {helper.into_str(inprogress_orders,session_id)}"
        else:
            updated_order = "After processing your remove request, your order is now empty."

        return JSONResponse(content={
            "fulfillmentText": f"{not_present_items}{more_in_quantities}{updated_order} Do you want to add anything else?"
        })


def add_to_order(parameters: dict, session_id: str):
    food_item = parameters["food_items"]
    quantities = parameters["number"]

    follow_ups = [
        "Anything else you want me to add?",
        "Should I include anything else for you?",
        "Need anything else added to your order?",
        "Let me know if you’d like to add something else!"
    ]

    if len(food_item) != len(quantities):
        fulfillment_text = '''Sorry I didn't understand.
        Can you please specify food items with their 
        respective Quantities'''
    else:
        new_food_dict = dict(zip(food_item, quantities))
        print("new food-items to be added", new_food_dict)

        if session_id in inprogress_orders:
            current_food_dict = inprogress_orders[session_id]
            print("current food_items", current_food_dict)

            # ✅ Add values instead of replacing
            for item, qty in new_food_dict.items():
                if item in current_food_dict:
                    current_food_dict[item] += qty
                else:
                    current_food_dict[item] = qty

            print("after update", current_food_dict)
        else:
            inprogress_orders[session_id] = new_food_dict
            print("new order", inprogress_orders[session_id])

        order_summary = helper.into_str(inprogress_orders,session_id)
        follow = [
            "Let me confirm your order:", "Currently your order is",
            "So far you have", "Here’s what you’ve ordered so far:",
            "Right now, your order has:"
        ]
        fulfillment_text = f"{random.choice(follow)} {order_summary}. {random.choice(follow_ups)}"

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })


def complete_order(parameters:dict,session_id:str):
    if session_id not in inprogress_orders:
        fulfillment_text='''We're sorry, but we’re having trouble finding your order.
         Could you please place a new one? We sincerely apologize for the inconvenience.'''
    else:
        order=inprogress_orders[session_id]
        order_id=save_to_db(order)
        if order_id==-1:
            fulfillment_text=''' Sorry, we can't process your order due to Backend Error.
            Please place a new Order again'''
        else:
            order_total=db_connector.get_total_order_price(order_id)
            fulfillment_text = f"Awesome, We have placed your order." \
                               f"Your Order Id  is {order_id}." \
                               f"Your order total is ₹{order_total:.2f}"\
                               f". Your order preparation will be started shortly."

        del inprogress_orders[session_id]
    return JSONResponse(content={
            "fulfillmentText": fulfillment_text
        })


def save_to_db(order: dict):
    next_order_id = db_connector.get_next_order_id()


    for item, qty in order.items():

        rcode = db_connector.insert_order_item(item, qty, next_order_id)
        if rcode == -1:
            return -1

    status = ["in preparation", "in transit", "delivered", "ready for pickup"]
    db_connector.insert_order_tracking(next_order_id, random.choice(status))
    return next_order_id






disturb_no_par= [
    "We apologize for the wait!Could you provide your order ID? I’ll check the status right away.",
    "Sorry for the wait! Could you share your order ID? I’ll look into the status immediately.",
    "We regret any inconvenience caused by the wait. Kindly share your order ID, and I will promptly check the status for you.",
    "We apologize for the delay and appreciate your understanding. Please share your order ID, and I’ll be happy to check the status for you.",
    "We regret any inconvenience caused by the delay. Please provide your order ID, and I will promptly check the status for you.",
    "We value your patience and sincerely apologize for the delay. If you could provide your order ID, I will check on its status immediately.",
    "We deeply regret any inconvenience this may have caused. Please let me know your order ID, and I will prioritize checking its status for you."
]
normal_no_par= [
    "Definitely. What is your order id for tracking your food.",
    "I can help you track your order! Please provide your order ID.",
    "Please share your order ID so I can check your order status.",
    "Certainly! Kindly share your order ID, and I will check the status for you.",
    "Let me find your order. Can you provide your order ID?",
    "Sure. Please enter your order ID for tracking.",
    "Sure. Please enter your order ID so I can track your food for you?",
    "Definitely. For tracking can you specify please is your order id?"
]
disturb_with_par=[
    "We apologize for the wait!?",
    "Apologies for the delay you’ve experienced.",
    "I’m really sorry for the inconvenience. ",
    "We regret any inconvenience caused by the wait.",
    "We apologize for the delay and appreciate your understanding.",
    "We regret any inconvenience caused by the delay.",
    "We value your patience and sincerely apologize for the delay.",
    "We deeply regret any inconvenience this may have caused."
]
# normal_with_par = [
#     "I'm currently checking the status of your order. Please give me a moment!",
#     " I’m checking your order status immediately.Please give me a moment!",
#     "One moment please, I’m checking the status of your order.",
#     "I’m on it! Just checking your order details now.",
# "I’m fetching the latest status of your order. Kindly hold on a second.",
# "Please give me a moment, I’m verifying the order details now.",
# "Give me a second, I'm retrieving the order status for you.",
#     "Checking the status of your order right away. Hang tight!",
#     "I'm processing your request and checking the order status.",
#     "Give me a second, I'm retrieving the order status for you.",
# ]
normal_with_par = [
    "We have checked the order  ",
]
def tracking_order(parameters:dict,user_message:str):

    print(parameters,user_message)
    if any(kw in user_message.lower() for kw in DELAY_KEYWORDS):
        emotion = "disturbed"

    else:
        detected_emotions = predict_emotion(user_message)
        print(f"Detected Emotions: {detected_emotions}")

        if any(emotion in detected_emotions for emotion in ANGER_EMOTIONS):
            emotion = "disturbed"
        else:
            emotion = "Normal"


    if not parameters.get('number'):
        if emotion == "Normal":
            fulfillment_text = random.choice(normal_no_par)
        else:
            fulfillment_text = random.choice(disturb_no_par)
        return JSONResponse(content={
            "fulfillmentText": fulfillment_text
        })
    else:
        if emotion == "Normal":
            fulfillment_text = random.choice(normal_with_par)
        else:
            fulfillment_text = f"{random.choice(disturb_with_par)}{random.choice(normal_with_par)}"

        return track_order_no(parameters,fulfillment_text)



def track_order_no(parameters: dict, fulfillment_text=None):
    order_id = int(parameters["number"])
    order_status = get_order_status(order_id)

    if order_status:
        result_message = f" The Order Status of order ID: {order_id} is: {order_status}"
    else:
        result_message = f"no Order Status for order ID: {order_id} is Found"

    # Append result_message to fulfillment_text if provided; otherwise use result_message as is.
    if fulfillment_text:
        final_message = f"{fulfillment_text}. {result_message}"
    else:
        final_message = result_message

    return JSONResponse(content={
        "fulfillmentText": final_message
    })

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)

