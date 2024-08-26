from setuptools import setup, find_packages

# Function to read the requirements from requirements.txt
def read_requirements():
    with open('requirements.txt') as req_file:
        return req_file.readlines()

setup(
    name="risk_game",
    version="0.2",
    packages=find_packages(),
    install_requires=read_requirements(),
)
