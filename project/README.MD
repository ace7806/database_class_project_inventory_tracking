## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3 and pip
- PostgreSQL

### Installing PostgreSQL

- **macOS:** You can install PostgreSQL using [Homebrew](https://brew.sh/):

  ```bash
  brew install postgresql

- **linux:** you can install postgresSQL using the command line: 
    ```bash
    sudo apt update
    sudo apt install postgresql postgresql-contrib
    ```

- **windows:** Windows: Download and install PostgreSQL from the [official website](https://www.postgresql.org/download/windows/). Make sure to note the installation directory and password for the 'postgres' user.


## Setting up Python
**Create and activate a virtual environment (optional but recommended)**

- For macOS/Linux:

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

- For Windows:

    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

**Install the requirements**

```bash
pip install -r requirements.txt
```

## Running the Project

Once the dependencies are installed, you can run the project using:

```bash
flask run