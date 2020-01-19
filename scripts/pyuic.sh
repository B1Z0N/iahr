for path in crud/ui/*.ui; do
  pyuic5 $path -o "${path%.ui}.py"
done
