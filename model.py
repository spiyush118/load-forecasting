from keras.models import model_from_json

def save_model(json_path,model):
    json_string=model.to_json()
    with open(json_path+'.json','w') as json_file:
        json_file.write(json_string)
    model.save_weights(json_path+'.h5')

def load_model(json_path) :
    with open(json_path+'.json') as json_file:
        json_string = json_file.read()
    model = model_from_json(json_string)
    model.load_weights(json_path+'.h5')
    return model
