# Requirements Document

## Introduction

Ushbu tizim Telegram platformasida yopiq guruhlar va kanallar uchun Payme to'lov tizimi orqali obuna boshqaruvini avtomatlashtiradi. Tizim ikki asosiy komponentdan iborat: foydalanuvchilar bilan muloqot qiluvchi Telegram bot va administratorlar uchun web-panel. Foydalanuvchi obunani to'lab, bir martalik taklif havola orqali yopiq guruh/kanalga qo'shiladi; obuna muddati tugaganda esa avtomatik ravishda chiqarib yuboriladi.

---

## Glossary

- **Bot**: Aiogram 3.x asosida ishlaydigan Telegram bot — foydalanuvchi bilan to'g'ridan-to'g'ri muloqot qiladi.
- **Admin_Panel**: Django asosida qurilgan web interfeys — administrator tomonidan boshqariladi.
- **Payme_API**: O'zbekiston to'lov tizimi Payme'ning merchant integratsiya API'si.
- **Webhook_Handler**: Payme serveridan kelgan callback so'rovlarini qabul qiluvchi va tekshiruvchi Django view.
- **Subscription_Manager**: Obuna yaratish, uzaytirish, bekor qilish va muddatini tekshirish mantiqini boshqaruvchi servis moduli.
- **Notification_Service**: Celery task orqali eslatma xabarlarini yuboruvchi servis.
- **Invite_Link_Service**: Telegram API orqali bir martalik, muddatli taklif havolasini yaratuvchi servis.
- **Scheduler**: Celery Beat asosida ishlaydigan vaqt jadvaliga ko'ra vazifalar bajaraguchi komponent.
- **Channel**: Telegram kanali yoki yopiq guruh — obuna sotib olinadigan platforma.
- **Tariff**: Obuna muddati va narxini belgilovchi konfiguratsiya yozuvi.
- **Transaction**: Payme to'lov operatsiyasining ma'lumotlar bazasidagi yozuvi.
- **Subscriber**: Faol obunasi mavjud Telegram foydalanuvchisi.
- **Admin**: Web-panelga kirish huquqiga ega tizim boshqaruvchisi.
- **Invite_Link**: Telegram tomonidan yaratilgan, bir martalik va vaqtinchalik guruh/kanal taklif havolasi.

---

## Requirements

### Requirement 1: Foydalanuvchini ro'yxatga olish

**User Story:** As a Telegram user, I want to register via /start command, so that the system can identify me and offer subscription plans.

#### Acceptance Criteria

1. WHEN a user sends `/start` to the Bot, THE Bot SHALL save the user's Telegram ID, first name, last name, and username to the database if the record does not already exist.
2. WHEN a user sends `/start` and the record already exists, THE Bot SHALL update the user's first name, last name, and username fields with the latest values from Telegram.
3. WHEN a user sends `/start`, THE Bot SHALL display a welcome message together with the main menu containing available Channels and subscription options; if either the welcome message or the menu fails to send, THE Bot SHALL not display either component and SHALL log the failure.
4. IF the Telegram API returns an error during user data retrieval, THEN THE Bot SHALL log the error and respond to the user with a generic error message in Uzbek.

---

### Requirement 2: Kanal va tarif tanlash

**User Story:** As a registered user, I want to browse available channels and subscription tariffs, so that I can choose the plan that suits me.

#### Acceptance Criteria

1. WHEN a user opens the subscription menu, THE Bot SHALL display all active Channels retrieved from the database.
2. WHEN a user selects a Channel, THE Bot SHALL display all active Tariffs for that Channel, each showing the duration in days and the price in UZS.
3. WHEN a user views the Channel list and the user has an active Subscription for a Channel with a future `end_date`, THE Bot SHALL display the remaining days until expiry next to that Channel's name; expired or cancelled Subscriptions SHALL not affect this display.
4. IF no active Tariffs exist for a selected Channel, THEN THE Bot SHALL notify the user that no plans are currently available for that Channel.

---

### Requirement 3: Payme orqali to'lov cheki yaratish

**User Story:** As a user, I want to receive a Payme payment link after selecting a tariff, so that I can complete the payment securely.

#### Acceptance Criteria

1. WHEN a user selects a Tariff, THE Bot SHALL call the Payme_API `CreateTransaction` method to generate a payment invoice with the exact Tariff price in tiyin (1 UZS = 100 tiyin).
2. WHEN the Payme_API returns a successful invoice, THE Bot SHALL send the payment URL to the user as an inline button with a 30-minute expiry warning.
3. WHEN the Payme_API returns a successful invoice, THE Subscription_Manager SHALL create a Transaction record in the database with status `pending`.
4. IF the Payme_API returns an error during invoice creation, THEN THE Bot SHALL notify the user that the payment link could not be generated and prompt the user to try again.
5. THE Bot SHALL not create duplicate pending Transaction records for the same user and Tariff if an unexpired pending transaction already exists.

