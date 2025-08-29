# NetamiTV-Bot-Old-Source-

This repository contains the old source code for the NetamiTV Bot, a Discord bot designed for server management, moderation, and various utility features.

## Features and Functionality

The bot provides a range of features, organized into cogs:

*   **Audit Logging:** Comprehensive logging of server events, including member actions, message changes, channel modifications, and more. Logs are stored in a SQLite database (`audit_logs.db`) and can be viewed via a web dashboard. See `cogs/audit_logger.py`.
*   **Auto Moderation:** Automatic moderation features such as banned word filtering and spam detection.  See `cogs/normal/automod.py`.
*   **Embed Handling:** Enhanced embed creation and management with rate limiting and caching for efficient bot responses. See `cogs/normal/embed_handler.py`.
*   **Protected Users:** System to protect specific users from being pinged by other members, applying timeouts to violators. See `cogs/normal/protected_users.py`.
*   **Server Protection:** Anti-nuke and raid protection features to safeguard the server from malicious attacks. See `cogs/normal/protection.py`.
*   **Response Handling:** Standardized command responses using embeds for a consistent user experience. See `cogs/normal/response_handler.py`.
*   **Review System:**  Allows users to submit images for review by admins. Approved images are then posted in a dedicated channel. See `cogs/normal/review.py`.
*   **Role Management:** Mass role assignment to all members of a Discord server. See `cogs/special/roleall.py`.
*   **Screening Role:** Automatically assigns a role to members who pass the Discord screening process. See `cogs/special/screenrole.py`.
*   **Stream Plan:**  Displays a streaming schedule for NetamiTV. See `cogs/special/streamplan.py`.
*   **Temporary Channels:**  Allows users to create temporary text and voice channels that are automatically deleted when empty. See `cogs/special/tempchannel.py` and `cogs/special/tempvoice.py`.
*   **Web Dashboard:**  A web interface for viewing audit logs and managing AutoMod settings (partially implemented - see `cogs/special/web_dashboard.py` and `web_dashboard/`).
*   **Ticket System:** A complete ticket system for user support including ticket creation panels, claiming, closing, and transcript generation. See `cogs/special/tickets.py`.
*   **Website Monitoring:** Monitors the status of a website and updates a channel name to reflect its online/offline status. See `cogs/special/website_monitor.py`.

## Technology Stack

*   [Python 3.7+](https://www.python.org/)
*   [discord.py](https://discordpy.readthedocs.io/en/stable/) - Discord API library
*   [Flask](https://flask.palletsprojects.com/en/2.0.x/) - Web framework (for dashboard)
*   [Flask-Session](https://flask-session.readthedocs.io/en/latest/) - Flask session management
*   [requests](https://requests.readthedocs.io/en/latest/) - HTTP library
*   [aiohttp](https://docs.aiohttp.org/en/stable/) - Asynchronous HTTP client/server framework
*   [sqlite3](https://docs.python.org/3/library/sqlite3.html) - SQLite database

## Prerequisites

*   Python 3.7 or higher
*   `pip` (Python package installer)

## Installation Instructions

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/MasterM142/NetamiTV-Bot-Old-Source-.git
    cd NetamiTV-Bot-Old-Source-
    ```

2.  **Install the required Python packages:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure the bot:**

    *   Edit the `main.py` file based on the `config.py.example` (if applicable for web dashboard).
    *   Set your bot token, application ID, authorized user IDs, and other necessary configuration variables in `main.py` and in the relevant cogs (e.g., `cogs/normal/review.py`, `cogs/special/web_dashboard.py`, `web_dashboard/config.py`).

4.  **Initialize the database (if necessary):**

    *   The `audit_logger.py` cog and `web_dashboard/app.py` attempts to create the `audit_logs.db` database on startup. However, you might need to create the database and tables manually if errors occur.

5.  **Web Dashboard Setup (Optional):**

    *   Navigate to the `web_dashboard/` directory.
    *   Run the `setup.py` script for initial configuration:
        ```bash
        cd web_dashboard
        python setup.py
        ```
    *   Start the Flask server using `start_dashboard.py`:
        ```bash
        python start_dashboard.py
        ```
    *   Access the dashboard in your browser at `http://neko.wisp.uno:12902` (or the configured host and port).

## Usage Guide

1.  **Run the bot:**

    ```bash
    python main.py
    ```

2.  **Interact with the bot** on your Discord server using the defined commands. Note: some commands might require administrator or other specific permissions.

## API Documentation

This project doesn't have a formal API. However, it utilizes the Discord API through the `discord.py` library.  Refer to the [discord.py documentation](https://discordpy.readthedocs.io/en/stable/) for details on interacting with the Discord API.

The `/api/logs` endpoint in `cogs/special/web_dashboard.py` (and `web_dashboard/app.py`) provides a simple API for fetching audit logs.

*   **Endpoint:** `/api/logs`
*   **Method:** GET
*   **Parameters:**
    *   `page`: Page number (default: 1)
    *   `per_page`: Number of logs per page (default: 25)
    *   `action_type`: Filter by action type
    *   `severity`: Filter by log severity
    *   `user_search`: Search for logs related to a specific user (by username or ID)
    *   `category`: Filter by log category (`bot`, `moderation`, `server`, `all`)
*   **Response:** JSON object containing:
    *   `logs`: A list of log entries (dictionaries)
    *   `total`: Total number of log entries matching the criteria
    *   `page`: Current page number
    *   `per_page`: Number of logs per page
    *   `total_pages`: Total number of pages

## Contributing Guidelines

Contributions are welcome! To contribute:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Implement your changes, ensuring code quality and proper testing.
4.  Submit a pull request with a clear description of your changes.

## License Information

No license information is provided. The code is currently provided "as-is" without warranty.  The original repository lacks a license file.

## Contact/Support Information

For questions, support, or to report issues, please contact the repository owner through GitHub.  No other contact information is available.