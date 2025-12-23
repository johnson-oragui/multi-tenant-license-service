echo "Runing Pylint recursive..."
pylint --recursive=y .
echo "Pylint recursive ended"
echo

echo "Running black (local formatting)..."
black .
echo "black formatting finished"
echo

echo "Running isort..."
isort .
echo "isort formatting finished"
echo

echo "Running CI-style checks (non-modifying)..."
black --check .
isort --check .
echo "CI-style checks finished"