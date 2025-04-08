from emotion_model import predict_emotion
sentences = [
    "Why is my order taking so long?!",
    "Do I need to cook something else, or is my order actually coming?",
    "This delay is unacceptable! Where's my food?!",
    "Is my food walking here by itself or what?",
    "I've been waiting forever! Where is my order?!",

    "This is ridiculous! Where's my food?!",
    "This is ridiculous! I've been waiting forever for my food!",
    "Unbelievable! How can it take so long to deliver a simple order?",
    "I'm extremely frustrated! My order is late again!",
    "This is totally unacceptable. I need my food now!",
    "I've been waiting for an hour! This service is awful!",
    "Why is my order taking so long? This delay is just not okay!",
    "I placed my order ages ago! What’s going on?",
    "This is the worst service ever! I demand an update now!",
    "I'm losing my patience. When will my food actually arrive?",
    "Seriously? I should have received my order by now!",

    "Hey, I just want to check my order status. Can you help?",
    "Can you tell me where my food is? Just curious!",
    "Is my order on the way? I’d love an update!",
    "How long will my food take to arrive?",
    "Can you track my order and let me know when it will be delivered?",
    "I’d like to check the estimated delivery time for my order.",
    "Can you confirm if my order has been dispatched?",
    "Just checking in—how much longer for my food to arrive?",
    "Any updates on my order? I’d appreciate it!",
    "Can you provide a tracking update for my food?",
]




for i in sentences:
  print(i.ljust(50),":",predict_emotion(i))







