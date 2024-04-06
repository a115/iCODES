from tenacity import retry, stop_after_attempt, retry_if_exception_type

from settings import settings
from openai import OpenAI, APIConnectionError


@retry(
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(APIConnectionError),
)
def _ask_gpt(client, model, messages):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
    )
    analysis = response.choices[0].message.content
    return analysis


def analyse_commit(commit_info: str) -> tuple[str, str]:
    # TODO: Refactor this, so it supports other LLMs (e.g. Anthropic's Claude models)
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    model = "gpt-3.5-turbo"

    system_prompt = """
    You are an experienced software engineer reviewing a commit on a git repository. Please carefully analyse the 
    commit and provide a summary of the key changes. Try your best to also infer the intent behind the changes, given 
    the available context. 
    """  # TODO: Chuck the project's README in here for context?

    prompt = (
        "Please summarise the key changes in this commit and infer the intent behind the changes: "
        + commit_info
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
    ]

    analysis = _ask_gpt(client, model, messages)

    # Call the LLM one more time to summarise the analysis into a single line that can be used as an improved commit message
    summarise_prompt = "Please summarise this analysis into a single line that can be used as an improved commit message. "

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "assistant", "content": analysis},
        {"role": "user", "content": summarise_prompt},
    ]

    summary = _ask_gpt(client, model, messages)

    return analysis, summary
