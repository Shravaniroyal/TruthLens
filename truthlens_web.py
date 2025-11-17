"""
TruthLens Web Interface - Enhanced Version
With example documents, batch processing, and result export
"""

import gradio as gr
import os
import json
from datetime import datetime
from src.fraud_detector import FraudDetector
from src.batch_processor import BatchProcessor
from pathlib import Path


# Initialize detector (only once, for speed)
print("🚀 Initializing TruthLens...")
fraud_detector = FraudDetector(use_segmentation=True)
batch_processor = BatchProcessor(use_cache=True)
print("✅ TruthLens ready!")


def analyze_document(image):
    """
    Analyze uploaded document
    
    Args:
        image: Uploaded image file (from Gradio)
        
    Returns:
        tuple: (result_text, confidence_html, details_html, json_output)
    """
    if image is None:
        return "⚠️ Please upload a document image", "", "", ""
    
    try:
        # Save temporary file
        temp_path = "temp_upload.jpg"
        image.save(temp_path)
        
        # Analyze using batch processor (uses cache)
        result = batch_processor.process_single(temp_path, verbose=False)
        
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        # Format results
        verdict = "🚨 FRAUD DETECTED" if result['fraud_detected'] else "✅ AUTHENTIC"
        confidence = result['confidence']
        
        # Main result
        result_text = f"""
# {verdict}

**Confidence:** {confidence:.1f}%

**Analysis completed at:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**Processing time:** {result.get('processing_time', 0):.2f} seconds
        """
        
        # Confidence gauge (HTML)
        color = "#dc2626" if result['fraud_detected'] else "#16a34a"
        confidence_html = f"""
        <div style="text-align: center; padding: 20px;">
            <div style="font-size: 64px; font-weight: bold; color: {color};">
                {confidence:.1f}%
            </div>
            <div style="font-size: 20px; color: #666; margin-top: 10px;">
                Confidence Level
            </div>
            <div style="width: 100%; background: #e5e7eb; border-radius: 10px; height: 40px; margin-top: 20px; overflow: hidden;">
                <div style="width: {confidence}%; background: {color}; height: 100%; transition: width 0.5s;"></div>
            </div>
        </div>
        """
        
        # Detection details (HTML) - BIGGER FONT
        ela_status = "🚨 Suspicious" if result['ela_suspicious'] else "✅ Clean"
        cm_status = "🚨 Suspicious" if result['copymove_suspicious'] else "✅ Clean"
        font_status = "🚨 Suspicious" if result['font_suspicious'] else "✅ Clean"
        
        details_html = f"""
        <div style="padding: 25px; background: #f9fafb; border-radius: 10px; font-size: 16px;">
            <h2 style="margin-top: 0; font-size: 24px;">📊 Detection Details</h2>
            
            <div style="margin: 20px 0; padding: 15px; background: white; border-radius: 8px;">
                <h3 style="font-size: 20px; margin-top: 0;">1️⃣ Error Level Analysis (ELA)</h3>
                <p style="font-size: 18px; margin: 5px 0;"><strong>Score:</strong> {result['ela_score']:.2f}/100</p>
                <p style="font-size: 18px; margin: 5px 0;"><strong>Status:</strong> {ela_status}</p>
            </div>
            
            <div style="margin: 20px 0; padding: 15px; background: white; border-radius: 8px;">
                <h3 style="font-size: 20px; margin-top: 0;">2️⃣ Copy-Move Detection</h3>
                <p style="font-size: 18px; margin: 5px 0;"><strong>Duplicates found:</strong> {result['copymove_duplicates']:,}</p>
                <p style="font-size: 18px; margin: 5px 0;"><strong>Status:</strong> {cm_status}</p>
                <p style="font-size: 16px; color: #666; margin: 5px 0;">Text regions excluded: {result['text_regions_excluded']}</p>
            </div>
            
            <div style="margin: 20px 0; padding: 15px; background: white; border-radius: 8px;">
                <h3 style="font-size: 20px; margin-top: 0;">3️⃣ Font Analysis</h3>
                <p style="font-size: 18px; margin: 5px 0;"><strong>Font variation:</strong> {result['font_variation']:.1f}%</p>
                <p style="font-size: 18px; margin: 5px 0;"><strong>Status:</strong> {font_status}</p>
            </div>
            
            <div style="margin-top: 25px; padding-top: 20px; border-top: 3px solid #e5e7eb;">
                <h3 style="font-size: 20px;">📋 Final Decision</h3>
                <p style="font-size: 18px;"><strong>{result['suspicious_count']}/3</strong> detectors flagged suspicious</p>
                <p style="font-size: 16px; color: #666;">Requires 2/3 agreement for fraud detection</p>
            </div>
            
            <div style="margin-top: 20px; padding: 20px; background: {'#fee2e2' if result['fraud_detected'] else '#dcfce7'}; border-radius: 8px; border-left: 4px solid {color};">
                <h3 style="font-size: 20px; margin-top: 0;">💡 Recommendation</h3>
                <p style="font-size: 16px; line-height: 1.6;">
                {'⚠️ This document shows signs of manipulation. Further verification recommended:<br/>• Request original document from source<br/>• Cross-reference with official records<br/>• Consider manual expert review' if result['fraud_detected'] else '✅ This document appears authentic based on AI analysis.<br/>• No significant manipulation detected<br/>• Consider as one verification tool in your process'}
                </p>
            </div>
        </div>
        """
        
        # JSON export
        json_output = json.dumps(result, indent=2)
        
        return result_text, confidence_html, details_html, json_output
        
    except Exception as e:
        error_msg = f"❌ Error analyzing document: {str(e)}"
        return error_msg, "", "", ""


