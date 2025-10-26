from flask import Flask, jsonify, request
from pypdf import PdfReader, PdfWriter
import io
import os
import uuid
import pdfplumber
import base64


app = Flask(__name__)

@app.route('/test/', methods = ['GET'])
def home():
    if (request.method != 'GET'):
        return jsonify({'error': f'Invalid request method, only get, {request.method}'}), 405
    
    data = "PDF 2 Text is alive!!!"
    try:
        for x in os.listdir('.'):
            if os.path.isfile(x) and x.casefold().endswith('.pdf'):
                os.remove(x)
    except Exception as e:
        print(f"No temp pdf files to remove: {e}")
    return jsonify({'data': data})


@app.route('/pdf2text/', methods = ['POST'])
def pdf2text():
    if(request.method != 'POST'):
        return jsonify({'error': f'Invalid request method, only post, {request.method}'}), 405
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    # data = request.get_json()
    pdf_base64 = request.get_json().get('pdf_base64')
    print(f"Received pdf_base64 is {len(pdf_base64)} characters long")
    if not pdf_base64:
        return jsonify({'error': 'Missing pdf_base64 parameter'}), 400
    try:
        pdf_base64 = clean_base64_string(pdf_base64)
        if pdf_base64 == "Not a valid base64 PDF string":
            return jsonify({'error': 'Invalid base64 PDF string'}), 500
        else:
            print(f"Cleaned pdf_base64 is {len(pdf_base64)} characters long")
        
        pdf_bytes = base64_to_bytes(pdf_base64)
        if not pdf_bytes:
            return jsonify({'error': 'Failed to decode base64 PDF string'}), 500
        # else:
        #    print(f"Pdf64 is correctly decoded to byte_array {len(pdf_bytes)} bytes long")
        pdf_file_object = io.BytesIO(pdf_bytes)
        text = ""
        with pdfplumber.open(pdf_file_object) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                text += page.extract_text(x_tolerance=1, y_tolerance=1, layout=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    if text.strip() == "":
        return jsonify({'error': 'No text could be extracted from PDF'}), 400
    return jsonify({'text': text})


@app.route('/pdfrepair/', methods = ['POST'])
def pdf_repair():
    if(request.method != 'POST'):
        return jsonify({'error': f'Invalid request method, only post, {request.method}'}), 405
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    pdf_base64 = request.get_json().get('pdf_base64')
    print(f"Received pdf_base64 is {len(pdf_base64)} characters long")
    if not pdf_base64:
        return jsonify({'error': 'Missing pdf_base64 parameter'}), 400
    try:
        pdf_base64 = clean_base64_string(pdf_base64)
        if pdf_base64 == "Not a valid base64 PDF string":
            return jsonify({'error': 'Invalid base64 PDF string'}), 500
        else:
            print(f"Cleaned pdf_base64 is {len(pdf_base64)} characters long")
        
        pdf_bytes = base64_to_bytes(pdf_base64)
        if not pdf_bytes:
            return jsonify({'error': 'Failed to decode base64 PDF string'}), 500

        input_file_path = f'{str(uuid.uuid4())}.pdf'
        output_file_path = f'{str(uuid.uuid4())}.pdf'
        
        with open(input_file_path, 'wb') as f:
            f.write(pdf_bytes)
        
        repair_pdf_with_pypdf(input_file_path, output_file_path)

        if not os.path.exists(output_file_path):
            return jsonify({'error': 'PDF repair failed'}), 500

        with open(output_file_path, 'rb') as f:
            repaired_pdf_bytes = f.read()
        repaired_pdf_base64 = base64.b64encode(repaired_pdf_bytes).decode('utf-8')
        
        text = ""
        with pdfplumber.open(output_file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                text += page.extract_text(x_tolerance=1, y_tolerance=1, layout=True)
        
        if os.path.exists(output_file_path):
            os.remove(output_file_path)

    except Exception as e:
        if os.path.exists(output_file_path):
            os.remove(output_file_path)
        return jsonify({'error': str(e)}), 500
    
    if text.strip() == "":
        return jsonify({'error': 'No text could be extracted from PDF'}), 400
    
    return jsonify({'repaired_pdf_base64': repaired_pdf_base64, 'text': text})


def base64_to_bytes(b64_string):
    """Convert base64 string to bytes"""
    try:
        pdf_bytes = base64.b64decode(b64_string)
        return pdf_bytes
    except Exception as e:
        print(f"Error decoding base64 string: {e}")
        return None


def clean_base64_string(b64_string):
    """remove data URL prefix if present white spaces and new lines"""
    pdf_signature = 'JVBERi0xLjQKJ'
    pos = b64_string.find(pdf_signature)
    if pos != -1:
        b64_string = b64_string[pos:]
    else:
        return "Not a valid base64 PDF string"
    b64_string = b64_string.replace('data:application/pdf;base64,', '')
    b64_string = b64_string.replace(os.linesep, '')
    b64_string = b64_string.replace(' ', '')
    return b64_string


def repair_pdf_with_pypdf(input_file_path, output_file_path):
    """
    Attempts to repair a PDF file by reading and rewriting its content using pypdf.
    """
    try:
        reader = PdfReader(input_file_path)
        writer = PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        with open(output_file_path, 'wb') as output_file:
            writer.write(output_file)
        print(f"PDF successfully processed and saved to: {output_file_path}")
    except Exception as e:
        print(f"Error repairing PDF {input_file_path}: {e}")
    os.remove(input_file_path)


if __name__ == '__main__':
    app.run(debug = True)

# A-Za-a-z0-9+/=
# data:application/pdf;base64
# signature pdf base64: JVBERi0xLjQKJcfsj6IKNSAwIG9iago8PC9UeXBlIC9QYWdlL1BhcmVudCA0IDAgUi9SZXNvdXJjZXMgPDwvRm9udCA8PC9GMSA2IDAgUj4+Pj4vTWVkaWFCb3ggWzAgMCA2MTIgNzkyXT4+CmVuZG9iago2IDAgb2JqCjw8L1R5cGUgL0ZvbnQvU3VidHlwZSAvVHlwZTEvQmFzZUZvbnQgL0hlbHZldGljYS9FbmNvZGluZyAvV2luQW5zaUVuY29kaW5nPj4KZW5kb2JqCjcgMCBvYmoKPDwvVHlwZSAvUGFnZXMvS2lkcyBbNSAwIFJdL0NvdW50IDE+PgplbmRvYmoKNSAwIG9iago8PC9UeXBlIC9QYWdlL1BhcmVudCA0IDAgUi9SZXNvdXJjZXMgPDwvRm9udCA8PC9GMSA2IDAgUj4+Pj4vTWVkaWFCb3ggWzAgMCA2MTIgNzkyXT4+CmVuZG9iago0IDAgb2JqCjw8L1R5cGUgL1BhZ2VzL0tpZHNbNSAwIFJdL0NvdW50IDE+PgplbmRvYmoKMyAwIG9iago8PC9UeXBlIC9DYXRhbG9nL1BhZ2VzIDQgMCBSL0xhbmcgKGVuLVVTKQo+PgplbmRvYmoKMCAwIG9iago8PC9UeXBlIC9DYXRhbG9nL1BhZ2VzIDQgMCBSL0xhbmcgKGVuLVVTKQo+PgplbmRvYmoKeHJlZgowIDgKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDEwIDAwMDAwIG4gCjAw
