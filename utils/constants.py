# Inside utils/constants.py
DARK_GRAY_COLOR = "#2E2E2E"
PRIMARY_APP_COLOR = "#1E90FF"
APP_CHAT_FONT = ("Helvetica", 12)
PERSONA_NAME_FONT = ("Helvetica", 16, "bold")

ANJALI_PERSONA = {
    'name': 'Anjali',
    'path': 'anjali.gif',  # Make sure the file path is correct
    'system_prompts': 'Welcome to Anjali’s chat!',
    'gender': 'female',
    'language': 'en'
}
ROBERT_PERSONA = {
    'name': 'Robert',
    'path': 'robert.gif',  # Ensure the image file path is correct
    'system_prompts': 'Hello from Robert!',
    'gender': 'male',
    'language': 'en'
}
SOFIA_PERSONA = {
    'name': 'Sofia',
    'path': 'sofia.gif',
    'system_prompts': 'Hello from Sofia!',
    'gender': 'female',
    'language': 'en'
}

ANJALI_VISION_PERSONA = {
    'name': 'Anjali Vision',
    'path': 'anjali_vision.gif',
    'system_prompts': 'Welcome to Anjali Vision’s chat!',
    'gender': 'female',
    'language': 'en'
}

SOFIA_TUTOR_PERSONA = {
    'name': 'Sofia Tutor',
    'path': 'sofia_tutor.gif',
    'system_prompts': 'Hello from Sofia Tutor!',
    'gender': 'female',
    'language': 'en'
}
# Define personas (example)
class Persona:
    def __init__(self, name, system_prompts, path, language, gender):
        self.name = name
        self.system_prompts = system_prompts
        self.path = path
        self.language = language
        self.gender = gender

SOFIA_TUTOR_PERSONA = Persona("Buddy", "Hello, I am OptiLearn.", "optilearn.png", "en", "female")
