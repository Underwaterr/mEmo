# mEmo

Finally, a self-hosted solution for people managing their emo cover bands. 

- *Event Scheduling* - keep track of gigs, rehearsals and more
- *Poll for Availability* - poll bandmates to collect availability and comments on potential dates

What's next? Push notifications with [ntfy](https://ntfy.sh/).
Future goals include tracking venues, tasks and finances.


## The Stack
- Python + Django REST Framework
- PostgreSQL
- Testing with pytest
- Deployed with Gunicorn, Caddy and Docker


## Setup

```
# Install Python
pyenv install 3.14.3

# Set up the local environment
pyenv local 3.14.3
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Set environment variables
cp .env.example .env

# Set up the database
[sudo] docker compose up -d
python manage.py migrate

# Create the first user
python manage.py createsuperuser
```
You can run the app with the `./start` script.


## API endpoints

Most endpoints are only available to the admin user and are marked as such.
 
### Authentication
 
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login/` | Log in with username and password |
| POST | `/api/auth/logout/` | End session |
| GET | `/api/auth/check/` | Get current user info and CSRF token |
 
### Events
 
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/events/` | List all events |
| POST | `/api/events/` | Create event (admin) |
| GET | `/api/events/<id>/` | Retrieve event |
| PATCH | `/api/events/<id>/` | Update event (admin) |
| DELETE | `/api/events/<id>/` | Delete event (admin) |
 
### Polls
 
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/polls/` | List all polls |
| POST | `/api/polls/` | Create poll (admin) |
| GET | `/api/polls/<id>/` | Retrieve poll |
| PATCH | `/api/polls/<id>/` | Update poll (admin) |
| DELETE | `/api/polls/<id>/` | Delete poll (admin) |
 
### Poll date options
 
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/polls/<poll_id>/date-options/` | List date options |
| POST | `/api/polls/<poll_id>/date-options/` | Add date option (admin) |
| PATCH | `/api/polls/<poll_id>/date-options/<id>/` | Update date option (admin) |
| DELETE | `/api/polls/<poll_id>/date-options/<id>/` | Delete date option (admin) |
 
### Poll invitations
 
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/polls/<poll_id>/invitations/` | List invitations |
| POST | `/api/polls/<poll_id>/invitations/` | Invite user (admin) |
| DELETE | `/api/polls/<poll_id>/invitations/<id>/` | Remove invitation (admin) |
 
### Poll responses
 
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/polls/<poll_id>/responses/` | List responses |
| POST | `/api/polls/<poll_id>/responses/` | Submit response (any member) |
| PATCH | `/api/polls/<poll_id>/responses/<id>/` | Update own response |
| DELETE | `/api/polls/<poll_id>/responses/<id>/` | Delete own response |



## License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0).
