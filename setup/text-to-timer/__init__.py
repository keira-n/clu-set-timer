import logging
import os
import json
import azure.functions as func
from azure.ai.language.conversations import ConversationAnalysisClient
from azure.core.credentials import AzureKeyCredential

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
    except Exception as e:
        return func.HttpResponse(f"Invalid JSON: {str(e)}", status_code=400)

    text = req_body.get("text")
    if not text:
        return func.HttpResponse("Missing 'text' field in JSON body", status_code=400)

    key = os.environ["LANGUAGE_KEY"]
    endpoint = os.environ["LANGUAGE_ENDPOINT"]
    project_name = os.environ["CLU_PROJECT_NAME"]
    deployment_name = os.environ["CLU_DEPLOYMENT_NAME"]

    client = ConversationAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    task = {
        "kind": "Conversation",
        "analysisInput": {
            "conversationItem": {
                "text": text,
                "id": "1",
                "participantId": "user1"
            }
        },
        "parameters": {
            "projectName": project_name,
            "deploymentName": deployment_name,
            "stringIndexType": "Utf16CodeUnit"
        },
        "taskName": "conversationTask"
    }

    try:
        result = client.analyze_conversation(task)
    except Exception as e:
        logging.error(f"CLU request failed: {e}")
        return func.HttpResponse("Error calling CLU service", status_code=500)

    # The CLU response has 'result' and then 'prediction'
    prediction = result.get("result", {}).get("prediction", {})

    top_intent = prediction.get("topIntent")
    logging.info(f"Top intent: {top_intent}")

    if top_intent == "set timer":
        entities = prediction.get("entities", [])

        numbers = []
        time_units = []

        for entity in entities:
            category = entity.get("category", "").lower()
            if category == "number":
                # Extract integer value from resolutions
                for resolution in entity.get("resolutions", []):
                    if resolution.get("resolutionKind") == "NumberResolution":
                        try:
                            numbers.append(int(resolution.get("value", 0)))
                        except ValueError:
                            logging.warning("Failed to parse number value")
            elif category == "time unit":
                time_units.append(entity.get("text", "").lower())

        total_seconds = 0
        for i in range(min(len(numbers), len(time_units))):
            number = numbers[i]
            time_unit = time_units[i]

            if time_unit.startswith("minute"):
                total_seconds += number * 60
            else:
                total_seconds += number

        return func.HttpResponse(json.dumps({"seconds": total_seconds}), status_code=200, mimetype="application/json")

    logging.info("Intent not found or not handled")
    return func.HttpResponse(status_code=404)
