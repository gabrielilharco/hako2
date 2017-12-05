import argparse
import cv2
import glob
import numpy as np
import os
import random
import settings
import uuid

import face_recognition

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SRC_DIR)
DATA_DIR = os.path.join(ROOT_DIR, 'data')
MODELS_DIR = os.path.join(ROOT_DIR, 'models')

CROPPED_DIR = os.path.join(DATA_DIR, 'images')
VIDEOS_DIR = os.path.join(DATA_DIR, 'videos')


def valid_face(x,y,w,h):
  """Checks if an rectangle contains a face.

  Assumes image is of size 450x800
  """

  # Face too small
  if (w < 50 or h < 50):
    return False
  
  # Face too large
  if (w > 200 or h > 200):
    return False

  if (y > 200 or y < 50):
    return False

  if (x > 250 or x < 100):
    return False

  return True

def face_haar_bbox(img):
  haar_cascade_file = os.path.join(MODELS_DIR, 'haarcascade_frontalface.xml')
  face_cascade = cv2.CascadeClassifier(haar_cascade_file)

  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  faces = face_cascade.detectMultiScale(gray,
    minNeighbors = settings.cascadeMinNeighbors)

  # There should be only one face
  for (x,y,w,h) in faces:
    if (valid_face(x, y, w, h)):
      print (x,y,w,h)
      return True, (x,y,w,h)

  # Did not find imag
  return False, None


def crop_video_and_save(in_video_file, out_video_file, fallback_haar):
  # cv2.namedWindow("frame")
  # cv2.setMouseCallback("frame", click_handler)
  inn = cv2.VideoCapture(in_video_file)

  haar_cascade_file = os.path.join(MODELS_DIR, 'haarcascade_frontalface.xml')
  face_cascade = cv2.CascadeClassifier(haar_cascade_file)

  last_bbox = (200,180,200,200)
  frame_count = 0
  while inn.isOpened():
    frame_count += 1
    ret, img = inn.read()

    if not ret: break
    if frame_count % 2 != 0: continue
    
    img = cv2.resize(img, (450, 800))
    
    cropped_img = img

    # Try CNN
    face_locations = face_recognition.face_locations(
        cropped_img, number_of_times_to_upsample=0, model="cnn")

    if len(face_locations) > 0:
      for face_location in face_locations:
        # Print the location of each face in this image
        top, right, bottom, left = face_location
        w = (right - left)
        h = (bottom - top)
  
        cropped_img = img[max(0, int(top - 0.8 * h)):min(img.shape[0], int(bottom + 3 * h)),
                          max(0, int(left - 1.5 * w)):min(img.shape[1], int(right + 1.8 * w))]
        print("CNN!")
        # cv2.rectangle(img,
        #               (int(left - 1.5 * w), int(top - 0.8 * h)),
        #               (int(right + 1.8 * w), int(bottom + 3 * h)),
        #               (255, 0, 0), 2)
        break
    elif fallback_haar:
      # Fallback! Try Haar Cascade
      gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
      face_locations = face_cascade.detectMultiScale(gray,
                                                     minNeighbors=settings.cascadeMinNeighbors)

      # There should be only one face
      for (x,y,w,h) in face_locations:
        if (valid_face(x, y, w, h)):
          top, right, bottom, left = y, x, y + h, x + w
          cropped_img = img[max(0, int(top - 0.8 * h)):min(img.shape[0], int(bottom + 3 * h)),
                            max(0, int(left - 2.2 * w)):min(img.shape[1], int(right + 2 * w))]
          # cv2.rectangle(cropped_img,
          #     (int(left - 2.2 * w), int(top - 0.8 * h)),
          #     (int(right + 2 * w), int(bottom + 3 * h)),
          #     (0, 255, 0), 2)
          print("Haar!")
          break


    # found, bbox = face_haar_bbox(img)
    # if (found):
    #   if ((bbox[0] - last_bbox[0])**2 + (bbox[1] - last_bbox[1])**2 < 10**2):
    #     last_bbox = bbox
    #   else:
    #     bbox = last_bbox
    # else:
    #   bbox = last_bbox

    # Face-to-body ratio crop
    # (x,y,w,h) = bbox
    # cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
    # cropped_img =  img[max(1,y-h):y + int(2.5*h),max(1,x- int(1.8*w)): x + int(2.3*w)]
    # cropped_img = img 

    resized_img = cv2.resize(cropped_img, (400, 400))

    # out.write(resized_img)
    cv2.imwrite(out_video_file + "_" + str(uuid.uuid4()) + ".png", resized_img)
    # cv2.imshow('resized_frame',resized_img)
    # cv2.imshow('frame',cropped_img)
    # cv2.imshow('original',img)

    # key = cv2.waitKey() & 0xFF
    # if key == 32:
    #   break
    cv2.waitKey(1)

  inn.release()
  cv2.destroyAllWindows()


def crop_videos_in_dir(dir, symbol_name, **kwargs):
  video_dir = os.path.join(dir, symbol_name)
  cropped_video_dir = os.path.join(CROPPED_DIR, symbol_name)

  if not os.path.exists(cropped_video_dir):
    os.makedirs(cropped_video_dir)

  for video_file in glob.glob(video_dir + '/*.mp4'):
    out_video = os.path.join(CROPPED_DIR, symbol_name, os.path.basename(video_file))
    crop_video_and_save(video_file, out_video, **kwargs)



### TESTING
def click_handler(event, x, y, flags, param):
  if event == cv2.EVENT_LBUTTONDOWN:
    print (x, y)

def test():
  crop_videos_in_dir(symbols_dir, symbol_name='casa')
  # crop_video_and_save(os.path.join(videos_dir, 'ajudar', '6_19.mp4'),
  #                     os.path.join(cropped_dir, 'ajudar', '6_19.mp4'))
###

def main(symbols_dir, **kwargs):
  # print(kwargs)
  for symbol in os.listdir(VIDEOS_DIR):
    crop_videos_in_dir(VIDEOS_DIR, symbol_name=symbol, **kwargs)
  


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--symbols-dir', type=str, default='aada')
  parser.add_argument('--fallback-haar', type=bool, default=True, help="Fallback to Haar")

  args = parser.parse_args()
  print (args)
  
  # TODO Iterate over all folder of list
  # crop_videos_in_dir(os.path.join(VIDEOS_DIR, args.symbols_dir), sym)
  main(**vars(args))
