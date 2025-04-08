# Emotion-Tracking-FoodBot
We're building a smart food delivery chatbot backend using FastAPI that connects with Dialogflow ES. The chatbot helps users:
- Place food orders.
- Update or remove items from their order.
- Track their order status.
- Get personalized responses based on their emotions.

## How it works:
- Dialogflow detects the user's intent (like "add to order", "track my food", etc.).
- It sends the request to our FastAPI webhook.
- The backend processes the request, interacts with the database, detects emotions if needed, and sends back a suitable response.
