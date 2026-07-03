#!/usr/bin/env python3

import os
import time
import argparse

# Heavyweight imports are done later to improve argparse responsiveness

def parse_arguments():
    parser = argparse.ArgumentParser(description="Analyze video(s) to find the best frame containing a person.")
    parser.add_argument("-f", "--file", help="Path to a single input video file")
    parser.add_argument("-i", "--input_dir", help="Directory of input videos (for example: /usb)")
    parser.add_argument("-o", "--output_dir", default=".", help="Directory to save output images (default: <current_dir>)")
    parser.add_argument("-s", "--skip", type=int, default=5, help="Process every Nth frame (default: 5)")
    parser.add_argument("-c", "--conf", type=float, default=0.4, help="Confidence threshold (default: 0.4)")
    parser.add_argument("-z", "--size", type=int, default=320, help="YOLO image size in pixels (default: 320)")
    parser.add_argument("-p", "--preserve", action="store_true", help="Preserve directory structure in output path")
    parser.add_argument("-r", "--recursive", action="store_true", help="Recursively process all videos in input directory")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress progress messages and final results")
    args = parser.parse_args()

    # Validate arguments
    if not args.file and not args.input_dir:
        parser.error("You must specify either --file or --input_dir")

    if args.file and not os.path.exists(args.file):
        raise FileNotFoundError(f"Video file '{args.file}' does not exist.")

    if args.input_dir and not os.path.exists(args.input_dir):
        raise FileNotFoundError(f"Input directory '{args.input_dir}' does not exist.")

    os.makedirs(args.output_dir, exist_ok=True)
    return args

