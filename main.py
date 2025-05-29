#!/usr/bin/env python3
"""
MP4 Video Merger Script
Merges two MP4 videos into a single output file.
"""

import os
import sys
from moviepy.editor import VideoFileClip, concatenate_videoclips

def merge_mp4_videos(video1_path, video2_path, output_path):
    """
    Merge two MP4 videos into a single output file.
    
    Args:
        video1_path (str): Path to the first video file
        video2_path (str): Path to the second video file
        output_path (str): Path for the output merged video
    """
    try:
        print("Loading video files...")
        
        # Load the video clips
        clip1 = VideoFileClip(video1_path)
        clip2 = VideoFileClip(video2_path)
        
        print(f"Video 1 duration: {clip1.duration:.2f} seconds")
        print(f"Video 2 duration: {clip2.duration:.2f} seconds")
        
        # Concatenate the clips
        print("Merging videos...")
        final_clip = concatenate_videoclips([clip1, clip2])
        
        print(f"Total merged duration: {final_clip.duration:.2f} seconds")
        
        # Write the result to a file
        print(f"Writing merged video to: {output_path}")
        final_clip.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            verbose=False,
            logger=None
        )
        
        # Clean up
        clip1.close()
        clip2.close()
        final_clip.close()
        
        print("✅ Video merge completed successfully!")
        
    except Exception as e:
        print(f"❌ Error merging videos: {str(e)}")
        return False
    
    return True

def validate_files(video1_path, video2_path):
    """Validate that input files exist and are accessible."""
    if not os.path.exists(video1_path):
        print(f"❌ Error: Video file '{video1_path}' not found.")
        return False
    
    if not os.path.exists(video2_path):
        print(f"❌ Error: Video file '{video2_path}' not found.")
        return False
    
    return True

def main():
    """Main function to handle command line arguments and execute merge."""
    if len(sys.argv) != 4:
        print("Usage: python merge_mp4.py <video1.mp4> <video2.mp4> <output.mp4>")
        print("Example: python merge_mp4.py first_video.mp4 second_video.mp4 merged_output.mp4")
        sys.exit(1)
    
    video1_path = sys.argv[1]
    video2_path = sys.argv[2]
    output_path = sys.argv[3]
    
    print("🎬 MP4 Video Merger")
    print("=" * 40)
    print(f"Input video 1: {video1_path}")
    print(f"Input video 2: {video2_path}")
    print(f"Output video: {output_path}")
    print("=" * 40)
    
    # Validate input files
    if not validate_files(video1_path, video2_path):
        sys.exit(1)
    
    # Check if output file already exists
    if os.path.exists(output_path):
        response = input(f"Output file '{output_path}' already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Operation cancelled.")
            sys.exit(0)
    
    # Perform the merge
    success = merge_mp4_videos(video1_path, video2_path, output_path)
    
    if success:
        output_size = os.path.getsize(output_path) / (1024 * 1024 * 1024)  # Size in GB
        print(f"📁 Output file size: {output_size:.2f} GB")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()