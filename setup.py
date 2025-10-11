from setuptools import find_packages, setup

setup(
    name="lizzy-cli",
    version="0.0.2",
    packages=find_packages(),
    install_requires=[
        "click",
        "requests",
        "gimme-aws-creds",
        "boto3",
        "python-gitlab",
        "PyChef",
        "setuptools"
    ],
    entry_points={
        "console_scripts": [
            "lizzy=lizzy.cli:lizzy",
        ],
    },
    author="Joeri Abbo",
    author_email="jabbo@schubergphilis.com",
    description="Lazzy jabbo cli, this tool is written for a lizard user :lizard smash:",
    url="https://gitlab.com/your-username/lizzy-cli",
    project_urls={
        "Source": "https://gitlab/Users/jabbo/Documents/wsus/patch.sh.com/your-username/lizzy-cli",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
