# Template Directory

This directory contains template files for AI processes. Each template should be stored as a YAML file with the following structure:

```yaml
name: "Template Name"
description: "Template description"
version: "1.0.0"
parameters:
  - name: "parameter_name"
    type: "string"
    description: "Parameter description"
    required: true
    default: null
steps:
  - name: "Step 1"
    description: "Step description"
    action: "action_type"
    parameters:
      param1: "value1"
      param2: "value2"
```

## Template Structure

- `name`: The name of the template
- `description`: A detailed description of what the template does
- `version`: The version of the template
- `parameters`: A list of parameters that can be configured when using the template
- `steps`: A list of steps that make up the process

## Naming Convention

Template files should be named using kebab-case and have the `.yaml` extension:
- `process-name.yaml`
- `another-process.yaml`

# Template Storage Format

Templates are stored as Markdown files within this directory (`templates/`).

Each template file should adhere to the following structure:

```markdown
---
title: "Your Template Title"
description: "A brief description of the template."
username: "creator_username"
created_at: "YYYY-MM-DDTHH:MM:SS.ffffff"
updated_at: "YYYY-MM-DDTHH:MM:SS.ffffff"
---

# Template Content

This is the main content of your template in Markdown format.

You can use standard Markdown syntax here.
```

**Key Points:**

*   **YAML Front Matter:** Metadata about the template (title, description, creator, timestamps) is stored in a YAML block enclosed by `---` at the beginning of the file.
*   **Content:** The actual template content follows the YAML front matter, written in standard Markdown.
*   **File Naming:** The filename should correspond to the template `title`, appropriately sanitized for the filesystem (e.g., spaces replaced with underscores, special characters removed). The specific conversion logic is handled by the application.
*   **Metadata Fields:**
    *   `title`: The unique identifier and display name of the template.
    *   `description`: A short summary of the template's purpose.
    *   `username`: The user who created or last modified the template.
    *   `created_at`, `updated_at`: Timestamps in ISO 8601 format, automatically managed by the system. 