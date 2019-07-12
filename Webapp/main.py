from flask import Flask, render_template, request, send_from_directory
import sys
sys.path.append('..')
from classifier import get_model, img_process
from potato_detection import hb_detect_potatoes
import shutil
import os
import time
            
app = Flask(__name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def kickstart():
   return render_template('start.html')

@app.route('/capture',methods=["GET","POST"])
def get_ses():
    errors = []
    segment_dir = os.path.join(APP_ROOT, 'Segment/')
    allowed_extensions = set(['png', 'jpg', 'jpeg', 'gif'])
    
    # Set production = True if a camera is available and the model is hosted on
    # the cloud
    production = False
    
    if production:
        from readCam import takePicture
        currentfile = takePicture()
    else:
        upload_folder = os.path.join(APP_ROOT, 'Uploads/')
        try:
            if request.method == 'POST':
                currentfile = request.files.get('file', '')
                filename = currentfile.filename
                destination = "".join([upload_folder,filename])
                currentfile.save(destination)
        except:
                    errors.append(
                            "Unable to read file. Please make sure it's valid and try again."
                            )
    # Create segment_dir if it does not exist
    if not os.path.isdir(segment_dir):
        os.mkdir(segment_dir)
        
    # Segment uploaded image and save them to segment_dir    
    hb_detect_potatoes(currentfile,threshold = .5, outdir = segment_dir)
    
    # Load trained model. Ensure that model.eval() is called.
    model = get_model('../classifier_model/trained_classifier.pt')
    model.eval();
        
    # Initialize good and bad counts as 0
    good = 0
    bad = 0
    
    # Run classifier over all segmented images
    for potato in os.listdir(segment_dir):
        
        CF = img_process(currentfile)
        pred = model(CF)
        pred = pred.data.numpy().argmax()
    
        if pred == 0:
            good += 1
        else:
            bad += 1
            
    # Remove segment_dir after use to clear out the images
    shutil.rmtree(segment_dir, ignore_errors=True)

    return render_template("result.html", quantity = good + bad, quality = good / (good+bad) * 100, user_image = filename)
    time.sleep(60)
    
@app.route('/Uploads/<filename>')
def send_image(filename):
    return send_from_directory('Uploads',filename)


if __name__ == '__main__':
    
    app.run(debug=True)
