from PIL import Image
import os
import os.path

from pil_services import PILService

INIT_PATH = '../batch_images'
END_PATH = '../batch_post_processed_images'


class ProcessBatchWaterMark(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.origin_path = INIT_PATH
        self.store_path = END_PATH
        self.pil_service = PILService()
        self.font_path = '../fonts/Roboto-LightItalic.ttf'
        self.text = '@ruddra'
        self.opacity = 50
        self.color = 'white'
        self.valid_images = [".jpg", ".gif", ".png", ".tga", '.jpeg']
        self.extention = 'PNG'
        self.margin = 20
        self.text_size_percentage = 20

    def process_image(self, img):
        updated_image = self.pil_service.water_mark_on_image(
                    img,
                    self.text,
                    self.text_size_percentage,
                    self.font_path,
                    opacity=self.opacity,
                    margin=self.margin
                )
        self.save_image(updated_image, img.filename)

    def save_image(self, img, file_name):
        new_name = '{}/{}'.format(self.store_path, file_name.split('/')[-1])
        img.save(new_name, self.extention)
        img.close()

    def process_from_image_name(self, ext, path, f):
            if ext.lower() in self.valid_images:
                img = Image.open(os.path.join(path, f))
                self.process_image(img)
                img.close()


    def process_batch_watermark(self):
        for f in os.listdir(self.origin_path):
            ext = os.path.splitext(f)[1]
            self.process_from_image_name(ext, self.origin_path, f)

if __name__ == '__main__':
    ProcessBatchWaterMark().process_batch_watermark()
