import cv2
import os
import argparse
import mediapipe as mp


def process_img(img, face_detection):
    H, W, _ = img.shape
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    out = face_detection.process(img_rgb)
    
    if out.detections is not None:
        for detection in out.detections:
            location_data = detection.location_data
            bbox = location_data.relative_bounding_box

            x1, y1, w, h = bbox.xmin, bbox.ymin, bbox.width, bbox.height
            x1 = int(x1 * W)
            y1 = int(y1 * H)
            w = int(w * W)
            h = int(h * H)

            # blur faces
            img[y1:y1+h, x1:x1+w, :] = cv2.blur(img[y1:y1+h, x1:x1+w, :], (50, 50)) # kernel size to determine how intense the blur should be...[] to apply only on the face

    return img

args = argparse.ArgumentParser()

args.add_argument("--mode", default = 'webcam') # mode slection depending on what the user wants to give imput - image, video or webcam
args.add_argument("--filePath", default = None)


args = args.parse_args()

output_dir = r"tuts\code\Face_Anonymizer\output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)



# detect faces
mp_face_detection = mp.solutions.face_detection

# model_selection can be either 0 or 1...we use 0 to select a short-range model that morks best for faces
# within 2 meters from the camera...we use 1 for a full-range model best for faces within 5 meters

# Minimum confidence value ([0.0, 1.0]) from the face detection model for the detection to be considered
# successful...default to 0.5
with mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5) as face_detection:
    if args.mode in ["image"]:
        # read image
        img= cv2.imread(args.filePath)
        
        img = process_img(img, face_detection)
        # save image
        cv2.imwrite(os.path.join(output_dir, 'output.jpg'), img)

    elif args.mode in ["video"]:

        cap = cv2.VideoCapture(args.filePath)
        ret, frame = cap.read()
        output_vid = cv2.VideoWriter(os.path.join(output_dir, "output.mp4"), cv2.VideoWriter_fourcc(* "MP4V"), 60, (frame.shape[1], frame.shape[0]))
        while ret:
            frame = process_img(frame, face_detection)

            output_vid.write(frame)

            ret, frame = cap.read()
        
        cap.release()
        output_vid.release()

    elif args.mode in ["webcam"]:
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        while ret:
            frame = process_img(frame, face_detection)

            cv2.imshow("frame",frame)
            cv2.waitKey(30)

            ret, frame = cap.read()

        cap.release()

            

        
