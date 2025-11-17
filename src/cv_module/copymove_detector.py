"""
Copy-Move Forgery Detection Module
Detects duplicated regions in documents (copy-paste fraud)
With semantic segmentation support to exclude text regions
"""

import cv2
import numpy as np


class CopyMoveDetector:
    """Detects copy-move forgery in document images"""
    
    def __init__(self, block_size=16, threshold=0.9):
        """
        Initialize detector
        
        Args:
            block_size (int): Size of blocks for comparison (16x16 pixels)
            threshold (float): Similarity threshold (0-1)
        """
        self.block_size = block_size
        self.threshold = threshold
    
    def _is_in_text_region(self, bx, by, text_regions, margin=5):
        """
        Check if a block overlaps with any text region
        
        Args:
            bx, by: Block top-left coordinates
            text_regions: List of (x, y, w, h) tuples
            margin: Extra margin around text regions
            
        Returns:
            bool: True if block is in text region
        """
        if not text_regions:
            return False
        
        block_right = bx + self.block_size
        block_bottom = by + self.block_size
        
        for tx, ty, tw, th in text_regions:
            # Add margin to text region
            text_left = tx - margin
            text_top = ty - margin
            text_right = tx + tw + margin
            text_bottom = ty + th + margin
            
            # Check for overlap
            if not (block_right < text_left or 
                   bx > text_right or 
                   block_bottom < text_top or 
                   by > text_bottom):
                return True
        
        return False
    
    def _extract_blocks(self, img, text_regions=None):
        """
        Extract blocks from image, excluding text regions
        
        Args:
            img: Grayscale image
            text_regions: List of (x, y, w, h) text regions to exclude
            
        Returns:
            dict: {position: block_features}
        """
        height, width = img.shape
        blocks = {}
        
        for y in range(0, height - self.block_size, self.block_size // 2):
            for x in range(0, width - self.block_size, self.block_size // 2):
                # Skip if in text region
                if self._is_in_text_region(x, y, text_regions):
                    continue
                
                block = img[y:y + self.block_size, x:x + self.block_size]
                
                # Skip if block is too small
                if block.shape[0] < self.block_size or block.shape[1] < self.block_size:
                    continue
                
                # Calculate block features
                std = np.std(block)
                mean = np.mean(block)
                
                # Enhanced filtering for uniform regions
                if std < 15:  # Increased threshold
                    continue
                
                # Filter out pure white/black regions
                if mean > 240 or mean < 15:
                    continue
                
                # Check for edge content (real structure vs uniform)
                edges = cv2.Laplacian(block, cv2.CV_64F)
                edge_intensity = np.std(edges)
                
                if edge_intensity < 5:  # Not enough structure
                    continue
                
                # Use block statistics as features
                features = (std, mean, edge_intensity)
                blocks[(x, y)] = features
        
        return blocks
    
    def detect(self, image_path, text_regions=None, visualize=False):
        """
        Detect copy-move forgery with optional text region exclusion
        
        Args:
            image_path (str): Path to image
            text_regions (list): List of (x, y, w, h) text regions to exclude
            visualize (bool): Whether to save visualization
            
        Returns:
            dict: Detection results
        """
        # Load and convert to grayscale
        img = cv2.imread(image_path)
        if img is None:
            return {
                'num_duplicates': 0,
                'duplicate_pairs': [],
                'text_regions_excluded': 0
            }
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Extract blocks (excluding text regions)
        blocks = self._extract_blocks(gray, text_regions)
        
        if len(blocks) < 2:
            return {
                'num_duplicates': 0,
                'duplicate_pairs': [],
                'text_regions_excluded': len(text_regions) if text_regions else 0
            }
        
        # Find similar blocks
        duplicate_pairs = []
        positions = list(blocks.keys())
        
        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                pos1, pos2 = positions[i], positions[j]
                features1, features2 = blocks[pos1], blocks[pos2]
                
                # Skip if blocks are too close (same region)
                distance = np.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
                if distance < self.block_size * 2:
                    continue
                
                # Compare features
                std_diff = abs(features1[0] - features2[0])
                mean_diff = abs(features1[1] - features2[1])
                edge_diff = abs(features1[2] - features2[2])
                
                # Similarity check (all features must match)
                if std_diff < 5 and mean_diff < 10 and edge_diff < 3:
                    duplicate_pairs.append((pos1, pos2))
        
        # Visualize if requested
        if visualize and duplicate_pairs:
            self._visualize_duplicates(img, duplicate_pairs, 
                                      f"{image_path.replace('.jpg', '_copymove.jpg')}")
        
        return {
            'num_duplicates': len(duplicate_pairs),
            'duplicate_pairs': duplicate_pairs,
            'text_regions_excluded': len(text_regions) if text_regions else 0
        }
    
    def _visualize_duplicates(self, img, duplicate_pairs, output_path):
        """Save visualization of detected duplicates"""
        vis = img.copy()
        
        for (x1, y1), (x2, y2) in duplicate_pairs[:10]:  # Show first 10
            cv2.rectangle(vis, (x1, y1), 
                         (x1 + self.block_size, y1 + self.block_size),
                         (0, 0, 255), 2)
            cv2.rectangle(vis, (x2, y2),
                         (x2 + self.block_size, y2 + self.block_size),
                         (255, 0, 0), 2)
        
        cv2.imwrite(output_path, vis)


# Test function
def test_copymove():
    """Test the copy-move detector"""
    import os
    
    detector = CopyMoveDetector()
    
    test_docs = [
        'data/sample_documents/authentic_doc.jpg',
        'data/sample_documents/fake_doc_copymove.jpg'
    ]
    
    print("\n" + "="*70)
    print("🧪 TESTING COPY-MOVE DETECTOR")
    print("="*70)
    
    for doc_path in test_docs:
        if os.path.exists(doc_path):
            print(f"\n📄 {os.path.basename(doc_path)}")
            result = detector.detect(doc_path, visualize=False)
            print(f"   Duplicates found: {result['num_duplicates']}")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    test_copymove()