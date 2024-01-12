from EncodeVideoViaThreads import process_video_with_executor
import cloudinary.uploader  

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
