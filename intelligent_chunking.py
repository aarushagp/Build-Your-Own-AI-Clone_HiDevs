# 📚 IMPROVED INTELLIGENT TEXT CHUNKING PIPELINE

# ============================================
# 1️⃣ FIRST, LET'S EXTRACT TEXT FROM A PDF
# ============================================

import PyPDF2
import os
import re
# Global variable so other files can import it
chunks = []

def extract_pdf_text(pdf_path):
    """
    Extract text from a PDF file
    """
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return ""

    print(f"📄 Extracting text from: {pdf_path}")
    text = ""

    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            num_pages = len(reader.pages)
            print(f"   Found {num_pages} pages")

            for page_num in range(num_pages):
                page = reader.pages[page_num]
                page_text = page.extract_text()
                text += page_text + "\n\n"

                # Show progress
                if (page_num + 1) % 10 == 0:
                    print(f"   Processed {page_num + 1}/{num_pages} pages")

        print(f"✅ Successfully extracted {len(text):,} characters")
        return text

    except Exception as e:
        print(f"❌ Error extracting PDF: {e}")
        return ""

# ============================================
# 2️⃣ IMPROVED INTELLIGENT TEXT CHUNKER
# ============================================

print("🔧 Setting up IMPROVED Intelligent Text Chunker...")

