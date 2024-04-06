from tenacity import retry, stop_after_attempt, retry_if_exception_type

from icds.settings import settings
from openai import OpenAI, APIConnectionError
import tiktoken


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


def max_tokens_for_model(model: str = settings.DEFAULT_MODEL) -> int:
    tokens_per_model = {
        "gpt-3.5-turbo": 16385
    }  # TODO: Build a more useful mapping of models to token limits
    return tokens_per_model.get(model, 8192)


def num_tokens_from_messages(messages, model=settings.DEFAULT_MODEL):
    encoding = tiktoken.encoding_for_model(model)
    return sum(
        len(encoding.encode(value))
        for message in messages
        for value in message.values()
    )


def truncate_tokens(
    messages: list[dict], model: str = settings.DEFAULT_MODEL
) -> list[dict]:
    # Truncate the last message, if needed, to make sure total tokens fit within the limit

    # First, reduce the limit by 5% to allow for some flexibility
    real_max_tokens = int(max_tokens_for_model(model) * 0.95)
    encoding = tiktoken.encoding_for_model(model)
    total_tokens = num_tokens_from_messages(messages, model)
    if total_tokens > real_max_tokens:
        last_message = messages[-1]
        tokens_to_remove = total_tokens - real_max_tokens
        encoded_last_message = encoding.encode(last_message["content"])
        truncated_last_message = encoding.decode(
            encoded_last_message[:-tokens_to_remove]
        )
        messages[-1]["content"] = truncated_last_message
    return messages


def analyse_commit(commit_info: str) -> tuple[str, str]:
    # TODO: Refactor this, so it supports other LLMs (e.g. Anthropic's Claude models)
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

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

    analysis = _ask_gpt(client, settings.DEFAULT_MODEL, truncate_tokens(messages))

    summarise_prompt = "Please summarise this analysis into a single line that can be used as an improved commit message. "

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "assistant", "content": analysis},
        {"role": "user", "content": summarise_prompt},
    ]

    summary = _ask_gpt(client, settings.DEFAULT_MODEL, truncate_tokens(messages))

    return analysis, summary
