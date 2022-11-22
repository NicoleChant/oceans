from google.cloud import storage
import os
from termcolor import colored

def _store_honey(storage_client : ... ,
                        bucket : ... ,
                        source_file : str ,
                        destination : str
                        ) -> None:

    blob = bucket.blob(destination)
    blob.upload_from_filename(source_file)
    print(colored("Moved honey 🍯 to cloud ☁️!","green"))

def create_bucket(client , bucket_name):
    bucket = client.bucket(bucket_name)
    new_bucket = client.create_bucket(bucket , location = "eu")
    return new_bucket

def store_honey_to_cloud(bucket_name : str = "ocean_images") -> None:
    storage_client = storage.Client()
    bucket = storage.Bucket(storage_client , bucket_name)
    if not bucket.exists():
        bucket = create_bucket(storage_client , bucket_name)

    for idx , (root, dirs, files) in enumerate(os.walk("images")):
        if idx == 0:
            blobs = dirs

        if files:
            for file in files:
                blob_name = os.path.join(blobs[idx-1] , file)
                source_file = os.path.join( "images" , blob_name)
                _store_honey(storage_client ,
                            bucket = bucket ,
                            source_file = source_file ,
                            destination = blob_name  )
                os.remove(source_file)
    storage_client.close()


if __name__ == "__main__":
    store_honey_to_cloud()
