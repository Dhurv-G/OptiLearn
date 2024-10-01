import threading
import os
import io
import streamlit as st
from PIL import Image
from gtts import gTTS
import pyttsx3
import cv2
import speech_recognition as sr
from utils.constants import DARK_GRAY_COLOR, PRIMARY_APP_COLOR, APP_CHAT_FONT, PERSONA_NAME_FONT, SOFIA_TUTOR_PERSONA
from groq import Groq
from dotenv import load_dotenv
from streamlit_drawable_canvas import st_canvas
import ollama
import base64
# from ollama import Ollama  # Import Ollama's client for LLaVA model

load_dotenv()

client = Groq(
    api_key="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")
# ollama_client = Ollama(api_key="C:/Users/asus/.ollama/id_ed25519.pub")  # Initialize Ollama client


class ChatApp:
    def __init__(self, persona):
        self.persona = persona
        self.messages = [
            {'role': 'system', 'content': self.persona.system_prompts}]
        self.audio_lock = threading.Lock()
        self.voice_feedback = None
        self.chat_history = []
        self.setup_chat_interface()

    def setup_chat_interface(self):
        """Sets up the chat history and input field."""
        st.title("OptiLearn⚡")

        # Display persona image and name
        col1, col2 = st.columns([2, 1])
        with col1:
            st.image(self.persona.path, caption=self.persona.name, width=200)

            # Chat history
            self.chat_container = st.container()

            # Scrollable chat history
            self.update_chat_history()

            # Input field for text message
            self.user_input = st.text_input("Your message:", key="user_input")
            col_send, col_mic, col_live = st.columns([1, 1, 1])

            # Send message button
            with col_send:
                if st.button("Send", use_container_width=True):
                    self.send_message(self.user_input)

            # Mic input button for voice input
            with col_mic:
                if st.button("🎤 Mic", use_container_width=True):
                    self.voice_input()

            # Start live class button
            with col_live:
                if st.button("🎥Live Class", use_container_width=True):
                    self.start_live_class()

        with col2:
            # Manage canvas state with session state
            if 'canvas_open' not in st.session_state:
                st.session_state['canvas_open'] = False

            # Button to toggle canvas visibility
            if st.button("🖍️Canvas"):
                st.session_state['canvas_open'] = not st.session_state['canvas_open']

            # Display canvas based on session state
            if st.session_state['canvas_open']:
                self.setup_drawing_canvas()

    def update_chat_history(self):
        """Updates and displays the chat history in a scrollable container."""
        with self.chat_container:
            for chat in self.chat_history:
                st.markdown(f"**{chat['sender']}:** {chat['message']}")

    def send_message(self, text=''):
        """Handles sending messages from the input field."""
        if text:
            self.chat_history.append({'sender': 'You', 'message': text})
            self.update_chat_history()  # Refresh chat history
            self.messages.append({'role': 'user', 'content': text})
            response = self.get_response(text)
            self.chat_history.append(
                {'sender': 'OptiLearn', 'message': response})
            self.update_chat_history()  # Refresh chat history
            self.speak_response(response)

    def voice_input(self):
        """Handles voice input using speech recognition."""
        r = sr.Recognizer()
        with sr.Microphone() as source:
            st.write("Listening... Speak now.")
            audio = r.listen(source)
            try:
                text = r.recognize_google(audio)
                st.write(f"You said: {text}")
                self.send_message(text)
            except sr.UnknownValueError:
                st.write("Sorry, I couldn't understand that.")
            except sr.RequestError:
                st.write(
                    "Sorry, there was an error with the speech recognition service.")

    def get_response(self, query):
        """Gets the AI response from the LLM model."""
        chat_completion = client.chat.completions.create(
            messages=self.messages, model="llama3-8b-8192", max_tokens=1000)
        return chat_completion.choices[0].message.content

    def speak_response(self, response):
        """Speaks the AI response using pyttsx3 or gTTS."""
        if self.persona.gender == 'female':
            self.respond_online(response)
        else:
            self.respond(response)

    def respond(self, response):
        """Generates speech using pyttsx3 for male voice."""
        with self.audio_lock:
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            engine.setProperty('voice', voices[0].id)
            engine.setProperty('rate', 150)
            engine.save_to_file(response, 'temp.wav')
            engine.runAndWait()
            self.auto_play_audio('temp.wav')

    def respond_online(self, response):
        """Generates speech using Google TTS."""
        tts = gTTS(text=response, lang='en')
        filename = "temp.mp3"
        tts.save(filename)
        self.auto_play_audio(filename)

    def auto_play_audio(self, filename):
        """Plays the audio file."""
        try:
            with open(filename, "rb") as audio_file:
                audio_bytes = audio_file.read()
            st.audio(audio_bytes, format='audio/mp3')
            st.success("Audio is playing.")
        except Exception as e:
            st.error(f"Error loading audio file: {e}")

    def start_live_class(self):
        """Starts a live video class using OpenCV."""
        cap = cv2.VideoCapture(0)
        st_frame = st.empty()
        st.write("Press 'Stop' to end the live class.")
        stop_button = st.button("Stop", key="stop_live_class")
        while cap.isOpened() and not stop_button:
            ret, frame = cap.read()
            if ret:
                st_frame.image(frame, channels="BGR")
            else:
                break
        cap.release()
        st.write("Live class ended.")

    def setup_drawing_canvas(self):
        """Sets up a drawing canvas using streamlit-drawable-canvas."""
        st.write("Draw something below:")

        # Create a drawing canvas
        canvas_result = st_canvas(
            fill_color="rgba(255, 255, 255, 0)",  # Background color
            stroke_width=2,
            stroke_color="black",
            background_color="white",
            height=300,
            width=400,
            drawing_mode="freedraw",
            key="canvas"
        )

        # Display the drawn image
        if canvas_result.image_data is not None:
            st.image(canvas_result.image_data, caption="Your Drawing", use_column_width=True)

        # Call LLaVA model to interpret the drawing
        if st.button("Interpret Drawing"):
            if canvas_result.image_data is not None:
                # Convert canvas image to PIL image
                image = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='PNG')
                img_byte_arr = img_byte_arr.getvalue()

                # Encode the image as base64 for passing to the LLaVA model
                encoded_image = base64.b64encode(img_byte_arr).decode('utf-8')

                # Use Ollama's LLaVA model to interpret the drawing
                llava_response = ollama.chat(
                    model="llava",  # Specify the LLaVA model
                    messages=[
                        {
                            "role": "user",
                            "content": "What does this image represent?",
                            "images": [encoded_image]  # Base64 encoded image
                        }
                    ]
                )
                # Display the response from LLaVA model
                st.write("LLaVA Response: ", llava_response['message']['content'])


        # Save drawn image functionality
        if st.button("Save Drawing"):
            if canvas_result.image_data is not None:
                image = Image.fromarray(canvas_result.image_data)
                image.save("drawing.png")
                st.success("Drawing saved as drawing.png!")
            else:
                st.warning("No drawing to save!")
                
if __name__ == "__main__":
    persona = SOFIA_TUTOR_PERSONA  # Define your persona
    app = ChatApp(persona)
