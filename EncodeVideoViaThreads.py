import os
import subprocess
import shutil
from concurrent.futures import ThreadPoolExecutor
import time
import cloudinary.uploader  
start_time = time.time()
# Function to split the input video into 5-minute segments and store them in a directory
def split_video(input_video, output_directory):
    # Create the temp directory in the output directory
    temp_directory = os.path.join(output_directory, 'temp')
    os.makedirs(temp_directory, exist_ok=True)

    # FFmpeg command to split the video into 5-minute segments and store them in the temp directory
    split_command = f'ffmpeg -i {input_video} -c copy -map 0 -segment_time 300 -f segment {temp_directory}/segment_%03d.mp4'

    # Run the split command
    subprocess.run(split_command, shell=True)

    # Count the number of segments created
    nbrseg = len([name for name in os.listdir(temp_directory) if os.path.isfile(os.path.join(temp_directory, name))])
    return temp_directory, nbrseg

# Function to compress a single video segment
def compress_segment(input_segment, output_directory):
    # Create the tempcom directory in the output directory
    tempcom_directory = os.path.join(output_directory, 'tempcom')
    os.makedirs(tempcom_directory, exist_ok=True)

    # Replace 'ffmpeg_command' with your actual compression command
    output_segment = os.path.join(tempcom_directory, f'comp_{os.path.basename(input_segment)}')
    ffmpeg_command = f'ffmpeg -i {input_segment} -c:v libx265 -preset veryfast -crf 34 -vf scale=480:-2 -c:a aac -b:a 96k {output_segment}'

    subprocess.run(ffmpeg_command, shell=True)

    return tempcom_directory

# Function to concatenate compressed segments into a single video
def concatenate_segments(input_video, output_directory):
    # Get the tempcom directory path
    tempcom_directory = os.path.join(output_directory, 'tempcom')

    # Concatenate all compressed segments into a single video
    # Replace 'concat_command' with the actual FFmpeg command to concatenate the videos
    output_video = f'{os.path.splitext(input_video)[0]}_comp.mp4'  # Output video name
    concat_command = f'ffmpeg -f concat -safe 0 -i {tempcom_directory}/filelist.txt -c copy {output_video}'

    # Create a list of input files for concatenation
    file_list = '\n'.join([f"file '{os.path.join(tempcom_directory, file)}'" for file in os.listdir(tempcom_directory)])
    with open(f'{tempcom_directory}/filelist.txt', 'w') as filelist:
        filelist.write(file_list)

    # Run the concatenate command
    subprocess.run(concat_command, shell=True)

    return output_video

# Function to process the video
def process_video_with_executor(input_video):
    output_directory = 'C:/Users/Asus/Desktop/videos'  

    # Split the input video into segments and count the number of segments
    temp_directory, nbrseg = split_video(input_video, output_directory)

    # Use ThreadPoolExecutor for compressing segments concurrently
    with ThreadPoolExecutor(max_workers=4) as executor:  
        futures = []

        for i in range(nbrseg):
            
            segment_file = os.path.join(temp_directory, f'segment_{i:03d}.mp4')

            # Submit compress_segment function to the ThreadPoolExecutor
            future = executor.submit(compress_segment, segment_file, output_directory)
            futures.append(future)

        # Wait for all submitted tasks to complete
        for future in futures:
            future.result()

    # Concatenate compressed segments into a single video
    output_video = concatenate_segments(input_video, output_directory)

    # Delete temporary directories (temp and tempcom)
    shutil.rmtree(temp_directory)
    shutil.rmtree(os.path.join(output_directory, 'tempcom'))

    return output_video
def process_video_and_upload(input_video):
    """Compresses a video, uploads it, and returns a clickable download link."""

    compressed_video = process_video_with_executor(input_video)  # Compress using optimized function
    print(compressed_video)
    
    try:
        cloudinary.config( 
            cloud_name = "de2j1iuvb", 
            api_key = "872526421864592", 
            api_secret = "NlZBFY_RJLANZb6Bh5tUon8SP3Q" 
        )
        upload_result = cloudinary.uploader.upload(compressed_video, resource_type = "video")
        download_link = upload_result['secure_url']
    except Exception as e:
        print(f"Cloudinary upload failed: {e}")
        download_link = None


    return download_link



# Record the ending time
end_time = time.time()

# Calculate the elapsed time
execution_time = end_time - start_time

# Print the execution time
print(f"Execution time: {execution_time} seconds")