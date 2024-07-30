# WhoopClient 🚀

Welcome to the WhoopClient repository! This project is designed to provide an easy way to interact with the WHOOP API, enabling effortless retrieval and processing of your health and fitness data. Whether you're a seasoned developer or just getting started, this project has everything you need to connect with your WHOOP data! 🌟

## Table of Contents 📚
- [Installation](#installation)
- [Usage](#usage)
- [Directory/File Structure](#directoryfile-structure)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## Installation ⚙️

You can install WhoopClient using pip:

```bash
pip install git+https://github.com/harperreed/whoop_client.git
```

Alternatively, you can clone the repository and install it locally:

1. Clone the repository:
    ```bash
    git clone https://github.com/harperreed/whoop_client.git
    ```
2. Navigate to the project directory:
    ```bash
    cd whoop_client
    ```
3. Install the package:
    ```bash
    pip install .
    ```

## Usage 📈

To utilize the client, you'll need to have your configuration set up.

1. Create a `config.yaml` file using `config.yaml.example` as a template.
2. Replace the placeholder values with your actual WHOOP account credentials.

After configuring, you can use the WhoopClient in your Python scripts:

```python
from whoop_client import WhoopClient
from whoop_client.utils import load_config

# Load configuration
config = load_config('path/to/your/config.yaml')

# Initialize the WhoopClient
client = WhoopClient(config)

# Use the client to interact with the WHOOP API
profile = client.get_profile()
print(f"User: {profile['first_name']} {profile['last_name']}")
```

## Directory/File Structure 📁

Here's the directory and file tree of the project:

```
whoop_client/
├── README.md
├── setup.py
├── config.yaml.example
├── example.py
├── requirements.txt
└── whoop_client/
    ├── __init__.py
    ├── auth.py
    ├── data_processing.py
    ├── data_retrieval.py
    └── utils.py
```

## Configuration ⚡

The `config.yaml` file contains your WHOOP account credentials:

```yaml
# WHOOP API Client Configuration
username: your_whoop_email@example.com
password: your_whoop_password
```

Feel free to customize this file based on your preferences! 🛠️

## Contributing 🤝

We welcome contributions! If you would like to contribute to this project, please follow these steps:

1. Fork the repository.
2. Create a new branch:
    ```bash
    git checkout -b my-feature
    ```
3. Make your changes and commit them:
    ```bash
    git commit -m "Add my feature"
    ```
4. Push to your branch:
    ```bash
    git push origin my-feature
    ```
5. Create a pull request.

## License 📜

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

Thank you for checking out WhoopClient! If you have any questions or feedback, don't hesitate to reach out. Happy coding! 💻✨