def get_output_path(video_path, output_dir, input_dir, preserve_structure=False):
    """Generate the output path for the result image"""
    if preserve_structure:
        # Get the relative path from the input directory
        try:
            relative_path = os.path.relpath(video_path, input_dir)
            output_subdir = os.path.join(output_dir, os.path.dirname(relative_path))
        except ValueError:
            # If video_path is not relative to input_dir, just use the filename
            output_subdir = output_dir

        os.makedirs(output_subdir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        return os.path.join(output_subdir, f"{base_name}.jpg")
    else:
        # Flat structure: all files in output directory
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        return os.path.join(output_dir, f"{base_name}.jpg")

def get_video_metadata(video_path):
    """Extract capture date from video file, since filenames are in UTC"""
    file_timestamp = os.path.getmtime(video_path)
    return {
        'date_time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_timestamp)),
        'base_name': os.path.splitext(os.path.basename(video_path))[0]
    }

def analyze_video(model, video_path, skip_frames, conf_threshold, size, quiet=False):
    # Make sure cv2 is loaded
    _ensure_cv2()
    video = cv2.VideoCapture(video_path)

    frame_number = 0
    best_score = 0.0
    best_data = None

    if not quiet:
        print(f"Processing: {video_path}")
        print(f"Skip={skip_frames}, Threshold={conf_threshold}")

    while True:
        ret, frame = video.read()
        if not ret:
            break

        frame_number += 1
        if frame_number % skip_frames != 0:
            continue

        # If this is the first frame, save it as the default
        if best_data is None:
            best_data = {
                'frame': frame.copy(),
                'detections': [],
                'frame_id': frame_number,
                'person_count': 0,
                'avg_conf': 0,
            }

        # Detect all people in frame (reduce image size to 256 for speed. 640/320 better but slower)
        results = model(frame, imgsz=size, classes=[0], max_det=5, verbose=False)
        detections = []

        for r in results:
            for box in r.boxes:
                if int(box.cls[0]) == 0:  # Person class
                    conf = float(box.conf[0])
                    if conf >= conf_threshold:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        detections.append((conf, (x1, y1, x2, y2)))
        del results # Clean up

        if detections:
            person_count = len(detections)
            avg_conf = sum(d[0] for d in detections) / person_count

            # Score rewards multiple people: 1 person=1x, 2 people=1.5x, 3 people=2x, etc.
            score = avg_conf * (1 + 0.5 * (person_count - 1))

            if not quiet:
                print(f"Frame {frame_number}: {person_count} people, "
                      f"avg_conf={avg_conf:.2f}, score={score:.2f}")

            if score > best_score:
                best_score = score
                best_data = {
                    'frame': frame.copy(),
                    'detections': detections,
                    'frame_id': frame_number,
                    'person_count': person_count,
                    'avg_conf': avg_conf,
                }

    video.release()
    return best_data

def add_overlay(image, video_path, metadata, best_data):
    # Make sure cv2 is loaded
    _ensure_cv2()
    h, w, _ = image.shape

    if best_data['detections']:
        # Draw bounding boxes for detected people
        for conf, (x1, y1, x2, y2) in best_data['detections']:
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(image, f"{conf:.2f}", (x1, y1 - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Prepare overlay text
    display_path = video_path if len(video_path) <= 60 else "..." + video_path[-57:]

    lines = [
        f"Capture Date: {metadata['date_time']}, Person Count: {best_data['person_count']}",
        f"File: {display_path}",
    ]

    # Draw semi-transparent panel
    margin, padding, line_height = 15, 10, 30
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale, thickness = 0.7, 2

    max_width = max(cv2.getTextSize(line, font, font_scale, thickness)[0][0] for line in lines)
    panel_w, panel_h = max_width + 2*padding, len(lines)*line_height + 2*padding
    px1, py1 = margin, h - panel_h - margin
    px2, py2 = px1 + panel_w, h - margin

    overlay = image.copy()
    cv2.rectangle(overlay, (px1, py1), (px2, py2), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.5, image, 0.5, 0, image)

    # Add text
    _, text_height = cv2.getTextSize("A", font, font_scale, thickness)[0]
    for i, line in enumerate(lines):
        y_pos = py1 + padding + i*line_height + (line_height + text_height)//2 - 2
        cv2.putText(image, line, (px1 + padding, y_pos),
                   font, font_scale, (0, 255, 0), thickness)


def get_video_files(directory, recursive=False):
    """Get all video files from directory"""
    video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv'}
    video_files = []

    if recursive:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if os.path.splitext(file)[1].lower() in video_extensions:
                    video_files.append(os.path.join(root, file))
    else:
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path) and os.path.splitext(file)[1].lower() in video_extensions:
                video_files.append(file_path)

    return sorted(video_files)


def process_video_file(model, video_path, output_dir, input_dir, skip_frames, conf_threshold, size, preserve, quiet=False):
    """Process a single video file and return True if successful"""
    # Make sure cv2 is loaded
    _ensure_cv2()

    metadata = get_video_metadata(video_path)
    output_path = get_output_path(video_path, output_dir, input_dir, preserve)

    # Check if output already exists
    if os.path.exists(output_path):
        if not quiet:
            print(f"Skipping {video_path} - output already exists")
        return False

    best_data = analyze_video(model, video_path, skip_frames, conf_threshold, size, quiet)

    if not best_data:
        if not quiet:
            print(f"No person detected in {video_path}")
        return False

    add_overlay(best_data['frame'], video_path, metadata, best_data)
    cv2.imwrite(output_path, best_data['frame'])

    if not quiet:
        print("==== RESULT ====")
        print(f"Saved: {output_path}")
        print(f"Frame: {best_data['frame_id']}")
        print(f"Person Count: {best_data['person_count']}, Avg Conf: {best_data['avg_conf']:.2f}")

    return True

def _ensure_cv2():
    global cv2
    if 'cv2' not in globals():
        try:
            import cv2 as _cv2
            cv2 = _cv2

        except ModuleNotFoundError as e:
            print(f"Missing module dependencies: {e}")
            print("Try creating and using a virtual environment (venv) with necessary modules")

        except Exception as e:
            print(f"Error: {e}")


def main():
    try:
        args = parse_arguments()

        # Lazy imports to improve responsiveness of argparse
        import cv2
        import torch
        from ultralytics import YOLO

        cache_dir = os.path.join(os.path.expanduser("~"),".cache","ultralytics")
        os.makedirs(cache_dir, exist_ok=True)

        model_path = os.path.join(cache_dir, "yolov8n.pt")
        model = YOLO(model_path)

        # Memory saving optimisations for Pi Zero (can be removed for higher spec. devices)
        torch.set_num_threads(1)
        torch.set_num_interop_threads(1)
        cv2.setNumThreads(1)
        cv2.ocl.setUseOpenCL(False)

        # Determine which files to process
        if args.file:
            # Single file mode
            video_files = [args.file]
            input_dir = os.path.dirname(args.file)
        else:
            # Batch mode (with or without recursion)
            video_files = get_video_files(args.input_dir, recursive=args.recursive)
            input_dir = args.input_dir

            if not video_files:
                print(f"No video files found in {args.input_dir}")
                return

        # Process each video file
        processed_count = 0
        for video_path in video_files:
            if process_video_file(model, video_path, args.output_dir, input_dir,
                                 args.skip, args.conf, args.size, args.preserve, args.quiet):
                processed_count += 1

        if not args.quiet:
            print("==== SUMMARY ====")

        print(f"Processed {processed_count} out of {len(video_files)} video files")

    except ModuleNotFoundError as e:
        print(f"Missing module dependencies: {e}")
        print("Try creating and using a virtual environment (venv) with necessary modules")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
