"""{{cookiecutter.description}}"""

from {{ cookiecutter.project_slug }}.server import server

__version__ = "0.1.0"
__author__ = "{{cookiecutter.author_name}}"
__email__ = "{{cookiecutter.author_email}}"

__all__ = ["server"]