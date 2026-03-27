# 🤝 Contribution Guide - Aureum

Thank you for considering contributing to Aureum! This is an **open-source** project and all contributions are welcome.

## 📜 Code of Conduct

This project follows the principles of respect, inclusion and collaboration. We expect all contributors to:

- Be respectful and constructive
- Accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other members

## 🎯 How to Contribute

### 1. Reporting Bugs

Found a bug? Help us improve!

**Before reporting:**
- Check if the bug has already been reported
- Test with the latest version
- Collect environment information (OS, versions)

**When reporting:**
- Use a clear and descriptive title
- Describe the steps to reproduce
- Explain expected vs actual behavior
- Include example code if possible
- Add screenshots if relevant

### 2. Suggesting Improvements

Have an idea to improve Aureum?

**Good suggestions include:**
- Clear description of the problem it solves
- Usage examples of the feature
- Comparison with existing solutions
- Expected impact on performance/usability

### 3. Contributing Code

#### Contribution Process

1. **Fork the repository**
   ```bash
   # On GitHub, click "Fork"
   git clone https://github.com/YOUR_USERNAME/aureum.git
   cd aureum
   ```

2. **Create a branch**
   ```bash
   git checkout -b feature/my-contribution
   # or
   git checkout -b fix/bug-fix
   ```

3. **Make your changes**
   - Write clean, documented code
   - Follow project conventions
   - Add tests when applicable

4. **Test your changes**
   ```bash
   # Python tests
   python test_compiler.py
   
   # Rust tests
   cd backend
   cargo test --release
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add 2D tensor support"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/my-contribution
   ```

7. **Open a Pull Request**
   - Describe your changes clearly
   - Reference related issues
   - Wait for review

## 📝 Code Conventions

### Python (Frontend)

```python
# Use docstrings
def my_function(parameter: str) -> int:
    """
    Brief function description.
    
    Args:
        parameter: Parameter description
        
    Returns:
        Return description
    """
    pass

# Type hints whenever possible
# Descriptive names in snake_case
# Maximum 100 characters per line
```

### Rust (Backend)

```rust
/// Function documentation using ///
/// 
/// # Parameters
/// - `input`: Description
/// 
/// # Returns
/// Return description
pub fn my_function(input: &[i32]) -> i64 {
    // Inline comments when necessary
    // Use descriptive names in snake_case
    // Prefer immutability
}
```

### Commits

Follow the [Conventional Commits](https://www.conventionalcommits.org/) standard:

```
feat: add new feature
fix: fix specific bug
docs: update documentation
test: add or modify tests
refactor: refactor code without changing functionality
perf: improve performance
style: formatting changes
chore: maintenance tasks
```

## 🎯 Areas to Contribute

### 🟢 Good First Contributions

- Improve documentation
- Add code examples
- Fix typos
- Improve error messages
- Add tests

### 🟡 Intermediate Contributions

- Implement new mathematical operators
- Add support for new types
- Improve parser error messages
- Optimize existing code
- Add benchmarks

### 🔴 Advanced Contributions

- Implement multidimensional tensors
- Add SIMD optimizations
- Implement GPU offloading
- Create Python binding (PyO3)
- Develop JIT compilation

## 🧪 Tests

### Running Tests

```bash
# All tests
python test_compiler.py
cd backend && cargo test --release

# Specific tests
cargo test test_matryoshka_scale
```

### Adding Tests

**Python:**
```python
def test_new_feature():
    """Tests new feature X"""
    # Arrange
    input = "aureum code"
    
    # Act
    result = compile(input)
    
    # Assert
    assert "expected" in result
```

**Rust:**
```rust
#[test]
fn test_new_feature() {
    let input = vec![1, 2, 3];
    let result = my_function(&input);
    assert_eq!(result, 6);
}
```

## 📚 Documentation

### Updating Documentation

When adding features, update:

- `README.md` - If basic usage changes
- `ARCHITECTURE.md` - If architecture changes
- `PERFORMANCE.md` - If performance is affected
- Docstrings/comments in code
- Examples in `examples/`

### Documentation Style

- Use clear and objective language
- Include practical examples
- Explain the "why", not just the "how"
- Maintain consistency with existing docs

## 🏗️ Project Structure

```
aureum/
├── frontend/           # Parser and transpiler (Python)
│   ├── grammar.lark    # Language grammar
│   └── aureum_compiler.py
├── backend/            # Inference kernel (Rust)
│   └── src/lib.rs
├── examples/           # .aur code examples
└── tests/              # Additional tests
```

## 🔍 Code Review

### What we expect in PRs

✅ Tested and working code  
✅ Updated documentation  
✅ Well-described commits  
✅ No commented/debug code  
✅ Follows project conventions  

### Review Process

1. Maintainer reviews the code
2. Requests changes if necessary
3. You update the PR
4. Approval and merge

## 🎓 Learning Resources

### Compilers
- [Crafting Interpreters](https://craftinginterpreters.com/)
- [Lark Documentation](https://lark-parser.readthedocs.io/)

### Rust
- [The Rust Book](https://doc.rust-lang.org/book/)
- [Rust by Example](https://doc.rust-lang.org/rust-by-example/)

### BitNet & Matryoshka
- [BitNet b1.58 Paper](https://arxiv.org/abs/2402.17764)
- [Matryoshka Paper](https://arxiv.org/abs/2205.13147)

## 💬 Communication

### Where to Get Help

- **Issues:** For bugs and features
- **Discussions:** For general questions
- **Instagram:** [@luizinvict](https://www.instagram.com/luizinvict/) for direct contact

## 🏆 Recognition

All contributors will be:

- Listed in the CONTRIBUTORS.md file
- Mentioned in release notes
- Credited in commits

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

## 🙏 Acknowledgements

Thank you for contributing to Aureum! Every contribution, no matter how small, helps make this project better.

**Together, we're building the future of efficient AI inference!** 🚀

---

**Created by:** Luiz Antônio De Lima Mendonça  
**Location:** Resende, RJ, Brazil  
**Instagram:** [@luizinvict](https://www.instagram.com/luizinvict/)

*Open-source project with 💛*
