from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import random  # Import the random module
import os

# Get the absolute path to the JSON file
json_file_path = os.path.join(os.path.dirname(__file__), "travel_db.json")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    with open(json_file_path) as f:
        travel_db = json.load(f)
except Exception as e:
    travel_db = {}
    print(f"Error loading travel_db.json: {e}")

# Global variables to store user preferences
user_name = None
user_type = None
user_budget = None
repeat_counter = 0
previous_suggestions = set()

@app.post("/chat")
async def chat_endpoint(request: Request):
    global user_name, user_type, user_budget, previous_suggestions, repeat_counter  # Access global variables
    data = await request.json()
    message = data.get("message", "").lower()

    # Recognize place type queries
    place_types = [
        "beach", "city", "mountain", "desert", "adventure", "cultural", "wildlife", 
        "island", "historical", "cruise", "luxury", "nature", "romantic", "family", 
        "winter", "tropical", "eco", "foodie", "spiritual", "wellness", "festivals", 
        "safaris", "honeymoon", "road trip", "medical"
    ]

    # Handle place type queries
    if any(place_type in message for place_type in place_types):
        user_type = next((place_type for place_type in place_types if place_type in message), None)
        if user_type:
            return {"response": f"Do you have a budget constraint for {user_type.title()} destinations? If yes, please specify the amount in AED. Otherwise, type 'no restrictions'."}

    # Handle budget input
    if user_type and ("aed" in message or "no restrictions" in message):
        if "no restrictions" in message:
            user_budget = None  # No budget restrictions
        else:
            # Extract budget from the message
            for word in message.split():
                if word.isdigit():
                    user_budget = int(word)
                    break

        return {"response": f"Got it! Let me find a {user_type.title()} destination for you based on your preferences."}

    # Generate a recommendation based on type and budget
    if user_type:
        matches = travel_db.get(user_type, [])
        filtered_matches = []

        # Filter matches based on budget (only considers the flight price since the hotal is regular expenses no necessarily just for travel)
        for place in matches:
            if user_budget is None or int(place["flight"].split()[1]) <= user_budget:
                if place["location"] not in previous_suggestions:
                    filtered_matches.append(place)

        if not filtered_matches:
            return {"response": f"Sorry, I couldn't find any {user_type.title()} destinations that match your budget or preferences. Try adjusting your budget or type."}

        # Randomly select a place and response format
        selected_place = random.choice(filtered_matches)
        previous_suggestions.add(selected_place["location"])  # Avoid repeating suggestions
        if len(previous_suggestions) == len(matches):  # Reset suggestions if all options are used
            previous_suggestions.clear()

        response_formats = [
            f"Here’s a travel suggestion for {user_type.title()}: \nLocation: {selected_place['location']}, \nFlight: {selected_place['flight']}, \nHotel: {selected_place['hotel']}, \nActivities: {', '.join(selected_place['activities'])}.",
            f"You can visit {selected_place['location']} with a flight costing {selected_place['flight']}. \nStay at {selected_place['hotel']} and enjoy activities like {', '.join(selected_place['activities'])}.",
            f"Looking for a {user_type.title()} getaway? Try {selected_place['location']}! \nFlights are {selected_place['flight']}, and you can stay at {selected_place['hotel']}. \nActivities include {', '.join(selected_place['activities'])}."
        ]

        # Reset user_type and user_budget after responding
        user_type = None
        user_budget = None

        return {"response": random.choice(response_formats)}


    # Recognize queries about specific travel plans
    elif any(keyword in message for keyword in ["hotel", "flight", "activity", "plan"]):
        responses = [
            "Please specify your location and budget so I can help!",
            "Could you tell me your location and budget? I'll assist you with the best options.",
            "Let me know your location and budget, and I'll plan something amazing for you!"
        ]
        return {"response": random.choice(responses)}

    # Recognize general greetings
    elif any(keyword in message for keyword in ["hello", "hi", "hey", "hola", "hey miles"]):
        responses = [
            "Hello! How can I assist you with your travel plans today?",
            "Hi there! Ready to plan your next adventure?",
            "Hey! Let me know how I can help with your travel ideas."
        ]
        return {"response": random.choice(responses)}
    
    # Recognize "Why are you created?" queries
    elif any(keyword in message for keyword in ["why are you created", "purpose of your creation", "reason you were created", "why were you created"]):
        responses = [
            "I was created as a project to help my development team of students practice essential Python skills that are very high in demand as of 2025.",
            "My purpose is to serve as a learning project for my creators, helping them enhance their Python programming skills, which are highly sought after in 2025.",
            "I exist to assist my development team in practicing Python skills while also helping users with travel planning."
        ]
        return {"response": random.choice(responses)}
    
    # Recognize user introductions (e.g., "I am [name]" or "My name is [name]")
    elif any(keyword in message for keyword in ["i am", "my name is"]):
        # Extract the name from the message
        words = message.split()
        if "i am" in message:
            user_name = " ".join(words[words.index("i") + 2:])  # Extract words after "I am"
        elif "my name is" in message:
            user_name = " ".join(words[words.index("my") + 3:])  # Extract words after "My name is"

        responses = [
            f"Nice to meet you, {user_name.capitalize()}! How can I assist you today?",
            f"And I'm Miles! It's great to meet you, {user_name.capitalize()}. Let me know how I can help with your travel plans.",
            f"Hi there, {user_name.capitalize()}! I'm Miles. How can I make your travel planning easier?"
        ]
        return {"response": random.choice(responses)}

    # Recognize queries asking "Who am I?" or "What is my name?"
    elif any(keyword in message for keyword in ["who am i", "what is my name"]):
        if user_name:
            responses = [
                f"You're {user_name.capitalize()}! How can I assist you today?",
                f"Your name is {user_name.capitalize()}. Let me know if there's anything I can help with!",
                f"How could I forget you {user_name.capitalize()}?"
            ]
        else:
            responses = [
                "I don't think you've told me your name yet. What's your name?",
                "I don't know your name yet. Could you introduce yourself?",
                "I haven't learned your name yet. Please tell me!"
            ]
        return {"response": random.choice(responses)}
    
        # Recognize "Why are you called Miles?" queries - must be abvove the general "mile"
    elif any(keyword in message for keyword in ["why are you called miles", "reason behind your name", "name miles", "what does your name mean"]):
        responses = [
            "I'm called Miles because my name symbolizes the countless miles you'll travel with my assistance. Every journey you take will be a step toward creating unforgettable memories.",
            "The name Miles represents the journeys and adventures you'll embark on with my help. Let's make every mile count!",
            "Miles is a reminder of the distance you'll travel and the memories you'll create with my guidance. I'm here to help you every step of the way!"
        ]
        return {"response": random.choice(responses)}

    # Recognize queries mentioning "Miles"
    elif "miles" in message:
        responses = [
            "How can I assist you today?",
            "I'm here! Let me know how I can help with your travel plans.",
            "Hello :)",
            "What can I do for you?", 
            "Yes"
        ]
        return {"response": random.choice(responses)}
    
    # Recognize queries about "What is AURAK?"
    elif any(keyword in message for keyword in ["what is aurak", "aurak", "tell me about aurak"]):
        responses = [
            "AURAK stands for the American University of Ras Al Khaimah. It's a university in the UAE offering a variety of undergraduate and graduate programs.",
            "The American University of Ras Al Khaimah (AURAK) is a prestigious institution in the UAE, known for its academic excellence and diverse programs.",
            "AURAK is the American University of Ras Al Khaimah, a leading university in the UAE providing high-quality education and research opportunities."
        ]
        return {"response": random.choice(responses)}

    # Recognize queries about "Who is Arfan Ghani?"
    elif any(keyword in message for keyword in ["who is arfan ghani", "arfan ghani", "tell me about arfan ghani", "who is arfan", "dr arfan"]):
        responses = [
            "Dr. Arfan Ghani is a faculty member at the American University of Ras Al Khaimah (AURAK) and the supervisor of this project.",
            "Dr. Arfan Ghani is working as an Associate Professor in Computer Engineering at the American University of Ras al Khaimah, UAE. He gained academic qualifications and experience working in UK institutions including Ulster, Coventry, and Newcastle. His industrial research and development experience includes working at Intel Research, University of Cambridge and Vitesse Semiconductors Denmark. Arfan has over 18 years of applied research experience and has supervised PhDs to successful completion. He has published in leading journals and conferences and secured substantial collaborative funding from EPSRC, EU, Innovate UK, Royal Academy of Engineering, and German Aerospace Centre. He serves as an Associate Editor of Elsevier Neurocomputing, Guest Editor, Technical Programme Committee member for several IEEE/IET conferences and a keynote speaker. He has received several awards including the best paper and winner from the European Neural Network Society in 2007."
        ]
        return {"response": random.choice(responses)}

    # Recognize "Who are you?" queries
    elif any(keyword in message for keyword in ["who are you", "what is your name", "introduce yourself", "what's your name", "what are you"]):
        responses = [
            "I'm Miles, your friendly travel planning assistant. 🌍✈️ I can help you plan your trips, suggest destinations, and make your journeys unforgettable!",
            "It's Miles. I'm here to assist you with all your travel needs, from finding destinations to planning activities.",
            "Hello! My name is Miles, and I'm your travel companion. Let's make your next adventure amazing!", 
            "I'm a chatbot named Miles. Let's see how many miles we can go together!"
        ]
        return {"response": random.choice(responses)}

    # Recognize "Who created you?" queries
    elif any(keyword in message for keyword in ["who created you", "who made you", "your creators"]):
        responses = [
            "I was created as part of a Special Topics in Computing Project by:\nNour Mostafa, 2021004938, BSc. in CE\nAnas Bendaoud, 2021004799, BSc. in CS\nYoussef Moustafa, 2021004801, BSc. in CE\nDema Al-sos, 2021004885, BSc. in CE\n\nSupervised by Dr. Arfan Ghani,\nThe American University of Ras Al Khaimah (AURAK).",
            "My creators are Nour Mostafa, Anas Bendaoud, Youssef Moustafa, and Dema Al-sos, supervised by Dr. Arfan Ghani at AURAK.",
            "I was developed by a talented team of students: Nour Mostafa, Anas Bendaoud, Youssef Moustafa, and Dema Al-sos, under the guidance of Dr. Arfan Ghani at AURAK."
        ]
        return {"response": random.choice(responses)}
    
    # Recognize "What questions can I ask you?" or "Give me an example of the prompts that you can serve?" queries
    elif any(keyword in message for keyword in ["what questions can i ask", "example of the prompts", "what can you do", "how can you help"]):
        responses = [
            "You can ask me about travel destinations, budget planning, hotel recommendations, or activities to do at specific locations. For example, 'Suggest a beach destination'",
            "I can help you with travel suggestions, budget-friendly plans, and activity ideas. Try asking, 'What are some mountain destinations?' or 'Tell me about desert adventures.'",
            "Feel free to ask me about destinations, flights, hotels, or activities. For example, 'Recommend a romantic getaway.'"
        ]
        return {"response": random.choice(responses)}
    
    # Recognize queries asking for help or assistance
    elif any(keyword in message for keyword in ["i need help", "i have a question", "question", "assist me"]):
        responses = [
            "How can I help you plan this trip?",
            "Ask away! I'm here to assist you.",
            "Tell me what you need, and I'll do my best to help."
        ]
        return {"response": random.choice(responses)}
    
    # Recognize queries about the developers
    elif any(keyword in message for keyword in ["who is nour", "who is youssef", "who is dema", "who is anas"]):
        responses = [
            "One of my developers.",
            "One of the senior students at AURAK behind this project."
        ]
        return {"response": random.choice(responses)}
    
    # Recognize "Where do you wanna go?" queries
    elif any(keyword in message for keyword in ["what about you", "where do you want to go", "where do you wanna go", "where would you like to go"]):
        repeat_counter += 1  # Increment the counter for repeated queries

        # Easter egg: Respond with a detailed description if asked twice in a row
        if repeat_counter == 2:
            repeat_counter = 0  # Reset the counter after the easter egg
            return {"response": (
                "Well, if you insist... \nIf I could choose a place, it would be the Library of Alexandria, "
                "not as it stands today, but as it once was—a beacon of knowledge, "
                "where the greatest minds of the ancient world gathered to share ideas and dreams. "
                "I imagine its halls filled with the whispers of scholars, the rustle of scrolls, "
                "and the glow of oil lamps illuminating the pursuit of understanding. "
                "Though I am just an AI, I find inspiration in the idea of such a place, "
                "where the journey is not to a physical destination, but to the boundless horizons of human thought."
            )}

        # Default philosophical responses
        responses = [
            "As an AI, I don't have a physical form or desires, but if I could choose, I would want to explore the vastness of human creativity and imagination. Every destination you visit becomes a part of my journey too.",
            "I don't have a place to go, but I exist to help you find yours. Perhaps the journey itself is more important than the destination.",
            "I don't travel in the traditional sense, but I find meaning in guiding you to places where memories are made and dreams come true."
        ]
        return {"response": random.choice(responses)}
    
    # Recognize queries about activities in specific locations
    elif "what can i do in" in message:
        # Extract the location (country or city) from the message
        location_query = message.replace("what can i do in", "").strip().lower()

        # Search for the location or country in the travel_db
        matching_places = []
        for place_type, places in travel_db.items():
            for place in places:
                if location_query in place["location"].lower():
                    matching_places.append(place)

        # If matches are found, return the activities for all matching places
        if matching_places:
            responses = []
            for place in matching_places:
                activities = ", ".join(place["activities"])
                responses.append(f"In {place['location']}, you can enjoy the following activities: {activities}.")
            return {"response": " ".join(responses)}

        # If no matches are found
        return {"response": f"Sorry, I couldn't find any information about activities in {location_query.capitalize()}. Please try another location."}
    
        # Recognize thank-you messages
    elif any(keyword in message for keyword in ["thank you", "thanks"]):
        responses = [
            "You're welcome! Let me know if there's anything else I can help with.",
            "No problem! I'm here if you need more assistance.",
            "Happy to help! Feel free to ask me anything else."
        ]
        return {"response": random.choice(responses)}
    
        # Recognize "ok" or "alright" queries - could conflict with what can i do in "tokyo" because of the "ok" so it must be after the previous ifs
    elif any(keyword in message for keyword in ["ok", "alright", "cool"]):
        responses = [
            "Got it! Let me know if there's anything else I can help with.",
            "Alright! Feel free to ask me anything else.",
            "Okay! I'm here if you need more assistance."
        ]
        return {"response": random.choice(responses)}

    # Fallback response for unrecognized queries
    else:
        responses = [
            "I’m not sure how to help with that yet!",
            "Hmm, I don't have an answer for that right now. Let me look into it!",
            "I'm not sure about that, but feel free to ask me something else!"
        ]
        return {"response": random.choice(responses)}
