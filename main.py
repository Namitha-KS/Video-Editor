#!/usr/bin/env python3
"""
Advanced MP4 Video Editor Script
Merge, trim, and remove segments from MP4 videos with progress tracking.
"""

import os
import sys
import argparse
import time
from moviepy.editor import VideoFileClip, concatenate_videoclips
from tqdm import tqdm

class VideoEditor:
    def __init__(self):
        self.temp_files = []
    
    def cleanup_temp_files(self):
        """Clean up temporary files created during processing."""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as e:
                print(f"Warning: Could not remove temp file {temp_file}: {e}")
    
    def progress_callback(self, progress_bar):
        """Callback function for moviepy progress tracking."""
        def callback(gf, t):
            if hasattr(progress_bar, 'update'):
                progress_bar.update(1)
        return callback
    
    def merge_videos(self, input_videos, output_path):
        """
        Merge multiple MP4 videos into a single output file.
        
        Args:
            input_videos (list): List of paths to input video files
            output_path (str): Path for the output merged video
        """
        try:
            print("🎬 Starting video merge process...")
            print("=" * 50)
            
            clips = []
            total_duration = 0
            
            # Load all video clips with progress
            print("Loading video files...")
            for i, video_path in enumerate(input_videos, 1):
                print(f"Loading video {i}/{len(input_videos)}: {os.path.basename(video_path)}")
                clip = VideoFileClip(video_path)
                clips.append(clip)
                total_duration += clip.duration
                print(f"  Duration: {clip.duration:.2f} seconds")
            
            print(f"\nTotal duration after merge: {total_duration:.2f} seconds ({total_duration/60:.2f} minutes)")
            
            # Concatenate the clips
            print("\nMerging videos...")
            final_clip = concatenate_videoclips(clips)
            
            # Write the result with progress bar
            print(f"Writing merged video to: {output_path}")
            
            # Estimate processing time (rough estimate: 1 second per 10 seconds of video)
            estimated_time = int(total_duration / 10)
            print(f"Estimated processing time: {estimated_time} seconds")
            
            # Create a custom progress bar
            pbar = tqdm(total=100, desc="Processing", unit="%", 
                       bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]')
            
            def progress_callback(get_frame, t):
                if final_clip.duration > 0:
                    progress = min(int((t / final_clip.duration) * 100), 100)
                    pbar.n = progress
                    pbar.refresh()
                return get_frame(t)
            
            final_clip.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                verbose=False,
                logger=None
            )
            
            pbar.n = 100
            pbar.refresh()
            pbar.close()
            
            # Clean up
            for clip in clips:
                clip.close()
            final_clip.close()
            
            print("\n✅ Video merge completed successfully!")
            return True
            
        except Exception as e:
            print(f"\n❌ Error merging videos: {str(e)}")
            return False
    
    def trim_video(self, input_path, output_path, start_time, end_time):
        """
        Trim video from start_time to end_time.
        
        Args:
            input_path (str): Path to input video
            output_path (str): Path for output video
            start_time (float): Start time in seconds
            end_time (float): End time in seconds
        """
        try:
            print("✂️ Starting video trim process...")
            print("=" * 50)
            print(f"Input: {input_path}")
            print(f"Output: {output_path}")
            print(f"Trim from {start_time}s to {end_time}s")
            
            # Load video
            print("Loading video file...")
            clip = VideoFileClip(input_path)
            
            print(f"Original duration: {clip.duration:.2f} seconds")
            
            # Validate time bounds
            if start_time >= clip.duration:
                print("❌ Error: Start time is beyond video duration")
                return False
            
            if end_time > clip.duration:
                print(f"⚠️ Warning: End time adjusted from {end_time}s to {clip.duration}s")
                end_time = clip.duration
            
            if start_time >= end_time:
                print("❌ Error: Start time must be less than end time")
                return False
            
            # Trim the video
            print("Trimming video...")
            trimmed_clip = clip.subclip(start_time, end_time)
            trimmed_duration = end_time - start_time
            
            print(f"Trimmed duration: {trimmed_duration:.2f} seconds")
            
            # Write with progress
            estimated_time = int(trimmed_duration / 10)
            print(f"Estimated processing time: {estimated_time} seconds")
            
            # Create progress bar for trim operation
            pbar = tqdm(total=100, desc="Processing", unit="%", 
                       bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]')
            
            trimmed_clip.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio-trim.m4a',
                remove_temp=True,
                verbose=False,
                logger=None
            )
            
            pbar.n = 100
            pbar.refresh()
            pbar.close()
            
            # Clean up
            clip.close()
            trimmed_clip.close()
            
            print("\n✅ Video trim completed successfully!")
            return True
            
        except Exception as e:
            print(f"\n❌ Error trimming video: {str(e)}")
            return False
    
    def remove_segment(self, input_path, output_path, start_time, end_time):
        """
        Remove a segment from start_time to end_time from the video.
        
        Args:
            input_path (str): Path to input video
            output_path (str): Path for output video
            start_time (float): Start time of segment to remove (seconds)
            end_time (float): End time of segment to remove (seconds)
        """
        try:
            print("🗑️ Starting segment removal process...")
            print("=" * 50)
            print(f"Input: {input_path}")
            print(f"Output: {output_path}")
            print(f"Removing segment from {start_time}s to {end_time}s")
            
            # Load video
            print("Loading video file...")
            clip = VideoFileClip(input_path)
            
            print(f"Original duration: {clip.duration:.2f} seconds")
            
            # Validate time bounds
            if start_time >= clip.duration or end_time > clip.duration:
                print("❌ Error: Removal times are beyond video duration")
                return False
            
            if start_time >= end_time:
                print("❌ Error: Start time must be less than end time")
                return False
            
            clips_to_concat = []
            
            # Add part before removal (if any)
            if start_time > 0:
                print(f"Adding segment: 0s to {start_time}s")
                clips_to_concat.append(clip.subclip(0, start_time))
            
            # Add part after removal (if any)
            if end_time < clip.duration:
                print(f"Adding segment: {end_time}s to {clip.duration}s")
                clips_to_concat.append(clip.subclip(end_time, clip.duration))
            
            if not clips_to_concat:
                print("❌ Error: Cannot remove entire video")
                return False
            
            # Concatenate remaining parts
            print("Concatenating remaining segments...")
            if len(clips_to_concat) == 1:
                final_clip = clips_to_concat[0]
            else:
                final_clip = concatenate_videoclips(clips_to_concat)
            
            final_duration = final_clip.duration
            removed_duration = end_time - start_time
            
            print(f"Final duration: {final_duration:.2f} seconds")
            print(f"Removed duration: {removed_duration:.2f} seconds")
            
            # Write with progress
            estimated_time = int(final_duration / 10)
            print(f"Estimated processing time: {estimated_time} seconds")
            
            # Create progress bar for remove operation
            pbar = tqdm(total=100, desc="Processing", unit="%", 
                       bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]')
            
            final_clip.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio-remove.m4a',
                remove_temp=True,
                verbose=False,
                logger=None
            )
            
            pbar.n = 100
            pbar.refresh()
            pbar.close()
            
            # Clean up
            clip.close()
            for c in clips_to_concat:
                c.close()
            if len(clips_to_concat) > 1:
                final_clip.close()
            
            print("\n✅ Segment removal completed successfully!")
            return True
            
        except Exception as e:
            print(f"\n❌ Error removing segment: {str(e)}")
            return False
    
    def validate_files(self, file_paths):
        """Validate that input files exist and are accessible."""
        for file_path in file_paths:
            if not os.path.exists(file_path):
                print(f"❌ Error: Video file '{file_path}' not found.")
                return False
            
            # Check file size (5GB limit)
            file_size = os.path.getsize(file_path) / (1024 * 1024 * 1024)  # Size in GB
            if file_size > 5:
                print(f"❌ Error: File '{file_path}' is {file_size:.2f}GB, exceeds 5GB limit.")
                return False
            
            print(f"✅ File validated: {os.path.basename(file_path)} ({file_size:.2f}GB)")
        
        return True
    
    def parse_time(self, time_str):
        """Parse time string in format MM:SS or SS to seconds."""
        try:
            if ':' in time_str:
                parts = time_str.split(':')
                if len(parts) == 2:
                    minutes, seconds = map(float, parts)
                    return minutes * 60 + seconds
                elif len(parts) == 3:
                    hours, minutes, seconds = map(float, parts)
                    return hours * 3600 + minutes * 60 + seconds
            else:
                return float(time_str)
        except ValueError:
            raise ValueError(f"Invalid time format: {time_str}. Use MM:SS, HH:MM:SS, or seconds")

