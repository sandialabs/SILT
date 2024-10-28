#import cv2


class ImagePrepreprocessor():
    def __init__(self):
        self.options = None
        # TODO. remove arguments and use options instead once options is figured out
        self.use_equalize = False  # TODO
        self.use_smoothen = False  # TODO


    # consider calling update_options inside of preprocess. not sure if need to separate them
    def preprocess(self, img):
        if self.use_equalize:
            img = self._equalize_image(img)
        if self.use_smoothen:
            img = self._smoothen_image(img)
        return img


    def update_options(self, options):
        self.options = options
        # self.use_equalize, self.use_smoothen
        # update the parameters for functions


    def _equalize_image(self, img, use_adaptive=True):
        """Increase the contrast in an image. Using either histogram equalization of adaptive histogram equalization!

        Args:
            img: the image
            use_adaptive: if True, use adaptive algorithm which can lead to better performance, while costing more computation time
        """
        # convert to grayscale first

        new_img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

        if use_adaptive:
            clahe = cv2.createCLAHE()  # default params: clipLimit: 40 (threshold for contrast limitting). tileGridsize: (8,8). sets the number of tiles 
            new_img = clahe.apply(new_img)
        else:
            new_img = cv2.equalizeHist(new_img)

        new_img = cv2.cvtColor(new_img, cv2.COLOR_GRAY2RGB)  # convert to have 3 color channels
        return new_img


    def _smoothen_image(self, img, h=10):
        """Smoothens the image. Uses fastNlMeansDenoisingColored() by default (what I experimented with).

        Args:
            img: input image in numpy
            h: Hyperparameter to control strength of smoothing. Higher h -> more smooth. Lower h -> Less smooth.
                e.g default value is 10, but I ramped it up to 100 for noticeably more smoothing"""
        # Experiment with image smoothing
        # h = 100  # 10 default  # higher values -> more smooth
        smooth_image = cv2.fastNlMeansDenoisingColored(img, None, h, h, 7, 21)
        # smooth_image = cv2.bilateralFilter(image, 5, 30, 30)  # supposedly good for noise removal while keeping sharp edges
        return smooth_image

    
    # unused at the moment
    def _convert_color_scale(img, use_gray_scale=True):
        """Assumes the image is loaded as BGR (cv2.imread default). converts either to grayscale or RGB """
        if use_gray_scale:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # convert to gray
            return cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)  # convert to have 3 color channels
        else:
            return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
