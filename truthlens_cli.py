"""
TruthLens CLI - Command-Line Interface for Document Fraud Detection
Easy-to-use tool for fraud analysis
"""

import argparse
import os
import sys
from pathlib import Path
from src.fraud_detector import FraudDetector
from src.batch_processor import BatchProcessor


def print_banner():
    """Print TruthLens banner"""
    banner = """
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║   ████████╗██████╗ ██╗   ██╗████████╗██╗  ██╗██╗     ███████╗███╗ ║
║   ╚══██╔══╝██╔══██╗██║   ██║╚══██╔══╝██║  ██║██║     ██╔════╝████╗║
║      ██║   ██████╔╝██║   ██║   ██║   ███████║██║     █████╗  ██╔═║
║      ██║   ██╔══██╗██║   ██║   ██║   ██╔══██║██║     ██╔══╝  ██║ ║
║      ██║   ██║  ██║╚██████╔╝   ██║   ██║  ██║███████╗███████╗██║ ║
║      ╚═╝   ╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝ ║
║                                                                    ║
║              AI-Powered Document Fraud Detection                   ║
║                        Version 1.0.0                               ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def analyze_single_document(file_path, verbose=True, use_cache=True):
    """
    Analyze a single document
    
    Args:
        file_path (str): Path to document
        verbose (bool): Show detailed analysis
        use_cache (bool): Use caching
    """
    print_banner()
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"❌ Error: File not found: {file_path}")
        sys.exit(1)
    
    print(f"📄 Analyzing: {os.path.basename(file_path)}")
    print("="*70)
    
    # Initialize processor
    if use_cache:
        processor = BatchProcessor(use_cache=True)
        result = processor.process_single(file_path, verbose=verbose)
    else:
        detector = FraudDetector(use_segmentation=True)
        result = detector.analyze_document(file_path, verbose=verbose)
    
    # Print summary
    if not verbose:
        print("\n" + "="*70)
        print("📊 ANALYSIS RESULTS")
        print("="*70)
        print(f"   Document: {os.path.basename(file_path)}")
        print(f"   Status: {'🚨 FRAUD DETECTED' if result['fraud_detected'] else '✅ AUTHENTIC'}")
        print(f"   Confidence: {result['confidence']:.1f}%")
        print(f"\n   Detection Details:")
        print(f"      • ELA Score: {result['ela_score']:.2f}/100")
        print(f"      • Copy-Move Duplicates: {result['copymove_duplicates']}")
        print(f"      • Font Variation: {result['font_variation']:.1f}%")
        print("="*70 + "\n")


def analyze_batch(directory, pattern='*.jpg', use_cache=True, output=None):
    """
    Analyze multiple documents in a directory
    
    Args:
        directory (str): Directory path
        pattern (str): File pattern (*.jpg, *.png)
        use_cache (bool): Use caching
        output (str): Output file path
    """
    print_banner()
    
    # Check if directory exists
    if not os.path.exists(directory):
        print(f"❌ Error: Directory not found: {directory}")
        sys.exit(1)
    
    print(f"📁 Analyzing directory: {directory}")
    print(f"   Pattern: {pattern}")
    print("="*70)
    
    # Initialize processor
    processor = BatchProcessor(use_cache=use_cache)
    
    # Process directory
    results = processor.process_directory(directory, pattern=pattern, show_progress=True)
    
    # Save results if output specified
    if output:
        processor.save_results(results, output_file=output)
        print(f"\n💾 Results saved to: {output}")


def clear_cache():
    """Clear all cached results"""
    print_banner()
    print("🗑️  Clearing cache...")
    
    processor = BatchProcessor(use_cache=True)
    processor.clear_cache()
    
    print("✅ Cache cleared successfully!")


def show_cache_info():
    """Show cache statistics"""
    print_banner()
    print("📦 Cache Information")
    print("="*70)
    
    processor = BatchProcessor(use_cache=True)
    size_mb = processor.get_cache_size()
    
    print(f"\n💡 Cache is saving time on repeated analyses!")
    print("   Run with --no-cache to bypass cache")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='TruthLens - AI-Powered Document Fraud Detection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze single document
  python truthlens_cli.py analyze document.jpg
  
  # Analyze single document (detailed)
  python truthlens_cli.py analyze document.jpg --verbose
  
  # Analyze entire directory
  python truthlens_cli.py batch data/documents/
  
  # Analyze with custom pattern
  python truthlens_cli.py batch data/documents/ --pattern "*.png"
  
  # Save batch results
  python truthlens_cli.py batch data/documents/ --output results.json
  
  # Clear cache
  python truthlens_cli.py clear-cache
  
  # Show cache info
  python truthlens_cli.py cache-info
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze a single document')
    analyze_parser.add_argument('file', help='Path to document file')
    analyze_parser.add_argument('--verbose', '-v', action='store_true',
                               help='Show detailed analysis')
    analyze_parser.add_argument('--no-cache', action='store_true',
                               help='Disable caching')
    
    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Analyze multiple documents')
    batch_parser.add_argument('directory', help='Directory containing documents')
    batch_parser.add_argument('--pattern', '-p', default='*.jpg',
                             help='File pattern (default: *.jpg)')
    batch_parser.add_argument('--output', '-o', help='Output file for results')
    batch_parser.add_argument('--no-cache', action='store_true',
                             help='Disable caching')
    
    # Clear cache command
    subparsers.add_parser('clear-cache', help='Clear cached results')
    
    # Cache info command
    subparsers.add_parser('cache-info', help='Show cache statistics')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute command
    if args.command == 'analyze':
        analyze_single_document(
            args.file,
            verbose=args.verbose,
            use_cache=not args.no_cache
        )
    
    elif args.command == 'batch':
        analyze_batch(
            args.directory,
            pattern=args.pattern,
            use_cache=not args.no_cache,
            output=args.output
        )
    
    elif args.command == 'clear-cache':
        clear_cache()
    
    elif args.command == 'cache-info':
        show_cache_info()
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()