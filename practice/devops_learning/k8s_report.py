from kubernetes import client
from kubernetes import config

RESTART_THRESHOLD = 10

READY_STATUS = "Ready"
RUNNING_STATUS = "Running"
CRASHLOOP_REASON = "CrashLoopBackOff"

def get_ready_nodes(node_list):
	ready_count = 0

	for node in node_list.items:
		for condition in node.status.conditions:
			if (condition.type == READY_STATUS 
				and 
			condition.status == "True") :
				ready_count += 1
				break

	return ready_count, len(node_list.items)

def get_running_pods(pod_list):

	running_count = 0

	for pod in pod_list.items:
		if (pod.status.phase == RUNNING_STATUS) :
			running_count += 1

	return running_count

def get_high_restart_pods(pod_list):

    restart_count = 0
    restart_pods = []

    for pod in pod_list.items:
        for status in pod.status.container_statuses or []:
            if status.restart_count >= RESTART_THRESHOLD:
                restart_count += 1
                restart_pods.append(
                    (
                        pod.metadata.namespace,
                        pod.metadata.name,
                        status.restart_count,
                    )
                )
                break

    return restart_count, restart_pods

def get_crashloop_pods(pod_list):

    crash_count = 0
    crash_pods = []

    for pod in pod_list.items:
        for status in pod.status.container_statuses or []:
            state = status.state

            if not state:
                continue

            waiting = state.waiting

            if not waiting:
                continue

            reason = waiting.reason

            if reason == CRASHLOOP_REASON:
                crash_count += 1
                crash_pods.append((pod.metadata.namespace,pod.metadata.name))
                break

    return crash_count, crash_pods

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

def print_report( ready_count,
	total_count,
	running_count,
	restart_count,
	restart_pods,
	crash_count,
	crash_pods,
	status):

	print("=" * 40)
	print(" Kubernetes Health Report")
	print("=" * 40)
	print()
	print(f"[INFO]  Ready Nodes        : {ready_count}/{total_count}")
	print(f"[INFO]  Running Pods       : {running_count}")
	print(f"[WARN]  High Restart Pods   : {restart_count}")
	print(f"[ERROR] CrashLoop Pods      : {crash_count}\n")

	print("-" * 40)
	print("High Restart Pod List\n")

	for namespace, name, restart in restart_pods:
		print(f"- {namespace}/{name} (Restart: {restart})")

	print()
	print("-" * 40)
	print("CrashLoop Pod List\n")

	for namespace, name in crash_pods:
                print(f"- {namespace}/{name}")

	print()
	print("-" * 40)
	print(f"\nOverall Status : {status}\n")

def main():

	config.load_kube_config()
	v1 = client.CoreV1Api()
	pod_list = v1.list_pod_for_all_namespaces()
	node_list = v1.list_node()
	
	ready_count, total_count = get_ready_nodes(node_list)
	running_count = get_running_pods(pod_list)
	restart_count,restart_pods = get_high_restart_pods(pod_list)
	crash_count,crash_pods = get_crashloop_pods(pod_list)

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
		restart_pods,
		crash_count,
		crash_pods,
		status
	)




if __name__ == "__main__":
	main()
