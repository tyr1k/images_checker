#!/usr/bin/python3

import os
import subprocess
import yaml
import glob
import sys

def get_image_names_from_docker_compose(file_path):
    try:
        with open(file_path, "r") as yaml_file:
            docker_compose_data = yaml.safe_load(yaml_file)

        image_names = set()
        for service_name, service_config in docker_compose_data.get("services", {}).items():
            image = service_config.get("image")
            if image:
                # Remove the "registry.example/" prefix
                image_name = image.replace("registry.example/", "")
                image_names.add(image_name)

        return image_names
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return set()

def check_remote_image(image_name):
    try:
        # Use port 444 to check on the remote registry registry.example:444 and the --insecure option
        subprocess.run(["docker", "manifest", "inspect", "--insecure", f"registry.example:444/{image_name}"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError as e:
        return False

if __name__ == "__main__":
    current_directory = os.getcwd()  # Current directory
    missing_images = set()

    docker_compose_files = glob.glob(os.path.join(current_directory, "**", "*docker-compose*"), recursive=True)
    
    for compose_file in docker_compose_files:
        image_names = get_image_names_from_docker_compose(compose_file)
        if not image_names:
            continue

        for image_name in image_names:
            if not check_remote_image(image_name):
                missing_images.add(image_name)

    if missing_images:
        print("Missing images:")
        for image_name in missing_images:
            print(image_name)
        sys.exit(1)  # Explicitly exit the script with exit code 1 if there are missing images
    else:
        sys.exit(0)  # Explicitly exit the script with exit code 0 upon successful execution
