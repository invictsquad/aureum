#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aureum - Main entry point
Supports .aur file compilation and interactive shell mode

Author: Luiz Antônio De Lima Mendonça
Location: Resende, RJ, Brazil
Instagram: @luizinvict
Date: 2026-03-25
"""

import sys
import argparse
from pathlib import Path


def main():
    """Main function with CLI"""
    parser = argparse.ArgumentParser(
        description="Aureum - High-Performance AI Language",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --shell                    # Start interactive REPL
  python main.py examples/inferencia.aur    # Compile .aur file
  python main.py --help                     # Show this help

Author: Luiz Antônio De Lima Mendonça
Resende, RJ, Brazil | @luizinvict
        """
    )
    
    parser.add_argument(
        '--shell',
        action='store_true',
        help='Start the interactive REPL (shell mode)'
    )
    
    parser.add_argument(
        'file',
        nargs='?',
        help='.aur file to compile'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output .rs file (default: same name with .rs)'
    )
    
    parser.add_argument(
        '--run',
        action='store_true',
        help='Compile and run the generated Rust code'
    )
    
    args = parser.parse_args()
    
    # Modo shell
    if args.shell:
        from shell import main as shell_main
        shell_main()
        return
    
    # Compilation mode
    if args.file:
        compile_file(args.file, args.output, args.run)
        return
    
    # Sem argumentos: mostra ajuda
    parser.print_help()


def compile_file(input_file: str, output_file: str = None, run: bool = False):
    """Compiles .aur file to .rs"""
    sys.path.insert(0, str(Path(__file__).parent / "frontend"))
    from aureum_compiler import AureumTranspiler
    
    source_path = Path(input_file)
    
    if not source_path.exists():
        print(f"❌ File not found: {input_file}")
        sys.exit(1)
    
    if not source_path.suffix == '.aur':
        print(f"⚠️  Warning: file does not have .aur extension")
    
    # Define output file
    if output_file:
        output_path = Path(output_file)
    else:
        output_path = source_path.with_suffix('.rs')
    
    # Compile
    print(f"📝 Compiling {source_path}...")
    
    grammar_path = Path(__file__).parent / "frontend" / "grammar.lark"
    transpiler = AureumTranspiler(str(grammar_path))
    
    try:
        source_code = source_path.read_text(encoding='utf-8')
        rust_code = transpiler.compile(source_code)
        
        # Save
        output_path.write_text(rust_code, encoding='utf-8')
        
        print(f"✅ Compilation complete: {output_path}")
        
        # Show generated code
        print("\n" + "="*70)
        print("Generated Rust Code:")
        print("="*70)
        print(rust_code)
        print("="*70 + "\n")
        
        # Run if requested
        if run:
            run_rust_code(output_path)
        
    except Exception as e:
        print(f"❌ Compilation error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def run_rust_code(rust_file: Path):
    """Compiles and runs Rust code"""
    import subprocess
    
    print(f"\n🔧 Compiling and running {rust_file}...")
    
    backend_dir = Path(__file__).parent / "backend"
    
    try:
        # Copy file to backend/examples
        examples_dir = backend_dir / "examples"
        examples_dir.mkdir(exist_ok=True)
        
        target_file = examples_dir / rust_file.name
        target_file.write_text(rust_file.read_text())
        
        # Compile and run
        result = subprocess.run(
            ["cargo", "run", "--release", "--example", rust_file.stem],
            cwd=backend_dir,
            capture_output=True,
            text=True
        )
        
        print("\n" + "="*70)
        print("Output:")
        print("="*70)
        print(result.stdout)
        
        if result.stderr:
            print("\nErrors/Warnings:")
            print(result.stderr)
        
        if result.returncode != 0:
            print(f"\n❌ Execution failed with code {result.returncode}")
            sys.exit(result.returncode)
        
        print("="*70 + "\n")
        
    except FileNotFoundError:
        print("❌ Cargo not found. Install Rust: https://rustup.rs/")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Execution error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
