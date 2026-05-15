
```
https://www.python.org/downloads/
```


```
https://code.visualstudio.com/download
```

```
#!/bin/bash

CURRENT_DIR=$(basename "$PWD")

echo "Creating virtual environment: $CURRENT_DIR"

python3 -m venv "$CURRENT_DIR"

source "$CURRENT_DIR/bin/activate"

echo "Virtual environment activated ✅"
```