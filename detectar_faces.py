import face_recognition
import os
import json
import sys
import pickle

# Função para carregar e salvar encodings de faces
def carregar_encodings():
    """Carrega os encodings salvos em um arquivo pickle."""
    try:
        with open('encodings.pickle', 'rb') as f:
            encodings = pickle.load(f)
        # Remover entradas de imagens que não existem mais
        encodings = [(path, encoding) for path, encoding in encodings if os.path.exists(path)]
        return encodings
    except FileNotFoundError:
        return []  # Retorna uma lista vazia caso o arquivo não exista

def salvar_encodings(imagem_path, encoding):
    """Salva os encodings das faces em um arquivo pickle."""
    encodings = carregar_encodings()  # Carrega os encodings existentes, se houver.

    # Verificar se a imagem já existe nos encodings e atualizar o caminho, caso necessário
    for i, (path, _) in enumerate(encodings):
        if path == imagem_path:
            encodings[i] = (imagem_path, encoding)  # Atualiza o caminho da imagem renomeada
            break
    else:
        encodings.append((imagem_path, encoding))  # Adiciona o novo encoding
    
    # Salvar os encodings no arquivo pickle
    with open('encodings.pickle', 'wb') as f:
        pickle.dump(encodings, f)

def remover_encoding(imagem_path):
    """Remove o encoding de uma imagem excluída."""
    encodings = carregar_encodings()
    encodings = [e for e in encodings if e[0] != imagem_path]  # Remove o encoding da imagem excluída
    with open('encodings.pickle', 'wb') as f:
        pickle.dump(encodings, f)

def carregar_face_temporaria(imagem_path):
    try:
        imagem = face_recognition.load_image_file(imagem_path)
        face_encodings = face_recognition.face_encodings(imagem)
        
        if not face_encodings:
            return None  # Nenhum rosto encontrado
        
        return face_encodings[0]
    except Exception as e:
        return {"error": f"Erro ao carregar imagem temporária: {str(e)}"}

def comparar_faces(imagem_temporaria_path, pasta):
    face_temp = carregar_face_temporaria(imagem_temporaria_path)
    
    if face_temp is None:
        return {"error": "Nenhum rosto encontrado na imagem capturada."}
    elif isinstance(face_temp, dict):
        return face_temp

    if not os.path.exists(pasta) or not os.path.isdir(pasta):
        return {"error": "Pasta de imagens inválida ou não encontrada."}

    imagens = [f for f in os.listdir(pasta) if f.endswith(('.jpg', '.jpeg', '.png'))]

    if not imagens:
        return {"error": "Nenhuma imagem encontrada na pasta especificada."}

    melhor_match = None
    menor_distancia = float('inf')

    # Carregar os encodings já armazenados
    encodings_salvos = carregar_encodings()

    # Verificar se o arquivo da imagem ainda existe
    encodings_salvos = [(path, encoding) for path, encoding in encodings_salvos if os.path.exists(path)]

    if not encodings_salvos:
        # Caso não existam encodings, processar todas as imagens da pasta
        for imagem in imagens:
            caminho_imagem = os.path.join(pasta, imagem)
            try:
                imagem_teste = face_recognition.load_image_file(caminho_imagem)
                face_encodings = face_recognition.face_encodings(imagem_teste)
                
                if not face_encodings:
                    continue  # Ignorar imagens sem rostos detectados

                for encoding in face_encodings:
                    distancia = face_recognition.face_distance([face_temp], encoding)[0]

                    if distancia < menor_distancia:
                        menor_distancia = distancia
                        melhor_match = imagem

                # Salvar os encodings para uso futuro
                salvar_encodings(caminho_imagem, face_encodings[0])

            except Exception as e:
                continue  # Segue para a próxima imagem
    else:
        # Caso existam encodings salvos, apenas comparar com os encodings
        for imagem_path, encoding in encodings_salvos:
            try:
                distancia = face_recognition.face_distance([face_temp], encoding)[0]
                if distancia < menor_distancia:
                    menor_distancia = distancia
                    melhor_match = imagem_path
            except Exception as e:
                continue  # Segue para a próxima imagem

    if melhor_match is not None:
        LIMIAR_CONFIRMACAO = 0.40
        status = "ALTA confiança" if menor_distancia <= LIMIAR_CONFIRMACAO else "REVISAO necessária"
        return {"imagem": melhor_match, "score": menor_distancia, "status": status}
    
    return {"mensagem": "Nenhuma correspondência encontrada."}

# Função para excluir a imagem
def excluir_imagem(imagem_path):
    """Remove a imagem e seu encoding"""
    if os.path.exists(imagem_path):
        os.remove(imagem_path)  # Exclui fisicamente a imagem
        remover_encoding(imagem_path)  # Remove o encoding da imagem do pickle

if __name__ == "__main__":
    try:
        if len(sys.argv) < 3:
            print(json.dumps({"error": "Parâmetros insuficientes"}))
            sys.exit(1)
        
        imagem_temporaria = sys.argv[1]
        pasta_imagens = sys.argv[2]

        resultado = comparar_faces(imagem_temporaria, pasta_imagens)

        print(json.dumps(resultado))
    except Exception as e:
        print(json.dumps({"error": f"Erro inesperado: {str(e)}"}))
