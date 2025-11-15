# goats-elt-project
Xccelerated training project

## Contributors
- Leonardo Amaro Drigo
- Konrad Van Kempen
- Elif Apaydin
- Jelle Willekes

## How to run

1. Go to /infra, create a `.env` file following `.env.example`
2. Build and run the ELT job with: `docker compose -f infra/docker-compose.elt.yml up -d --build`