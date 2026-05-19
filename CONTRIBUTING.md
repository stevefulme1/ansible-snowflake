# Contributing

Contributions are welcome! Please follow these guidelines.

## How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes
4. Run linting and tests:
   ```bash
   ansible-lint
   ansible-test sanity
   ansible-test units
   ```
5. Commit your changes (`git commit -m 'Add my feature'`)
6. Push to the branch (`git push origin feature/my-feature`)
7. Open a Pull Request

## Development Setup

```bash
pip install ansible-core ansible-lint
```

## Code Standards

- All modules must include `DOCUMENTATION`, `EXAMPLES`, and `RETURN` docstrings
- All modules must have a GPL-3.0-or-later license header
- Sensitive parameters must use `no_log=True`
- SSL validation must default to `True` (`validate_certs`)
- Follow [Ansible module development guidelines](https://docs.ansible.com/ansible/latest/dev_guide/developing_modules.html)

## Reporting Issues

Please open a GitHub issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Ansible and Python versions

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).
