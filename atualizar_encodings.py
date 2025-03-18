import os
import pickle
import face_recognition

# Função para carregar os encodings salvos em um arquivo pickle
def carregar_encodings():
    """Carrega os encodings salvos em um arquivo pickle."""
    try:
        with open('encodings.pickle', 'rb') as f:
            encodings = pickle.load(f)
        return encodings
    except FileNotFoundError:
        return []  # Retorna uma lista vazia caso o arquivo não exista

# Função para salvar os encodings das imagens no arquivo pickle
def salvar_encodings(imagem_path, encoding):
    """Salva os encodings das faces em um arquivo pickle."""
    encodings = carregar_encodings()  # Carrega os encodings existentes, se houver.
    encodings.append((imagem_path, encoding))  # Adiciona o novo encoding
    with open('encodings.pickle', 'wb') as f:
        pickle.dump(encodings, f)

# Função para carregar e processar uma imagem
def carregar_face(imagem_path):
    """Carrega uma imagem e retorna os encodings das faces."""
    try:
        imagem = face_recognition.load_image_file(imagem_path)
        face_encodings = face_recognition.face_encodings(imagem)
        if not face_encodings:
            return None  # Nenhum rosto encontrado
        return face_encodings[0]  # Retorna o primeiro rosto detectado
    except Exception as e:
        print(f"Erro ao processar a imagem {imagem_path}: {e}")
        return None

# Função principal para atualizar os encodings no arquivo pickle
def atualizar_encodings():
    """Atualiza o arquivo encodings.pickle com os encodings das imagens na pasta 'imagens'."""
    # A pasta de imagens que está na raiz do projeto ****************************************************************
    pasta_imagens = 'imagens'  

    if not os.path.exists(pasta_imagens):
        print(f"A pasta {pasta_imagens} não existe.")
        return

    # Lista todas as imagens na pasta
    imagens = [f for f in os.listdir(pasta_imagens) if f.endswith(('.jpg', '.jpeg', '.png'))]
    
    if not imagens:
        print(f"Nenhuma imagem encontrada na pasta {pasta_imagens}.")
        return

    for imagem in imagens:
        caminho_imagem = os.path.join(pasta_imagens, imagem)
        encoding = carregar_face(caminho_imagem)

        if encoding is not None:
            salvar_encodings(caminho_imagem, encoding)
            print(f"Encoding salvo para a imagem {imagem}")
        else:
            print(f"Nenhum rosto encontrado na imagem {imagem}. Ignorando...")

# Executar a atualização dos encodings
if __name__ == "__main__":
    atualizar_encodings()
    print("Atualização de encodings concluída.")
