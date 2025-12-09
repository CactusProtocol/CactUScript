# CactUScript v1.0
CactUScript by CactusProtocol
# 🌵 CactUScript: The Secure and Simplified Solana Programming Language

![Status Kompilatora](https://img.shields.io/badge/Compiler_Status-60%25_Complete-blue)
![License](https://img.shields.io/badge/License-MIT-green) 
![Built With](https://img.shields.io/badge/Built_With-Python-yellow)
***

## 💡 Vision & Problem Statement

CactUScript is a new high-level programming language designed specifically for the Solana Virtual Machine (SVM). Our primary goal is to fundamentally **eliminate common security vulnerabilities** associated with Cross-Program Invocation (CPI) and complex memory management in existing Solana languages.

By simplifying the syntax and introducing secure abstractions, CactUScript aims to be the **safest and fastest** way to deploy DeFi and high-performance applications on Solana.

---

## 🛠️ Project Architecture

The CactUScript compiler and interpreter are written in Python, providing a robust and transparent architecture for the community to audit and contribute to.

### Core Components (`./Cactus-Script/src/cactuscript`)

| Component | File | Function |
| :--- | :--- | :--- |
| **Execution Core** | `vm.py` & `interpreter.py` | Handles runtime interpretation and acts as the foundation for the future BPF/eBPF compilation step. |
| **Language Processing** | `lexer.py` & `parser.py` | Tokenizes and constructs the Abstract Syntax Tree (AST), ensuring strict syntax validation. |
| **CLI & Testing** | `cli.py` & `repl.py` | Command Line Interface and Read-Eval-Print Loop for rapid development and testing. |

### Project Directory Layout

| Folder | Purpose |
| :--- | :--- |
| **`Cactus-Script/src/`** | The core compiler and interpreter source code. **(The engine)** |
| **`Cactus-Script/examples/`** | Demonstrative `.cact` programs (e.g., `smart_contract.cact`, `fibonacci.cact`). |
| **`Cactus-Script/main.py`** | The main entry point for the CactUScript compiler/CLI. |

---

## 🚀 Getting Started

### Prerequisites

* Python 3.9+
* `pip` (Python package installer)

### Installation & Setup

1. **Clone the repository:**
```bash
git clone [https://github.com/CactusProtocol/CactUScript.git](https://github.com/CactusProtocol/CactUScript.git)
cd CactUScript/Cactus-Script

pip install -r requirements.txt

python main.py repl

python main.py run examples/hello.cact





---




🤝 Contribution & SupportWe are an Open Source project and invite all Solana developers, security researchers, and Python enthusiasts to contribute.How to ContributeCode Review: Review the src/ directory for potential optimizations or security vulnerabilities.Pull Requests (PRs): Submit PRs for new features, bug fixes, or improvements to the documentation.Issues: Report bugs or suggest new language features.Join the Founders TierDevelopment of a secure compiler requires sustained resources. By participating in our Pool Bonding mechanism, you directly fund auditing and core language development.Early supporters gain GUARANTEED ALLOCATION for the $CACTUS$ token distribution.
