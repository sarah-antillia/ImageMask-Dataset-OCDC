# copy_test.py

import shutil
import traceback


if __name__ == "__main__":
  try:
    test_images_dir = "./OCDC-test/images"
    test_masks_dir  = "./OCDC-test/masks"
    dest_images_dir = "./OCDC-ImageMaskDataset-V1/test/images"
    dest_masks_dir  = "./OCDC-ImageMaskDataset-V1/test/masks"

    shutil.copytree(test_images_dir, dest_images_dir)

    shutil.copytree(test_masks_dir, dest_masks_dir)

  except:
    traceback.print_exc()
