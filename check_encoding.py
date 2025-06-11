#для распознавания кодировки .env

import chardet

with open('.env', 'rb') as f:
    raw_data = f.read()
    result = chardet.detect(raw_data)
    print(f"Encoding: {result['encoding']}, Confidence: {result['confidence']}")
