import os
import shutil
import subprocess
from utils import converttime, convertname

def run_command(command, log_func):
    """
    Runs a shell command and sends each line of its output to log_func in real time.
    Returns the completed process.
    """
    log_func(f"Executing: {command}")
    proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    while True:
        line = proc.stdout.readline()
        if line:
            log_func(line.strip())
        if not line and proc.poll() is not None:
            break
    return proc

def process_full_video_gui(url, output_name, out_dir, log_func, status_func, progress_bar):
    # Step 1: Download Video (Overall: 0% -> 60%)
    status_func("Downloading video... 0%")
    log_func("Starting yt-dlp download for full video...")
    cmd = f'yt-dlp "{url}" --no-playlist --merge-output-format mp4 -o input.mp4'
    run_command(cmd, log_func)
    if not os.path.exists("input.mp4"):
        log_func("Video download failed.")
        status_func("Download failed")
        return
    progress_bar['value'] = 60
    status_func("Video download complete. (60%)")
    log_func("Video downloaded successfully.")
    
    # Step 2: Process Video (60% -> 95%)
    status_func("Processing video... 60%")
    log_func("Moving downloaded video to output location...")
    destination = os.path.join(out_dir, convertname(output_name) + ".mp4")
    try:
        shutil.move("input.mp4", destination)
        progress_bar['value'] = 95
        status_func("Video processing complete. (95%)")
        log_func("Video saved successfully at: " + destination)
    except Exception as e:
        log_func("Error during processing: " + str(e))
        status_func("Error during processing")
        return
    
    # Step 3: Clean Up (95% -> 100%)
    progress_bar['value'] = 100
    status_func("Process complete. (100%)")

def process_cut_video_gui(url, output_name, out_dir, start, end, log_func, status_func, progress_bar):
    # Step 1: Download Video (Overall: 0% -> 60%)
    status_func("Downloading video... 0%")
    log_func("Starting yt-dlp download for video cutting...")
    cmd = f'yt-dlp "{url}" --no-playlist --merge-output-format mp4 -o input.mp4'
    run_command(cmd, log_func)
    if not os.path.exists("input.mp4"):
        log_func("Video download failed.")
        status_func("Download failed")
        return
    progress_bar['value'] = 60
    status_func("Video download complete. (60%)")
    log_func("Video downloaded successfully.")
    
    # Step 2: Process (Cut) Video (Overall: 60% -> 95%)
    # If start is empty, assume 0; if end is empty, process until the end (omit duration).
    actual_start = converttime(start) if start.strip() else 0
    if end.strip():
        actual_end = converttime(end)
        duration = actual_end - actual_start
        duration_option = f"-t {duration}"
        log_func(f"Cutting video from {start if start.strip() else '0:00'} to {end}...")
    else:
        duration_option = ""
        log_func(f"Cutting video from {start if start.strip() else '0:00'} until end...")
    status_func("Cutting video... 60%")
    
    destination = os.path.join(out_dir, convertname(output_name) + ".mp4")
    cmd = f'ffmpeg.exe -v quiet -stats -ss {actual_start} {duration_option} -i input.mp4 -y -c:v libx264 "{destination}"'
    run_command(cmd, log_func)
    progress_bar['value'] = 95
    status_func("Video cutting complete. (95%)")
    log_func("Video cut and saved successfully at: " + destination)
    
    # Step 3: Clean Up
    subprocess.run('del input.mp4 /s /q /f', shell=True, check=True)
    progress_bar['value'] = 100
    status_func("Process complete. (100%)")

def process_full_audio_gui(url, output_name, out_dir, log_func, status_func, progress_bar):
    # Step 1: Download Audio (Overall: 0% -> 60%)
    status_func("Downloading audio... 0%")
    log_func("Starting yt-dlp download for full audio...")
    cmd = f'yt-dlp "{url}" --no-playlist --extract-audio --audio-format mp3 -o input_audio.mp3'
    run_command(cmd, log_func)
    if not os.path.exists("input_audio.mp3"):
        log_func("Audio download failed.")
        status_func("Download failed")
        return
    progress_bar['value'] = 60
    status_func("Audio download complete. (60%)")
    log_func("Audio downloaded successfully.")
    
    # Step 2: Process Audio (Overall: 60% -> 95%)
    status_func("Processing audio... 60%")
    log_func("Moving downloaded audio to output location...")
    destination = os.path.join(out_dir, convertname(output_name) + ".mp3")
    try:
        shutil.move("input_audio.mp3", destination)
        progress_bar['value'] = 95
        status_func("Audio conversion complete. (95%)")
        log_func("Audio saved successfully at: " + destination)
    except Exception as e:
        log_func("Error during processing: " + str(e))
        status_func("Error during processing")
        return
    
    # Step 3: Clean Up
    progress_bar['value'] = 100
    status_func("Process complete. (100%)")

def process_cut_audio_gui(url, output_name, out_dir, start, end, log_func, status_func, progress_bar):
    # Step 1: Download Audio (Overall: 0% -> 60%)
    status_func("Downloading audio... 0%")
    log_func("Starting yt-dlp download for audio cutting...")
    cmd = f'yt-dlp "{url}" --no-playlist --extract-audio --audio-format mp3 -o input_audio.mp3'
    run_command(cmd, log_func)
    if not os.path.exists("input_audio.mp3"):
        log_func("Audio download failed.")
        status_func("Download failed")
        return
    progress_bar['value'] = 60
    status_func("Audio download complete. (60%)")
    log_func("Audio downloaded successfully.")
    
    # Step 2: Process (Cut) Audio (Overall: 60% -> 95%)
    if start.strip():
        actual_start = converttime(start)
    else:
        actual_start = 0
    if end.strip():
        actual_end = converttime(end)
        duration = actual_end - actual_start
        duration_option = f"-t {duration}"
        log_func(f"Cutting audio from {start if start.strip() else '0:00'} to {end}...")
    else:
        duration_option = ""
        log_func(f"Cutting audio from {start if start.strip() else '0:00'} until end...")
    status_func("Cutting audio... 60%")
    
    destination = os.path.join(out_dir, convertname(output_name) + ".mp3")
    cmd = f'ffmpeg.exe -v quiet -stats -ss {actual_start} {duration_option} -i input_audio.mp3 -y -vn -acodec libmp3lame "{destination}"'
    run_command(cmd, log_func)
    progress_bar['value'] = 95
    status_func("Audio cutting complete. (95%)")
    log_func("Audio cut and saved successfully at: " + destination)
    
    # Step 3: Clean Up
    subprocess.run('del input_audio.mp3 /s /q /f', shell=True, check=True)
    progress_bar['value'] = 100
    status_func("Process complete. (100%)")