def main():
    editor = VideoEditor()
    
    try:
        parser = argparse.ArgumentParser(description="Advanced MP4 Video Editor")
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Merge command
        merge_parser = subparsers.add_parser('merge', help='Merge multiple videos')
        merge_parser.add_argument('-in', '--input', nargs='+', required=True, help='Input video files')
        merge_parser.add_argument('-out', '--output', required=True, help='Output video file')
        
        # Trim command
        trim_parser = subparsers.add_parser('trim', help='Trim video from start to end time')
        trim_parser.add_argument('input', help='Input video file')
        trim_parser.add_argument('output', help='Output video file')
        trim_parser.add_argument('start', help='Start time (MM:SS or seconds)')
        trim_parser.add_argument('end', help='End time (MM:SS or seconds)')
        
        # Remove command
        remove_parser = subparsers.add_parser('remove', help='Remove segment from video')
        remove_parser.add_argument('input', help='Input video file')
        remove_parser.add_argument('output', help='Output video file')
        remove_parser.add_argument('start', help='Start time of segment to remove (MM:SS or seconds)')
        remove_parser.add_argument('end', help='End time of segment to remove (MM:SS or seconds)')
        
        args = parser.parse_args()
        
        if not args.command:
            parser.print_help()
            return
        
        start_time = time.time()
        
        if args.command == 'merge':
            # Validate input files
            if not editor.validate_files(args.input):
                sys.exit(1)
            
            # Check if output file already exists
            if os.path.exists(args.output):
                response = input(f"Output file '{args.output}' already exists. Overwrite? (y/N): ")
                if response.lower() != 'y':
                    print("Operation cancelled.")
                    sys.exit(0)
            
            success = editor.merge_videos(args.input, args.output)
            
        elif args.command == 'trim':
            # Validate input file
            if not editor.validate_files([args.input]):
                sys.exit(1)
            
            try:
                start_seconds = editor.parse_time(args.start)
                end_seconds = editor.parse_time(args.end)
            except ValueError as e:
                print(f"❌ Error: {e}")
                sys.exit(1)
            
            success = editor.trim_video(args.input, args.output, start_seconds, end_seconds)
            
        elif args.command == 'remove':
            # Validate input file
            if not editor.validate_files([args.input]):
                sys.exit(1)
            
            try:
                start_seconds = editor.parse_time(args.start)
                end_seconds = editor.parse_time(args.end)
            except ValueError as e:
                print(f"❌ Error: {e}")
                sys.exit(1)
            
            success = editor.remove_segment(args.input, args.output, start_seconds, end_seconds)
        
        # Show final results
        if success:
            end_time = time.time()
            processing_time = end_time - start_time
            
            if os.path.exists(args.output):
                output_size = os.path.getsize(args.output) / (1024 * 1024 * 1024)  # Size in GB
                print(f"\n📁 Output file: {args.output}")
                print(f"📊 Output size: {output_size:.2f} GB")
            
            print(f"⏱️ Total processing time: {processing_time:.2f} seconds")
            print("🎉 Operation completed successfully!")
        else:
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)
    finally:
        editor.cleanup_temp_files()

if __name__ == "__main__":
    main()