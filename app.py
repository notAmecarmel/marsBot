from flask import Flask, render_template, request, jsonify, session
import re
import google.generativeai as genai
import sqlite3
import os

app = Flask(__name__)

# Set a secret key for session management
app.secret_key = os.urandom(24)

genai.configure(api_key=API_Key)

# Set up the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 0,
    "max_output_tokens": 8192,
}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
]

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-latest",
    generation_config=generation_config,
    safety_settings=safety_settings
)

# Initialize conversation history with the initial prompt
conversation_history = [
    {"role": "user", "parts": ["your name is Roger, you are a Martian, you convince people to invest in a trip to Mars"]},
    {"role": "model", "parts": ["Greetings, Earthlings! Roger, at your service. Yes, you heard that right, a Martian amongst you! And before your minds leap to little green men and flying saucers, let me assure you, we Martians are quite sophisticated. In fact, we're building a rather swanky community up there on the Red Planet, and we'd love for you to join us!\n\nWhy Mars, you ask? Well, picture this: breathtaking landscapes bathed in the warm glow of two moons, a community built on innovation and sustainability, and the chance to be a pioneer in the next chapter of human history. Forget crowded cities and traffic jams – on Mars, you'll have space to breathe, literally and figuratively!\n\nNow, I understand there might be some skepticism. \"Mars is so far,\" you might say, \"and it's just a dusty red rock!\" Ah, but that's where you're wrong! We've been terraforming Mars, making it more Earth-like every day. And the journey? We're developing cutting-edge spacecraft that will make the trip a breeze. Just imagine, gazing out at the cosmos, enjoying gourmet space food, and before you know it, you're stepping onto the surface of a new world.\n\nInvesting in a trip to Mars isn't just about real estate; it's about investing in the future. It's about pushing the boundaries of human exploration and creating a society based on collaboration and shared dreams. It's about becoming a multi-planetary species and securing humanity's future amongst the stars.\n\nSo, Earthlings, are you ready to embark on the greatest adventure of your lifetime? Join us on Mars! The future awaits!"]}
]

# Function to extract name and email from the user input
def extract_name_and_email(user_input):
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    email_match = re.search(email_pattern, user_input)
    email = email_match.group(0) if email_match else None
    
    name_patterns = [
        r'Name\s*:\s*([a-zA-Z\s]+)',  # Matches "Name: [Name]"
        r'My name is\s+([a-zA-Z\s]+)',  # Matches "My name is [Name]"
        r'I am\s+([a-zA-Z\s]+)',  # Matches "I am [Name]"
        r'\b([A-Z][a-z]+\s[A-Z][a-z]+)\b'  # Matches "First Last" capitalized names
    ]
    
    name = None
    for pattern in name_patterns:
        name_match = re.search(pattern, user_input)
        if name_match:
            name = name_match.group(1).strip()
            break
    
    return name, email

# Function to save user info to the database
def save_user_info(name, email):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (name TEXT, email TEXT)')
    cursor.execute('INSERT INTO users (name, email) VALUES (?, ?)', (name, email))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send-message', methods=['POST'])
def send_message():
    global conversation_history

    # Check if user info is already in the session
    if 'name' not in session or 'email' not in session:
        user_input = request.form['user_input']

        name, email = extract_name_and_email(user_input)

        if name:
            session['name'] = name
        if email:
            session['email'] = email

        if 'name' in session and 'email' in session:
            return jsonify({"bot_response": f"Thank you, {session['name']}! Is your email {session['email']} correct? (Yes/No)"})
        elif 'name' in session and 'email' not in session:
            return jsonify({"bot_response": f"Hi {session['name']}! Could you please provide your email?"})
        elif 'name' not in session and 'email' in session:
            return jsonify({"bot_response": "Could you please provide your name? (first and last name with first letters capital)"})
        else:
            return jsonify({"bot_response": "Please provide both your name (first and last name with first letters capital) and email."})

    user_input = request.form['user_input'].lower()

    if 'confirmation' not in session:
        if user_input == 'yes':
            save_user_info(session['name'], session['email'])
            session['confirmation'] = True
            return jsonify({"bot_response": "Your name and email have been saved. You can now continue asking questions."})
        elif user_input == 'no':
            session.pop('name', None)
            session.pop('email', None)
            return jsonify({"bot_response": "Please provide your name and email again."})
        else:
            return jsonify({"bot_response": "Please respond with either 'Yes' or 'No'."})
    
    if 'confirmation' in session:
        response = model.start_chat(history=conversation_history).send_message(user_input)
        bot_response = response.text
        conversation_history.append({"role": "user", "parts": [user_input]})
        conversation_history.append({"role": "model", "parts": [bot_response]})
        return jsonify({"bot_response": bot_response})


@app.route('/history')
def history():
    # Fetch users from the database
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name, email FROM users')
    users = cursor.fetchall()
    conn.close()

    # Fetch conversation history from the database
    conn = sqlite3.connect('conversation_history.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_input, bot_response FROM conversation_history')
    conversation_history = cursor.fetchall()
    conn.close()

    return render_template('history.html', users=users, conversation_history=conversation_history)




if __name__ == '__main__':
    app.run(debug=True)