def analyze_batch_documents(files):
    """Analyze multiple documents at once"""
    if not files or len(files) == 0:
        return "⚠️ Please upload at least one document", ""
    
    results_list = []
    file_paths = []
    
    try:
        # Files are already paths in batch mode
        file_paths = [f.name if hasattr(f, 'name') else f for f in files]
        
        # Process batch
        results = batch_processor.process_batch(file_paths, show_progress=False)
        
        # Clean up
        for path in file_paths:
            if os.path.exists(path):
                os.remove(path)
        
        # Format results
        fraud_count = sum(1 for r in results if r.get('fraud_detected', False))
        authentic_count = len(results) - fraud_count
        
        summary = f"""
# 📦 Batch Analysis Complete

**Total documents:** {len(results)}  
**Fraud detected:** {fraud_count} 🚨  
**Authentic:** {authentic_count} ✅  
**Fraud rate:** {(fraud_count/len(results)*100):.1f}%

---

## 📊 Individual Results:
        """
        
        for i, result in enumerate(results, 1):
            verdict = "🚨 FRAUD" if result.get('fraud_detected', False) else "✅ AUTHENTIC"
            confidence = result.get('confidence', 0)
            summary += f"\n**Document {i}:** {verdict} (Confidence: {confidence:.1f}%)"
        
        # JSON export for batch
        json_output = json.dumps(results, indent=2)
        
        return summary, json_output
        
    except Exception as e:
        return f"❌ Error in batch processing: {str(e)}", ""


def load_example_document(example_name):
    """Load example document"""
    examples_map = {
        "Bank Statement (Authentic)": "data/sample_documents/bank_statement_authentic.jpg",
        "Bank Statement (Fake)": "data/sample_documents/bank_statement_fake.jpg",
        "Contract (Authentic)": "data/sample_documents/contract_authentic.jpg",
        "Invoice (Mixed Fonts)": "data/sample_documents/contract_mixed_fonts.jpg"
    }
    
    file_path = examples_map.get(example_name)
    
    if file_path and os.path.exists(file_path):
        from PIL import Image
        return Image.open(file_path)
    
    return None


