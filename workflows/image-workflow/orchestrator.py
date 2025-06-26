import requests
import base64
import json
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, Tuple

# Constants
GATEWAY: str = "http://172.16.44.202:8081/function"
LOGFILE: str = "workflow_log.jsonl"
REPEATS: int = 50


def invoke(function_name: str, payload: Dict[str, Any]) -> Tuple[Dict[str, Any], float]:
    """
    Sends a POST request to an OpenFaaS function and measures its execution time.

    Args:
        function_name (str): The name of the OpenFaaS function to invoke.
        payload (Dict[str, Any]): The JSON-serializable payload to send.

    Returns:
        Tuple[Dict[str, Any], float]: Parsed JSON response and execution duration in seconds.
    """
    start = time.time()
    response = requests.post(f"{GATEWAY}/{function_name}", json=payload)
    duration = time.time() - start
    response.raise_for_status()
    return response.json(), duration


def log(step: str, duration: float, iteration: int) -> None:
    """
    Logs a workflow step execution to a JSON Lines file.

    Args:
        step (str): Name of the function step.
        duration (float): Duration of the step in seconds.
        iteration (int): Iteration number of the workflow run.
    """
    entry = {
        "step": step,
        "duration": duration,
        "iteration": iteration,
        "timestamp": time.time()
    }
    with open(LOGFILE, "a") as f:
        f.write(json.dumps(entry) + "\n")


def run_iteration(iteration: int, image_b64: str) -> None:
    """
    Executes one full iteration of the synthetic workflow.

    Args:
        iteration (int): The current iteration number.
        image_b64 (str): The base64-encoded image to process.
    """
    # Step A: Resize image
    step_a, dur_a = invoke("resize-image", {"image_base64": image_b64})
    log("resize-image", dur_a, iteration)

    # Step B + C: Run edge detection and color analysis in parallel
    with ThreadPoolExecutor() as executor:
        f_edge = executor.submit(invoke, "edge-detect", step_a)
        f_color = executor.submit(invoke, "color-analysis", step_a)

        edge_result, dur_b = f_edge.result()
        color_result, dur_c = f_color.result()

    log("edge-detect", dur_b, iteration)
    log("color-analysis", dur_c, iteration)

    # Step D: Merge results
    merged_input = {
        "edges_base64": edge_result["edges_base64"],
        "color_histogram": color_result["color_histogram"]
    }
    merged, dur_d = invoke("merge-results", merged_input)
    log("merge-results", dur_d, iteration)

    # Step T: Transfer result (simulated network)
    _, dur_t = invoke("transfer-result", merged)
    log("transfer-result", dur_t, iteration)

    # Step E: Final output
    _, dur_e = invoke("result-output", merged)
    log("result-output", dur_e, iteration)


def main() -> None:
    """
    Main workflow loop that executes the full DAG for a specified number of repetitions.
    Each iteration is logged to disk for later statistical analysis.
    """
    with open("sample.jpg", "rb") as f:
        image_b64: str = base64.b64encode(f.read()).decode()

    for i in range(1, REPEATS + 1):
        print(f"🔁 Iteration {i}/{REPEATS}")
        try:
            run_iteration(i, image_b64)
        except Exception as e:
            print(f"⚠️ Error in iteration {i}: {e}")
            log("error", -1.0, i)


if __name__ == "__main__":
    main()
