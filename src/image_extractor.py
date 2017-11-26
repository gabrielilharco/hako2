import argparse
import cv2
import numpy as np
import os
import settings
import uuid
import random

src_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(src_dir)
data_dir = os.path.join(root_dir, 'data')
models_dir = os.path.join(root_dir, 'models')

class Box:
  def __init__(self, color, x, y, half_size, img_shape, name):
    self.center_x = x
    self.center_y = y
    self.half_size = half_size
    self.color = color
    self.img_height = img_shape[0]
    self.img_width = img_shape[1]
    self.selected = False
    self.name = name

  def bounds(self):
    x_min = self.center_x - self.half_size
    x_max = self.center_x + self.half_size
    y_min = self.center_y - self.half_size
    y_max = self.center_y + self.half_size
    return x_min, x_max, y_min, y_max

  def display(self, img):
    x_min, x_max, y_min, y_max = self.bounds()
    cv2.rectangle(img, (x_min, y_min), (x_max, y_max), self.color)

  def move_left(self, step = 5):
    self.center_x -= step
    if self.center_x - self.half_size < 0:
      self.center_x = self.half_size

  def move_right(self, step = 5):
    self.center_x += step
    if self.center_x + self.half_size > self.img_width:
      self.center_x = self.img_width - self.half_size

  def move_up(self, step = 5):
    self.center_y -= step
    if self.center_y - self.half_size < 0:
      self.center_y = self.half_size

  def move_down(self, step = 5):
    self.center_y += step
    if self.center_y + self.half_size > self.img_height:
      self.center_y = self.img_height - self.half_size

  def scale_down(self, factor = 0.9):
    self.half_size = int(np.ceil(self.half_size*factor))

  def scale_up(self, factor = 1.1):
    max_possible_half_size = min(
      int(np.ceil(self.half_size * factor)),
      self.center_x,
      self.center_y,
      self.img_width - self.center_x,
      self.img_height - self.center_y)

    self.half_size = max_possible_half_size

  def save(self, img, path=None):
    if path is None:
      path = os.path.join( 
          data_dir,
          'images_raw',
          self.name + uuid.uuid4().hex + '.png')
    x_min, x_max, y_min, y_max = self.bounds()
    roi = img[y_min: y_max, x_min: x_max]
    cv2.imwrite(path, roi)

  def handle_key(self, key, img):
    if key == 83: # right key: move selected box right
      self.move_right()
    elif key == 81: # left key: move selected box left
      self.move_left()
    elif key == 82: # up key: move selected box up
      self.move_up()
    elif key == 84: # down key: move selected box down
      self.move_down()
    elif key == 112: # p: scale up
      self.scale_up()
    elif key == 111: # q: scale down
      self.scale_down()
    elif key == 115: # s: save
      self.save(img)

def resize(img):
  original_height = img.shape[0]
  original_width = img.shape[1]
  scale = float(min(settings.resizedWidth, original_width)) / original_width
  return cv2.resize(img, (int(scale*original_width), int(scale*original_height)))

