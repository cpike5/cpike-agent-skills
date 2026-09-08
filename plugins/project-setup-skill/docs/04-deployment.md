# Deployment (VPS)

A single Linux box running Docker Compose behind nginx. The VPS builds nothing:
it pulls a published image, reads a `.env`, and restarts. Everything that
decides *what the code is* happened in CI.

## Layout

```
/opt/<appname>/
  docker-compose.yml        # the prod stack, pulling ghcr.io/<owner>/<appname>
  .env                      # configuration + secrets, root:root 0600
/usr/local/bin/deploy-<appname>.sh
/etc/nginx/sites-available/<appname>.example.com
```

One directory per app, one deploy script per app, one nginx site per app. Two
apps on the same box do not share a compose file, a network, or a database
container — they differ only in `<appname>` and their host port.

Templates: `${CLAUDE_PLUGIN_ROOT}/assets/deploy/`.

## First-time setup

```bash
sudo mkdir -p /opt/<appname>
sudo cp docker-compose.prod.yml /opt/<appname>/docker-compose.yml
sudo cp env.example /opt/<appname>/.env
sudo chown root:root /opt/<appname>/.env && sudo chmod 600 /opt/<appname>/.env
sudo nano /opt/<appname>/.env          # fill in secrets

sudo install -m 755 deploy-appname.sh /usr/local/bin/deploy-<appname>.sh
sudo sed -i 's/^APP=.*/APP=<appname>/' /usr/local/bin/deploy-<appname>.sh

# GHCR: public images need no login. Private ones need a PAT with read:packages:
#   echo "$PAT" | sudo docker login ghcr.io -u <github-user> --password-stdin

sudo cp nginx-site.conf /etc/nginx/sites-available/<appname>.example.com
sudo ln -s /etc/nginx/sites-available/<appname>.example.com /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d <appname>.example.com

sudo deploy-<appname>.sh
```

Point the DNS A record at the box *before* running certbot — it validates over
HTTP against the live domain, and a missing record is the usual failure.

## The deploy script

```bash
#!/bin/bash
set -euo pipefail
APP=changeme
cd "/opt/$APP"
docker compose pull --quiet
docker compose up -d
docker image prune -f
```

`APP` is a variable rather than an inline `<appname>` placeholder so the script
is valid shell before it is customised — a bare `<appname>` is a redirect and
fails to parse. Each remaining line is load-bearing:

- **`set -euo pipefail`** — without `-e`, a failed `pull` is followed cheerfully
  by `up -d`, which restarts the stack on the *old* image and reports success.
- **`pull` then `up -d`** — compose only recreates containers whose image
  actually changed, so a no-op deploy causes no downtime.
- **`image prune -f`** — untagged images accumulate one per deploy, and a full
  disk on a small VPS takes the database down with it.

There is no rollback logic in the script on purpose: rollback is `APP_TAG=` in
`.env` plus a re-run, which is one concept rather than two.

## The compose file

Differences from a local compose file, all of them deliberate:

- **`image:`, never `build:`.** The VPS pulls what CI published. A box that can
  build is a box where the running code can silently diverge from the tag.
- **Bind the app port to `127.0.0.1`.** `"127.0.0.1:5000:8080"`, not
  `"5000:8080"` — the latter publishes to `0.0.0.0`, and Docker writes iptables
  rules that bypass ufw, so the container is reachable from the internet on port
  5000 even with a firewall that says otherwise. This is the single most common
  way a Compose-behind-nginx setup leaks.
- **No `ports:` on the database at all.** The app reaches it over the compose
  network; you reach it with `docker compose exec db psql`.
- **`restart: unless-stopped`** on every service, so a reboot brings the stack
  back.
- **A healthcheck on the database and `depends_on: condition: service_healthy`
  on the app.** Without it the app starts against a Postgres that is still
  initialising, fails its migration, and restarts a few times before catching.
- **`${VAR:?message}` for anything with no safe default.** Compose then refuses
  to start and says which variable is missing, instead of silently running with
  a default password.

## nginx

The template in `${CLAUDE_PLUGIN_ROOT}/assets/deploy/nginx-site.conf` is plain
HTTP; certbot rewrites it in place to add the TLS server block and the redirect.
Re-running certbot after you edit the file is safe — it preserves the `location`
block.

The parts that are not boilerplate:

- **`X-Forwarded-Proto`** is what makes the app emit `https://` URLs and set
  `Secure` cookies. Without it, OAuth redirect URIs come back as `http://` and
  the provider rejects them — a failure that looks like an auth bug and is a
  proxy bug. The app must also be configured to trust forwarded headers
  (`UseForwardedHeaders` in ASP.NET Core), or it ignores them.
- **`proxy_http_version 1.1` + `Upgrade`/`Connection`** — the WebSocket
  handshake. Blazor Server silently falls back to long polling without it, which
  works well enough to hide the misconfiguration until latency gets strange.
- **`proxy_read_timeout 100s`** — an idle SignalR circuit is dropped at nginx's
  60s default, and the user sees a spurious "reconnecting" banner.
- **`proxy_buffering off`** — required for server-sent events and streamed LLM
  responses. With buffering on, tokens arrive in one lump at the end.
- **`client_max_body_size`** must be at least the app's own upload limit, or
  nginx returns 413 before the app ever sees the request.

## Operating it

```bash
docker compose -f /opt/<appname>/docker-compose.yml logs -f app
docker compose -f /opt/<appname>/docker-compose.yml ps
docker compose -f /opt/<appname>/docker-compose.yml exec db psql -U postgres <appname>
```

**Back up the database volume, not the container.** A nightly `pg_dump` to a
file plus off-box copy is enough, and it is the only part of the box that is not
reproducible from the repository. Test the restore once — an untested backup is
a hypothesis.

**Firewall:** allow 22, 80, 443; nothing else. Given the iptables caveat above,
verify from *outside* the box (`nmap`, or curl the public IP on the app port)
rather than trusting the ufw status output.
