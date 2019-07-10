from azure.storage.blob import BlockBlobService, PublicAccess
import os, sys


def AzureUpload(currentfile):
	
	try:
	    # Create the BlockBlockService that is used to call the Blob service for the storage account
	    block_blob_service = BlockBlobService(account_name='produceimages', account_key='m8BZlDWt8wDI+wHPVwyhzyKCeMDz53GKy73o6sA5u57PyyTN1tvQg9pv4BRDBCOdlBEkKbb5pKu15fUTP59sNg==')

	    # Create a container called 'quickstartblobs'.
	    container_name ='quickstartblobs'
	    block_blob_service.create_container(container_name)

	    # Set the permission so the blobs are public.
	    block_blob_service.set_container_acl(container_name, public_access=PublicAccess.Container)

	    # Create a file in Documents to test the upload and download.
	    local_path=os.path.expanduser("./static/")
	    local_file_name = currentfile
	    full_path_to_file =os.path.join(local_path, local_file_name)

	    print('Uploading..'+currentfile)
	    # Upload the created file, use local_file_name for the blob name
	    block_blob_service.create_blob_from_path(container_name, local_file_name, full_path_to_file)

	    sys.stdout.flush()
	    # input()

	    # Clean up resources. This includes the container and the temp files
	    # block_blob_service.delete_container(container_name)
	    # os.remove(full_path_to_file)
	    
	except Exception as e:
	    print(e)
