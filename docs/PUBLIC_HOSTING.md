# Public Hosting From Your Own PC

This project can be exposed from the same machine that is running the stack. The simplest supported path is:

1. run the Online Boutique + observability stack locally with Docker
2. run the packaged AEGIS backend and dashboard locally with Docker Compose
3. expose only the dashboard over HTTPS with ngrok
4. keep the backend private behind the dashboard's `/api` reverse proxy

## What You Need

- Docker Desktop or Docker Engine
- a Google Cloud project with a Web OAuth client
- an ngrok account
- a stable public URL if you want Google sign-in to keep working without reconfiguration

## Why A Stable ngrok Domain Matters

Google Identity Services validates the browser origin of your site. If your public URL changes every time you start ngrok, you must update the Google OAuth client's **Authorized JavaScript origins** every time too.

For a durable public demo, use:

- a reserved ngrok domain on a paid ngrok plan, or
- your own HTTPS domain pointed at a stable endpoint

## Step 1: Create The Google Web Client

In Google Cloud Console:

1. open **APIs & Services -> Credentials**
2. create an **OAuth client ID**
3. choose **Web application**
4. add your public dashboard origin to **Authorized JavaScript origins**

Examples:

- `http://localhost:8088`
- `https://your-stable-ngrok-domain.ngrok.app`

Copy the generated client ID. It looks like:

`1234567890-abc123.apps.googleusercontent.com`

## Step 2: Create Your Public Env File

Copy the example file and fill it in:

```bash
cp .env.public.example .env.public
```

Edit `.env.public` and set:

- `AEGIS_ALLOWED_ORIGINS`
- `AEGIS_API_TOKEN`
- `AEGIS_GOOGLE_CLIENT_ID`
- `AEGIS_OPERATOR_EMAILS`

## Step 3: Start The Base Runtime

Bring up the app + observability stack first:

```bash
docker compose up -d
```

This must succeed before the platform containers start because the public dashboard expects the boutique network and telemetry stack to exist.

## Step 4: Start The Public Platform Containers

Run the AEGIS backend and dashboard with the public env file:

```bash
docker compose --env-file .env.public -f docker-compose.platform.yml up -d --build
```

Expected local URLs:

- dashboard: `http://localhost:8088`
- backend health: `http://localhost:8001/health`

## Step 5: Verify Locally Before Publishing

Check:

```bash
curl -s http://localhost:8001/health
curl -s http://localhost:8001/auth/config
open http://localhost:8088
```

You should see:

- backend health JSON
- auth config JSON
- the dashboard login screen if Google OAuth is enabled

## Step 6: Expose Only The Dashboard With ngrok

Install and connect ngrok:

```bash
brew install ngrok
ngrok config add-authtoken YOUR_NGROK_AUTHTOKEN
```

Start a tunnel to the dashboard container:

```bash
ngrok http 8088
```

If you have a reserved domain, use the domain you configured in your Google client setup.

## Step 7: Update Google OAuth Origin If Needed

If ngrok gives you a different public URL than the one already registered in Google Cloud, update **Authorized JavaScript origins** to match the exact scheme and host.

## Operational Notes

- expose the dashboard, not the backend
- the dashboard proxies `/api` to the backend and injects the operator token
- if `AEGIS_OPERATOR_EMAILS` is set, only those Google accounts can trigger remediation or the demo flow
- all Google users can still sign in and view the site
- your PC must stay online for the site to remain available

## Shutdown

```bash
docker compose -f docker-compose.platform.yml down
docker compose down
```
