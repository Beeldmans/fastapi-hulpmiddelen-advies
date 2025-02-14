from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import Optional

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

@app.post("/advies")
def geef_advies(data: HulpmiddelAdviesRequest):
    """
    Bepaalt een passend hulpmiddel en de mogelijke vergoedingsroutes
    """
    aanbevolen_hulpmiddelen = []
    vergoedingsstromen = set()

    # Simpele beslislogica
    if data.mobiliteitsbeperking:
        aanbevolen_hulpmiddelen.append("rolstoel")
        aanbevolen_hulpmiddelen.append("AD-zitkussen")
        vergoedingsstromen.update(hulpmiddelen_data["rolstoel"]["vergoedingsopties"])
    elif data.aandoening.lower() in ["artrose", "spierziekte", "ouderdom"]:
        aanbevolen_hulpmiddelen.append("rollator")
        vergoedingsstromen.update(hulpmiddelen_data["rollator"]["vergoedingsopties"])
    elif data.woonsituatie and data.woonsituatie.lower() == "instelling":
        aanbevolen_hulpmiddelen.append("tillift")
        vergoedingsstromen.update(hulpmiddelen_data["tillift"]["vergoedingsopties"])
    
    if not aanbevolen_hulpmiddelen:
        return {"advies": "Geen passend hulpmiddel gevonden, neem contact op met een specialist."}
    
    return {
        "aanbevolen_hulpmiddelen": aanbevolen_hulpmiddelen,
        "mogelijke_vergoedingsstromen": list(vergoedingsstromen),
        "opvolgstap": "Neem contact op met een leverancier of gemeente voor verdere aanvraag."
    }

@app.get("/")
def root():
    return {"message": "Welkom bij de AI-hulpmiddelenadvies API"}
