import time

from src.telemetry.logger import logger


class PerformanceTracker:
    """Tracking industry-standard metrics for LLMs."""

    def __init__(self, cost_table: dict[str, tuple[float, float]]):
        """Initialize a performance tracker.

        Params:
        - cost_table: a dict containing models cost per 1M tokens.
          Format: { model_name: (cost per 1M input tokens, cost per 1M output tokens) }.
        """
        self.session_metrics = []
        self.cost_table = cost_table

    def track_request(
        self,
        provider: str,
        model: str,
        usage: dict[str, int],
        latency_ms: int,
    ) -> None:
        """Logs a single request metric to our telemetry."""
        metric = {
            'provider': provider,
            'model': model,
            'prompt_tokens': usage.get('prompt_tokens', 0),
            'completion_tokens': usage.get('completion_tokens', 0),
            'total_tokens': usage.get('total_tokens', 0),
            'latency_ms': latency_ms,
            'cost_estimate': self._calculate_cost(
                model,
                usage,
            ),
        }
        self.session_metrics.append(metric)
        logger.log_event('LLM_METRIC', metric)

    def _calculate_cost(self, model: str, usage: dict[str, int]) -> float:
        input_price, output_price = self.cost_table.get(model, (0, 0))
        return (
            usage.get('input_tokens', 0) / 1_000_000 * input_price
            + usage.get('output_tokens', 0) / 1_000_000 * output_price
        )


# Global tracker instance
