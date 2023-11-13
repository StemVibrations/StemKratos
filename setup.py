from setuptools import setup
from setuptools.command.install import install
import os
import shutil

class CustomStemInstallCommand(install):
    def run(self):
        # Call the default install process
        install.run(self)
        
        folder_path = os.getcwd()
        folder_contents = os.listdir(folder_path + "/StemKratos")
        # Print the contents of the folder
        print("Contents of the folder:")
        for item in folder_contents:
            print(item)
            
        # Custom logic to move data from my_package to another_package
        source_path = 'StemKratos/StemApplication'
        destination_path = 'KratosMultiphysics/StemApplication'

        # Ensure the destination directory exists
        os.makedirs(destination_path, exist_ok=True)

        # Move the entire directory
        shutil.move(source_path, destination_path)

if __name__ == '__main__':
    setup(
    cmdclass={
        'install': CustomStemInstallCommand,
    })
