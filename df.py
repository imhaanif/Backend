from deepface import DeepFace


MODELS = [
    "VGG-Face",
    "Facenet",
    "Facenet512",
    "OpenFace",
    "DeepFace",
    "DeepID",
    "ArcFace",
    "Dlib",
    "SFace",
]
METRICS = ["cosine", "euclidean", "euclidean_l2"]
BACKENDS = ["opencv", "ssd", "dlib", "mtcnn", "retinaface", "mediapipe"]


# model: VGG-FACE
# distance_metric: euclidean
# detector_backend: retinaface and mtcnn
# enforce_detection: false


def face_verify(img1_path, img2_path):
    result = DeepFace.verify(
        img1_path=img1_path,
        img2_path=img2_path,
        detector_backend=BACKENDS[4],
        model_name=MODELS[6],
        distance_metric = metrics[0],
        enforce_detection=False,
    )
    return result


if "__main__" == __name__:
    result = face_verify("pic1.png", "chef.jpg")
    print(result)
#     df = DeepFace.find(img_path = "img_1.jpeg",
#       db_path = "/mnt/mydisk/Zprojs/Bawsala/backend",
#       enforce_detection = False,
#       model_name = models[0]
# )

# {'verified': True, 'distance': 0.13544194286037026, 'threshold': 0.6, 'model': 'VGG-Face', 'detector_backend': 'mtcnn', 'similarity_metric': 'euclidean'}
# hawairas  memoryview{'verified': True, 'distance': 0.5441585736570382, 'threshold': 0.6, 'model': 'VGG-Face', 'detector_backend': 'mtcnn', 'similarity_metric': 'euclidean'}
# me vs me different euclidean {'verified': True, 'distance': 0.4085475125053407, 'threshold': 0.6, 'model': 'VGG-Face', 'detector_backend': 'mtcnn', 'similarity_metric': 'euclidean'}


# me vs me differn cosine t {'verified': True, 'distance': 0.1934601939945556, 'threshold': 0.4, 'model': 'VGG-Face', 'detector_backend': 'mtcnn', 'similarity_metric': 'cosine'}
# me vs hawaras {'verified': False, 'distance': 0.4199423639498512, 'threshold': 0.4, 'model': 'VGG-Face', 'detector_backend': 'mtcnn', 'similarity_metric': 'cosine'}
# saem image {'verified': True, 'distance': 0.020796054731996305, 'threshold': 0.4, 'model': 'VGG-Face', 'detector_backend': 'mtcnn', 'similarity_metric': 'cosine'#}

# codsine works well 0.4 threshold
