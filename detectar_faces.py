from flask import Flask, request, jsonify
import face_recognition

app = Flask(__name__)

@app.route('/compare', methods=['POST'])
def compare_faces():
    try:
        # Receber as imagens via formulário
        img1 = request.files['image1']
        img2 = request.files['image2']
        
        # Processamento das imagens
        image1 = face_recognition.load_image_file(img1)
        image2 = face_recognition.load_image_file(img2)

        # Comparar as imagens
        encoding1 = face_recognition.face_encodings(image1)
        encoding2 = face_recognition.face_encodings(image2)

        if encoding1 and encoding2:
            matches = face_recognition.compare_faces([encoding1[0]], encoding2[0])
            return jsonify({'match': matches[0]})
        else:
            return jsonify({'error': 'Faces não detectadas nas imagens.'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
