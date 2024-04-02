import os
import cv2
import numpy as np
import tensorflow as tf
import sys


# Importing utility functions from local files
from utils import label_map_util
from utils import visualization_utils as vis_util

# Constants
MODEL_NAME = 'inference_graph'
NUM_CLASSES = 6

# Getting current working directory
CWD_PATH = os.getcwd()

# Path to frozen detection graph .pb file
PATH_TO_CKPT = os.path.join(CWD_PATH, MODEL_NAME, 'frozen_inference_graph.pb')

# Path to label map file
PATH_TO_LABELS = os.path.join(CWD_PATH, 'training', 'labelmap.pbtxt')

# Load the label map
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)

# Load the Tensorflow model into memory
detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

    sess = tf.Session(graph=detection_graph)

# Define input and output tensors for the object detection classifier
image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
num_detections = detection_graph.get_tensor_by_name('num_detections:0')

# image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
# detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
# detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
# detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
# num_detections = detection_graph.get_tensor_by_name('num_detections:0')


# Initialize webcam feed
video = cv2.VideoCapture(0)
ret = video.set(3, 1280)  # Setting width
ret = video.set(4, 720)   # Setting height

while True:
    # Capture frame-by-frame
    ret, frame = video.read()

    # Expand frame dimensions to have shape: [1, None, None, 3]
    frame_expanded = np.expand_dims(frame, axis=0)

    # Perform the actual detection by running the model with the image as input
    (boxes, scores, classes, num) = sess.run(
        [detection_boxes, detection_scores, detection_classes, num_detections],
        feed_dict={image_tensor: frame_expanded})

    # Draw the results of the detection
    vis_util.visualize_boxes_and_labels_on_image_array(
        frame,
        np.squeeze(boxes),
        np.squeeze(classes).astype(np.int32),
        np.squeeze(scores),
        category_index,
        use_normalized_coordinates=True,
        line_thickness=8,
        min_score_thresh=0.85)

    # Display the resulting frame
    cv2.imshow('Object detector', frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Clean up
video.release()
cv2.destroyAllWindows()


