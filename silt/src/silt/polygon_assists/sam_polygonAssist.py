import heapq
import numpy as np
import cv2
import torch
from segment_anything import sam_model_registry, SamPredictor
from polygon_assist import PolygonAssist

CKPT_FOLDER = "ckpts"
# Model Types
# model_type == "vit_h":  # 3162MiB  3.315 GB
# model_type == "vit_l":  # 1794MiB  1.881 GB
# model_type == "vit_b":  # 988 MiB  1.036 GB

class SegmentAnythingAssist(PolygonAssist):

    def __init__(self, model_type):
        # Call parent class's constructor (__init__ function)
        super().__init__()

        self.predictor = self._get_sam_predictor(model_type)
        self.num_contours = None


    def set_image(self, img_chip):
        super().set_image(img_chip)

        with torch.no_grad():
            self.predictor.set_image(self.processed_img)


    # def set_inputs():  # see base class

    # set_options():  # see base class

    # TODO: get_two_pts_from_box

    # ovverries base class
    def refine_polygon(self):
        with torch.no_grad():
            mask, _, _ = self.predictor.predict(**sam_args)
        
        mask = self._select_biggest_area_of_mask(mask, self.num_contours)

        new_polygon = self._extract_edge_from_mask(mask)

        # TODO. may need to look into getting new_polygon in the right format

        return new_polygon


    # For defining a way to order the contour tuple
    class _heap_item:
        def __init__(self, area, contour):
            self.contour = contour
            self.area = area
        def __lt__(self, other):
            return self.area < other.area


    def _select_biggest_area_of_mask(self, mask, num_contours):
        """Inspired by https://z-uo.medium.com/opencv-automatic-select-big-contour-areas-and-remove-8d79464a06e7
        Modified so that it now saves the top `num_contours` contours using a max heap
        
        Args:
            mask: mask to modify
            num_contours: number of contours to keep. Algorithm will keep the largest N contours"""
        mask = mask.transpose(1,2,0).astype('float32')  # change to (x,y,c) and from bool to float
        mask = cv2.inRange(mask, np.array([1]), np.array([1]))
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # highest_area = 0
        selected_contours = []
        max_heap = []  # python library uses min_heap so add a negative to each one

        for contour in contours:
            neg_area = - cv2.contourArea(contour)
            max_heap.append(self._heap_item(neg_area, contour))

        heapq.heapify(max_heap)

        for i in range(num_contours):
            if len(max_heap) == 0:
                break
            selected_contours.append(heapq.heappop(max_heap).contour)

        out_mask = np.zeros(mask.shape, np.uint8)
        cv2.fillPoly(out_mask, pts=selected_contours, color= (1,1,1))

        out_mask = out_mask[np.newaxis, :, :]  # convert mask back to (1, x, y)
        return out_mask


    def _extract_edge_from_mask(mask):
        """
        Assumes Mask is in [1, x, y] shape
        https://medium.com/@rootaccess/how-to-detect-edges-of-a-mask-in-python-with-opencv-4bcdb3049682
        """
        # consider looking into cv2 canny or sobel edge detection
        img_data = np.asarray(mask[0, :, :], dtype=np.double)  # shape assumption
        gx, gy = np.gradient(img_data)
        temp_edge = gy * gy + gx * gx
        temp_edge[temp_edge != 0.0] = 255.0
        edge_img = np.asarray(temp_edge, dtype=np.uint8)
        return edge_img


    def _get_sam_predictor(model_type):
        if model_type == "vit_h":
            sam_checkpoint = f"{CKPT_FOLDER}/sam_vit_h_4b8939.pth"  # 3162MiB  3.315 GB
        elif model_type == "vit_l":
            sam_checkpoint = f"{CKPT_FOLDER}/sam_vit_l_0b3195.pth"  # 1794MiB  1.881 GB
        elif model_type == "vit_b":
            sam_checkpoint =f"{CKPT_FOLDER}/sam_vit_b_01ec64.pth"  # 988 MiB  1.036 GB

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # print(device)
        # TODO. maybe log or output on silt whether gpu or cpu is being used
        sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
        sam.to(device=device)
        predictor = SamPredictor(sam)
        return predictor
