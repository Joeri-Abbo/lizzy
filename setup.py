from setuptools import setup, find_packages

setup(
    name="lizzy-cli",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "click",
        "requests",
        "gimme-aws-creds",
        "boto3",
        "python-gitlab"
    ],
    entry_points={
        "console_scripts": [
            "lizzy=lizzy.cli:lizzy",
        ],
    },
    author="Joeri Abbo",
    author_email="jabbo@schubergphilis.com",
    description="A CLI tool with subcommands including update and hello world.",
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
