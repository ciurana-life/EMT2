# README

This repo is for a project that shows **the real-time locations of buses in Palma de Mallorca** (estimated). You can find it deployed here: [https://where-is-the-bus-emt.pages.dev/](https://where-is-the-bus-emt.pages.dev/)

## Requirements
**Backend**:
* [python3](https://www.python.org/downloads/)
* [poetry](https://python-poetry.org/docs/#installing-with-the-official-installer)

**Frontend**
* [nodejs](https://nodejs.org/en/download/)
* [sass](https://sass-lang.com/install/)

## Installation
You can run `poetry install` to get all the dependencies.

## Development
* live sass changes <br> `sass assets/sass/main.scss assets/css/main.css --watch --style=compressed`

## Deployment
1. Move all to compiled folder `npm run build`
2. If the routes are not there `./manage.py pre_compile_front_end_json`
3. Drop on cloduflare (will try to automate)

## Is missing
1. Tests
2. Some refactoring, specially on the front.
3. Github actions.

## Technical decisions
1. **No backend** - This was my goal from the start. It has been made possible because the official EMT (Palma bus) API does not enforce CORS, allowing our front-end to request a bearer token and fetch data directly. This might change in the future, as it is out of my control.
2. **Pre-compiled json** - Even though we can ignore CORS, I didn’t want to spam the API or make the end user’s device do unnecessary calculations. For every bus stop, I have pre-compiled all the GPS routes that go to that stop. This way, the user’s device only needs to make one request to us.
3. **Cloudflare** - Since we have no backend and all necessary data is pre-compiled, we can use Cloudflare Pages to deploy the project completely for free. This also allows web analytics without cookies, and ensures fast file serving.