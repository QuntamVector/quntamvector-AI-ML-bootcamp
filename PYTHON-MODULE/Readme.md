
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



# How to Create a Virtual Environment on Mac

## Steps

1. **Open Terminal**

2. **Navigate to your project directory** (or where you want the virtual environment to be created):
   ```bash
   cd /path/to/your/project
   ```   
3. **Create the virtual environment:**
   ```bash
   python3.12 -m venv pythonclass-py-3.12
   python3 -m venv pythonclass-py-3.12
   ``` 
4. **Activate the virtual environment:**
   ```bash
   source pythonclass-py-3.12/bin/activate
   ```    
5. **Verify Python version inside the virtual environment:**   
    ```bash
    python --version
    ```
6. **Install any necessary packages:**
   ```bash
   pip install -r requirements.txt
   ```
7. **Deactivate the virtual environment:**
    ```bash
    deactivate
    ```


# How to Install Python on Windows

## Steps

1. **Download the Python Installer:**

   - Go to the official Python website:  
     [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/)
   
   - Click on the latest Python 3.x version (for example, Python 3.12.x).

2. **Run the Installer:**

   - Open the downloaded `.exe` file.

   - **Important:** On the first installation screen, **check the box** that says:  
     `Add Python 3.x to PATH`
   
   - Click **Install Now** to proceed with default settings.

3. **Wait for Installation to Complete:**

   - The installer will install Python and pip (the package manager).

   - Once done, click **Close**.

4. **Verify Python Installation:**

   - Open **Command Prompt** (search `cmd`).

   - Type:
     ```cmd
     python --version
     ```
   
   - You should see the installed Python version, e.g., `Python 3.12.x`.

5. **Verify pip Installation:**

   - In the same Command Prompt, type:
     ```cmd
     pip --version
     ```
   
   - This confirms pip is installed and working.

---

### Optional: Install Multiple Python Versions and Manage Them

- You can install multiple versions (like 3.10, 3.12) and use tools like **py launcher** or **virtual environments** to select which version you want to run.

# How to Create a Virtual Environment on Windows

## Steps

1. **Open Command Prompt or PowerShell**

2. **Navigate to your project directory** (or where you want the virtual environment to be created):
   ```powershell
   cd C:\path\to\your\project
   ```

3. **Create the virtual environment:**
   ```powershell
      python3.12 -m venv pythonclass-py-3.12
   ```
4. **Activate the virtual environment:**

- Command Prompt
   ```powershell
   pythonclass-py-3.12\Scripts\activate.bat
   ```
- For PowerShell:
   ```powershell
   .\pythonclass-py-3.12\Scripts\Activate.ps1
   ```

5. **Verify Python version inside the virtual environment:**
   ```powershell
   python --version
   ```

6. **Install any necessary packages:**
   ```powershell
   pip install -r requirements.txt
   ```   

7. **Deactivate the virtual environment:**
   ```powershell
   deactivate
   ```