import requests
import json
import time
from pathlib import Path

from tqdm import tqdm

headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
}

params = {
    "agg.synonyms": "true",
    "aggFilters": "docs:icf prot",
    "checkSpell": "true",
    "from": "0",
    "limit": "50",
    "fields": "OverallStatus,HasResults,BriefTitle,Condition,InterventionType,InterventionName,LocationFacility,LocationCity,LocationState,LocationCountry,LocationStatus,LocationZip,LocationGeoPoint,LocationContactName,LocationContactRole,LocationContactPhone,LocationContactPhoneExt,LocationContactEMail,CentralContactName,CentralContactRole,CentralContactPhone,CentralContactPhoneExt,CentralContactEMail,Gender,MinimumAge,MaximumAge,StdAge,NCTId,StudyType,LeadSponsorName,Acronym,EnrollmentCount,StartDate,PrimaryCompletionDate,CompletionDate,StudyFirstPostDate,ResultsFirstPostDate,LastUpdatePostDate,OrgStudyId,SecondaryId,Phase,LargeDocLabel,LargeDocFilename,PrimaryOutcomeMeasure,SecondaryOutcomeMeasure,DesignAllocation,DesignInterventionModel,DesignMasking,DesignWhoMasked,DesignPrimaryPurpose,DesignObservationalModel,DesignTimePerspective,LeadSponsorClass,CollaboratorClass",
    "columns": "conditions,interventions,collaborators",
    "highlight": "true",
    "sort": "@relevance",
}

response: dict = requests.get(
    "https://clinicaltrials.gov/api/int/studies", params=params, headers=headers
).json()

with open("output.json", "w", encoding="utf-8") as f:
    json.dump(response, f)

hits = response["hits"]

for hit in tqdm(hits):
    nctid: str = hit["id"]
    largeDocs: list[dict] = hit["study"]["documentSection"]["largeDocumentModule"]["largeDocs"]

    Path("icf").mkdir(parents=True, exist_ok=True)
    Path("prot").mkdir(parents=True, exist_ok=True)


    for doc in largeDocs:
        filename = doc["filename"]
        url = f"https://cdn.clinicaltrials.gov/large-docs/{nctid[-2:]}/{nctid}/{filename}"
        if "ICF" in filename:
            fp_write = Path("icf")
            with open(Path(fp_write, f"{nctid}_{filename}"), 'wb') as f:
                r = requests.get(url)
                f.write(r.content)
        if "Prot" in filename:
            fp_write = Path("prot")
            with open(Path(fp_write, f"{nctid}_{filename}"), 'wb') as f:
                r = requests.get(url)
                f.write(r.content)
        print(url)
        time.sleep(2)
