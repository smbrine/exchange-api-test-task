# exchange-api-test-task

## Introduction
A simple FastAPI service for converting currencies.

---

## Quick Start

### Installation

#### Option 1: Docker compose
1. **Run compose deploy**
     ```bash
     docker compose -f deploy/docker-compose.yml run -d --remove-orphans
     ```

#### Option 2: Local Setup

1. **Install dependencies**  
   Choose your preferred method to install the dependencies:

   - **Using Poetry (Recommended):**
     ```bash
     poetry install
     ```
   - **Using pip:**
     ```bash
     pip install -r requirements.txt
     ```

2. **Start Redis**  
   You can use Docker Compose or any other method to start a Redis instance:

   - **Using Docker Compose:**
     ```bash
     docker compose -f deploy/docker-compose.yml run redis -d --no-deps --remove-orphans
     ```

3. **Configure Redis Endpoint**  
   Update the `.env` file to point to the correct Redis endpoint.

4. **Run the Application**  
   Start the application with:
   ```bash
   python -m app.main
   ```

