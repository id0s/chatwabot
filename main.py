import requests
from fastapi import FastAPI, Form, Depends, Request
from sqlalchemy.orm import Session
from decouple import config
from models import Conversation, SessionLocal
from utils import logger
from twilio.rest import Client  # Impor Twilio Client

app = FastAPI()

# Mengambil SID dan token Twilio dari variabel yang ada (jangan diubah)
twillio_sid = config('TWILIO_ACCOUNT_SID')
twillio_auth_token = config('TWILIO_AUTH_TOKEN')
twillio_number = config('TWILIO_NUMBER')

# Inisialisasi Twilio client
client = Client(twillio_sid, twillio_auth_token)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

# Basic test endpoint
@app.get("/")
async def index():
    return {"msg": "working"}

# Message processing endpoint
@app.post("/message")
async def reply(request: Request, Body: str = Form(), db: Session = Depends(get_db)):
    # Extract the phone number from the incoming request
    form_data = await request.form()
    whatsapp_number = form_data['From'].split("whatsapp:")[-1]
    print(f"Received message from: {whatsapp_number}")

    # Process the message and get the response
    chatgpt_response = get_chat_response(Body, whatsapp_number, db)

    return {"message": chatgpt_response}

# Function to get chat response from an API
def get_chat_response(user_input, whatsapp_number, db):
    url = "https://api.ryzendesu.vip/api/ai/blackbox"
    params = {"chat": user_input, "options": "gpt-4o"}

    try:
        # Make the API call to get the chat response
        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            chatgpt_response = data.get("response", "Tidak ada response")

            # Store the conversation in the database
            conversation = Conversation(
                sender=whatsapp_number,
                message=user_input,
                response=chatgpt_response
            )
            db.add(conversation)
            db.commit()
            logger.info(f"Conversation #{conversation.id} stored in database")

            # Send the response back to WhatsApp
            send_message(whatsapp_number, chatgpt_response)
            return chatgpt_response
        else:
            logger.error(f"Error from API: {response.status_code}")
            return "Terjadi kesalahan saat menghubungi API."
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return f"Terjadi kesalahan: {str(e)}"

# Function to send a message using Twilio
def send_message(to_number, body_text):
    try:
        # Menggunakan Twilio client untuk mengirim pesan WhatsApp
        message = client.messages.create(
            from_=f"whatsapp:{twillio_number}",
            body=body_text,
            to=f"whatsapp:{to_number}"
        )
        logger.info(f"Message sent to {to_number}: {message.sid}")
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")

# Jalankan aplikasi jika skrip ini dijalankan langsung
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)

