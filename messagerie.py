import time
import mysql.connector
from openai import OpenAI
import os 
from fastapi import  FastAPI
from pydantic import BaseModel
from PIL import Image
import uvicorn

from EncodeVideoViaThreads import process_video_and_upload
from ImageToText import process_image , process_image_vgg16
print(os.environ.get('OPENAI_API_KEY'))

#----------------------------

def get_message_byid(message_id):
    try:
        connection = mysql.connector.connect(
        host="localhost",
        user="root",
        database="security"
                     )  

        cursor = connection.cursor(dictionary=True)

        # Query to fetch messages between user_id_1 and user_id_2
        query = """
            SELECT  photolink , content
            FROM message 
            WHERE (id = %s) 
            
        """

        # Execute the query with user IDs as parameters
        cursor.execute(query, (message_id,))

        # Fetch all messages
        message = cursor.fetchone()

        return message

    except mysql.connector.Error as error:
        print("Error retrieving messages:", error)
        return None

    finally:
        if 'cursor' in locals() and cursor is not None:
            cursor.close()

#-----------------------------

def translatemsg(language ,message):

    
    #---------------------------------
    client = OpenAI() 
    if message:
    
        completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
            messages=[
            {"role": "system", "content": f"just translate this to {language} "},

            {"role": "user", "content": f"{message}"}
                    ]
        )
        
        content = completion.choices[0].message.content
        str_content = str(content)

        # Remove [{ from the beginning
        str_content = str_content.lstrip('[{')

        # Remove }] from the end
        str_content = str_content.rstrip('}]')

        # Remove 'content': from the beginning
        str_content = str_content.replace("'content':", '')
        str_content = str_content.rstrip("'")
        str_content = str_content.lstrip(" '")
        return(str_content)





        # Modify this according to how you want to process each message
        time.sleep(4)
    else:
        return("No messages found or an error occurred.")
    
#-----------------------------
def is_video_file(path):
    video_extensions = ('.mp4','.mov','.m4a','.3gp','.3g2','.mj2')  # Add more extensions if needed
    return path.lower().endswith(video_extensions)
app1 = FastAPI()
class RequestBodyF(BaseModel):
    message_id: int 


# FastAPI endpoint
@app1.post("/chat/download")
def root(request_body: RequestBodyF):
    message = get_message_byid(request_body.message_id)
    photolink = message['photolink']   
    photo_paths = [path.strip() for path in photolink.split("[IMG]") if path.strip()]
    base_directory = r"C:\springootsecirity\spring-boot-3-jwt-security"
    i=0
    final=""
    for path in photo_paths:
        # Assuming process_image and process_image_vgg16 take the file path as an argument
        i=i+1
        if is_video_file(path):
            print("This is an image file.")
            adjusted_path = adjust_path(path, base_directory)
            download_link = process_video_and_upload(adjusted_path)
            final=final + f" || video {i} : {download_link} "
        else:
            final=final + f" __file {i} : This is not an video file "
        
    return  final
    
   
class RequestBody(BaseModel):
    language: str
    message_id: int
def adjust_path(original_path, base_directory):
    # Remove any leading './' or '.\' from the original path
    adjusted_original_path = original_path.lstrip('.\\').lstrip('./')
    # Combine base directory and adjusted original path using os.path.join
    return os.path.join(base_directory, adjusted_original_path)
def is_image_file(path):
    image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')  # Add more extensions if needed
    return path.lower().endswith(image_extensions)
@app1.post("/chat")
def root(request_body: RequestBody):
    language = request_body.language
    message_id = request_body.message_id

    # Assuming you have a function to fetch the message content and photo paths
    message = get_message_byid(message_id)
    photolink = message['photolink']  # Access fields using dictionary syntax
    content = message['content']
    # Extract photo paths from the message content
    photo_paths = [path.strip() for path in photolink.split("[IMG]") if path.strip()]
    base_directory = r"C:\springootsecirity\spring-boot-3-jwt-security"
    i=0
    final=""
    # Process each image file and make predictions
    for path in photo_paths:
        # Assuming process_image and process_image_vgg16 take the file path as an argument
        i=i+1
        if is_image_file(path):
            print("This is an image file.")
            adjusted_path = adjust_path(path, base_directory)
            prediction_1 = process_image(adjusted_path)
            prediction_2 = process_image_vgg16(adjusted_path)
            final=final + f" || photo {i} : {prediction_1} or {prediction_2}"
        else:
            final=final + f" __file {i} : This is not an image file "
    translated_content = translatemsg(language, content)
    translated_images=translatemsg(language,final)
    return {
        "translated_content": translated_content,
        "translated_images":translated_images
    
    }
#-----------------------------------------
#Serverhost-------------------------------
if __name__ == "__main__" :
   
    uvicorn.run(app1, host="localhost", port=5001, reload=True)
