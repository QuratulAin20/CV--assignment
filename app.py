import streamlit as st
import cv2
import numpy as np
import os
import yt_dlp
from PIL import Image

# Function to categorize brightness
def categorize_brightness(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    brightness = np.mean(hsv[:, :, 2])
    if brightness > 100:  # Start with a lower threshold
        return "Day"
    elif brightness > 50:
        return "Evening"
    else:
        return "Night"
# Streamlit app title
st.title("Video Brightness Categorization")

# URL input box
url = st.text_input("Enter a video URL (optional):")

# Upload video file
uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "avi", "mov"])

# Function to process the video
def process_video(video_path):
    day_count = 0
    evening_count = 0
    night_count = 0
    total_frames = 0
    sample_frame = None  # To hold a sample frame for display

    # Process the video frames
    cap = cv2.VideoCapture(video_path)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Categorize the current frame
        category = categorize_brightness(frame)
        
        # Increment the appropriate counter and save a sample frame
        if category == "Day":
            day_count += 1
            if day_count == 1:  # Save the first Day frame as a sample
                sample_frame = frame
        elif category == "Evening":
            evening_count += 1
            if evening_count == 1:  # Save the first Evening frame as a sample
                sample_frame = frame
        else:
            night_count += 1
            if night_count == 1:  # Save the first Night frame as a sample
                sample_frame = frame
        
        total_frames += 1
    
    # Release the video capture object
    cap.release()

    return total_frames, day_count, evening_count, night_count, sample_frame

# Process the uploaded video
if uploaded_file is not None:
    # Save the uploaded file temporarily
    video_path = "temp_video.mp4"
    with open(video_path, "wb") as f:
        f.write(uploaded_file.read())
    
    # Display the uploaded video
    st.video(uploaded_file)

    # Process the video
    total_frames, day_count, evening_count, night_count, sample_frame = process_video(video_path)

    # Calculate percentages
    if total_frames > 0:
        day_percentage = (day_count / total_frames) * 100
        evening_percentage = (evening_count / total_frames) * 100
        night_percentage = (night_count / total_frames) * 100

        # Display results
        st.write(f"Total frames processed: {total_frames}")
        st.write(f"Day Percentage: {day_percentage:.2f}%")
        st.write(f"Evening Percentage: {evening_percentage:.2f}%")
        st.write(f"Night Percentage: {night_percentage:.2f}%")

        # Display a sample frame if available
        if sample_frame is not None:
            # Convert the frame from BGR to RGB for display
            sample_frame_rgb = cv2.cvtColor(sample_frame, cv2.COLOR_BGR2RGB)
            st.image(sample_frame_rgb, caption='Sample Frame', use_column_width=True)

# Process the URL if provided
if url:
    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'temp_video_from_url.mp4',  # Save as temp_video_from_url.mp4
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Display the downloaded video
        st.video('temp_video_from_url.mp4')

        # Process the downloaded video
        total_frames, day_count, evening_count, night_count, sample_frame = process_video('temp_video_from_url.mp4')

        # Calculate percentages
        if total_frames > 0:
            day_percentage = (day_count / total_frames) * 100
            evening_percentage = (evening_count / total_frames) * 100
            night_percentage = (night_count / total_frames) * 100

            # Display results
            st.write(f"Total frames processed: {total_frames}")
            st.write(f"Day Percentage: {day_percentage:.2f}%")
            st.write(f"Evening Percentage: {evening_percentage:.2f}%")
            st.write(f"Night Percentage: {night_percentage:.2f}%")

            # Display a sample frame if available
            if sample_frame is not None:
                sample_frame_rgb = cv2.cvtColor(sample_frame, cv2.COLOR_BGR2RGB)
                st.image(sample_frame_rgb, caption='Sample Frame', use_column_width=True)
        else:
            st.write("No frames processed.")
    except Exception as e:
        st.error(f"Error downloading video: {e}")