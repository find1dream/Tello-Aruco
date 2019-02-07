from torchvision import transforms
import torch
from PIL import Image, ImageDraw, ImageFont
import cv2 as cv2
import numpy as np
import os
from utils import *

voc_labels = ('face',)
label_map = {k: v + 1 for v, k in enumerate(voc_labels)}
label_map['background'] = 0
rev_label_map = {v: k for k, v in label_map.items()}  # Inverse mapping

# Color map for bounding boxes of detected objects from https://sashat.me/2017/01/11/list-of-20-simple-distinct-colors/
distinct_colors = ['#32CD32', '#FFFFFF']
label_color_map = {k: distinct_colors[i] for i, k in enumerate(label_map.keys())}


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Transforms
resize = transforms.Resize((300, 300))
to_tensor = transforms.ToTensor()
normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])

class HeadDetector():
    def __init__(self, modelpath):
        # Load model
        self.model = torch.load(modelpath)
        self.model = self.model.to(device)
        self.model.eval()
    
    
    def detect(self, original_image, min_score, max_overlap, top_k, suppress=None):
        """
        Detect objects in an image with a trained SSD300, and visualize the results.
    
        :param original_image: image, a PIL Image
        :param min_score: minimum threshold for a detected box to be considered a match for a certain class
        :param max_overlap: maximum overlap two boxes can have so that the one with the lower score is not suppressed via Non-Maximum Suppression (NMS)
        :param top_k: if there are a lot of resulting detection across all classes, keep only the top 'k'
        :param suppress: classes that you know for sure cannot be in the image or you do not want in the image, a list
        :return: annotated image, a PIL Image
        """
    
        # Transform
        image = normalize(to_tensor(resize(original_image)))
    
        # Move to default device
        image = image.to(device)
    
        # Forward prop.
        predicted_locs, predicted_scores = self.model(image.unsqueeze(0))
    
        # Detect objects in SSD output
        det_boxes, det_labels, det_scores = self.model.detect_objects(predicted_locs, predicted_scores, min_score=min_score,
                                                                 max_overlap=max_overlap, top_k=top_k)
    
        # Move detections to the CPU
        det_boxes = det_boxes[0]#.to('cpu')
    
        # Transform to original image dimensions
        original_dims = torch.cuda.FloatTensor(
            [original_image.width, original_image.height, original_image.width, original_image.height]).unsqueeze(0)
        det_boxes = det_boxes * original_dims
    
        # Decode class integer labels
        det_labels = [rev_label_map[l] for l in det_labels[0].tolist()]
        #det_labels = [rev_label_map[l] for l in det_labels[0].to('cpu').tolist()]
    
        # If no objects found, the detected labels will be set to ['0.'], i.e. ['background'] in SSD300.detect_objects() in model.py
        if det_labels == ['background']:
            # Just return original image
            return original_image
    
        # Annotate
        annotated_image = original_image
        draw = ImageDraw.Draw(annotated_image)
    
        # Suppress specific classes, if needed
        for i in range(det_boxes.size(0)):
            if suppress is not None:
                if det_labels[i] in suppress:
                    continue
    
            # Boxes
            box_location = det_boxes[i].tolist()
            draw.rectangle(xy=box_location, outline=label_color_map[det_labels[i]])
            draw.rectangle(xy=[l + 1. for l in box_location], outline=label_color_map[
                det_labels[i]])  # a second rectangle at an offset of 1 pixel to increase line thickness
            draw.rectangle(xy=[l + 2. for l in box_location], outline=label_color_map[
                 det_labels[i]])  # a third rectangle at an offset of 1 pixel to increase line thickness
            draw.rectangle(xy=[l + 3. for l in box_location], outline=label_color_map[
                det_labels[i]])  # a fourth rectangle at an offset of 1 pixel to increase line thickness
    
        del draw
    
        return annotated_image

    def head_detect(self, frame):
        pilImg = Image.fromarray(np.uint8(frame))
        annotated_image = self.detect(pilImg, min_score=0.5, max_overlap=0.5,
                                 top_k=100)
        open_cv_image = np.array(annotated_image) 
        return open_cv_image

if __name__ == '__main__':
    cap = cv2.VideoCapture(0)
    test = HeadDetector("../model/best_head.pth")
    _, frame = cap.read(0)
    test.head_detect(frame)
