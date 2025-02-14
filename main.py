from fastapi import FastAPI, Query, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn

app = FastAPI()

# Data voor hulpmiddelen en vergoedingsstromen
hulpmiddelen_data = {
    "rolstoel": {"categorie": "mobiliteit", "vergoedingsopties": ["Zorgkantoor (WLZ)", "Wmo", "Particulier"]},
    "rollator": {"categorie": "mobiliteit", "vergoedingsopties": ["Wmo", "Particulier"]},
    "scootmobiel": {"categorie": "mobiliteit", "vergoedingsopties": ["Wmo", "Particulier"]},
    "AD-zitkussen": {"categorie": "decubituszorg", "vergoedingsopties": ["Zvw", "Particulier"]},
    "tillift": {"categorie": "tillen & transfers", "vergoedingsopties": ["WLZ", "Particulier"]},
    "sta-opstoel": {"categorie": "zithulpmiddelen", "vergoedingsopties": ["Particulier"]},
    "bedbeugel": {"categorie": "slaapondersteuning", "vergoedingsopties": ["Particulier"]}
}

# Model voor inputvalidatie
class HulpmiddelAdviesRequest(BaseModel):
    aandoening: str
    mobiliteitsbeperking: Optional[bool] = None
    medische_noodzaak: Optional[bool] = None
    woonsituatie: Optional[str] = Query(None, description="Zelfstandig of instelling?")
    vergoedingstype: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
        <head>
            <title>Hulpmiddelen Advies</title>
        </head>
        <body>
            <h2>Vraag hulpmiddelenadvies</h2>
            <form action="/advies" method="post">
                Aandoening: <input type="text" name="aandoening" required><br>
                Mobiliteitsbeperking? <input type="checkbox" name="mobiliteitsbeperking" value="true"><br>
                Medische noodzaak? <input type="checkbox" name="medische_noodzaak" value="true"><br>
                Woonsituatie:
                <select name="woonsituatie">
                    <option value="zelfstandig">Zelfstandig</option>
                    <option value="instelling">Instelling</option>
                </select><br>
                <input type="submit" value="Verstuur">
            </form>
        </body>
    </html>
    """

@app.post("/advies")
def geef_advies(
    aandoening: str = Form(...),
    mobiliteitsbeperking: Optional[str] = Form(None),
    medische_noodzaak: Optional[str] = Form(None),
    woonsituatie: Optional[str] = Form(None)
):
    """
    Bepaalt een passend hulpmiddel en de mogelijke vergoedingsroutes
    """
    aanbevolen_hulpmiddelen = []
    vergoedingsstromen = set()

    # Convert checkboxes to boolean values
    mobiliteitsbeperking = mobiliteitsbeperking == "true"
    medische_noodzaak = medische_noodzaak == "true"

    # Simpele beslislogica
    if mobiliteitsbeperking:
        aanbevolen_hulpmiddelen.append("rolstoel")
        aanbevolen_hulpmiddelen.append("AD-zitkussen")
        vergoedingsstromen.update(hulpmiddelen_data["rolstoel"]["vergoedingsopties"])
    elif aandoening.lower() in ["artrose", "spierziekte", "ouderdom"]:
        aanbevolen_hulpmiddelen.append("rollator")
        vergoedingsstromen.update(hulpmiddelen_data["rollator"]["vergoedingsopties"])
    elif woonsituatie and woonsituatie.lower() == "instelling":
        aanbevolen_hulpmiddelen.append("tillift")
        vergoedingsstromen.update(hulpmiddelen_data["tillift"]["vergoedingsopties"])
    
    if not aanbevolen_hulpmiddelen:
        return {"advies": "Geen passend hulpmiddel gevonden, neem contact op met een specialist."}
    
    return {
        "aanbevolen_hulpmiddelen": aanbevolen_hulpmiddelen,
        "mogelijke_vergoedingsstromen": list(vergoedingsstromen),
        "opvolgstap": "Neem contact op met een leverancier of gemeente voor verdere aanvraag."
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
