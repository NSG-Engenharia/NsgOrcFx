import os

# production
os.system(r'del .\dist\*.* /f /q')
os.system(r'py -m build')
os.system(r'py -m twine upload dist/*')
os.system(r'py -m pip install --upgrade NsgOrcFx')


# testing
# Testing
# * Upload:
# ```
# py -m build
# py -m twine upload --repository testpypi dist/*
# ```

# * Install the package (test):
# ```
# py -m pip install --index-url https://test.pypi.org/simple --no-deps NsgOrcFx_nsgeng
# ```
# If already installed:
# ```
# py -m pip uninstall NsgOrcFx_nsgeng
# py -m pip install --upgrade --index-url https://test.pypi.org/simple --no-deps NsgOrcFx_nsgeng
# ```
