name: Bug Report
description: Report a bug
labels: [bug]
body:
  - type: markdown
    attributes:
      value: |
        ## 🐛 Bug Report
        
        Thanks for reporting a bug! Please fill out the form below.
        
  - type: textarea
    id: description
    attributes:
      label: Bug Description
      description: Describe the bug clearly
      placeholder: A clear description of the bug
    validations:
      required: true

  - type: textarea
    id: reproduction
    attributes:
      label: Steps to Reproduce
      description: How can we reproduce this?
      placeholder: |
        1. Go to '...'
        2. Click on '...'
        3. See error
    validations:
      required: true

  - type: textarea
    id: expected
    attributes:
      label: Expected Behavior
      description: What did you expect to happen?
    validations:
      required: true

  - type: textarea
    id: logs
    attributes:
      label: Relevant Logs
      description: Please include any relevant error logs
      placeholder: Paste logs here

  - type: dropdown
    id: os
    attributes:
      label: Operating System
      options:
        - Windows
        - macOS
        - Linux
    validations:
      required: true

---

name: Feature Request
description: Suggest a new feature
labels: [enhancement]
body:
  - type: markdown
    attributes:
      value: |
        ## ✨ Feature Request
        
        Have an idea for a new feature? We'd love to hear it!
        
  - type: textarea
    id: feature
    attributes:
      label: Feature Description
      description: Describe the feature
      placeholder: A clear description of the feature
    validations:
      required: true

  - type: textarea
    id: motivation
    attributes:
      label: Motivation
      description: Why do you need this feature?
      placeholder: This feature would help because...
    validations:
      required: true

  - type: textarea
    id: alternatives
    attributes:
      label: Alternatives Considered
      description: Any alternatives you've considered?
