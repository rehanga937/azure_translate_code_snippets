import os
import urllib.parse

from httpx import AsyncClient

from src.log_handling import myLogger


async def transliterate_to_sinhala(texts: list[str]) -> list[str]:
    """Transliterate romanized sinhala to sinhala. Uses Azure Translation service.

    Args:
        texts (list[str]): u can put multiple texts here

    Returns:
        list[str]: transliterated texts
    """
    session = AsyncClient()

    # When using the Azure Translate resource, there're 2 URLs that can be used.
    # 1. https://api.cognitive.microsofttranslator.com/
    # 2. https://<resource-name>.cognitiveservices.azure.com/
    # 
    # With the 1st URL, you can just append /transliterate or whatever and use the endpoint
    # With the 2nd URL, you must use the thing I have used below.
    # https://learn.microsoft.com/en-us/azure/ai-services/translator/text-translation/reference/v3/reference
    #
    # We anyway have to use the 2nd URL type if we want to use with an app service running inside a vnet.
    # (This is stated if u go to the translator resource in the portal -> Keys and Endpoint -> Virtual Network tab)

    url = urllib.parse.urljoin(os.getenv("AZURE_TRANSLATOR_ENDPOINT"), "translator/text/v3.0/translate")
    url = urllib.parse.urljoin(url, "transliterate")
    myLogger.debug(f"transliterate_to_sinhala url: {url}")

    request_params = { # https://api.cognitive.microsofttranslator.com/languages?api-version=3.0
        "api-version": "3.0",
        "language": "si",
        "fromScript": "Latn",
        "toScript": "Sinh",
    }

    headers = {
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Key": os.getenv("AZURE_TRANSLATOR_KEY"),
        "Ocp-Apim-Subscription-Region": os.getenv("AZURE_TRANSLATE_REGION"),
    }

    request_body = []
    for text in texts:
        request_body.append({"text": text})

    response = await session.post(
        url=url,
        params=request_params,
        headers=headers,
        json=request_body,
    )

    response = response.json()
    myLogger.debug(f"Response from azure transliterate: {response}")

    output = []
    for item in response:
        output.append(item['text'])

    await session.aclose()
    return output