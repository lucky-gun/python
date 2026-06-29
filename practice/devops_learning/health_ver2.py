import json
import subprocess


RESTART_THRESHOLD = 10

READY_STATUS = "Ready"
RUNNING_STATUS = "Running"
CRASHLOOP_REASON = "CrashLoopBackOff"


def get_k8s_json(command):

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True
    )

    return json.loads(result.stdout)


def get_pods():

    return get_k8s_json(
        ["kubectl", "get", "pods", "-A", "-o", "json"]
    )


def get_nodes():

    return get_k8s_json(
        ["kubectl", "get", "nodes", "-o", "json"]
    )



def get_ready_nodes(node_data):

    ready_count = 0

    for node in node_data["items"]:

        for condition in node["status"]["conditions"]:

            if (
                condition.get("type") == READY_STATUS
                and
                condition.get("status") == "True"
            ):

                ready_count += 1
                break

    return ready_count, len(node_data["items"])


def get_running_pods(pod_data):

    running_count = 0

    for pod in pod_data["items"]:

        if pod["status"]["phase"] == RUNNING_STATUS:
            running_count += 1

    return running_count


def get_high_restart_pods(pod_data):

    restart_count = 0

    for pod in pod_data["items"]:

        container_statuses = pod["status"].get(
            "containerStatuses"
        )

        if (
            container_statuses
            and
            container_statuses[0]["restartCount"] >= RESTART_THRESHOLD
        ):

            restart_count += 1

    return restart_count


def get_crashloop_pods(pod_data):

    crash_count = 0

    for pod in pod_data["items"]:

        container_statuses = pod["status"].get(
            "containerStatuses"
        )

        if not container_statuses:
            continue

        state = container_statuses[0].get("state")

        if not state:
            continue

        waiting = state.get("waiting")

        if not waiting:
            continue

        reason = waiting.get("reason")

        if reason == CRASHLOOP_REASON:
            crash_count += 1

    return crash_count


def evaluate_status(
    ready_count,
    total_count,
    crash_count,
    restart_count
):

    if (
        ready_count != total_count
        or crash_count > 0
        or restart_count > 0
    ):
        return "FAIL"

    return "PASS"


def print_report(
    ready_count,
    total_count,
    running_count,
    restart_count,
    crash_count,
    status
    ):

    print("=" * 40)
    print(" Kubernetes Health Report")
    print("=" * 40)
    print()

    print(f"[INFO]  Ready Nodes         : {ready_count}/{total_count}")
    print(f"[INFO]  Running Pods        : {running_count}")
    print(f"[WARN]  High Restart Pods   : {restart_count}")
    print(f"[ERROR] CrashLoop Pods      : {crash_count}")

    print()

    print(f"Overall Status : {status}")


def main():

    node_data = get_nodes()
    pod_data = get_pods()

    ready_count, total_count = get_ready_nodes(node_data)

    running_count = get_running_pods(pod_data)

    restart_count = get_high_restart_pods(pod_data)

    crash_count = get_crashloop_pods(pod_data)

    status = evaluate_status(
        ready_count,
        total_count,
        crash_count,
        restart_count
    )

    print_report(
        ready_count,
        total_count,
        running_count,
        restart_count,
        crash_count,
        status
    )


if __name__ == "__main__":
    main()