class IntelligentTextSplitter:
    """An intelligent text splitter that preserves sentence and paragraph boundaries"""

    def __init__(self, chunk_size=500, chunk_overlap=100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def find_optimal_break_point(self, text, start, end):
        """Find the best place to break text within the given range"""
        # If we're near the end of text, just return end
        if end >= len(text) - 10:
            return end

        # Look for paragraph breaks first (highest priority)
        paragraph_break = text.rfind('\n\n', start, end)
        if paragraph_break != -1:
            return paragraph_break + 2  # Include the double newline

        # Look for sentence endings with proper punctuation
        # Try to find complete sentences
        sentence_patterns = [
    r'\.\s+[A-Z]',   # Period + space + capital
    r'!\s+[A-Z]',    # Exclamation + space + capital
    r'\?\s+[A-Z]',   # Question mark + space + capital
    r'\.\s*\n',      # Period + newline
    r'\.\s+[a-z]'    # Period + lowercase
]
        for pattern in sentence_patterns:
            matches = list(re.finditer(pattern, text[start:end]))
            if matches:
                # Get the last match
                match = matches[-1]
                return start + match.start() + 1  # Include the punctuation

        # Look for common break points
        break_points = [
            '. ', '! ', '? ',      # Sentence endings
            '.', '!', '?',   # Sentence endings with newline
            '; ', ';',             # Semicolons
            ': ', ':',             # Colons
            ', ', ',',             # Commas
            ' - ', ' – ', ' — ',   # Dashes
            ') ', '] ', '} ',      # Closing brackets
            ' ', '	',             # Whitespace
            '',                    # Last resort
        ]

        for break_point in break_points:
            break_pos = text.rfind(break_point, start, end)
            if break_pos != -1:
                return break_pos + len(break_point)

        # If no good break found, just break at the limit
        return end

    def split_text(self, text):
        """Split text into intelligent chunks with overlap"""
        # Clean and normalize the text
        text = text.replace('\n', '\n').replace('\r', '\n')

        # Remove excessive whitespace but keep paragraph breaks
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line:  # Keep non-empty lines
                cleaned_lines.append(line)
            elif cleaned_lines and cleaned_lines[-1] != '':  # Keep one empty line for paragraphs
                cleaned_lines.append('')

        text = '\n'.join(cleaned_lines)

        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            # Calculate target end position
            end = min(start + self.chunk_size, text_length)

            # If we have room and not at end, find optimal break point
            if end < text_length - 10:
                optimal_end = self.find_optimal_break_point(text, start, end)
                # Make sure we're making progress
                if optimal_end > start + (self.chunk_size // 2):
                    end = optimal_end

            # Extract the chunk
            chunk = text[start:end].strip()

            # Clean up the chunk
            if chunk:
                # Remove leading/trailing punctuation from chunk edges
                chunk = re.sub(r'^[,-:;.s]+', '', chunk)
                chunk = re.sub(r'[,-:;.s]+$', '', chunk)

                # Ensure chunk ends with reasonable punctuation if it's long enough
                if len(chunk) > 50 and not chunk[-1] in '.!?;:':
                    # Add ellipsis if we cut off mid-sentence
                    if not chunk.endswith('...'):
                        chunk = chunk + '...'

                chunks.append(chunk)

            # Calculate next start with overlap
            next_start = end - self.chunk_overlap

            # Ensure we're making progress
            if next_start <= start:
                next_start = start + (self.chunk_size // 2)

            start = min(next_start, text_length - 1)

            # Safety: prevent infinite loop
            if start >= text_length:
                break

        return chunks

# ============================================
# 3️⃣ IMPROVED FUNCTION TO CHUNK TEXT
# ============================================

def chunk_text_improved(text, chunk_size=500, chunk_overlap=100):
    """
    Split text into meaningful chunks with intelligent boundaries.
    """

    print(f"Starting IMPROVED chunking process...")
    print(f"   Chunk size: {chunk_size} characters")
    print(f"   Overlap: {chunk_overlap} characters")
    print(f"   Input text length: {len(text):,} characters")

    # Initialize the improved splitter
    splitter = IntelligentTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    # Perform the chunking
    chunks = splitter.split_text(text)

    # Analysis and reporting
    print(f"✅ Created {len(chunks)} chunks from the text")

    if chunks:
        # Calculate statistics
        chunk_lengths = [len(chunk) for chunk in chunks]
        avg_length = sum(chunk_lengths) / len(chunks)
        min_length = min(chunk_lengths)
        max_length = max(chunk_lengths)

        print(f"📊 IMPROVED CHUNK STATISTICS:")
        print(f"   • Average length: {avg_length:.1f} characters")
        print(f"   • Min length: {min_length} characters")
        print(f"   • Max length: {max_length} characters")
        print(f"   • Length distribution: {', '.join(map(str, chunk_lengths[:10]))}{'...' if len(chunks) > 10 else ''}")

        # Check text preservation
        original_length = len(text)
        chunked_length = sum(chunk_lengths)
        preservation_rate = (chunked_length / original_length) * 100

        print(f"   • Text preservation: {preservation_rate:.1f}%")

        if preservation_rate < 95:
            print(f"   ⚠️  {100-preservation_rate:.1f}% of text may be lost")
            print(f"   💡 Try reducing chunk_overlap or checking text cleaning")

    return chunks

# ============================================
# 4️⃣ VISUALIZE AND ANALYZE CHUNKS
# ============================================

def analyze_chunks(chunks, text, chunk_size):
    """Analyze and visualize chunk quality"""

    print("🔍 DETAILED CHUNK ANALYSIS:")
    print("-"*60)

    # Show each chunk with context
    for i, chunk in enumerate(chunks):
        print(f"📦 Chunk {i+1}/{len(chunks)}:")
        print(f"   Length: {len(chunk)} chars | Words: {len(chunk.split())}")

        # Show chunk boundaries in original text
        if i < len(chunks) - 1:
            # Find where this chunk ends in original text
            end_pos = text.find(chunk[-50:]) + 50 if len(chunk) >= 50 else text.find(chunk)
            if end_pos != -1 and end_pos < len(text):
                next_chars = text[end_pos:end_pos+20]
                print(f"   Next in text: '{next_chars}'")

        # Show preview
        preview = chunk[:100].replace('\n', '↲')
        if len(chunk) > 100:
            preview += "..."
        print(f"   Preview: {preview}")

        # Assess chunk quality
        quality_issues = []

        if len(chunk) < chunk_size * 0.3:
            quality_issues.append("Very short chunk")

        if not chunk.strip():
            quality_issues.append("Empty or whitespace-only")

        if chunk.startswith(('and ', 'but ', 'or ', 'the ', 'a ', 'an ')):
            quality_issues.append("Starts with conjunction/article")

        if chunk.endswith((' and', ' but', ' or', ' the', ' a', ' an')):
            quality_issues.append("Ends with conjunction/article")

        if quality_issues:
            print(f"   ⚠️  Issues: {', '.join(quality_issues)}")
        else:
            print(f"   ✅ Good quality")

    # Calculate overall quality metrics
    print("OVERALL QUALITY METRICS:")
    print("-"*40)

    well_formed = 0
    complete_sentences = 0

    for chunk in chunks:
        # Check if chunk starts with capital and ends with punctuation
        if chunk and chunk[0].isupper() and chunk[-1] in '.!?;':
            complete_sentences += 1

        # Check reasonable length
        if 50 <= len(chunk) <= chunk_size * 1.2:
            # Check doesn't start/end with broken words
            if not (chunk.startswith(' ') or chunk.endswith(' ')):
                well_formed += 1

    total_chunks = len(chunks)
    sentence_score = (complete_sentences / total_chunks) * 100
    formation_score = (well_formed / total_chunks) * 100

    print(f"   Complete sentences: {sentence_score:.1f}% ({complete_sentences}/{total_chunks})")
    print(f"   Well-formed chunks: {formation_score:.1f}% ({well_formed}/{total_chunks})")

    if formation_score >= 80:
        print("   ✅ Excellent chunk quality!")
    elif formation_score >= 60:
        print("   ⚠️  Acceptable chunk quality")
    else:
        print("   ❌ Poor chunk quality - consider adjusting parameters")

# ============================================
# 5️⃣ COMPLETE IMPROVED PIPELINE
# ============================================

def main_improved():
    """Complete improved PDF extraction and chunking pipeline"""

    # Example PDF path
    pdf_path = "ITI_AITechnologyStack.pdf"

    # Check if we have a PDF to process
    if not os.path.exists(pdf_path):
        print(f"⚠️ No PDF found at '{pdf_path}', using sample text instead")

        # Improved sample text with more natural breaks
        sample_text = """Natural Language Processing (NLP) is a subfield of artificial intelligence that focuses on the interaction between computers and human language. It enables machines to understand, interpret, and generate human language in a valuable way.

NLP combines computational linguistics with statistical, machine learning, and deep learning models. These technologies enable computers to process human language in the form of text or voice data and understand its full meaning, complete with the speaker or writer's intent and sentiment.

Key applications of NLP include:
1. Machine Translation (e.g., Google Translate)
2. Sentiment Analysis
3. Chatbots and Virtual Assistants
4. Text Summarization
5. Named Entity Recognition

The field has evolved significantly with the advent of deep learning and transformer models like BERT and GPT. These models have achieved state-of-the-art results on various NLP tasks by learning contextual representations of text.

Challenges in NLP include understanding context, sarcasm, idioms, and cultural nuances. Despite these challenges, NLP continues to advance rapidly and is becoming increasingly integrated into our daily lives through applications like smart assistants, recommendation systems, and automated customer service.

Future directions include more contextual understanding, better handling of low-resource languages, and more ethical AI systems that avoid biases present in training data.

The development of large language models has revolutionized how we approach NLP problems. With proper chunking and embedding, these models can provide powerful semantic search capabilities across large document collections."""

        pdf_text = sample_text
        print(f"📝 Using sample text ({len(pdf_text):,} characters)")
    else:
        # Extract text from real PDF
        pdf_text = extract_pdf_text(pdf_path)

    # Check if we have text to chunk
    if pdf_text and len(pdf_text.strip()) > 0:
        print("" + "="*60)
        print("🚀 APPLYING IMPROVED INTELLIGENT CHUNKING")
        print("="*60)

        # Try different chunking strategies
        strategies = [
            (300, 50, "Standard - balanced"),
            (400, 100, "Context-heavy - more overlap"),
            (250, 30, "Precise - less overlap"),
        ]

        best_chunks = None
        best_score = 0

        for chunk_size, overlap, description in strategies:
            print(f"Testing strategy: {description}")
            print(f"   Size: {chunk_size}, Overlap: {overlap}")

            chunks = chunk_text_improved(pdf_text, chunk_size, overlap)

            if chunks:
                # Simple quality score
                good_chunks = sum(1 for c in chunks if 100 <= len(c) <= chunk_size * 1.2)
                score = (good_chunks / len(chunks)) * 100

                print(f"   Quality score: {score:.1f}%")

                if score > best_score:
                    best_score = score
                    best_chunks = chunks
                    best_params = (chunk_size, overlap, description)

        print(f"🏆 BEST STRATEGY: {best_params[2]}")
        print(f"   Parameters: size={best_params[0]}, overlap={best_params[1]}")
        print(f"   Quality: {best_score:.1f}%")

        # Analyze the best chunks
        if best_chunks:
            analyze_chunks(best_chunks, pdf_text, best_params[0])

            # Show final chunks
            print("📋 FINAL CHUNKS:")
            print("-"*60)

            for i, chunk in enumerate(best_chunks[:10]):  # Show first 10
                print(f"[{i+1}] ({len(chunk)} chars):")
                print("-"*40)

                # Format chunk for display
                display_chunk = chunk.replace('\n', ' ↩ ')
                if len(display_chunk) > 120:
                    display_chunk = display_chunk[:120] + "..."
                print(display_chunk)

            if len(best_chunks) > 10:
                print(f"... and {len(best_chunks) - 10} more chunks")

        return best_chunks if best_chunks else []
    else:
        print("❌ No text available for chunking")
        return []

# ============================================
# 6️⃣ RUN THE IMPROVED PIPELINE
# ============================================

# ✅ Create chunks so other files can import it
chunks = main_improved()

if __name__ == "__main__":
    print("="*60)
    print("🔄 IMPROVED TEXT CHUNKING PIPELINE")
    print("="*60)

    # Final summary
    if chunks:
        print("" + "="*60)
        print("🎯 PIPELINE COMPLETE - CHUNKS READY FOR USE")
        print("="*60)

        print(f"📊 FINAL SUMMARY:")
        print(f"   • Total chunks created: {len(chunks)}")
        print(f"   • Total characters: {sum(len(c) for c in chunks):,}")
        print(f"   • Average chunk size: {sum(len(c) for c in chunks)/len(chunks):.1f} chars")

        print("🚀 NEXT STEPS:")
        print("   1. Generate embeddings for each chunk")
        print("   2. Store in vector database (FAISS, Pinecone, etc.)")
        print("   3. Implement semantic search")
        print("   4. Use with LLM for RAG applications")

        print("💡 TIPS FOR BETTER RESULTS:")
        print("   • Adjust chunk_size based on document type")
        print("   • Increase overlap for better context preservation")
        print("   • Clean text before chunking (remove headers/footers)")
        print("   • Consider sentence-based chunking for highly structured text")