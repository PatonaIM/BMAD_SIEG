"""Token counting and cost estimation utilities."""

from decimal import Decimal

import structlog
import tiktoken

logger = structlog.get_logger()

# Pricing per 1 million tokens (as of October 2025)
PRICING_TABLE = {
    "gpt-4o-mini": {
        "input": Decimal("0.150"),  # $0.150 per 1M input tokens
        "output": Decimal("0.600"),  # $0.600 per 1M output tokens
    },
    "gpt-4": {
        "input": Decimal("30.00"),  # $30 per 1M input tokens
        "output": Decimal("60.00"),  # $60 per 1M output tokens
    },
    "gpt-4-turbo": {
        "input": Decimal("10.00"),  # $10 per 1M input tokens
        "output": Decimal("30.00"),  # $30 per 1M output tokens
    },
}


def count_tokens_for_messages(messages: list[dict[str, str]], model: str = "gpt-4o-mini") -> int:
    """
    Count tokens for a list of messages using tiktoken.

    This provides accurate token counting that matches OpenAI's billing.
    Essential for:
    - Cost tracking
    - Context window management
    - API usage monitoring

    Args:
        messages: List of message dicts with 'role' and 'content' keys
        model: Model name for encoding selection

    Returns:
        int: Total token count for all messages

    Example:
        messages = [
            {"role": "system", "content": "You are an interviewer"},
            {"role": "user", "content": "Tell me about React"}
        ]
        tokens = count_tokens_for_messages(messages, "gpt-4o-mini")
        # Returns: ~15 tokens
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        logger.warning(
            "model_not_found_using_default",
            model=model,
            default="cl100k_base",
        )
        encoding = tiktoken.get_encoding("cl100k_base")

    # Token counting logic per OpenAI's recommendations
    # Each message has overhead: <role> + <content> + message separators
    tokens_per_message = 3  # Role, content separator, and message end
    tokens_per_name = 1  # If name field is present

    num_tokens = 0

    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name

    # Add 3 tokens for reply priming
    num_tokens += 3

    logger.debug(
        "tokens_counted_for_messages",
        model=model,
        message_count=len(messages),
        total_tokens=num_tokens,
    )

    return num_tokens


def estimate_cost(
    input_tokens: int,
    output_tokens: int,
    model: str = "gpt-4o-mini"
) -> Decimal:
    """
    Estimate cost for API call based on token counts.

    Uses pricing table to calculate actual USD cost:
    - GPT-4o-mini: $0.150/1M input, $0.600/1M output
    - GPT-4: $30/1M input, $60/1M output

    Args:
        input_tokens: Number of prompt/input tokens
        output_tokens: Number of completion/output tokens
        model: Model name for pricing lookup

    Returns:
        Decimal: Estimated cost in USD

    Example:
        # For 1000 input + 500 output tokens on GPT-4o-mini:
        cost = estimate_cost(1000, 500, "gpt-4o-mini")
        # Returns: Decimal('0.00045')  # $0.00045
    """
    if model not in PRICING_TABLE:
        logger.warning(
            "model_pricing_not_found",
            model=model,
            available_models=list(PRICING_TABLE.keys()),
        )
        # Default to gpt-4o-mini pricing for unknown models
        model = "gpt-4o-mini"

    pricing = PRICING_TABLE[model]

    # Calculate costs (price is per 1M tokens)
    input_cost = (Decimal(input_tokens) / Decimal(1_000_000)) * pricing["input"]
    output_cost = (Decimal(output_tokens) / Decimal(1_000_000)) * pricing["output"]
    total_cost = input_cost + output_cost

    logger.debug(
        "cost_estimated",
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        input_cost_usd=float(input_cost),
        output_cost_usd=float(output_cost),
        total_cost_usd=float(total_cost),
    )

    return total_cost


def count_tokens_for_text(text: str, model: str = "gpt-4o-mini") -> int:
    """
    Count tokens in a plain text string.

    Args:
        text: Text string to count tokens for
        model: Model name for encoding selection

    Returns:
        int: Token count
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        logger.warning(
            "model_not_found_using_default",
            model=model,
            default="cl100k_base",
        )
        encoding = tiktoken.get_encoding("cl100k_base")

    tokens = encoding.encode(text)
    token_count = len(tokens)

    logger.debug(
        "tokens_counted_for_text",
        model=model,
        text_length=len(text),
        token_count=token_count,
    )

    return token_count


def get_model_pricing(model: str) -> dict[str, Decimal]:
    """
    Get pricing information for a specific model.

    Args:
        model: Model name

    Returns:
        Dict with 'input' and 'output' pricing per 1M tokens

    Raises:
        KeyError: If model not in pricing table
    """
    if model not in PRICING_TABLE:
        logger.error(
            "model_pricing_not_found",
            model=model,
            available_models=list(PRICING_TABLE.keys()),
        )
        raise KeyError(f"Pricing not available for model: {model}")

    return PRICING_TABLE[model]


def estimate_interview_cost(
    avg_message_length: int = 100,
    message_count: int = 20,
    model: str = "gpt-4o-mini"
) -> Decimal:
    """
    Estimate total cost for a complete interview session.

    Useful for budgeting and cost monitoring.

    Args:
        avg_message_length: Average tokens per message (default: 100)
        message_count: Expected number of exchanges (default: 20)
        model: Model to use

    Returns:
        Decimal: Estimated total cost in USD

    Example:
        # Estimate cost for typical interview:
        cost = estimate_interview_cost(
            avg_message_length=150,
            message_count=25,
            model="gpt-4o-mini"
        )
    """
    # Estimate total tokens (input ≈ output for conversational use)
    total_tokens = avg_message_length * message_count
    input_tokens = int(total_tokens * 0.6)  # 60% input (prompts + history)
    output_tokens = int(total_tokens * 0.4)  # 40% output (AI responses)

    cost = estimate_cost(input_tokens, output_tokens, model)

    logger.info(
        "interview_cost_estimated",
        model=model,
        message_count=message_count,
        avg_message_length=avg_message_length,
        estimated_cost_usd=float(cost),
    )

    return cost