---

### Requirement 4: Payme Webhook orqali to'lovni tasdiqlash

**User Story:** As the system, I want to process Payme webhook callbacks securely, so that subscriptions are activated only after verified payments.

#### Acceptance Criteria

1. WHEN the Webhook_Handler receives a request, THE Webhook_Handler SHALL verify that the request originates from an authorised Payme IP address before processing.
2. WHEN the Webhook_Handler receives a request, THE Webhook_Handler SHALL validate the `Authorization` header against the configured Payme merchant secret key using Basic Auth encoding.
3. IF the request IP address is not in the authorised Payme IP list, THEN THE Webhook_Handler SHALL return HTTP 200 with a JSON-RPC error code `-32504` (Insufficient privilege).
4. IF the `Authorization` header is invalid, THEN THE Webhook_Handler SHALL return HTTP 200 with a JSON-RPC error code `-32504`.
5. WHEN the Webhook_Handler receives a `CheckPerformTransaction` call, THE Webhook_Handler SHALL verify that the `order_id` references an existing pending Transaction and return `allow: true` or the appropriate error code.
6. WHEN the Webhook_Handler receives a `CreateTransaction` call, THE Webhook_Handler SHALL record the `transaction_id` from Payme against the matching Transaction record and return the transaction state.
7. WHEN the Webhook_Handler receives a `PerformTransaction` call, THE Webhook_Handler SHALL update the Transaction status to `paid` and trigger subscription activation via the Subscription_Manager.
8. WHEN the Webhook_Handler receives a `CancelTransaction` call, THE Webhook_Handler SHALL update the Transaction status to `cancelled` and, if the Subscription linked to that Transaction has status `active` (i.e., the Transaction was previously in `paid` status), THE Webhook_Handler SHALL mark that Subscription as `cancelled`.
9. WHEN the Webhook_Handler receives a `CheckTransaction` call, THE Webhook_Handler SHALL return the current state and timestamps of the matching Transaction.
10. THE Webhook_Handler SHALL respond to every Payme method call within 10 seconds to prevent Payme timeout errors.

---

### Requirement 5: Obunani faollashtirish va Invite Link yuborish

**User Story:** As a paying user, I want to receive a one-time invite link immediately after payment confirmation, so that I can join the private channel or group.

#### Acceptance Criteria

1. WHEN the Subscription_Manager is triggered after a successful `PerformTransaction`, THE Subscription_Manager SHALL create a Subscription record in the database with `start_date` set to the current UTC time and `end_date` set to `start_date` plus the Tariff duration in days.
2. WHEN a Subscription record is created, THE Invite_Link_Service SHALL call the Telegram Bot API `createChatInviteLink` method to generate an Invite_Link that expires in 24 hours and allows a single join.
3. WHEN the Invite_Link_Service successfully generates an Invite_Link, THE Bot SHALL attempt to send the Invite_Link to the user via a private message within 15 seconds of payment confirmation; if the Bot API returns an error preventing message delivery, THE Subscription_Manager SHALL log the failure and mark the delivery status as `failed` without reversing the payment.
4. IF the Telegram Bot API returns an error during Invite_Link creation, THEN THE Subscription_Manager SHALL retry the operation up to 3 times with a 5-second interval before logging the failure and alerting the Admin.
5. IF the user is already a member of the Channel at the time of subscription activation, THEN THE Subscription_Manager SHALL record the subscription without sending an Invite_Link and notify the user that the subscription has been extended.

---

### Requirement 6: Obuna muddati eslatmalari

**User Story:** As a subscriber, I want to receive timely reminders before my subscription expires, so that I can renew it without losing access.

#### Acceptance Criteria

1. WHEN a Subscription's `end_date` is exactly 3 days away (within a 5-minute scheduling window), THE Notification_Service SHALL send the Subscriber a reminder message via the Bot stating the exact expiry date and a renewal button.
2. WHEN a Subscription's `end_date` is exactly 1 day away (within a 5-minute scheduling window), THE Notification_Service SHALL send the Subscriber a reminder message via the Bot stating the exact expiry date and a renewal button.
3. WHEN a Subscription's `end_date` is exactly 1 hour away (within a 5-minute scheduling window), THE Notification_Service SHALL send the Subscriber a final reminder message via the Bot.
4. THE Scheduler SHALL run the expiry check task every 5 minutes.
5. IF a reminder has already been sent for any interval (3 days, 1 day, or 1 hour) for a given Subscription, THEN THE Notification_Service SHALL not send any further reminders for that Subscription, regardless of which interval triggered first.

