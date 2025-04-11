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