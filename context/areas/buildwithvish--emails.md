# buildwithvish/emails

Generate and store welcome email templates and metadata for MailerLite automation.

- `emails/html/email-1.html`: You&#x27;re in. Here&#x27;s where to start.
- `emails/html/email-1.txt`: Welcome email with links to start path, AI setup, brief, and website guide, asks for user goal.
- `emails/html/email-2.html`: The follow-up that fixes weak AI answers
- `emails/html/email-2.txt`: Email explaining generic answer fix line, links to 12 follow-ups, encourages real use.
- `emails/html/email-3.html`: Build one real thing this weekend
- `emails/html/email-3.txt`: Email promoting weekend website project, launch checklist, invites sharing link.
- `emails/html/emails.json`: JSON: list of 3
- `emails/make_emails.py`: Script that builds three welcome emails from source blocks into HTML and plain text for MailerLite. (uses emails.json)
- `emails/welcome-series.md`: Defines MailerLite automation triggers, email subjects, previews, and content for the Build Notes welcome series.
