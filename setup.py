from setuptools import setup, find_packages

setup(
    name='runpod_serverless_proxy',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        # List your project's dependencies here.
        # They will be installed by pip when your project is installed.
        'fastapi[all]',
        'pydantic',
        'aiohttp',
        'requests',
        'uvicorn[standard]'
    ],
    # Add all additional information here.
)