---

### Requirement 7: Muddati tugagan foydalanuvchini kanaldan chiqarish

**User Story:** As the system, I want to automatically remove expired subscribers from channels, so that only paying members have access.

#### Acceptance Criteria

1. WHEN a Subscription's `end_date` is reached (within a 5-minute scheduling window), THE Subscription_Manager SHALL mark the Subscription status as `expired`.
2. WHEN a Subscription is marked as `expired`, THE Bot SHALL call the Telegram Bot API `banChatMember` method for the corresponding Channel and Telegram user ID.
3. WHEN the `banChatMember` call succeeds, THE Bot SHALL immediately call `unbanChatMember` to allow the user to rejoin in the future; if the `unbanChatMember` call fails, THE Bot SHALL leave the user banned and log the failure for Admin review.
4. IF the Telegram Bot API returns an error during `banChatMember`, THEN THE Subscription_Manager SHALL retry the operation up to 3 times with a 10-second interval only when each attempt fails, and SHALL log a failure alert for Admin review after all retries are exhausted.
5. WHEN a Subscription is marked as `expired`, THE Bot SHALL send the Subscriber a notification that their subscription has ended, including a renewal button.

---

### Requirement 8: Foydalanuvchi profil menyusi

**User Story:** As a subscriber, I want to view my active subscriptions, expiry dates, and payment history, so that I can manage my account.

#### Acceptance Criteria

1. WHEN a user opens the profile menu, THE Bot SHALL display all active Subscriptions belonging to the user, each showing the Channel name and the remaining days until expiry.
2. WHEN a user requests payment history, THE Bot SHALL display the 20 most recent Transaction records for the user, each showing the date, Channel name, Tariff duration, amount in UZS, and status, including transactions with zero amounts or failed statuses.
3. WHEN a user selects an active Subscription in the profile menu, THE Bot SHALL provide a renewal button that initiates the payment flow for the same Channel and Tariff.

---

### Requirement 9: Web Admin Panel — Dashboard

**User Story:** As an Admin, I want to see key business metrics on a dashboard, so that I can monitor the system's health and revenue at a glance.

#### Acceptance Criteria

1. WHEN an Admin opens the dashboard, THE Admin_Panel SHALL display the total count of active Subscribers.
2. WHEN an Admin opens the dashboard, THE Admin_Panel SHALL display the total revenue for the current calendar month in UZS, calculated from `paid` Transactions.
3. WHEN an Admin opens the dashboard, THE Admin_Panel SHALL display the count of Subscriptions expiring within the next 7 days.
4. WHEN an Admin opens the dashboard, THE Admin_Panel SHALL display the count of `pending` Transactions older than 30 minutes.
5. THE Admin_Panel SHALL refresh dashboard data without requiring a full page reload at an interval configurable by the Admin (default: 60 seconds).

---

### Requirement 10: Web Admin Panel — Kanal va Tarif boshqaruvi

**User Story:** As an Admin, I want to manage channels and tariffs through the web panel, so that I can configure the system without touching the codebase.

#### Acceptance Criteria

1. WHEN an Admin adds a Channel, THE Admin_Panel SHALL verify via the Telegram Bot API that the Bot has administrator rights in the specified Channel before saving the record; if the API call fails due to network issues or Telegram API downtime, THE Admin_Panel SHALL treat the failure as missing admin rights, display an error message, and not save the Channel record.
2. IF the Bot does not have administrator rights in the Channel, THEN THE Admin_Panel SHALL display an error message and not save the Channel record.
3. WHEN an Admin creates a Tariff, THE Admin_Panel SHALL require a name, duration in days (minimum 1), and price in UZS (minimum 100 UZS) before saving.
4. WHEN an Admin deactivates a Tariff, THE Admin_Panel SHALL mark the Tariff as inactive so that it no longer appears in the Bot's menu, without deleting existing Subscription records linked to it.
5. WHEN an Admin deactivates a Channel, THE Admin_Panel SHALL mark all associated active Tariffs as inactive and prevent new Subscriptions from being created for that Channel.

---

### Requirement 11: Web Admin Panel — Foydalanuvchilar boshqaruvi

**User Story:** As an Admin, I want to manually manage subscriber records, so that I can handle edge cases like failed payments or customer support requests.

#### Acceptance Criteria

