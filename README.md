# Bitaxe Notifier

A Python-based monitoring and notification system for Bitaxes. This tool periodically checks the status of your Bitaxes and sends email notifications for important events.

## Features

- **Multi-Bitaxe Support**: Monitor multiple Bitaxes simultaneously
- **Email Notifications**: Get alerts for:
  - Overheating
  - New all-time best difficulty achievements
  - New session best difficulty achievements
- **Configurable Settings**: Customize polling interval and notification preferences
- **Logging**: Comprehensive logging to both console and file

## Requirements

- Python 3.6+
- A Gmail account (for sending notifications)
- One or more Bitaxes on your network

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/steven-s-martins/bitaxe-notifier.git
   cd bitaxe-notifier
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create your configuration file:
   ```bash
   cp .env.example .env
   ```

4. Edit the `.env` file with your specific settings:
   - Add the IPs and names of your Bitaxes
   - Configure your Gmail credentials
   - Adjust notification preferences as needed

## Gmail App Password Setup

To send email notifications, you'll need to create an App Password for your Gmail account:

1. First, enable 2-Step Verification on your Google account:
   - Go to your Google Account settings
   - Navigate to Security > [2-Step Verification](https://myaccount.google.com/signinoptions/twosv)
   - Add and set up a 2-Step Verification method (like SMS, authenticator app, etc.)
   - Click "Turn on 2-Step Verification"

2. Once 2-Step Verification is enabled, create an App Password:
   - Search for the [App passwords](https://myaccount.google.com/apppasswords) page
   - Enter a name like "Bitaxe Notifier"
   - Click "Create"
   - Copy the 16-character password that appears

3. Use this generated password in your `.env` file as the `GMAIL_APP_PASSWORD` value

Note: App passwords are only available if you've enabled 2-Step Verification on your Google account.

## Usage

Run Bitaxe Notifier:

```bash
python bitaxe-notifier.py
```

The program will:
1. Check your configuration
2. Connect to your Bitaxes
3. Begin monitoring according to your settings
4. Send email notifications when specified events occur

To run in the background or as a service, consider using tools like `systemd`, `supervisor`, or `screen`.

## Configuration Options

| Setting | Description | Default |
|---------|-------------|---------|
| `BITAXE_X_IP` | IP address of your Bitaxe | Required |
| `BITAXE_X_NAME` | Custom name for your Bitaxe | "Bitaxe X" |
| `GMAIL_USER` | Your Gmail address | Required |
| `GMAIL_APP_PASSWORD` | Your Gmail app password | Required |
| `RECIPIENT` | Email address to receive notifications | Required |
| `POLLING_INTERVAL_SECONDS` | How often to check Bitaxes (in seconds) | 60 |
| `NOTIFY_ON_OVERHEAT` | Send notifications when overheat mode is activated | true |
| `NOTIFY_ON_NEW_BEST_DIFFICULTY` | Send notifications for all-time best difficulties | true |
| `NOTIFY_ON_NEW_BEST_SESSION_DIFFICULTY` | Send notifications for session best difficulties | true |

## Logging

Logs are written to both the console and `bitaxe-notifier.log` in the application directory.

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
