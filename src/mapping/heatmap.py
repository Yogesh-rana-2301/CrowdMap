import cv2
import folium
from folium.plugins import HeatMap
import numpy as np

class HeatmapGenerator:
    """
    A class to generate heatmaps from crowd data.
    """
    def __init__(self, map_tiles='OpenStreetMap', zoom_start=15):
        """
        Initializes the HeatmapGenerator.

        Args:
            map_tiles (str): The tile layer for the map.
            zoom_start (int): The initial zoom level for the map.
        """
        self.map_tiles = map_tiles
        self.zoom_start = zoom_start

    def create_heatmap_on_map(self, crowd_data, map_center):
        """
        Creates a heatmap on an OpenStreetMap.

        Args:
            crowd_data (list): A list of dictionaries, where each dictionary 
                               contains 'lat', 'lon', and 'weight' for a data point.
            map_center (list or tuple): The center of the map as [latitude, longitude].

        Returns:
            A folium.Map object with the heatmap layer.
        """
        # Create a map centered at the specified location
        m = folium.Map(location=map_center, zoom_start=self.zoom_start, tiles=self.map_tiles)

        # Prepare data for the heatmap
        heat_data = [[point['lat'], point['lon'], point['weight']] for point in crowd_data]

        # Add the heatmap layer to the map
        HeatMap(heat_data).add_to(m)

        return m

    def create_heatmap_on_image(self, frame, bounding_boxes):
        """
        Creates a heatmap overlay on an image based on bounding box centers.
        This is a simplified version for visual effect on a static image/frame.

        Args:
            frame: The image frame (as a NumPy array).
            bounding_boxes (list): A list of bounding boxes.

        Returns:
            The frame with a heatmap overlay.
        """
        heatmap = np.zeros_like(frame, dtype=np.float32)
        
        for box in bounding_boxes:
            x1, y1, x2, y2 = map(int, box)
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            
            # Add a "heat" spot at the center of the bounding box
            # This is a very basic implementation. A more advanced version
            # would use Gaussian kernels.
            cv2.circle(heatmap, (center_x, center_y), radius=30, color=(0, 0, 1), thickness=-1)

        # Blur the heatmap to create a smooth gradient
        heatmap = cv2.GaussianBlur(heatmap, (99, 99), 0)
        
        # Normalize the heatmap
        heatmap = cv2.normalize(heatmap, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
        
        # Apply a colormap
        heatmap_colored = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)

        # Overlay the heatmap on the original frame
        overlayed_frame = cv2.addWeighted(frame, 0.6, heatmap_colored, 0.4, 0)

        return overlayed_frame


if __name__ == '__main__':
    # This is an example, In a real application, this data would come from GPS-tagged cameras or other sources.
    sample_data = [
        {'lat': 28.6139, 'lon': 77.2090, 'weight': 10}, # New Delhi
        {'lat': 28.6145, 'lon': 77.2095, 'weight': 15},
        {'lat': 28.6130, 'lon': 77.2100, 'weight': 5},
        {'lat': 28.6150, 'lon': 77.2085, 'weight': 20},
    ]

    map_generator = HeatmapGenerator()
    heatmap_map = map_generator.create_heatmap_on_map(sample_data, map_center=[28.6139, 77.2090])

    # Save the map to an HTML file
    heatmap_map.save("heatmap_example.html")
    print("Heatmap example saved to heatmap_example.html")

    