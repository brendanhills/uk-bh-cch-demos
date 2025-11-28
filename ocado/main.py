import openai
from google.auth import default
import google.auth.transport.requests


# TODO(developer): Update and un-comment below lines
project_id = "uk-bh-experiments-argolis"
location = "us-central1"


# # Programmatically get an access token
credentials, _ = default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
credentials.refresh(google.auth.transport.requests.Request())
def openai_counter(client, number):
    print(f"Counting to: {number}")

    response = client.chat.completions.create(
    model="google/gemini-2.5-flash",
    messages=[
        {"role": "system", "content": "you are good at counting in many languages"},
        {"role": "user", "content": f"Count to {number} in French, Japanese, Mandardin, Arabic, and English.  Provide the output in words, not numbers "}
    ]
    )

    return(response.choices[0].message)


def main():
    # OpenAI Client
    client = openai.OpenAI(
    base_url=f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/endpoints/openapi",
    api_key=credentials.token
    )

    for i in range(100):
        message = openai_counter(client, i)

        print(f"{message=}")


if __name__ == "__main__":
    main()
