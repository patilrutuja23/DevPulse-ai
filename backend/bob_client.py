"""
IBM Bob Client - calls watsonx.ai REST API directly.
No SDK required — works on Python 3.9+.
"""

import os
import json
import requests


WATSONX_URL    = 'https://us-south.ml.cloud.ibm.com'
IAM_TOKEN_URL  = 'https://iam.cloud.ibm.com/identity/token'


def _get_iam_token(api_key: str) -> str:
    """Exchange IBM Cloud API key for a short-lived IAM bearer token."""
    resp = requests.post(
        IAM_TOKEN_URL,
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        data={
            'grant_type': 'urn:ibm:params:oauth:grant-type:apikey',
            'apikey': api_key,
        },
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()['access_token']


class BobClient:
    def __init__(self):
        self.api_key    = os.getenv('WATSONX_API_KEY')
        self.project_id = os.getenv('WATSONX_PROJECT_ID')
        self.model_id   = os.getenv('WATSONX_MODEL_ID', 'ibm/granite-34b-code-instruct')

        if not self.api_key or not self.project_id:
            raise EnvironmentError(
                'WATSONX_API_KEY and WATSONX_PROJECT_ID must be set in .env'
            )

        self._token: str | None = None
        print('✓ IBM Bob (watsonx REST) ready')

    def _token_headers(self) -> dict:
        """Return auth headers, refreshing the IAM token if needed."""
        if not self._token:
            self._token = _get_iam_token(self.api_key)
        return {
            'Authorization': f'Bearer {self._token}',
            'Content-Type':  'application/json',
            'Accept':        'application/json',
        }

    def ask(self, prompt: str) -> dict:
        """
        Send prompt to IBM Bob (watsonx.ai), return parsed JSON dict.
        Auto-refreshes IAM token on 401.
        """
        payload = {
            'model_id':   self.model_id,
            'project_id': self.project_id,
            'input':      prompt,
            'parameters': {
                'decoding_method':    'greedy',
                'max_new_tokens':     2000,
                'min_new_tokens':     1,
                'temperature':        0.1,
                'repetition_penalty': 1.0,
            },
        }

        url = f'{WATSONX_URL}/ml/v1/text/generation?version=2023-05-29'

        resp = requests.post(url, headers=self._token_headers(), json=payload, timeout=60)

        # Token expired — refresh once and retry
        if resp.status_code == 401:
            self._token = _get_iam_token(self.api_key)
            resp = requests.post(url, headers=self._token_headers(), json=payload, timeout=60)

        resp.raise_for_status()
        raw = resp.json()['results'][0]['generated_text'].strip()

        # Strip markdown fences
        cleaned = raw
        for fence in ('```json', '```'):
            if cleaned.startswith(fence):
                cleaned = cleaned[len(fence):]
        if cleaned.endswith('```'):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Try to extract first {...} block
            start = cleaned.find('{')
            end   = cleaned.rfind('}')
            if start != -1 and end != -1:
                try:
                    return json.loads(cleaned[start:end + 1])
                except json.JSONDecodeError:
                    pass
            raise ValueError(f'Bob returned non-JSON: {cleaned[:300]}')


# Singleton
_bob: BobClient | None = None


def get_bob() -> BobClient:
    global _bob
    if _bob is None:
        _bob = BobClient()
    return _bob
