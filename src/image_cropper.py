import argparse
import cv2
import glob
import numpy as np
import os
import random
import settings
import uuid

src_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(src_dir)
data_dir = os.path.join(root_dir, 'data')
models_dir = os.path.join(root_dir, 'models')

cropped_dir = os.path.join(data_dir, 'cropped_videos')
videos_dir = os.path.join(data_dir, 'videos')


def valid_face(x,y,w,h):
  """Checks if an rectangle contains a face.

  Assumes image is of size 900x1600
  """

  # Face too small
  if (w < 20 or h < 20):
    return False
  
  # Face too large
  if (w > 200 or h > 200):
    return False

  if (y > 200):
    return False

  return True

def crop_image(img):
  img = cv2.resize(img, (450, 800)) 

  haar_cascade_file = os.path.join(models_dir, 'haarcascade_frontalface.xml')
  face_cascade = cv2.CascadeClassifier(haar_cascade_file)

  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  faces = face_cascade.detectMultiScale(gray,
    minNeighbors = settings.cascadeMinNeighbors)

  # There should be only one face
  for (x,y,w,h) in faces:
    if (valid_face(x, y, w, h)):
      # cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)

      return img[max(1,y-h):y+(5*h)//2,max(1,x-2*w): x + 2*w]

  return img


def crop_video_and_save(in_video_file, out_video_file):
  inn = cv2.VideoCapture(in_video_file)

  # Define the codec and create VideoWriter object
  fourcc = cv2.VideoWriter_fourcc(*'MJPG')

  out = cv2.VideoWriter(out_video_file,fourcc, 20.0, (450,800),True)

  while inn.isOpened():
    ret, img = inn.read()

    if not ret:
      break
    
    cropped_img = crop_image(img)
    resized_img = cv2.resize(cropped_img, (450, 800))

    out.write(resized_img)
    cv2.imshow('resized_frame',resized_img)
    cv2.imshow('frame',img)

    # if cv2.waitKey(1) & 0xFF:
    #   break
  
  inn.release()
  out.release()
  cv2.destroyAllWindows()


def crop_videos_in_dir(dir, symbol_name):
  video_dir = os.path.join(dir, symbol_name)
  cropped_video_dir = os.path.join(cropped_dir, symbol_name)

  if not os.path.exists(cropped_video_dir):
    os.makedirs(cropped_video_dir)

  for video_file in glob.glob(video_dir + '/*.mp4'):
    out_video = os.path.join(cropped_dir, symbol_name, os.path.basename(video_file))
    crop_video_and_save(video_file, out_video)


def test():
  crop_video_and_save(os.path.join(videos_dir, 'aada', '1_1.mp4'),
                      os.path.join(cropped_dir, 'aada', '1_1.mp4'))


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--videos-dir', type=str, default='aada')

  args = parser.parse_args()
  
  # TODO Iterate over all folder of list
  # crop_videos_in_dir(os.path.join(videos_dir, args.videos_dir), sym)
  test()