def get_cache_stats():
    """Get cache statistics"""
    try:
        cache_size = batch_processor.get_cache_size()
        cache_dir = batch_processor.cache_dir
        
        # Count cache files
        cache_files = len(list(Path(cache_dir).glob('*.json'))) if os.path.exists(cache_dir) else 0
        
        stats_html = f"""
        <div style="padding: 20px; background: #f0f9ff; border-radius: 10px; border-left: 5px solid #3b82f6;">
            <h3 style="margin-top: 0; color: #1e40af; font-size: 22px;">📦 Cache Statistics</h3>
            <div style="margin: 15px 0; font-size: 18px;">
                <p><strong>Cached documents:</strong> {cache_files}</p>
                <p><strong>Cache size:</strong> {cache_size:.2f} MB</p>
                <p><strong>Status:</strong> ⚡ Cache enabled (faster analysis on repeated documents)</p>
            </div>
        </div>
        """
        return stats_html
    except:
        return "<div>Cache statistics unavailable</div>"


def clear_cache_action():
    """Clear cache and return confirmation"""
    try:
        batch_processor.clear_cache()
        return "✅ Cache cleared successfully! Next analysis will build new cache."
    except Exception as e:
        return f"❌ Error clearing cache: {str(e)}"


# Create Gradio interface
with gr.Blocks(title="TruthLens - AI Document Fraud Detection", theme=gr.themes.Soft()) as demo:
    
    # Header
    gr.Markdown("""
    # 🔍 TruthLens
    ## AI-Powered Document Fraud Detection
    
    Upload documents to detect potential fraud using multimodal AI analysis.
    
    **Detects:** Image manipulation, copy-paste forgery, font inconsistencies
    """)
    
    # Tabs for different modes
    with gr.Tabs():
        
        # TAB 1: Single Document Analysis
        with gr.Tab("📄 Single Document"):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### 📤 Upload Document")
                    image_input = gr.Image(
                        type="pil",
                        label="Document Image",
                        height=400
                    )
                    
                    analyze_btn = gr.Button(
                        "🔍 Analyze Document",
                        variant="primary",
                        size="lg"
                    )
                    
                    gr.Markdown("### 📂 Or Try Examples")
                    example_dropdown = gr.Dropdown(
                        choices=[
                            "Bank Statement (Authentic)",
                            "Bank Statement (Fake)",
                            "Contract (Authentic)",
                            "Invoice (Mixed Fonts)"
                        ],
                        label="Select Example",
                        value=None
                    )
                    load_example_btn = gr.Button("📥 Load Example")
                    
                    gr.Markdown("""
                    **Supported:** JPG, PNG  
                    **Examples:** Bank statements, invoices, contracts
                    """)
                
                with gr.Column(scale=1):
                    gr.Markdown("### 📊 Analysis Results")
                    result_output = gr.Markdown(label="Verdict")
                    confidence_output = gr.HTML(label="Confidence")
                    details_output = gr.HTML(label="Details")
                    
                    with gr.Accordion("💾 Download Results (JSON)", open=False):
                        json_output = gr.Textbox(
                            label="JSON Output",
                            lines=10,
                            max_lines=20
                        )
                        download_btn = gr.Button("📥 Copy JSON")
        
        # TAB 2: Batch Processing
        with gr.Tab("📦 Batch Processing"):
            gr.Markdown("""
            ### Upload Multiple Documents
            Analyze multiple documents at once for efficient processing.
            """)
            
            batch_input = gr.File(
                label="Upload Documents (Multiple)",
                file_count="multiple",
                type="filepath"
            )
            
            analyze_batch_btn = gr.Button(
                "🔍 Analyze All Documents",
                variant="primary",
                size="lg"
            )
            
            batch_results = gr.Markdown(label="Batch Results")
            
            with gr.Accordion("💾 Download Batch Results (JSON)", open=False):
                batch_json_output = gr.Textbox(
                    label="JSON Output",
                    lines=15,
                    max_lines=30
                )
        
        # TAB 3: Information
        with gr.Tab("ℹ️ How It Works"):
            gr.Markdown("""
            ## 🔬 Detection Techniques
            
            TruthLens uses three advanced detection methods:
            
            ### 1️⃣ Error Level Analysis (ELA)
            - **What it detects:** Image compression artifacts
            - **How it works:** Recompresses the image and analyzes differences
            - **Indicates:** Potential Photoshop edits, digital manipulation
            - **Score:** 0-100 (higher = more suspicious)
            
            ### 2️⃣ Copy-Move Forgery Detection
            - **What it detects:** Duplicated regions in the document
            - **How it works:** Divides image into blocks, finds matching patterns
            - **Indicates:** Copy-pasted signatures, logos, or text
            - **Features:** Uses semantic segmentation to exclude legitimate text
            
            ### 3️⃣ Font Consistency Analysis
            - **What it detects:** Font variations across document
            - **How it works:** OCR analysis to identify font characteristics
            - **Indicates:** Mixed fonts (sign of tampering)
            - **Threshold:** >30% variation = suspicious
            
            ---
            
            ## ⚙️ System Specifications
            
            **Processing Speed:** ~2 seconds per document  
            **Throughput:** 0.46 documents/second  
            **Daily Capacity:** 39,927 documents  
            **Caching:** Enabled (repeat analysis is instant)
            
            **Optimal Parameters:**
            - Block size: 16×16 pixels
            - ELA quality: 95
            - Detection threshold: 5 duplicates
            - Segmentation: Enabled
            
            ---
            
            ## 🎯 Best Practices
            
            1. **Upload Quality:** Use high-resolution scans (300+ DPI)
            2. **File Format:** JPG or PNG (JPG preferred for ELA)
            3. **Verification:** Use AI as one tool, not sole decision maker
            4. **False Positives:** Some authentic documents may flag (especially synthetic)
            5. **Real Documents:** System performs best on scanned physical documents
            
            ---
            
            ## 📚 Research Foundation
            
            **Based on published research:**
            - Error Level Analysis (Krawetz, 2007)
            - Copy-Move Detection (Fridrich et al., 2003)
            - Font Analysis (OCR-based consistency checking)
            
            **M.Tech Project | IIIT Dharwad**
            """)
    
    # Settings accordion (below tabs)
    with gr.Accordion("⚙️ System Settings", open=False):
        cache_stats = gr.HTML(label="Cache Statistics")
        
        with gr.Row():
            refresh_cache_btn = gr.Button("🔄 Refresh Stats")
            clear_cache_btn = gr.Button("🗑️ Clear Cache")
        
        cache_message = gr.Textbox(label="Status", interactive=False)
        
        # Cache actions
        refresh_cache_btn.click(
            fn=get_cache_stats,
            outputs=cache_stats
        )
        
        clear_cache_btn.click(
            fn=clear_cache_action,
            outputs=cache_message
        )
    
    # Footer
    gr.Markdown("""
    ---
    **TruthLens v1.0.0** | M.Tech Project | IIIT Dharwad  
    ⚡ Powered by Computer Vision + Generative AI + Semantic Segmentation
    """)
    
    # Connect analyze button (single document)
    analyze_btn.click(
        fn=analyze_document,
        inputs=image_input,
        outputs=[result_output, confidence_output, details_output, json_output]
    )
    
    # Connect example loader
    load_example_btn.click(
        fn=load_example_document,
        inputs=example_dropdown,
        outputs=image_input
    )
    
    # Connect batch analysis
    analyze_batch_btn.click(
        fn=analyze_batch_documents,
        inputs=batch_input,
        outputs=[batch_results, batch_json_output]
    )
    
    # Load cache stats on startup
    demo.load(
        fn=get_cache_stats,
        outputs=cache_stats
    )


# Launch configuration
if __name__ == "__main__":
    print("\n" + "="*70)
    print("🌐 LAUNCHING TRUTHLENS WEB INTERFACE (ENHANCED)")
    print("="*70)
    print("\n🚀 Starting server...")
    print("📱 Interface will open in your default browser")
    print("🔗 Or manually visit: http://localhost:7860")
    print("\n💡 Press Ctrl+C to stop the server")
    print("\n✨ NEW FEATURES:")
    print("   • Example documents (one-click testing)")
    print("   • Batch processing (multiple documents)")
    print("   • JSON export (download results)")
    print("   • Bigger fonts (better readability)")
    print("="*70 + "\n")
    
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        show_error=True,
        inbrowser=True
    )