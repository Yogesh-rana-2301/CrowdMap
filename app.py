import streamlit as st
import cv2
import tempfile
from src.detection.detector import YOLOCrowdDetector
from src.mapping.heatmap import HeatmapGenerator
import numpy as np
import folium
from streamlit_folium import st_folium

 
st.set_page_config(
    page_title="CrowdMap: Real-time Crowd Density",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Helper Functions  
def get_crowd_status(count, high_risk_threshold=61, crowded_threshold=30):
    """Classifies crowd status based on count and returns status and color."""
    if count >= high_risk_threshold:
        return "High-Risk", "red"
    elif count >= crowded_threshold:
        return "Crowded", "orange"
    else:
        return "Safe", "green"

# Main App
def main():
    st.title("CrowdMap: Real-time Crowd Density Monitoring")

    # Sidebar 
    st.sidebar.header("Input Options")
    
    # Disable webcam in cloud
    try:
        if 'WEBCAM_DISABLED' in st.secrets:
            source_option = st.sidebar.radio("Select Source", ("Upload Video",))
        else:
            source_option = st.sidebar.radio("Select Source", ("Upload Video", "Webcam"))
    except Exception:
        source_option = st.sidebar.radio("Select Source", ("Upload Video", "Webcam"))

    confidence_threshold = st.sidebar.slider("Confidence Threshold", 0.0, 1.0, 0.5, 0.05)
    
    
    detector = YOLOCrowdDetector()
    heatmap_gen = HeatmapGenerator()

    #  Panel for Video and Data 
    col1, col2 = st.columns(2)

    with col1:
        st.header("Live Feed & Detection")
        video_placeholder = st.empty()

    with col2:
        st.header("Crowd Analytics")
        count_placeholder = st.empty()
        status_placeholder = st.empty()
        heatmap_placeholder = st.empty()

    #  Video Processing Logic
    if source_option == "Webcam":
        cap = cv2.VideoCapture(0)
        st.sidebar.info("Webcam feed selected. Press 'Stop' to end.")
        stop_button = st.sidebar.button("Stop")
    else:
        uploaded_file = st.sidebar.file_uploader("Choose a video file", type=["mp4", "avi", "mov"])
        cap = None
        stop_button = False
        if uploaded_file:
            tfile = tempfile.NamedTemporaryFile(delete=False)
            tfile.write(uploaded_file.read())
            cap = cv2.VideoCapture(tfile.name)

    if cap and not stop_button:
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_area = frame_width * frame_height

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                st.warning("Video stream ended or failed.")
                break

            #  AI Detection
            boxes, count = detector.detect_crowds(frame, conf=confidence_threshold)
            
            # Visualization 
            frame_with_detections = detector.draw_detections(frame.copy(), boxes)
            
            #  Analytics Display
            status, color = get_crowd_status(count)
            
            with count_placeholder.container():
                st.metric(label="People Count", value=count)
            
            with status_placeholder.container():
                 st.markdown(f"**Zone Status:** <span style='color:{color};'>{status}</span>", unsafe_allow_html=True)

            #Heatmap on Image 
            heatmap_image = heatmap_gen.create_heatmap_on_image(frame.copy(), boxes)
            with heatmap_placeholder.container():
                st.image(heatmap_image, caption="Density Heatmap on Frame")

            # Display Video
            video_placeholder.image(frame_with_detections, channels="BGR")

            # Small delay to prevent browser from crashing
            cv2.waitKey(1)

        cap.release()
    elif source_option == "Webcam" and stop_button:
        st.info("Webcam feed stopped.")

if __name__ == '__main__':
    main()