1. WHEN an Admin searches for a user by Telegram ID or username, THE Admin_Panel SHALL return matching user records within 2 seconds.
2. WHEN an Admin manually extends a Subscription, THE Admin_Panel SHALL add the specified number of days (minimum 0) to the current `end_date` and log the action with the Admin's ID, timestamp, and reason.
3. WHEN an Admin manually cancels a Subscription via the Admin_Panel, THE Admin_Panel SHALL mark the Subscription as `cancelled`, trigger the Telegram channel removal flow, and log the action; automated cancellation processes and failed payment cancellations SHALL not trigger Telegram channel removal.
4. THE Admin_Panel SHALL display the full Transaction history for a selected user, including Payme `transaction_id`, amount, status, and timestamps.

---

### Requirement 12: Web Admin Panel — Moliyaviy tranzaksiyalar

**User Story:** As an Admin, I want to view and filter transaction records, so that I can reconcile payments and investigate issues.

#### Acceptance Criteria

1. WHEN an Admin opens the transactions list, THE Admin_Panel SHALL display transactions filterable by status (`paid`, `pending`, `cancelled`), date range, and Channel.
2. THE Admin_Panel SHALL display for each Transaction: the user's Telegram ID and username, Channel name, Tariff name, amount in UZS, Payme `transaction_id`, and timestamps for creation and completion.
3. WHEN an Admin exports transactions, THE Admin_Panel SHALL generate a CSV file containing all filtered Transaction records within 10 seconds.

---

### Requirement 13: Web Admin Panel — Broadcast xabarnoma

**User Story:** As an Admin, I want to send broadcast messages to all or filtered subscribers, so that I can communicate promotions or system updates.

#### Acceptance Criteria

1. WHEN an Admin composes a broadcast, THE Admin_Panel SHALL allow input of a text message (up to 4096 characters) and an optional image attachment.
2. WHEN an Admin sends a broadcast, THE Admin_Panel SHALL allow targeting: all registered users, active Subscribers of a specific Channel, or Subscribers whose Subscription expires within a specified number of days.
3. WHEN an Admin confirms a broadcast, THE Notification_Service SHALL enqueue individual messages via Celery and send them at a hard limit of no more than 30 messages per second to comply with Telegram Bot API rate limits; if the sending rate would exceed 30 messages per second, THE Notification_Service SHALL delay subsequent messages to the next second rather than rejecting them.
4. WHEN a broadcast is in progress, THE Admin_Panel SHALL display the total count of recipients, sent count, and failed count in real time.
5. IF sending a message to an individual user fails due to the user blocking the Bot, THEN THE Notification_Service SHALL mark that user's broadcast delivery as `failed` and continue sending to remaining recipients.

---

### Requirement 14: Xavfsizlik va autentifikatsiya

**User Story:** As a system operator, I want the admin panel and webhook endpoint to be protected, so that unauthorised access is prevented.

#### Acceptance Criteria

1. THE Admin_Panel SHALL require authentication using a session-based login with username and password before granting access to any admin page.
2. WHEN an unauthenticated user attempts to access an Admin_Panel page, THE Admin_Panel SHALL redirect the user to the login page.
3. THE Webhook_Handler SHALL only accept requests from IP addresses listed in the official Payme server IP whitelist, which SHALL be configurable via an environment variable.
4. THE Admin_Panel SHALL enforce HTTPS for all connections; HTTP requests SHALL be redirected to HTTPS by Nginx.
5. IF an Admin fails to log in 5 consecutive times within 15 minutes, THEN THE Admin_Panel SHALL lock that account for 15 minutes and log the event.
6. THE Bot SHALL store all secrets (Payme merchant key, Bot token, database credentials) exclusively in environment variables and never in source code or version control.

---

### Requirement 15: Tizim ishonchliligi va monitoring

**User Story:** As a system operator, I want the system to handle failures gracefully and be observable, so that issues can be detected and resolved quickly.

#### Acceptance Criteria

1. WHEN a Celery task fails, THE Scheduler SHALL retry the task according to the configured retry policy (maximum 3 retries with exponential backoff starting at 60 seconds).
2. WHEN any unhandled exception occurs in the Bot or Admin_Panel, THE system SHALL log the full stack trace to the configured logging backend (file or external service).
3. THE system SHALL expose a `/health` endpoint that returns HTTP 200 when the database, Redis, and Bot API connections are all healthy, and HTTP 503 with a descriptive JSON body when any dependency is unavailable.
4. WHILE the Redis connection is unavailable, THE Subscription_Manager SHALL fall back to direct database queries and log a warning without interrupting active user flows; if the database fallback itself fails to initialise, THE system SHALL continue operating with degraded functionality and log the failure.
5. THE system SHALL be deployable via Docker Compose with a single `docker-compose up` command on Ubuntu 22.04, including all services (Django, Celery, Redis, PostgreSQL, Nginx).
