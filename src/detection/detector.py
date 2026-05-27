import cv2
from ultralytics import YOLO

class YOLOCrowdDetector:
    """
    A class for detecting and counting people in images or video frames using YOLOv8.
    """
    def __init__(self, model_path='yolov8n.pt'):
        """
        Initializes the YOLOCrowdDetector.

        Args:
            model_path (str): Path to the YOLOv8 model file. Defaults to 'yolov8n.pt', a small and fast model.
        """
        self.model = YOLO(model_path)
        # The 'person' class is index 0 in the COCO dataset, which YOLOv8 is trained on.
        self.person_class_index = 0

    def detect_crowds(self, frame, conf=0.5):
        """
        Detects people in a single frame.

        Args:
            frame: The image frame (as a NumPy array) to process. conf (float): The confidence threshold for detection.

        Returns:
            A tuple containing:
            - list: A list of bounding boxes for detected people.
            - int: The total count of detected people.
        """
        # Perform inference on the frame with the specified confidence
        results = self.model(frame, conf=conf)

        person_count = 0
        bounding_boxes = []

        # Process results
        for result in results:
            for box in result.boxes:
                if box.cls == self.person_class_index:
                    person_count += 1
                    bounding_boxes.append(box.xyxy[0].tolist()) # [x1, y1, x2, y2]

        return bounding_boxes, person_count

    def draw_detections(self, frame, bounding_boxes):
        """
        Draws bounding boxes on the frame for detected people.

        Args:
            frame: The image frame to draw on. bounding_boxes (list): A list of bounding boxes.

        Returns:
            The frame with bounding boxes drawn on it.
        """
        for box in bounding_boxes:
            x1, y1, x2, y2 = map(int, box)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        return frame

if __name__ == '__main__':

    detector = YOLOCrowdDetector()

    cap = cv2.VideoCapture(0) 

    if not cap.isOpened():
        print("Error: Could not open video source.")
    else:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Detect crowds
            boxes, count = detector.detect_crowds(frame)

            # Draw detections on the frame
            frame_with_detections = detector.draw_detections(frame, boxes)

            # Display the count on the frame
            cv2.putText(frame_with_detections, f'People Count: {count}', (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            # Show the frame
            cv2.imshow('Crowd Detection', frame_with_detections)

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
