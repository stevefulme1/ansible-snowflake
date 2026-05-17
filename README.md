# stevefulme1.snowflake

Ansible collection for managing Snowflake data warehouse resources via the SQL REST API.

## Overview

This collection provides **104 modules** for automating Snowflake infrastructure, along with 4 operational roles and CI/CD workflows.

## Requirements

- ansible-core >= 2.16
- Python >= 3.11

## Installation

```bash
ansible-galaxy collection install stevefulme1.snowflake
```

Or from source:

```bash
ansible-galaxy collection build
ansible-galaxy collection install stevefulme1-snowflake-2.0.0.tar.gz
```

## Included Content

### Modules (104)

This collection includes CRUD and info modules for the following Snowflake resources:

- **Warehouses** — create, resize, suspend, resume
- **Databases** — databases, schemas, tables
- **Users & Roles** — user management, role grants, privileges
- **Security** — network policies, masking policies, row access policies
- **Data Loading** — stages, pipes, file formats, streams, tasks
- **Dynamic Tables** — dynamic table management and monitoring
- **Cortex Functions** — Cortex ML function management
- **Shares** — data sharing configuration
- **Integrations** — storage, notification, and API integrations

### Roles (4)

| Role | Description |
|------|-------------|
| `warehouse_setup` | Provision and configure warehouses |
| `database_provision` | Set up databases and schemas |
| `security_config` | Configure network policies and access controls |
| `data_pipeline` | Set up stages, pipes, and streaming |

## Usage

```yaml
- name: Create a Snowflake warehouse
  stevefulme1.snowflake.snowflake_warehouse:
    account: "{{ snowflake_account }}"
    user: "{{ snowflake_user }}"
    password: "{{ snowflake_password }}"
    name: ANALYTICS_WH
    warehouse_size: MEDIUM
    auto_suspend: 300
    state: present
```

## License

GPL-3.0-or-later
