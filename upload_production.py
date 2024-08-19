import os

# production
os.system(r'del .\dist\*.* /f /q')
os.system(r'py -m build')
os.system(r'py -m twine upload dist/*')
os.system(r'py -m pip install --upgrade NsgOrcFx')