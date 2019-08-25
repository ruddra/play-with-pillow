import os
from PIL import Image


class ConvertToWebp:
    """
    You need to install webp driver in your machine. For mac use
    > brew install webp
    Then re-install pillow
    """

    def __init__(self, directory, replace_files=True, convert_image_types=list()):
        self.directory = directory  # path to directory
        self.replace_files = replace_files  # if .webp files will replace exiting files
        self.convert_image_types = convert_image_types
        # list of extension types, empty list will take any format of image

    def should_convert(self, ext):
        if len(self.convert_image_types) > 0:
            if ext in self.convert_image_types:
                return True
        elif len(self.convert_image_types) == 0:
            return True
        return False

    def start(self):
        for root, dirs, files in os.walk(self.directory):
            for file in files:
                print('processing file: {}'.format(file))
                infile = os.path.join(root, file)
                name, ext = os.path.splitext(file)
                if not self.should_convert(ext):
                    continue
                try:
                    im = Image.open(infile)
                    im.save(os.path.join(root, name) + ".webp", "WEBP")
                    if self.replace_files:
                        print("removing {}".format(infile))
                        os.remove(infile)
                except Exception as e:
                    print(e)


if __name__ == "__main__":
    ConvertToWebp(
        '/path/to/image'
    ).start()
