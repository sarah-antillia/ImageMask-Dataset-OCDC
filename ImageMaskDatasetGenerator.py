
# Copyright 2024 antillia.com Toshiyuki Arai
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# 2024/05/05 
# ImageMaskDatasetGenerator.py

import os
import shutil
import glob
import cv2
import traceback
import numpy as np

from scipy.ndimage.filters import gaussian_filter

class ImageMaskDatasetGenerator:

  def __init__(self, root_dir, output_dir, resize=640, augmentation=False):
 
    self.root_dir   = root_dir
    self.output_dir = output_dir

    if os.path.exists(self.output_dir):
      shutil.rmtree(self.output_dir)

    if not os.path.exists(self.output_dir):
      os.makedirs(self.output_dir)

    self.output_images_dir = self.output_dir + "/images"
    self.output_masks_dir  = self.output_dir + "/masks"

    os.makedirs(self.output_images_dir)
    os.makedirs(self.output_masks_dir)
    self.augmentation = augmentation
    self.W      = 640
    self.H      = 640
    self.resize = resize
    
    self.hflip  = True
    self.vflip  = True
    self.rotation = True
    self.ANGLES   =[90, 180, 270]

    self.distortion=True
    self.gaussina_filer_rsigma = 40
    self.gaussina_filer_sigma  = 0.5
    self.distortions           = [0.01, 0.02]
    self.rsigma = "sigma"  + str(self.gaussina_filer_rsigma)
    self.sigma  = "rsigma" + str(self.gaussina_filer_sigma)
    
  def generate(self):
    # 640/*/01-roi/01-original/*.png"
    image_files = glob.glob(self.root_dir + "/*/01-roi/01-original/*.png")
    mask_files  = glob.glob(self.root_dir + "/*/01-roi/02-mask/*.png"    )
    print("--number of image_files {}".format(len(image_files)))
    print("--number of mask_files  {}".format(len(mask_files)))
    for image_file in image_files:

      image = cv2.imread(image_file)
      image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)
      basename = os.path.basename(image_file)
      basename = basename.replace(".png", ".jpg")
      output_filepath = os.path.join(self.output_images_dir, basename)
      cv2.imwrite(output_filepath, image)
      if self.augmentation:
        self.augment(image, basename, self.output_images_dir)

    for mask_file in mask_files:
 
      mask = cv2.imread(mask_file)
      image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)
      basename = os.path.basename(mask_file)
      basename = basename.replace(".png", ".jpg")

      output_filepath = os.path.join(self.output_masks_dir, basename)
      cv2.imwrite(output_filepath, mask)
      if self.augmentation:
        self.augment(mask, basename, self.output_masks_dir)


  def augment(self, image, basename, output_dir):
    #image = self.pil2cv(image)
    if self.hflip:
      flipped = self.horizontal_flip(image)
      output_filepath = os.path.join(output_dir, "hflipped_" + basename)
      cv2.imwrite(output_filepath, flipped)
      print("--- Saved {}".format(output_filepath))

    if self.vflip:
      flipped = self.vertical_flip(image)
      output_filepath = os.path.join(output_dir, "vflipped_" + basename)
      cv2.imwrite(output_filepath, flipped)
      print("--- Saved {}".format(output_filepath))

    if self.rotation:
      self.rotate(image, basename, output_dir)

    if self.distortion:
      self.distort(image, basename, output_dir)

  def horizontal_flip(self, image): 
    print("shape image {}".format(image.shape))
    if len(image.shape)==3:
      return  image[:, ::-1, :]
    else:
      return  image[:, ::-1, ]

  def vertical_flip(self, image):
    if len(image.shape) == 3:
      return image[::-1, :, :]
    else:
      return image[::-1, :, ]

  def rotate(self, image, basename, output_dir):
    for angle in self.ANGLES:      

      center = (self.W/2, self.H/2)
      rotate_matrix = cv2.getRotationMatrix2D(center=center, angle=angle, scale=1)

      rotated_image = cv2.warpAffine(src=image, M=rotate_matrix, dsize=(self.W, self.H))
      output_filepath = os.path.join(output_dir, "rotated_" + str(angle) + "_" + basename)
      cv2.imwrite(output_filepath, rotated_image)
      print("--- Saved {}".format(output_filepath))
     
  def distort(self, image, basename, output_dir):
    shape = (image.shape[1], image.shape[0])
    (w, h) = shape
    xsize = w
    if h>w:
      xsize = h
    # Resize original img to a square image
    resized = cv2.resize(image, (xsize, xsize))
 
    shape   = (xsize, xsize)
 
    t = np.random.normal(size = shape)
    for size in self.distortions:
      filename = "distorted_" + str(size) + "_" + self.sigma + "_" + self.rsigma + "_" + basename
      output_file = os.path.join(output_dir, filename)    
      dx = gaussian_filter(t, self.gaussina_filer_rsigma, order =(0,1))
      dy = gaussian_filter(t, self.gaussina_filer_rsigma, order =(1,0))
      sizex = int(xsize*size)
      sizey = int(xsize*size)
      dx *= sizex/dx.max()
      dy *= sizey/dy.max()

      image = gaussian_filter(image, self.gaussina_filer_sigma)

      yy, xx = np.indices(shape)
      xmap = (xx-dx).astype(np.float32)
      ymap = (yy-dy).astype(np.float32)

      distorted = cv2.remap(resized, xmap, ymap, cv2.INTER_LINEAR)
      distorted = cv2.resize(distorted, (w, h))
      cv2.imwrite(output_file, distorted)
      print("=== Saved distorted image file{}".format(output_file))


if __name__ == "__main__":
  try:
    root_dir   = "./training/tumor/patch/640x640"
    output_dir = "./OCDC-master"

    generator = ImageMaskDatasetGenerator(root_dir, output_dir, augmentation=True)
    generator.generate()
    
    root_dir   = "./testing/tumor/patch/640x640"
    output_dir = "./OCDC-test"
    generator = ImageMaskDatasetGenerator(root_dir, output_dir, augmentation=False)
    generator.generate()

  except:
    traceback.print_exc()
