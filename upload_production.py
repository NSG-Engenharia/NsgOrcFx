import os

# production
# first, update the version (increse number) in the `pyproject.toml` file
os.system(r'del .\dist\*.* /f /q')
os.system(r'py -m build')
os.system(r'py -m twine upload dist/*')
os.system(r'py -m pip install --upgrade NsgOrcFx')