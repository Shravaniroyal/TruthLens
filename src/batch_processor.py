"""
Batch Processing System for TruthLens
Handles multiple documents efficiently with caching and progress tracking
"""

import os
import json
import hashlib
import time
from datetime import datetime
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.fraud_detector import FraudDetector


class BatchProcessor:
    """
    Processes multiple documents with caching and progress tracking
    """
    
    def __init__(self, use_cache=True, cache_dir='data/cache'):
        """
        Initialize batch processor
        
        Args:
            use_cache (bool): Enable result caching
            cache_dir (str): Directory for cache files
        """
        self.fraud_detector = FraudDetector(use_segmentation=True)
        self.use_cache = use_cache
        self.cache_dir = cache_dir
        
        # Create cache directory
        if self.use_cache:
            os.makedirs(cache_dir, exist_ok=True)
        
        # Statistics
        self.stats = {
            'total_processed': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'fraud_detected': 0,
            'authentic': 0,
            'errors': 0,
            'total_time': 0
        }
        
        print("🚀 Batch Processor initialized")
        print(f"   📦 Caching: {'ENABLED' if use_cache else 'DISABLED'}")
        if use_cache:
            print(f"   📁 Cache directory: {cache_dir}")
    
    def _get_file_hash(self, file_path):
        """
        Calculate MD5 hash of file for cache key
        
        Args:
            file_path (str): Path to file
            
        Returns:
            str: MD5 hash of file content
        """
        hash_md5 = hashlib.md5()
        
        try:
            with open(file_path, "rb") as f:
                # Read file in chunks to handle large files
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            print(f"⚠️  Error calculating hash for {file_path}: {e}")
            return None
    
    def _get_cache_path(self, file_hash):
        """Get cache file path for a document hash"""
        return os.path.join(self.cache_dir, f"{file_hash}.json")
    
    def _load_from_cache(self, file_hash):
        """
        Load result from cache if available
        
        Args:
            file_hash (str): File hash (cache key)
            
        Returns:
            dict: Cached result or None if not found
        """
        if not self.use_cache:
            return None
        
        cache_path = self._get_cache_path(file_hash)
        
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r') as f:
                    cached_result = json.load(f)
                    self.stats['cache_hits'] += 1
                    return cached_result
            except Exception as e:
                print(f"⚠️  Error reading cache: {e}")
                return None
        
        self.stats['cache_misses'] += 1
        return None
    
    def _save_to_cache(self, file_hash, result):
        """
        Save result to cache
        
        Args:
            file_hash (str): File hash (cache key)
            result (dict): Analysis result to cache
        """
        if not self.use_cache:
            return
        
        cache_path = self._get_cache_path(file_hash)
        
        try:
            # Add cache metadata
            cached_result = {
                'result': result,
                'cached_at': datetime.now().isoformat(),
                'file_hash': file_hash
            }
            
            with open(cache_path, 'w') as f:
                json.dump(cached_result, f, indent=2)
        except Exception as e:
            print(f"⚠️  Error saving to cache: {e}")
    
    def process_single(self, file_path, verbose=False):
        """
        Process a single document (with caching)
        
        Args:
            file_path (str): Path to document
            verbose (bool): Print detailed results
            
        Returns:
            dict: Analysis result
        """
        # Calculate file hash
        file_hash = self._get_file_hash(file_path)
        
        if not file_hash:
            return {'error': 'Could not calculate file hash'}
        
        # Check cache
        cached_result = self._load_from_cache(file_hash)
        
        if cached_result:
            if verbose:
                print(f"   ⚡ Loaded from cache")
            return cached_result['result']
        
        # Process document
        if verbose:
            print(f"   🔍 Analyzing...")
        
        start_time = time.time()
        result = self.fraud_detector.analyze_document(file_path, verbose=verbose)
        processing_time = time.time() - start_time
        
        # Add processing metadata
        result['processing_time'] = processing_time
        result['processed_at'] = datetime.now().isoformat()
        result['file_path'] = file_path
        result['file_hash'] = file_hash
        
        # Save to cache
        self._save_to_cache(file_hash, result)
        
        return result
    
    def process_batch(self, file_paths, show_progress=True):
        """
        Process multiple documents with progress tracking
        
        Args:
            file_paths (list): List of document paths
            show_progress (bool): Show progress bar
            
        Returns:
            list: Results for all documents
        """
        print("\n" + "="*70)
        print("📦 BATCH PROCESSING")
        print("="*70)
        print(f"   Total documents: {len(file_paths)}")
        print(f"   Caching: {'ENABLED' if self.use_cache else 'DISABLED'}")
        print("="*70)
        
        results = []
        start_time = time.time()
        
        for i, file_path in enumerate(file_paths, 1):
            if show_progress:
                # Progress indicator
                percent = (i / len(file_paths)) * 100
                bar_length = 40
                filled = int(bar_length * i / len(file_paths))
                bar = '█' * filled + '░' * (bar_length - filled)
                
                print(f"\n[{i}/{len(file_paths)}] {bar} {percent:.1f}%")
                print(f"📄 {os.path.basename(file_path)}")
            
            try:
                # Process document
                result = self.process_single(file_path, verbose=False)
                
                # Update statistics
                self.stats['total_processed'] += 1
                
                if result.get('fraud_detected'):
                    self.stats['fraud_detected'] += 1
                    if show_progress:
                        print(f"   🚨 FRAUD DETECTED (confidence: {result['confidence']:.1f}%)")
                else:
                    self.stats['authentic'] += 1
                    if show_progress:
                        print(f"   ✅ AUTHENTIC (confidence: {result['confidence']:.1f}%)")
                
                results.append(result)
                
            except Exception as e:
                self.stats['errors'] += 1
                error_result = {
                    'file_path': file_path,
                    'error': str(e),
                    'fraud_detected': False
                }
                results.append(error_result)
                if show_progress:
                    print(f"   ❌ ERROR: {e}")
        
        total_time = time.time() - start_time
        self.stats['total_time'] = total_time
        
        # Print summary
        self._print_batch_summary(len(file_paths), total_time)
        
        return results
    
    def _print_batch_summary(self, total_docs, total_time):
        """Print batch processing summary"""
        print("\n" + "="*70)
        print("📊 BATCH PROCESSING COMPLETE")
        print("="*70)
        
        # Processing stats
        print(f"\n📈 Processing Statistics:")
        print(f"   Total documents: {self.stats['total_processed']}")
        print(f"   Fraud detected: {self.stats['fraud_detected']}")
        print(f"   Authentic: {self.stats['authentic']}")
        print(f"   Errors: {self.stats['errors']}")
        
        if self.stats['total_processed'] > 0:
            fraud_rate = (self.stats['fraud_detected'] / self.stats['total_processed']) * 100
            print(f"   Fraud rate: {fraud_rate:.1f}%")
        
        # Cache stats
        if self.use_cache:
            print(f"\n⚡ Cache Performance:")
            total_cache_ops = self.stats['cache_hits'] + self.stats['cache_misses']
            if total_cache_ops > 0:
                hit_rate = (self.stats['cache_hits'] / total_cache_ops) * 100
                print(f"   Cache hits: {self.stats['cache_hits']}")
                print(f"   Cache misses: {self.stats['cache_misses']}")
                print(f"   Hit rate: {hit_rate:.1f}%")
                
                if self.stats['cache_hits'] > 0:
                    time_saved = self.stats['cache_hits'] * 2.164  # Average processing time
                    print(f"   Time saved: {time_saved:.1f} seconds")
        
        # Performance stats
        print(f"\n⏱️  Performance:")
        print(f"   Total time: {total_time:.2f} seconds")
        print(f"   Average per document: {(total_time / total_docs):.2f} seconds")
        print(f"   Throughput: {(total_docs / total_time):.2f} documents/second")
        
        print("="*70 + "\n")
    
    def process_directory(self, directory_path, pattern='*.jpg', show_progress=True):
        """
        Process all documents in a directory
        
        Args:
            directory_path (str): Path to directory
            pattern (str): File pattern (e.g., '*.jpg', '*.png')
            show_progress (bool): Show progress
            
        Returns:
            list: Results for all documents
        """
        # Find all matching files
        path = Path(directory_path)
        file_paths = list(path.glob(pattern))
        
        if not file_paths:
            print(f"❌ No files found matching pattern: {pattern}")
            return []
        
        print(f"📁 Found {len(file_paths)} files in {directory_path}")
        
        # Convert to strings
        file_paths = [str(f) for f in file_paths]
        
        # Process batch
        return self.process_batch(file_paths, show_progress=show_progress)
    
    def save_results(self, results, output_file='data/batch_results.json'):
        """
        Save batch results to JSON file
        
        Args:
            results (list): Batch processing results
            output_file (str): Output file path
        """
        # Prepare output
        output = {
            'processed_at': datetime.now().isoformat(),
            'total_documents': len(results),
            'statistics': self.stats,
            'results': results
        }
        
        # Save to file
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"💾 Results saved to: {output_file}")
    
    def clear_cache(self):
        """Clear all cached results"""
        if not self.use_cache:
            print("⚠️  Caching is disabled")
            return
        
        cache_files = list(Path(self.cache_dir).glob('*.json'))
        
        for cache_file in cache_files:
            try:
                os.remove(cache_file)
            except Exception as e:
                print(f"⚠️  Error deleting {cache_file}: {e}")
        
        print(f"🗑️  Cleared {len(cache_files)} cache files")
    
    def get_cache_size(self):
        """Get total size of cache directory"""
        if not self.use_cache:
            return 0
        
        total_size = 0
        cache_files = list(Path(self.cache_dir).glob('*.json'))
        
        for cache_file in cache_files:
            total_size += os.path.getsize(cache_file)
        
        # Convert to MB
        size_mb = total_size / (1024 * 1024)
        
        print(f"📦 Cache size: {size_mb:.2f} MB ({len(cache_files)} files)")
        
        return size_mb


# Test function
def test_batch_processor():
    """Test the batch processor"""
    print("\n" + "="*70)
    print("🧪 TESTING BATCH PROCESSOR")
    print("="*70)
    
    # Initialize processor
    processor = BatchProcessor(use_cache=True)
    
    # Test with sample documents
    doc_folder = 'data/sample_documents'
    
    if not os.path.exists(doc_folder):
        print(f"❌ Directory not found: {doc_folder}")
        return
    
    # First run (no cache)
    print("\n1️⃣  FIRST RUN (Building cache)")
    results1 = processor.process_directory(doc_folder, pattern='*.jpg', show_progress=True)
    
    # Second run (with cache)
    print("\n2️⃣  SECOND RUN (Using cache)")
    processor2 = BatchProcessor(use_cache=True)
    results2 = processor2.process_directory(doc_folder, pattern='*.jpg', show_progress=True)
    
    # Save results
    processor2.save_results(results2)
    
    # Show cache size
    processor2.get_cache_size()
    
    print("\n✅ Batch processor test complete!")


if __name__ == "__main__":
    test_batch_processor()