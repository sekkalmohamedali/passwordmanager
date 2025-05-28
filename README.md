# Password Manager Application

A secure and user-friendly password management solution built with PyQt6, implementing multiple design patterns for robust architecture and security.

## Features

- 🔐 Secure password storage with encryption (Fernet/AES-256)
- 🎯 Password strength checking
- 🔄 Password generation with customizable options
- 🔍 Search and filter capabilities
- 📋 Import/Export functionality (CSV, JSON, XML)
- 💾 Automatic backup system
- 👥 Multiple encryption strategies
- 📊 Password strength visualization
- 🔄 Duplicate password detection

## Design Patterns Implemented

1. **Strategy Pattern**
   - Interchangeable encryption algorithms (Fernet/AES)
   - Flexible password validation strategies

2. **Observer Pattern**
   - Real-time UI updates on database changes
   - Password strength monitoring

3. **Proxy Pattern**
   - Controlled access to sensitive operations
   - Access logging for security

4. **Memento Pattern**
   - Password entry state management
   - Backup and restore functionality

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/password-manager.git
cd password-manager
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

## Usage Guide

### First Time Setup

1. Launch the application
2. Create a master password when prompted
3. This password will be required for future access

### Managing Passwords

#### Adding New Entries
- Click the "+" button or use File > New Entry
- Enter website URL, username, and password
- Use the password generator if needed
- Click Save

#### Viewing/Editing Entries
- Click the "View" icon to see password
- Click "Edit" to modify entries
- Double-click to copy password to clipboard

#### Password Generation
1. Click "Generate Password" button
2. Configure options:
   - Password length (12-75 characters)
   - Include capitals
   - Include numbers
   - Include special characters
3. Click "Generate"

### Security Features

#### Encryption
- Choose between Fernet and AES-256 encryption
- Change encryption strategy in Settings > Encryption Settings
- All passwords are encrypted before storage

#### Backups
- Regular automatic backups
- Manual backup: File > Backup Database
- Restore: File > Restore Database

#### Password Strength
- Real-time strength checking
- Color-coded indicators
- Detailed feedback on password quality

## Development

### Requirements
- Python 3.8+
- PyQt6
- cryptography
- SQLite3

### Project Structure
```
passwordmanager/
├── app/
│   ├── ui/            # User interface components
│   └── utils/         # Utility classes and functions
├── tests/             # Unit tests
└── main.py           # Application entry point
```

## Security Considerations

- Master password is never stored directly
- All passwords are encrypted at rest
- Access logging for security monitoring
- Regular security updates recommended

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request


