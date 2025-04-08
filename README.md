# Emotion-Tracking-FoodBot
We're building a smart food delivery chatbot backend using FastAPI that connects with Dialogflow ES. The chatbot helps users:
- Place food orders.
- Update or remove items from their order.
- Track their order status.
- Get personalized responses based on their emotions.

## Architecture Overview
- Frontend: Dialogflow ES handles user interaction (via text/voice).
- Backend: FastAPI serves as a webhook for Dialogflow intents.
- Emotion Engine: A custom emotion detection model predicts user emotions from their messages.
- Database: Stores order data, item quantities, and order status.

## Request Flow (End-to-End)
1. User Message: Sent to Dialogflow (e.g., “Where is my food?”).

2. Dialogflow Intent Detection: Identifies the intent (e.g., Tracking.Order).

3. Webhook Trigger: Dialogflow calls our FastAPI /webhook endpoint with:
    - queryText (user message),
    - intent.displayName (identified intent),
    - parameters (extracted entities),
    - outputContexts (for session ID tracking).

4. FastAPI Router:
   Intent is routed to one of these handlers:
   - `add_to_order`
   - `remove_from_order`
   - `complete_order`
   - `tracking_order`
   - `track_order_no`
## Database Operations
Located in `db_connector.py`, key DB functions include:
- `get_next_order_id()`: Returns the next available order ID.
- `insert_order_item(item, qty, order_id)`: Adds individual items to DB.
- `insert_order_tracking(order_id, status)`: Initializes status like "in preparation".
- `get_order_status(order_id)`: Retrieves the current status of an order.
- `get_total_order_price(order_id)`: Returns the price of the completed order.

Disclaimer : I have use the resources of database from  codebasics github
