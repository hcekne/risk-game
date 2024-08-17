import boto3
import json

client = boto3.client('bedrock-runtime', region_name='us-west-2')



def invoke_bedrock_model(model_id, prompt, max_gen_len=2000, 
                         temperature=0, top_p=1):
    input_data = {
        "modelId": model_id,
        "contentType": "application/json",
        "accept": "application/json",
        "body": json.dumps({
            "prompt": prompt,
            "max_gen_len": max_gen_len,
            "temperature": temperature,
            "top_p": top_p
        })
    }

    # Invoke the model
    response = client.invoke_model(
        contentType=input_data["contentType"], 
        body=input_data["body"],
        modelId=input_data["modelId"]
    )

    # Read the StreamingBody and decode it
    response_body = response["body"].read().decode("utf-8")

    # Parse the JSON response
    generated_text = json.loads(response_body).get('generation', '')
    cleaned_text = generated_text.replace('\n', ' ')
    return cleaned_text

data = invoke_bedrock_model("meta.llama3-1-405b-instruct-v1:0",
                            "Tell me about yourself")

print(data)
