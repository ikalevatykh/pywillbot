from setuptools import setup, find_packages

# version
exec(open('pywillbot/version.py').read())

# requirements
with open("./requirements.txt", "r") as f:
    requirements = [l.strip() for l in f.readlines() if len(l.strip()) > 0]


setup(
    name="pywillbot",
    version=__version__,
    author="Igor Kalevatykh",
    description="Control Willbot without ROS!",
    long_description="",
    packages=find_packages(),
    install_requires=requirements,
    zip_safe=False,
)
