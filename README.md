# passwordmanager
password mg
# PyQt6 Password Manager

This project is a password manager application built using PyQt6, offering a graphical user interface for securely storing and managing passwords.

## Features
- User authentication (login and signup)
- Secure password storage using encryption
- Add new passwords
- Edit existing passwords
- View stored passwords
- Password generation with customizable options
- Master password modification
- Export password database to CSV
- Intuitive and responsive user interface


## Installation

1. Clone the repository:

  ``git clone https://github.com/ZoidEee/pyqt-password-manager.git``

2. Navigate to the project directory:

``cd pyqt-password-manager``

3. Install the required packages:

``pip install -r requirements.txt``


## Usage

Run the main script to start the application:


``python main.py``

### Creating a Master Password
If this is your first time running the application, you will be prompted to create a master password.
Choose a strong and memorable password, as this will be required to access your stored passwords in future sessions.
### Logging In
- For subsequent launches, you will need to enter your master password to access the main interface.
- If you forget your master password, there is no way to recover it, so make sure to remember it!
### Using the Main Interface
Once logged in, you can:
- **Add New Passwords**: Click on the "Add" button to input new credentials.
- **Edit Existing Passwords**: Select a stored password and click "Edit" to modify its details.
- **View Stored Passwords**: Browse through your saved passwords in a secure table format.
- **Generate Strong Passwords**: Use the built-in password generator for creating secure passwords.
- **Modify Master Password**: Access the settings to change your master password if needed.
- **Export Database**: Export your password database to a CSV file.
### Exiting the Application
When you're done, simply close the application window. Your data will be securely stored and encrypted until your next login.
### Important Notes
- Always ensure that your master password is kept confidential.
- Regularly update your passwords for enhanced security.
### Contributing
Contributions are welcome! Please feel free to submit a Pull Request.
### License
This project is open source and available under the MIT License.
### Acknowledgements
- PyQt6 for the GUI framework.
- cryptography for secure encryption.
### Support
For support, please open an issue in the GitHub repository.
#### to restart
del password.db
reg delete HKCU\Software\PyQtPasswordManager /f