if __name__ == '__main__':
  # Parse command line args
  parser = argparse.ArgumentParser(description='Extract bounding boxes')

  parser.add_argument('--mode', type=str, default='box',
                      help='Mode. Box for image extraction and clean for cleaning.')
  parser.add_argument('--video', type=str, default='aada/1',
                      help='Name of the video, without the extension')
  parser.add_argument('--resize', type=int, default=0,
                      help='The size, if any, to resize the images.')
  parser.add_argument('--rotate', type=bool, default=False,
                      help='Rotation on the image.')

  args = parser.parse_args()
  mode = args.mode
  rotate = args.rotate

  # rename images sequentially
  if mode == 'clean':
    images_path = os.path.join(data_dir, 'images_raw')
    folders = os.walk(images_path).next()[1]
    total_images = 0
    for folder in folders:
      files = os.walk(os.path.join(images_path, folder)).next()[2]
      for file in files:
        file_path = os.path.join(images_path, folder, file)
        # give a uuid name to avoid ovewriting
        new_file_path = os.path.join(images_path, folder, uuid.uuid4().hex)
        os.rename(file_path, new_file_path)
      files = os.walk(os.path.join(images_path, folder)).next()[2]
      number = 0
      for file in files:
        file_path = os.path.join(images_path, folder, file)
        new_file_path = os.path.join(images_path, folder, str(number) + '.png')
        os.rename(file_path, new_file_path)
        number += 1
      total_images += number
    for folder in sorted(folders):
      files = os.walk(os.path.join(images_path, folder)).next()[2]
      print((folder + ':').ljust(15) + str(len(files)) + ' files')
    print("-----------------------------")
    print("Total images: " + str(total_images))
    print("Avg imgs per class: " + str(total_images/len(folders)))
    exit()

  # resize images if requested
  size = args.resize
  if size != 0:
    raw_images_dir = os.path.join(data_dir, 'images_raw')
    folders = os.walk(raw_images_dir).next()[1]
    images_dir = os.path.join(data_dir, 'images_' + str(size))
    if not os.path.exists(images_dir):
      os.makedirs(images_dir)
    for folder in folders:
      folder_dir = os.path.join(images_dir, folder)
      if not os.path.exists(folder_dir):
        os.makedirs(folder_dir)
      files = os.walk(os.path.join(raw_images_dir, folder)).next()[2]
      for file in files:
        file_path = os.path.join(raw_images_dir, folder, file)
        img = cv2.imread(file_path)
        resized_img = cv2.resize(img, (size, size))
        resized_file_path = os.path.join(folder_dir, file)
        cv2.imwrite(resized_file_path, resized_img)
    exit()


  video_path = os.path.join(data_dir, 'videos', args.video + '.mp4')  
  video_capture = cv2.VideoCapture(video_path)

  # reshape img if necessary
  ret, img = video_capture.read()
  if img is None:
    print('Error while reading image. Is the path correct?')
    exit()
  # rotate image if necessary
  if rotate:
    img = cv2.transpose(img)
    img = cv2.flip(img, 1)
  if img.shape[1] != settings.resizedWidth:
    img = resize(img)
  height, width, _ = img.shape

  t = img.shape[1]
  center_window_size = 0.15*t
  max_center_x = int(t/2 + center_window_size/2)
  min_center_x = int(t/2 - center_window_size/2)
  max_center_y = int(t/2 + center_window_size/2)
  min_center_y = int(t/2 - center_window_size/2)
  offset = int(0.15*t)
  max_x = t - offset - 1
  min_x = offset + 1
  max_y = t - offset - 1
  min_y = offset + 1

  selected_box = Box((0, 255, 0), 200, 200, 200, img.shape, args.video)
  modified_img = img.copy()
  selected_box.display(modified_img)
  cv2.imshow('img', modified_img)
  
  # Haar cascade for face detection
  haar_cascade_file = os.path.join(models_dir, 'haarcascade_frontalface.xml')
  print(haar_cascade_file)
  face_cascade = cv2.CascadeClassifier(haar_cascade_file)
  minFaceSize = (int(width*settings.minFaceSize), int(width*settings.minFaceSize))
  maxFaceSize = (int(width*settings.maxFaceSize), int(width*settings.maxFaceSize))

  while video_capture.isOpened():
    # Detect faces
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray,
      scaleFactor = settings.cascadeScaleFactor,
      minNeighbors = settings.cascadeMinNeighbors,
      minSize = minFaceSize,
      maxSize = maxFaceSize)
    
    for (x,y,w,h) in faces:
        cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
    cv2.imshow('img',img)

    key = cv2.waitKey() & 0xff
    if key == 27: # Esc: exit
      break
    if key == 32: # space: go to next frame
      ret, img = video_capture.read()
      # rotate image if necessary
      if rotate:
        img = cv2.transpose(img)
        img = cv2.flip(img, 1)
      if img is None: # video ended
        break
      if img.shape[1] != settings.resizedWidth:
        img = resize(img)    

    if key == 114: # crop random
      x = random.randint(min_center_x+1, max_center_x)
      y = random.randint(min_center_y+1, max_center_y)
      
      min_h = max(x-min_x, max_x-x)
      min_w = max(y-min_y, max_y-y)
      min_hw = max(min_h, min_w)

      max_h = min(x, t-x)
      max_w = min(y, t-y)
      max_hw = min(max_h, max_w)

      crop_sz = random.randint(min_hw, max_hw)
      crop_box = Box((255, 0, 0), x, y, crop_sz, img.shape, args.video)
      file_name = os.path.join( 
        data_dir,
        'crops',
        uuid.uuid4().hex + '.png')
      crop_box.save(img, file_name)

    selected_box.handle_key(key, img)

    modified_img = img.copy()
    selected_box.display(modified_img)
    #cv2.imshow('img', modified_img)

  print('Exiting...')
  video_capture.release()
  cv2.destroyAllWindows()

