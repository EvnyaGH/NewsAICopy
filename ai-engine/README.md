# Zara ETL Production - Sprint 2

> **Production-ready ETL pipeline for automated scientific article generation from arXiv papers**
> 
> Built for: **University of Melbourne - Software Processes and Management**  
> Sprint: **Sprint 2 - EP1-US1: Reliable arXiv Bulk and Daily Ingestion**

---

## 🚀 **Quick Start for Team Members**

Get the entire system running in **3 simple commands**:

### **Prerequisites (One-Time Setup)**

**Before you start, ensure you have:**

1. **Docker Desktop** installed and running
   - [Download for Mac](https://docs.docker.com/desktop/install/mac-install/)
   - [Download for Windows](https://docs.docker.com/desktop/install/windows-install/)
   - [Download for Linux](https://docs.docker.com/desktop/install/linux-install/)
   - Minimum 4GB RAM allocated to Docker
   - Minimum 10GB free disk space

2. **OpenAI API Key** (required for LLM operations)
   - Get yours at: https://platform.openai.com/api-keys
   - Keep it handy, you'll need it in Step 2

3. **Git** (to clone the repository)
   - Should already be installed on most systems
   - Check with: `git --version`

---

## 📦 **Team Setup (2-3 Commands)**

### **Step 1: Clone and Enter Project**
```bash
# Clone the repository
git clone <repository-url>
cd zara-etl-production
```

### **Step 2: Configure Your API Key**
```bash
# Copy environment template
cp env.example .env

# Edit .env and add your OpenAI API key
# For Mac/Linux:
nano .env
# For Windows (use any text editor):
notepad .env

# Find this line and replace with your actual key:
# OPENAI_API_KEY=sk-your_openai_api_key_here
```

### **Step 3: Run Automated Setup**
```bash
# Make setup script executable and run it
chmod +x scripts/quick-setup.sh
./scripts/quick-setup.sh

# ✨ That's it! The script handles everything:
#    - Creates all required directories
#    - Sets up secure secrets management
#    - Builds Docker containers
#    - Starts all services
#    - Initializes Airflow with configuration
#    - Runs health checks
```

**⏱️ Setup Time:** 5-10 minutes (first time), 2-3 minutes (subsequent runs)

---

## 🎯 **Access Your Running System**

After setup completes, you can access:

| **Service** | **URL** | **Credentials** | **Purpose** |
|-------------|---------|-----------------|-------------|
| **Airflow UI** | http://localhost:8080 | `admin` / `admin` | Manage DAGs and workflows |
| **Database UI** | http://localhost:8081 | System: `PostgreSQL`<br>Server: `postgres`<br>User: `zara_user`<br>Password: `zara_password`<br>Database: `zara_etl_dev` | Browse database directly |

---

## 🔍 **Verify Everything Works**

### **1. Check Airflow UI**
```bash
# Open in browser:
open http://localhost:8080  # Mac
start http://localhost:8080  # Windows
xdg-open http://localhost:8080  # Linux
```

**What to check:**
- ✅ Login with `admin` / `admin`
- ✅ See `health_check_dag` in the DAGs list
- ✅ DAG should be running or completed (green checkmark)
- ✅ Go to **Admin → Variables** - you should see 40+ configuration variables

### **2. Run Health Check Manually**
```bash
# Trigger health check from command line
make airflow-health

# Or click "Play" button on health_check_dag in Airflow UI
```

### **3. View System Status**
```bash
# See all running services and their health
make status

# Watch logs in real-time
make monitor
```

---

## 🛠️ **Daily Development Commands**

### **Essential Commands**
```bash
# Start everything
make dev-start

# Stop everything
make dev-stop

# Restart services
make dev-restart

# View logs
make dev-logs

# Run health check
make airflow-health

# System status
make status
```

### **Working with the Database**
```bash
# Run database migrations
make db-migrate

# Access database shell
make db-shell

# Check migration status  
make db-status

# Create new migration
make db-migration name="add_new_feature"
```

### **Configuration Management**
```bash
# Validate your secrets
make secrets-validate

# Security audit
make secrets-security-report

# Import updated variables
make airflow-import-variables
```

---

## 📂 **Project Structure Overview**

```
zara-etl-production/
├── 🐳 docker-compose.yml        # Service orchestration
├── 📄 README.md                 # This file
├── 🔧 Makefile                  # Convenient commands
├── 📦 requirements.txt          # Python dependencies
│
├── 🏗️ airflow/                  # Airflow configuration
│   ├── dags/                    # DAG definitions
│   │   ├── health_check_dag.py # System health validation ✅
│   │   └── arxiv_ingestion_dag.py # Coming in Sprint 3
│   ├── plugins/                 # Custom operators
│   ├── variables/               # PUBLIC config (safe for Git)
│   │   ├── development-public.json
│   │   ├── staging-public.json
│   │   └── production-public.json
│   └── secrets/                 # SECRETS (excluded from Git)
│       ├── secrets-template.json
│       └── secrets-development.json (generated)
│
├── 🗄️ database/                 # Database models & DTOs
│   ├── models/                  # SQLAlchemy ORM models
│   │   ├── papers.py           # Paper model
│   │   ├── articles.py         # Article model
│   │   ├── authors.py          # Author model
│   │   ├── fields.py           # Taxonomy/fields model
│   │   └── prompts.py          # AI prompt templates
│   ├── dto/                     # Pydantic DTOs
│   ├── mappers/                 # Model ↔ DTO conversion
│   └── migrations/              # Alembic migrations
│
├── 🔧 services/                 # Business logic services
│   ├── arxiv_service.py
│   ├── ingestion_service.py
│   └── database_service.py
│
├── 🛠️ scripts/                  # Utility scripts
│   ├── quick-setup.sh          # Automated team setup ⚡
│   ├── secrets_manager.py      # Secure secrets management
│   └── manage_variables.py     # Variable management
│
└── 📊 data/                     # Data storage (generated)
    ├── input/                   # Downloaded PDFs
    ├── processed/               # Processing intermediate files
    ├── output/                  # Generated articles
    └── logs/                    # Application logs
```

---

## 🔐 **Security & Secrets Management**

### **What's Safe to Commit to Git?**

✅ **SAFE - Commit these:**
- `airflow/variables/*-public.json` - Public configuration
- `airflow/secrets/secrets-template.json` - Template file
- `.env.example` - Example environment file
- All code files

❌ **NEVER COMMIT these:**
- `airflow/secrets/secrets-*.json` - Actual secrets
- `.env` - Your environment file
- Any file with API keys, passwords, or tokens

### **How Secrets Work**

1. **Local Development:**
   ```bash
   # Secrets stored in: airflow/secrets/secrets-development.json
   # File is automatically created by quick-setup.sh
   # File is in .gitignore (never committed)
   ```

2. **Airflow Variables:**
   - **Public config** → Stored in `*-public.json` files (committed to Git)
   - **Secrets** → Stored encrypted in Airflow's database (never in Git)
   - **Runtime** → DAGs read from Airflow Variables (secure)

3. **Changing Secrets:**
   ```bash
   # Option 1: Via Airflow UI (recommended)
   Admin → Variables → Edit the secret → Save
   
   # Option 2: Via secrets file
   nano airflow/secrets/secrets-development.json
   make secrets-setup  # Re-import
   ```

---

## 👥 **Team Collaboration Workflow**

### **For New Team Members**

1. **Clone repo** (get repository URL from team)
2. **Get API key** (from OpenAI or team lead)
3. **Run setup** (`./scripts/quick-setup.sh`)
4. **Start coding!** 🎉

### **Daily Workflow**

```bash
# Morning - Start your environment
make dev-start

# Check everything is healthy
make airflow-health

# Work on your features...
# Make changes to DAGs, models, services, etc.

# Test your changes
make test

# Check code quality
make lint

# Evening - Stop environment (optional)
make dev-stop
```

### **Before Committing Code**

```bash
# 1. Run tests
make test

# 2. Check linting
make lint

# 3. Ensure no secrets in code
make secrets-security-report

# 4. Commit your changes
git add <files>
git commit -m "feat: your feature description"
git push origin your-branch
```

---

## 📊 **Sprint 2 Implementation Status**

### **✅ Completed (Ready for Team)**

| Component | Status | Description |
|-----------|--------|-------------|
| **Health Check DAG** | ✅ | Validates all system components |
| **Variable Management** | ✅ | 60+ configurable parameters |
| **Database Schema** | ✅ | Full ER diagram implemented |
| **DTOs & Mappers** | ✅ | Pydantic models for all entities |
| **Docker Setup** | ✅ | Multi-service orchestration |
| **Secrets Management** | ✅ | Secure credential handling |
| **Team Setup Script** | ✅ | One-command setup |

### **🔄 Sprint 3 - Coming Next**

- arXiv Ingestion DAG (EP1-US2 to EP1-US12)
- PDF Processing Pipeline
- AI Article Generation (EP2-US1 to EP2-US7)
- Quality Control System
- Publishing Pipeline

---

## 🧪 **Testing**

### **Run All Tests**
```bash
make test
```

### **Run Specific Test Types**
```bash
# Unit tests
make test-unit

# Integration tests  
make test-integration

# DAG validation
make test-dag
```

### **Test Coverage**
```bash
# Generate coverage report
docker-compose exec airflow-webserver pytest --cov=. --cov-report=html
```

---

## 📈 **Monitoring & Debugging**

### **View System Status**
```bash
# Quick status overview
make status

# Detailed monitoring dashboard
make monitor

# View specific service logs
docker-compose logs -f airflow-webserver
docker-compose logs -f postgres
```

### **Debug Issues**

```bash
# 1. Check service health
docker-compose ps

# 2. View recent logs
make dev-logs

# 3. Check Airflow DAG logs
# Go to Airflow UI → DAGs → Click on DAG → Graph View → Click task → Logs

# 4. Access shell for debugging
make dev-shell

# 5. Run health check
make airflow-health
```

### **Common Issues**

| Issue | Solution |
|-------|----------|
| **Port 8080 already in use** | `lsof -ti:8080 \| xargs kill -9` |
| **Docker out of memory** | Increase Docker memory to 4GB+ in Docker Desktop settings |
| **Services won't start** | `make clean && make dev-start` |
| **API key invalid** | Check `.env` file and ensure key starts with `sk-` |
| **Database connection failed** | `make db-init && make db-migrate` |

---

## 🔧 **Advanced Operations**

### **Database Operations**
```bash
# Backup database
make backup-db

# Restore from backup
make restore-db file=backups/zara_etl_20240101.sql

# Reset database (⚠️ destroys all data)
make db-reset
```

### **Production Deployment**
```bash
# Deploy to staging
make deploy-staging

# Deploy to production (requires confirmation)
make deploy-production
```

### **Configuration Management**
```bash
# Compare environments
python scripts/manage_variables.py compare development production

# Validate configuration
python scripts/manage_variables.py validate --env development

# Export current variables
python scripts/manage_variables.py export --output current_config.json
```

---

## 📚 **Documentation & Resources**

### **Internal Documentation**
- **User Stories**: `context/User-Stories.md`
- **Personas**: `context/Personas.md`
- **Requirements**: `context/Functional-Requirements.md`
- **Database Schema**: See ERD in `context/ERD.md`

### **External Resources**
- [Apache Airflow Docs](https://airflow.apache.org/docs/)
- [DocETL Documentation](https://docetl.org/docs/)
- [arXiv API Guide](https://info.arxiv.org/help/api/index.html)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)

### **Getting Help**
- 💬 **Team Chat**: [Your team communication channel]
- 🐛 **Report Issues**: [Your issue tracker]
- 📧 **Email**: [Team lead email]

---

## 🎓 **Learning Resources for New Team Members**

### **If you're new to:**

**Docker:**
- [Docker 101 Tutorial](https://www.docker.com/101-tutorial)
- Understanding docker-compose: `docker-compose.yml` defines all our services

**Apache Airflow:**
- [Airflow Concepts](https://airflow.apache.org/docs/apache-airflow/stable/concepts/index.html)
- Our DAGs are in: `airflow/dags/`
- Start with: `health_check_dag.py`

**Python (SQLAlchemy & Pydantic):**
- Models: `database/models/` - Database structure
- DTOs: `database/dto/` - API data transfer objects

**This Project:**
1. Read this README completely
2. Run `./scripts/quick-setup.sh` and explore Airflow UI
3. Check `health_check_dag.py` - it shows how everything works
4. Look at database models in `database/models/`
5. Ask questions in team chat!

---

## 🤝 **Contributing**

### **Git Workflow**
```bash
# 1. Create feature branch
git checkout -b feature/your-feature-name

# 2. Make changes and commit frequently
git add .
git commit -m "feat: add new feature"

# 3. Push to remote
git push origin feature/your-feature-name

# 4. Create Pull Request on GitHub/GitLab
```

### **Commit Message Convention**
```
feat: Add new feature
fix: Fix bug in component
docs: Update documentation  
test: Add tests
refactor: Refactor code
chore: Update dependencies
```

### **Code Quality Standards**
- **Linting**: All code must pass `make lint`
- **Tests**: New features need tests
- **Documentation**: Update README for significant changes
- **Security**: Never commit secrets

---

## 📞 **Support & Contact**

### **Team Contact**
- **Project Lead**: [Name] - [email]
- **Technical Lead**: [Name] - [email]  
- **Team Chat**: [Link to Slack/Discord/Teams]

### **Emergency Contacts**
- **Production Issues**: [On-call contact]
- **Security Issues**: [Security team contact]

---

## 📄 **License**

[Add your license information here]

---

## 🎉 **Acknowledgments**

Built with ❤️ by the Zara ETL Team for University of Melbourne

**Key Technologies:**
- Apache Airflow 2.8.1
- Docker & Docker Compose
- PostgreSQL 15
- Python 3.11
- OpenAI GPT-4
- DocETL

---

**Last Updated**: January 2024  
**Version**: 1.0.0 - Sprint 2  
**Status**: ✅ Production-Ready for Team Collaboration