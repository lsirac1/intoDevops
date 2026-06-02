# TempConverter — Intro to DevOps Project

A Flask web application that converts Celsius to Fahrenheit and stores conversion history in a MySQL 8 database.  
Built for the Intro to DevOps course at Algebra Bernays University.

---

## Repository Structure

```
tempconverter/
├── app.py                          # Flask application (source: github.com/jstanesic/tempconverter)
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Container image definition
├── podman-compose.yml              # Local deployment (Task 4)
├── docker-stack.yml                # Docker Swarm deployment (Tasks 6-7)
├── templates/
│   └── index.html                  # HTML template (title updated for Task 3)
├── tests/
│   ├── __init__.py
│   └── test_app.py                 # Unit & integration tests (Task 4)
├── k8s/
│   ├── secret.yaml                 # DB credentials
│   ├── pvc.yaml                    # Persistent storage for MySQL
│   ├── mysql.yaml                  # MySQL Deployment + Service
│   └── app.yaml                    # App Deployment + Service + Ingress
└── .github/
    └── workflows/
        └── ci.yml                  # GitHub Actions CI/CD pipeline
```

---

## Quickstart – Local with Podman (Task 4)

### Prerequisites
- [Podman](https://podman.io/getting-started/installation) installed
- [podman-compose](https://github.com/containers/podman-compose) installed

### Steps

```bash
# 1. Clone this repository
git clone https://github.com/YOURUSERNAME/tempconverter.git
cd tempconverter

# 2. Edit student info in podman-compose.yml (STUDENT and COLLEGE env vars)

# 3. Start the stack (app + MySQL)
podman-compose up -d

# 4. Open the application
open http://localhost:5000

# 5. Stop everything
podman-compose down
```

---

## Building the Image (Tasks 1 & 2)

```bash
# Build image
podman build -t YOURDOCKERHUBUSER/tempconverter:latest .

# Login to Docker Hub
podman login docker.io

# Push latest tag
podman push YOURDOCKERHUBUSER/tempconverter:latest

# Push dev tag (Task 3)
podman build -t YOURDOCKERHUBUSER/tempconverter:dev .
podman push YOURDOCKERHUBUSER/tempconverter:dev
```

---

## Running Tests (Task 4)

```bash
pip install pytest pytest-cov
pytest tests/ -v --cov=app
```

---

## Docker Swarm Deployment (Tasks 6 & 7)

```bash
# Initialize Swarm (once, on manager node)
docker swarm init

# Add worker nodes using the join token printed above

# Deploy the stack
docker stack deploy -c docker-stack.yml tempconverter

# Check services
docker service ls
docker service ps tempconverter_app

# Scale to 3 replicas
docker service scale tempconverter_app=3

# Tear down
docker stack rm tempconverter
```

---

## Kubernetes Deployment (Task 8)

```bash
# Apply all manifests
kubectl apply -f k8s/

# Watch pods come up
kubectl get pods -w

# Verify pods are on different nodes
kubectl get pods -o wide

# Scale to 3 replicas
kubectl scale deployment tempconverter --replicas=3

# Tear down
kubectl delete -f k8s/
```

### Prerequisites for Kubernetes
- A running cluster (minikube, kind, or cloud-managed)
- [nginx Ingress Controller](https://kubernetes.github.io/ingress-nginx/deploy/) installed:
  ```bash
  helm upgrade --install ingress-nginx ingress-nginx \
    --repo https://kubernetes.github.io/ingress-nginx \
    --namespace ingress-nginx --create-namespace
  ```
- Add `tempconverter.local` to your `/etc/hosts` pointing to the Ingress IP

---

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `DB_USER` | MySQL username (non-root) | `CHANGEME` |
| `DB_PASS` | MySQL password | `CHANGEME` |
| `DB_HOST` | MySQL hostname | `CHANGEME` |
| `DB_NAME` | MySQL database name | `CHANGEME` |
| `STUDENT` | Your name displayed on the page | `Default Student` |
| `COLLEGE` | Your college displayed on the page | `Default College` |

---

## CI/CD Pipeline

The GitHub Actions pipeline in `.github/workflows/ci.yml` automatically:
1. Runs all unit and integration tests on every push/PR
2. Builds and pushes the Docker image to Docker Hub (only if tests pass)

**Required GitHub Secrets:**
- `DOCKERHUB_USERNAME` — your Docker Hub username
- `DOCKERHUB_TOKEN` — your Docker Hub access token
