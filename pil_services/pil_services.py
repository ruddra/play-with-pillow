"""
PIL Specific Methods
"""
import logging
from PIL import Image, ImageFont, ImageDraw, ImageEnhance
from io import BytesIO

logger = logging.getLogger(__name__)

try:
    from django.core.files.base import ContentFile
except ImportError:
    logger.error("You will need Django for Django related Processing")


class PILService(object):
    """
    PIL Services
    """

    def __init__(self, size=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not size:
            self.size = 1200, 1200
        self.logger = logger

    def get_resize_image_size(self, image, baseheight=None):
        """
        Get resize image size
        """
        self.logger.info("Getting resize image size")
        if not baseheight:
            baseheight = self.size[1]
        hpercent = (baseheight / float(image.size[1]))
        wsize = int((float(image.size[0]) * float(hpercent)))
        return wsize, baseheight

    def crop_image(self, img):
        """
        CROP Image
        img: Image file opened by PIL
        """
        self.logger.info("Cropping image")
        return img.crop(box=self.crop_position(img))

    def resize_image(self, img, size=None):
        """
        Resize Image
        img: Image file opened by PIL
        size: if Size not given, it will be calculated from default settings
        """
        self.logger.info("Resizing image")
        if not size:
            size = self.get_resize_image_size(img)
        img = img.resize(size, Image.ANTIALIAS)
        return img

    def crop_position(self, image):
        """
        Get Crop Image Positions
        """
        self.logger.info("Getting Crop Image Positions")
        width, height = image.size
        new_width, new_height = self.size

        left = (width - new_width) / 2
        top = (height - new_height) / 2
        right = (width + new_width) / 2
        bottom = (height + new_height) / 2
        return left, top, right, bottom

    def convert_image(self, image):
        """
        Process Background Image from Wikipedia/Background Image
        """
        try:
            path = image.path
            pil_image = Image.open(path)
            if pil_image.size == self.size:
                self.logger.info("Nothing to change, returning image")
                return image
            # Resize to size given in settings
            pil_image = self.resize_image(pil_image)
            # Cropping to adjust size given in settings
            pil_image = self.crop_image(pil_image)
            pil_image.save(path)
        except (KeyError, Exception) as exp:
            self.logger.error(str(exp))
            raise exp

    def convert_rgba(self, image):
        """
        RGBA Convertion
        """
        return image.convert("RGBA")

    def get_image(self, image_object):
        """
        We may get PIL object or Django ImageFile Object. We will simply check
        If it has attribute path and return PIL Image
        """
        try:
            return Image.open(image_object.path)

        except AttributeError:
            return image_object

    def add_overlay_over_background(self, background, overlay, offset=(0, 0)):
        """
        Add overlay image over background image
        """
        background_image = self.get_image(background)
        overlay_image = self.get_image(overlay)
        background_image.paste(overlay_image, offset, mask=overlay_image)
        return background_image

    def process_django_file(self, pil_image, name, format='png'):
        """
        Process the PIL file to Django File
        """
        file_object = BytesIO()
        pil_image.save(file_object, format=format)
        content = file_object.getvalue()
        return ContentFile(content, name=name)

    def write_text_on_image(self, image, text,
                            position, color, size, font=None, path=None, vertical_only=False):
        """
        Write Text over Image
        image: PIL Image object
        font: Font Object (Django Font Object)
        text: String Text
        position: position from where the texts will be start printing
        color: print text with color
        size: size of text
        path: path to the font
        vertical_only: if text position is vertical_only only, it will satisfy CASE TWO in tutorial
        """
        draw = ImageDraw.Draw(image)
        if font:
            path = font.path
        font = self.get_font(path, size)
        position = self._process_coordination(
            position, font, vertical_only, text
        )
        draw.text(position, text, font=font, fill=color)
        return image

    def convert_mode(self, img, mode="RGBA"):
        return img.convert(mode)

    def get_text_size(self, img_height, percentage):
        return int(img_height/percentage)

    def water_mark_on_image(self, image, text, percentage, path=None, margin=5, opacity=255, font=None):
        """
        Write watermark on image
        """
        if font:
            path = font.path
        image = self.convert_mode(image)
        width, height = image.size
        size = self.get_text_size(height, percentage)
        font = self.get_font(path, size)
        txt = Image.new('RGBA', image.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt)
        textwidth, textheight = draw.textsize(text, font)
        x = width - textwidth - margin
        y = height - textheight - margin

        draw.text((x, y), text, font=font,  fill=(255, 255, 255, opacity))

        combined = Image.alpha_composite(image, txt)
        return combined

    def write_list_on_image(self, image, data,
                            init_position, gap, color, size, font=None, path=None, is_horizontal=True):
        """
        Write List of data in Image
        image: PIL Image object
        font: Font Object (Django Font Object)
        data: list Object, ie we want to print in image ["this", 'is' , 'test', 'image'], it will be printed vertically
        init_position: initial position from where the texts will be start printing
        gap: gap between texts
        color: print text with color
        size: size of text
        path: path to the font
        is_horizontal: if texts will be printed horizontally
        """
        draw = ImageDraw.Draw(image)
        if font:
            path = font.path
        font = self.get_font(path, size)
        initial_position = self._process_coordination(
            init_position
        )
        txt_positions = self._get_list_positions(
            initial_position, data, gap, is_horizontal)
        for count, position in enumerate(txt_positions):
            draw.text(position, data[count], font=font, fill=color)

        return image

    def _get_list_positions(self, init_position, data, gap, is_horizontal=True):
        """
        Get List Text Positions
        """
        if not len(data) > 0:
            return []
        list_positions = [init_position]
        for i in range(1, len(data)):
            if not is_horizontal:
                init_position = init_position[0] + gap, init_position[1]
            else:
                init_position = init_position[0], init_position[1] + gap
            list_positions.append(init_position)
        return list_positions

    def _process_coordination(self, position, font=None, vertical_only=False, text=None):
        """
        Process Co-Ordination of the position
        """
        if vertical_only:
            size = font.getsize(text)
            width = (self.size[0] - size[0]) / 2
            return width, position

        try:
            # Assuming Data Comming from ArrayField
            return position[0][0], position[1][0]
        except (IndexError, TypeError):
            return position  # Given manually like (0,0)

    def get_font(self, path, size):
        """
        Get Font Object
        """
        return ImageFont.truetype(path, size=size)

    def darken_or_lighten_pixels(self, image, amount=0.5):
        """
        Enhance Image Brightness
        """
        converter = ImageEnhance.Brightness(image)
        return converter.enhance(amount)

    def add_color_saturation(self, image, amount=0.5):
        """
        Enhance Color saturation
        """
        converter = ImageEnhance.Color(image)
        return converter.enhance(amount)
