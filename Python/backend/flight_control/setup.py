"""Flugsteuerungs-Setup.

Dieses Modul enthält die Setup-Konfiguration für das Flugsteuerungs-Paket.
"""

from setuptools import setup, find_packages

setup(
    name="flight_control",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "PySide6>=6.0.0",
        "numpy>=1.20.0",
        "scipy>=1.7.0"
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.0.0",
            "pytest-qt>=4.0.0"
        ]
    },
    python_requires=">=3.8",
    author="RZGCS Team",
    author_email="rzgcs@example.com",
    description="Flugsteuerungskomponenten für RZGCS",
    keywords="flight control, uav, drone",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ]
) 