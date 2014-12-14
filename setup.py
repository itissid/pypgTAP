from setuptools import setup, find_packages

setup(
    name = "rsTAP",
    version = "0.1-DEV",
    author = "Sid",
    author_email = "itissid@gmail.com",
    packages = find_packages(),
    entry_points = {
        'console_scripts':[
            'start_harness = \
                rstap.core.test_kit.postgres_env:start_postgres_harness',
            'stop_harness = \
                rstap.core.test_kit.postgres_env:stop_postgres_harness'
        ]
    },
    package_data = {
        "": ["*.yml"],
        "rstap.core.workflow": ["*.sql"]
    },
    install_requires = open("requirements.txt").read(),
    description = "A project that brings python closer to pgTAP",
    long_description = "\n" + open("README.md").read(),
)
