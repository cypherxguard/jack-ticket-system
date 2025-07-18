# Jack Ticket Management System

A Flask-based web application for managing traffic tickets, users, and automated court date reminders.

---

## Features

- **User Authentication:** Login/logout, password management, admin/user roles.
- **User Management:** Admins can add, edit, and delete users.
- **Ticket Management:**
  - Add, view, and delete tickets.
  - Each ticket has a unique Ticket ID (e.g., TCKT-XXXXX).
  - Upload ticket images and attach details (court date, type, county, etc.).
- **Automated Reminders:**
  - Set up email reminders for court dates when creating a ticket.
  - Customizable: choose how many days before the court date to send the reminder.
  - Enter recipient email and SMTP credentials (Gmail supported via App Password).
  - View reminder status (Scheduled, Due Today, Overdue, Sent) and send reminders manually from the UI.
- **Notifications:**
  - Manual notification sending via the Send Notification tab (with SMTP setup).
- **Bulk Upload:** Import tickets from Excel files.
- **Export:** Export tickets or raw uploads to Excel.
- **Dashboard:** Overview of ticket stats and quick actions.

---

## Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd jack-ticket-system
   ```
2. **Create a virtual environment and install dependencies:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Run the application:**
   ```bash
   python app.py
   ```
   The app will be available at [http://localhost:9000](http://localhost:9000)

---

## Usage

### 1. **Logging In**
- Default admin user: `admin` / `admin123` (change password after first login).
- Login at `/auth/login` or via the dashboard link.

### 2. **Managing Users**
- Admins can add, edit, or delete users from the "Manage Users" tab.
- Change your password from the user menu.

### 3. **Creating Tickets**
- Go to "Add Ticket".
- Fill in ticket details (name, court date, type, etc.).
- Optionally upload a ticket image.
- **Set up a reminder:**
  - Enter how many days before the court date to send a reminder.
  - Enter the recipient email.
  - Enter SMTP credentials (Gmail: use an App Password, not your main password).

### 4. **Reminder Notifications**
- Reminders are shown in the "View Tickets" table with their status:
  - **Scheduled:** Not yet due.
  - **Due Today:** Reminder is due today.
  - **Overdue:** Reminder is past due.
  - **Sent:** Reminder has been sent.
- Click **Send Now** to send a reminder immediately (even if not yet due).
- Reminders are sent using the SMTP credentials you provided when creating the ticket.

### 5. **Viewing & Deleting Tickets**
- Go to "View Tickets" to see all tickets and their reminders.
- Delete tickets (reminders are deleted automatically).
- View ticket details, including images and notes.

### 6. **Ticket ID System**
- Every ticket gets a unique Ticket ID (e.g., TCKT-12345) for easy reference and export.

### 7. **Bulk Upload & Export**
- Upload Excel files to add multiple tickets at once.
- Export tickets or raw uploads to Excel from the "View Tickets" page.

### 8. **Manual Notifications**
- Use the "Send Notification" tab to send custom emails (set SMTP settings in the form).

---

## SMTP Setup (Gmail)
- Use an [App Password](https://support.google.com/mail/?p=BadCredentials) (not your main Gmail password).
- Enable 2-Step Verification in your Google Account.
- Enter your Gmail address and App Password in the SMTP fields when creating a ticket or sending a notification.

---

## Deployment
- The app runs on any platform supporting Python and Flask.
- For cloud deployment (e.g., Render), ensure the database is persistent and SMTP credentials are entered via the UI.

---

## Support
- For issues, open an issue on the repository or contact the maintainer.

 