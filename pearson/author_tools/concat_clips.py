from moviepy import VideoFileClip, concatenate_videoclips

def concatenate_videos(video_files, output_path):
    """
    Concatenates a list of video files into a single video.

    Args:
        video_files (list): A list of paths to the video files to concatenate.
        output_path (str): The path to save the concatenated video.
            Must include the file extension (e.g., ".mp4").

    Returns:
        bool: True if the concatenation was successful, False otherwise.
    """
    try:
        # 1. Load the video clips
        video_clips = [VideoFileClip(video_file) for video_file in video_files]

        # 2. Concatenate the video clips
        final_clip = concatenate_videoclips(video_clips)

        # 3. Write the concatenated video to a file
        #  Use the 'auto' preset, which is generally recommended and handles codec/fps
        final_clip.write_videofile(output_path, preset='ultrafast')

        # 4. Close the clips to release resources
        for clip in video_clips:
            clip.close()
        final_clip.close()

        print(f"Successfully concatenated videos to {output_path}")
        return True
    except Exception as e:
        print(f"Error concatenating videos: {e}")
        return False

if __name__ == "__main__":
    # Example usage:
    # List of video file paths
    video_files = [
        "clip1.mp4",
        "clip2.mp4",
        "clip3.mp4",
        # Add more video file paths as needed
    ]
    # Output file path
    output_path = "concatenated_video.mp4"

    # Create dummy video files for demonstration
    from moviepy import ColorClip
    for i, file_name in enumerate(video_files):
        # Create a short, different colored clip
        color = [[255,0,0], [0,255,0], [0,0,255]][i % 3] # simple color cycling
        # color = ['red', 'green', 'blue'][i % 3] # simple color cycling
        clip = ColorClip(size=(640, 480), color=color, duration=2)  # 2 seconds each
        clip.write_videofile(file_name, fps=24, preset='ultrafast') # Use ultrafast
        clip.close() # Close the clip

    # Concatenate the videos
    success = concatenate_videos(video_files, output_path)

    if success:
        print(f"Concatenated video saved to {output_path}")
    else:
        print("Failed to concatenate videos.")
