# Maintenance

## Publishing to pypi

```sh
pip3 install setuptools wheel twine keyring with_op --upgrade
new_version=$(./setup.py --version)
git tag -a "v${new_version:?}" -m "release ${new_version:?}"
git push origin --tags
python3 setup.py sdist bdist_wheel
TWINE_USERNAME=$(with-op op get item PyPI | jq -r '.details.fields | map(select(.designation == "username"))[0].value')
export TWINE_USERNAME
TWINE_PASSWORD=$(with-op op get item PyPI | jq -r '.details.fields | map(select(.designation == "password"))[0].value')
export TWINE_PASSWORD
twine upload dist/*
TWINE_PASSWORD=
```
