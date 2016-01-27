import setuptools

setuptools.setup(
        name = "varscan-tool",
        author = "Stuti Agrawal",
        author_email = "stutia@uchicago.edu",
        version = 0.1,
        description = "variant calling tools",
        url = "https://github.com/NCI-GDC/varscan-tool",
        license = "Apache 2.0",
        packages = setuptools.find_packages(),
        install_requires = [
            'SQLAlchemy',
            'psycopg2'
            ],
        classifiers = [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: Apache Software License",
            "Programming Language :: Python",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            ],
    )

