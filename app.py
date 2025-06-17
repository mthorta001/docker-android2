#!/usr/bin/env python3
"""
Docker Android Build Script
A Python implementation of app.sh with better readability and maintainability.
"""

import argparse
import subprocess
import sys
from typing import List, Dict, Optional


class DockerAndroidBuilder:
    """Main class for building Docker Android images."""
    
    # Configuration constants
    TASKS = ["test", "build", "push"]
    PROJECTS = ["base", "emulator", "genymotion", "pro-emulator", "pro-emulator_headless"]
    SUPPORTED_ANDROID_VERSIONS = ["9.0", "10.0", "11.0", "12.0", "13.0", "14.0", "15.0", "16.0"]
    API_LEVELS = {
        "9.0": 28, "10.0": 29, "11.0": 30, "12.0": 32,
        "13.0": 33, "14.0": 34, "15.0": 35, "16.0": 36
    }
    DOCKER_USERNAME = "rcswain"
    
    def __init__(self):
        self.task: str = ""
        self.project: str = ""
        self.release_version: str = ""
        self.android_version: Optional[str] = None
        self.api_level: Optional[int] = None
        
        self.folder_path: str = ""
        self.image_name: str = ""
        self.tag_name: str = ""
        self.image_name_latest: str = ""
        self.image_name_specific_release: str = ""
    
    def validate_choice(self, value: str, valid_options: List[str], option_name: str) -> None:
        """Validate if the given value is in the list of valid options."""
        if value not in valid_options:
            print(f"Error: '{value}' is not a supported {option_name}!")
            print(f"Supported {option_name}s: {', '.join(valid_options)}")
            sys.exit(1)
    
    def get_user_input(self, prompt: str, valid_options: List[str]) -> str:
        """Get user input with validation."""
        options_str = "|".join(valid_options)
        while True:
            value = input(f"{prompt} ({options_str}): ").strip()
            if value in valid_options:
                return value
            print(f"Invalid choice. Please select from: {', '.join(valid_options)}")
    
    def parse_arguments(self) -> None:
        """Parse command line arguments or get interactive input."""
        parser = argparse.ArgumentParser(
            description="Build Docker Android images",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        parser.add_argument("task", nargs="?", choices=self.TASKS,
                          help="Task to perform")
        parser.add_argument("project", nargs="?", choices=self.PROJECTS,
                          help="Project type to build")
        parser.add_argument("release_version", nargs="?",
                          help="Release version (e.g., v2.0.0-p0)")
        parser.add_argument("android_version", nargs="?", choices=self.SUPPORTED_ANDROID_VERSIONS,
                          help="Android version (for emulator projects)")
        
        args = parser.parse_args()
        
        # Get task
        if args.task:
            self.task = args.task
        else:
            self.task = self.get_user_input("Task", self.TASKS)
        
        # Get project
        if args.project:
            self.project = args.project
        else:
            self.project = self.get_user_input("Project", self.PROJECTS)
        
        # Get release version
        if args.release_version:
            self.release_version = args.release_version
        else:
            self.release_version = input("Release Version (v2.0.0-p0|v2.0.0-p1|etc): ").strip()
        
        # Get Android version for emulator projects
        if "emulator" in self.project:
            if args.android_version:
                self.android_version = args.android_version
            else:
                self.android_version = self.get_user_input("Android Version", self.SUPPORTED_ANDROID_VERSIONS)
            
            self.validate_choice(self.android_version, self.SUPPORTED_ANDROID_VERSIONS, "Android version")
            self.api_level = self.API_LEVELS[self.android_version]
    
    def setup_build_configuration(self) -> None:
        """Setup build configuration based on project type."""
        if self.project.startswith("pro"):
            # Handle pro projects: pro-emulator -> docker/pro/emulator
            parts = self.project.split("-", 1)
            self.folder_path = f"docker/{parts[0]}/{parts[1]}"
            self.image_name = f"{self.DOCKER_USERNAME}/docker-android-{parts[0]}"
            self.tag_name = parts[1]
        else:
            # Handle regular projects
            self.folder_path = f"docker/{self.project}"
            self.image_name = f"{self.DOCKER_USERNAME}/docker-android"
            self.tag_name = self.project
        
        # Add Android version to tag if it's an emulator project
        if "emulator" in self.project and self.android_version:
            self.tag_name += f"_{self.android_version}"
        
        # Setup image names
        self.image_name_latest = f"{self.image_name}:{self.tag_name}"
        self.image_name_specific_release = f"{self.image_name}:{self.tag_name}_{self.release_version}"
        
        print(f"Building: {self.image_name_specific_release} or {self.image_name_latest}")
    
    def run_command(self, command: List[str], description: str = "") -> bool:
        """Run a shell command and return success status."""
        if description:
            print(f"Running: {description}")
        
        print(f"Command: {' '.join(command)}")
        
        try:
            result = subprocess.run(command, check=True, capture_output=False)
            return result.returncode == 0
        except subprocess.CalledProcessError as e:
            print(f"Error: Command failed with exit code {e.returncode}")
            return False
        except FileNotFoundError:
            print(f"Error: Command not found: {command[0]}")
            return False
    
    def build_image(self) -> bool:
        """Build Docker image."""
        print("=" * 50)
        print("Building Docker Image")
        print("=" * 50)
        
        # Build docker command
        cmd = [
            "docker", "build",
            "-t", self.image_name_specific_release,
            "--build-arg", f"DOCKER_ANDROID_VERSION={self.release_version}"
        ]
        
        # Add Android-specific build args for emulator projects
        if self.android_version and self.api_level:
            cmd.extend([
                "--build-arg", f"EMULATOR_ANDROID_VERSION={self.android_version}",
                "--build-arg", f"EMULATOR_API_LEVEL={self.api_level}"
            ])
        
        cmd.extend(["-f", self.folder_path, "."])
        
        # Build the image
        if not self.run_command(cmd, "Building Docker image"):
            return False
        
        # Tag as latest
        if not self.run_command([
            "docker", "tag", 
            self.image_name_specific_release, 
            self.image_name_latest
        ], "Tagging as latest"):
            return False
        
        # Tag as default latest if this is the last Android version
        if (self.android_version and 
            self.android_version == self.get_last_android_version()):
            print(f"{self.android_version} is the last version, tagging as default latest")
            if not self.run_command([
                "docker", "tag",
                self.image_name_specific_release,
                f"{self.image_name}:latest"
            ], "Tagging as default latest"):
                return False
        
        return True
    
    def get_last_android_version(self) -> str:
        """Get the last Android version from the supported versions."""
        # Sort versions and get the second to last (as per original logic)
        sorted_versions = sorted(self.SUPPORTED_ANDROID_VERSIONS, key=lambda x: float(x))
        return sorted_versions[-2] if len(sorted_versions) > 1 else sorted_versions[-1]
    
    def run_tests(self) -> bool:
        """Run tests in Docker container."""
        print("=" * 50)
        print("Running Tests")
        print("=" * 50)
        
        # Build first
        if not self.build_image():
            return False
        
        # Setup test environment
        cli_path = "/home/androidusr/docker-android/cli"
        results_path = "test-results"
        tmp_folder = "tmp"
        
        # Create tmp directory
        subprocess.run(["mkdir", "-p", tmp_folder], check=True)
        
        # Run tests in container
        test_cmd = [
            "docker", "run", "-it", "--rm", "--name", "test",
            "--entrypoint", "/bin/bash",
            "-v", f"{subprocess.check_output(['pwd']).decode().strip()}/{tmp_folder}:{cli_path}/{tmp_folder}",
            self.image_name_specific_release,
            "-c", (
                f"cd {cli_path} && "
                f"sudo rm -rf {tmp_folder}/* && "
                f"nosetests -v && "
                f"sudo mv .coverage {tmp_folder} && "
                f"sudo cp -r {results_path}/* {tmp_folder} && "
                f"sudo chown -R 1300:1301 {tmp_folder} && "
                f"sudo chmod a+x -R {tmp_folder}"
            )
        ]
        
        return self.run_command(test_cmd, "Running tests in container")
    
    def push_images(self) -> bool:
        """Build and push images to Docker Hub."""
        print("=" * 50)
        print("Pushing Images to Docker Hub")
        print("=" * 50)
        
        # Build first
        if not self.build_image():
            return False
        
        # Push specific release
        if not self.run_command([
            "docker", "push", self.image_name_specific_release
        ], "Pushing specific release"):
            return False
        
        # Push latest
        if not self.run_command([
            "docker", "push", self.image_name_latest
        ], "Pushing latest tag"):
            return False
        
        # Push default latest if applicable
        if (self.android_version and 
            self.android_version == self.get_last_android_version()):
            if not self.run_command([
                "docker", "push", f"{self.image_name}:latest"
            ], "Pushing default latest"):
                return False
        
        return True
    
    def execute_task(self) -> bool:
        """Execute the specified task."""
        task_methods = {
            "build": self.build_image,
            "test": self.run_tests,
            "push": self.push_images
        }
        
        method = task_methods.get(self.task)
        if not method:
            print(f"Error: Unknown task '{self.task}'")
            return False
        
        return method()
    
    def run(self) -> None:
        """Main execution method."""
        try:
            print("Docker Android Builder")
            print("=" * 50)
            
            self.parse_arguments()
            self.setup_build_configuration()
            
            success = self.execute_task()
            
            if success:
                print("\n" + "=" * 50)
                print("✅ Task completed successfully!")
            else:
                print("\n" + "=" * 50)
                print("❌ Task failed!")
                sys.exit(1)
                
        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user.")
            sys.exit(1)
        except Exception as e:
            print(f"\nUnexpected error: {e}")
            sys.exit(1)


def main():
    """Entry point for the script."""
    builder = DockerAndroidBuilder()
    builder.run()


if __name__ == "__main__":
    main() 