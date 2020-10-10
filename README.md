# isolation-web
A visualized network of human connections.

## Setup

1. Ensure Python3, Django, and Pipenv are installed
2. Set up a `.env` file with `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
3. Run `pipenv install`
4. If you are pointed at a local Postgres database, run `pipenv run superuser`
5. Run `pipenv run migrate`
6. Run `pipenv run start`
