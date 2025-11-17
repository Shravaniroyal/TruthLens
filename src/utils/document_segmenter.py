"""
Document Segmentation Module
Identifies text regions in documents to exclude from Copy-Move detection
"""

import cv2
import pytesseract

# Configure Tesseract path (Windows)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


class DocumentSegmenter:
    """Segments documents to identify text regions"""
    
    def __init__(self):
        """Initialize the segmenter"""
        # Verify Tesseract is available
        try:
            pytesseract.get_tesseract_version()
            print("✅ Tesseract found at:", pytesseract.pytesseract.tesseract_cmd)
        except Exception as e:
            print(f"❌ Tesseract not found: {e}")
            raise
    
    def get_text_regions(self, image_path, min_confidence=30):
        """
        Detect text regions in document using OCR
        
        Args:
            image_path (str): Path to document image
            min_confidence (int): Minimum OCR confidence (0-100)
            
        Returns:
            list: List of text bounding boxes as (x, y, w, h) tuples
        """
        # Load image
        img = cv2.imread(image_path)
        if img is None:
            return []
        
        # Convert to RGB for Tesseract
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Get detailed OCR data
        try:
            data = pytesseract.image_to_data(rgb, output_type=pytesseract.Output.DICT)
        except Exception as e:
            print(f"⚠️  OCR failed: {e}")
            return []
        
        # Extract text regions with sufficient confidence
        text_regions = []
        n_boxes = len(data['text'])
        
        for i in range(n_boxes):
            # Only process entries with text and sufficient confidence
            if int(data['conf'][i]) > min_confidence:
                text = data['text'][i].strip()
                if text:  # Non-empty text
                    x = data['left'][i]
                    y = data['top'][i]
                    w = data['width'][i]
                    h = data['height'][i]
                    
                    # Only add valid boxes
                    if w > 0 and h > 0:
                        text_regions.append((x, y, w, h))
        
        return text_regions
    
    def visualize_text_regions(self, image_path, output_path='text_regions_debug.jpg'):
        """
        Visualize detected text regions (for debugging)
        
        Args:
            image_path (str): Path to document image
            output_path (str): Path to save visualization
        """
        img = cv2.imread(image_path)
        if img is None:
            return
        
        text_regions = self.get_text_regions(image_path)
        
        # Draw rectangles around text regions
        for x, y, w, h in text_regions:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Add count text
        cv2.putText(img, f"Text Regions: {len(text_regions)}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        cv2.imwrite(output_path, img)
        print(f"✅ Visualization saved: {output_path}")
        print(f"   Text regions detected: {len(text_regions)}")


# Test function
def test_segmenter():
    """Test the document segmenter"""
    import os
    
    segmenter = DocumentSegmenter()
    
    # Test on available documents
    test_docs = [
        'data/sample_documents/authentic_doc.jpg',
        'data/sample_documents/advanced_bank_authentic.jpg',
        'data/sample_documents/fake_doc_copymove.jpg'
    ]
    
    for doc_path in test_docs:
        if os.path.exists(doc_path):
            print(f"\n📄 Testing: {doc_path}")
            text_regions = segmenter.get_text_regions(doc_path)
            print(f"   Found {len(text_regions)} text regions")
            
            # Show first 5 regions
            for i, (x, y, w, h) in enumerate(text_regions[:5]):
                print(f"   Region {i+1}: x={x}, y={y}, w={w}, h={h}")
            
            # Save visualization
            output = doc_path.replace('.jpg', '_text_regions.jpg')
            segmenter.visualize_text_regions(doc_path, output)


if __name__ == "__main__":
    test_segmenter()