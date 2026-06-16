# OpenAI Chatbot Application using Python, Streamlit, Docker

## Overview

This project demonstrates how to build a simple chatbot using:

* Python
* Streamlit
* OpenAI API
* Docker

The chatbot accepts user input, sends it to OpenAI, and displays the response in a conversational interface.

---

# Architecture

```text
+-------------+
|   Browser   |
+------+------+
       |
       v
+-------------+
|  Streamlit  |
| Application |
+------+------+
       |
       v
+-------------+
| OpenAI API  |
+-------------+
```

---

# Project Structure

```text
chatbot/
├── app.py
├── requirements.txt
├── Dockerfile
├── .env
└── README.md
```

---

# Step 1: Install Dependencies

## requirements.txt

```txt
streamlit
openai
python-dotenv
```

---

# Step 2: Create OpenAI Key

Create a `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

Never commit this file to Git.

---

# Step 3: Create Chatbot Application

## app.py

```python
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

st.set_page_config(
    page_title="DevOps AI Chatbot",
    page_icon="🤖"
)

st.title("🤖 DevOps AI Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

prompt = st.chat_input("Ask me anything...")

if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):
        st.write(prompt)

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=st.session_state.messages
    )

    answer = response.choices[0].message.content

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    with st.chat_message("assistant"):
        st.write(answer)
```

---

# Run Locally

```bash
pip install -r requirements.txt

streamlit run app.py
```

Application URL:

```text
http://localhost:8501
```

---

# Containerization

## Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
```

---

# Build Docker Image

```bash
docker build -t openai-chatbot .
```

---

# Run Docker Container

```bash
docker run -d \
-p 8501:8501 \
--env-file .env \
--name chatbot \
openai-chatbot
```

---

# Verify

```bash
docker ps
```

Open:

```text
http://localhost:8501
```

---

# Difference Between ChatGPT and Your Own Chatbot

| Feature         | ChatGPT                   | Your Chatbot       |
| --------------- | ------------------------- | ------------------ |
| UI              | Ready-made                | Customizable       |
| Hosting         | OpenAI                    | Self-hosted        |
| Branding        | ChatGPT                   | Your Company       |
| Integrations    | Limited                   | Unlimited          |
| Authentication  | Managed by OpenAI         | Custom             |
| Database        | Managed by OpenAI         | Your choice        |
| RAG Support     | Not directly customizable | Fully customizable |
| MCP Support     | Not user controlled       | Can build your own |
| Cost Visibility | Subscription based        | API usage based    |
| Business Logic  | Fixed                     | Fully customizable |

---

# Why Build Your Own Chatbot?

A custom chatbot allows you to:

* Integrate with Kubernetes
* Connect Jenkins pipelines
* Query Prometheus
* Query Grafana
* Query ServiceNow
* Query Jira
* Trigger Terraform deployments
* Automate DevOps operations
* Build RAG over internal documentation
* Add MCP servers
* Add AI Agents

Example:

```text
User:
Show me failed pods in production

Chatbot:
Queries Kubernetes API
Returns failed pods
Suggests remediation steps
```

This level of customization is not available in standard ChatGPT.

---

# Example Future Enhancements

## Add Authentication

* Login page
* Registration page
* Role-based access

## Add Database

* PostgreSQL
* MySQL
* MongoDB

## Add Chat History

Store conversations.

## Add RAG

Use:

* LangChain
* LlamaIndex
* Vector Database

## Add MCP

Connect:

* Kubernetes
* Jenkins
* Grafana
* Jira
* GitHub

## Add AI Agents

Examples:

* Kubernetes Agent
* Terraform Agent
* AWS Agent
* Monitoring Agent

---

# Production Deployment

## Kubernetes Deployment

```text
Developer
    |
    v
Ingress
    |
    v
Streamlit Chatbot
    |
    v
OpenAI API
```

Deploy using:

* Kubernetes
* Helm
* ArgoCD
* Jenkins Pipeline

---

# Security Best Practices

* Store API keys in Kubernetes Secrets
* Enable authentication
* Use HTTPS
* Rate limit requests
* Enable audit logging
* Restrict model access
* Use RBAC

---

# Next Level Architecture

```text
User
 |
 v
Frontend
 |
 v
AI Gateway
 |
 +----> OpenAI
 |
 +----> RAG Database
 |
 +----> Kubernetes MCP
 |
 +----> Jenkins MCP
 |
 +----> Grafana MCP
 |
 +----> Jira MCP
 |
 +----> GitHub MCP
```

This architecture is typically used for enterprise DevOps AI assistants.
