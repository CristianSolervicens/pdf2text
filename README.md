## **pdf2text**

### Pequeña API que recibe un PDF codificado en Base64 y retorna el Texto Contenido en él

Tiene tres puntos de entrada:
* /test/   Para probar si la api está activa y borrar los pdf's intermedios si los hubiere. En general se borran de forma automática, pero siempre puede quedar algo por ahí.
* /pdf2text/  Para obtener el Texto 
* /pdfrepair/  Para reparar y obtener el texto, también entrega el PDF (Base64) reparado.


### **Entrada (json):**

**_Header requerido:_**
```
{'Content-Type': 'application/json'}
```
**_Payload (json):_**
```
{'pdf_base64': data}
```

### **Salida (json):**
```
{
    "text": "texto contenido en el pdf...",
    "error: "error encontrado",
    "repaired_pdf_base64": "Pdf en Base64"
}

"text": sólo cuando responde 200 - OK
"error": sólo cuando no responde 200 - OK
"repaired_pdf_base64": Sólo para "pdfrepair" con 200 - OK

````


**Ejemplo de llamada a "/_pdf2text_/"**
```python
response = requests.post(url, json={'pdf_base64': data}, headers={'Content-Type': 'application/json'})
if response.status_code == 200:
    print('Success!')
    js = response.json()
    if 'text' in js.keys():
        print(js['text'].strip())
else:
    print(js['error'])
```

**Ejemplo de llamada a "/_pdfrepair_/"**
```python
response = requests.post(url_repair, json={'pdf_base64': data}, headers={'Content-Type':'application/json'})
if response.status_code == 200:
    print('Success!')
    js = response.json()
    if 'text' in js.keys():
        print(js['text'].strip())
        print(js['repaired_pdf_base64'])
else:
    print(js['error'])
```

**Ejemplo de llamada a "/_test_/"**
```python
response = requests.get(test_url)
if response.status_code == 200:
    print(f"{test_url} says: <{response.json()['data']}>")
else:
    print("Service Error...")
    return
```

### **Autor** : Cristian Solervicéns C.
