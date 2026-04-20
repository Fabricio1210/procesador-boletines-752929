from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
import boto3

app = FastAPI(title="Servicio Mostrador - 752929")

REGION = "us-east-1"
TABLE_NAME = "boletines_reporte"

dynamodb = boto3.resource('dynamodb', region_name=REGION)
tabla = dynamodb.Table(TABLE_NAME)

@app.get("/boletines/{boletinID}", response_class=HTMLResponse)
def mostrar_boletin(boletinID: str, correoElectronico: str = Query(...)):
    try:
        response = tabla.get_item(Key={'boletin_id': boletinID})
        item = response.get('Item')
        if not item:
            raise HTTPException(status_code=404, detail="Boletin no encontrado")
        if item['correo'] != correoElectronico:
            raise HTTPException(status_code=403, detail="El correo no coincide con el registro")
        tabla.update_item(
            Key={'boletin_id': boletinID},
            UpdateExpression="set leido = :l",
            ExpressionAttributeValues={':l': True}
        )
        html_content = f"""
        <html>
            <head><title>Visualizador de Boletín</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1>Boletín ID: {boletinID}</h1>
                <p><strong>Mensaje:</strong> {item['mensaje']}</p>
                <div style="margin: 20px 0;">
                    <img src="{item['url_imagen']}" style="max-width: 80%;">
                </div>
                <p>Link directo a S3: <a href="{item['url_imagen']}" target="_blank">{item['url_imagen']}</a></p>
                <br>
                <p style="color: green;">Estado: Boletin marcado como leído.</p>
            </body>
        </html>
        """
        return HTMLResponse(content=html_content)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("Servicio mostrador listo")
