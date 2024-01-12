from keras.applications.vgg16 import VGG16, preprocess_input, decode_predictions
from keras.applications.mobilenet import MobileNet, preprocess_input, decode_predictions
from keras.preprocessing import image
import numpy as np

#--------------------------------------------
#-------------------------------------------

def process_image(image_data)-> str:
    # Load the MobileNet model pre-trained on ImageNet data
    model = MobileNet(weights='imagenet')
    
    # Preprocess the image for MobileNet model
    img = image.img_to_array(image.load_img(image_data, target_size=(224, 224)))
    img = np.expand_dims(img, axis=0)
    img = preprocess_input(img)
    
    # Predict the image using the model
    preds = model.predict(img)
    
    # Decode the predictions
    decoded_preds = decode_predictions(preds, top=1)[0]
    
    # Get the top prediction label
    label = decoded_preds[0][1]
    
    return label  # Return the predicted label'''

#--------------------------------------------
#--------------------------------------------

def process_image_vgg16(image_data)-> str:
    # Load the VGG16 model pre-trained on ImageNet data
    model = VGG16(weights='imagenet')
    
    # Preprocess the image for VGG16 model
    img = image.img_to_array(image.load_img(image_data, target_size=(224, 224)))
    img = np.expand_dims(img, axis=0)
    img = preprocess_input(img)
    
    # Predict the image using the model
    preds = model.predict(img)
    
    # Decode the predictions
    decoded_preds = decode_predictions(preds, top=1)[0]
    
    # Get the top prediction label
    label = decoded_preds[0][1]
    
    return label  # Return the predicted label

