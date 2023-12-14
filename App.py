from sqlalchemy import DateTime
from fastapi import FastAPI
import uvicorn
from openai import OpenAI
import os 
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import ForeignKey


   # Connect the database  (MySQM)
# -----------------------------------------
# -----------------------------------------
Base = declarative_base()
engine = create_engine('mysql://root@localhost/bot')

Session = sessionmaker(bind=engine)
session = Session()


  # Create tables 
# -----------------------------------------
# -----------------------------------------

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))



class ConversationHistory(Base):
    __tablename__ = 'conversation_history'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    history = Column(String(500))
    date = Column(DateTime)

  # create or update tables stricture
# -----------------------------------------
# -----------------------------------------
Base.metadata.create_all(engine)

  # Functions used 
  #history is the content of the old message
# -----------------------------------------
# -----------------------------------------

def store_conversation_history(user_id, message):
    new_history = ConversationHistory(user_id=user_id, history=message)
    session.add(new_history)
    session.commit()

def get_conversation_history(user_id):
    history = session.query(ConversationHistory).filter_by(user_id=user_id).order_by(ConversationHistory.date).all()
    return [h.history for h in history] if history else None


  # Test
# -----------------------------------------
# ----user id and message must be passed as an imput to our apiapp-------------------------------------
def generate_response(userid , message) :
 user = session.query(User).filter_by(id=userid).first()
  # user_info_text contain the client name and more info 
 user_info_text = f"name={user.name}"
   # -----------------------------------------
  # conversation_history_text  contain the full conversation (session with user)
 conversation_history_text = "\n".join(get_conversation_history(userid)) if get_conversation_history(userid) else "No conversation history found"
 #-----------------------------------------
 #generalcontext.txt is a txt static file that contain any requirment we need about profiling the chatbot
 with open('generalcontext.txt', 'r') as file:
    generalcontext = file.read()
#-----------------------------------------
#-----------------------------------------
#init the client openai
 print(os.environ.get('OPENAI_API_KEY'))
 client = OpenAI()
#-----------------------------------------
#-----------------------------------------
#complement contain the respons of the api with multiple choises[]
 completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": f"this is the general context you must be :{generalcontext}/n this is the client name you are talking to {user_info_text} /n this is the old conversation between you and him {conversation_history_text}"},
    {"role": "user", "content": f"{message}"}
  ]
)
#-----------------------------------------
#-----------------------------------------
#save the conversation 
 store_conversation_history(userid, f"[{user.name}]: {message}")
 store_conversation_history(userid, f"[psychic]: {completion.choices[0].message.content}")
 return {"message0": completion.choices[0].message.content ,"message1": conversation_history_text }
#-----------------------------------------
#-----------------------------------------
#create our api
app = FastAPI()
#-----------------------------------------
#-----------------------------------------
#define a POST method 
@app.post("/chat/{userid}/{message}")
def root(userid: int, message: str):
    return generate_response(userid, message)
#-----------------------------------------
#Serverhost-------------------------------
if __name__ == "__main__" :
    uvicorn.run('app:app', host="localhost", port=5001, reload=True)
#-----------------------------------------
#run the app with this command
#python -m  uvicorn App:app --reload
