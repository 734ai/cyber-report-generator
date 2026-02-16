# Contributing

Contributions are welcome. Please follow these guidelines:

1. **Fork** the repository and create a branch for your feature or fix
2. **Install** dependencies: `pip install -r requirements.txt`
3. **Test** your changes: `python -c "from tests.test_evaluation import *; test_precision_recall_f1(); test_rouge_n(); test_bleu_simple(); print('OK')"`
4. **Commit** with clear messages
5. **Open a Pull Request**

## Code style

- Use type hints where helpful
- Docstrings for public functions
- Keep commits focused and atomic
