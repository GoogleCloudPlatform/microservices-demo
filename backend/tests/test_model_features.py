import os
import sys
import unittest


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_ROOT = os.path.join(REPO_ROOT, "backend")
for path in [REPO_ROOT, BACKEND_ROOT]:
    if path not in sys.path:
        sys.path.insert(0, path)

from anomaly_api.ingestion import Observation
from anomaly_api.model_features import (
    IF_FEATURES,
    LSTM_SEQUENCE_WINDOW,
    SEQUENCE_FEATURES,
    build_if_feature_vector,
    build_sequence_rows,
    rows_to_sequence_array,
)


class ModelFeatureTests(unittest.TestCase):
    def test_sequence_rows_and_if_vector_have_expected_shapes(self):
        window = []
        for idx in range(LSTM_SEQUENCE_WINDOW):
            window.append(
                Observation(
                    timestamp=float(idx),
                    service="frontend",
                    cpu_percent=10 + idx,
                    mem_percent=20 + idx,
                    mem_bytes=1000 + idx,
                    mem_limit_bytes=10000,
                    net_rx_mbps=0.1,
                    net_tx_mbps=0.2,
                    block_read_mbps=0.0,
                    block_write_mbps=0.0,
                    log_count=5 + idx,
                    error_count=1,
                    warn_count=0,
                    info_count=4 + idx,
                    error_rate=0.1,
                    warn_rate=0.0,
                    exception_count=0,
                    timeout_count=0,
                    template_entropy=0.2,
                    unique_templates=1,
                    new_templates_seen=0,
                    oom_mention_count=0,
                    avg_message_length=42.0,
                    log_volume_change_pct=0.0,
                    trace_count=2,
                    trace_error_count=0,
                    trace_duration_mean=1.5,
                )
            )

        rows = build_sequence_rows(window)
        sequence = rows_to_sequence_array(rows)
        if_vector = build_if_feature_vector(sequence)

        self.assertEqual(len(rows), LSTM_SEQUENCE_WINDOW)
        self.assertEqual(sequence.shape, (LSTM_SEQUENCE_WINDOW, len(SEQUENCE_FEATURES)))
        self.assertEqual(len(if_vector), len(IF_FEATURES))


if __name__ == "__main__":
    unittest.main()
