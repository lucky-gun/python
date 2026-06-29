import subprocess
import json


def get_k8s_json(command):

	result = subprocess.run(
		command,
		capture_output=True,
		text=True,
		check=True
	)

	return json.loads(result.stdout)

def get_ready_nodes():

	data = get_k8s_json(["kubectl", "get", "nodes", "-o", "json"])
	ready_node_count = 0

	for node in data["items"]:
		for condition in node["status"]["conditions"]:
			if (condition.get("type") == "Ready" and condition["status"] == "True"):
				ready_node_count += 1
				break

	return ready_node_count,len(data["items"])
	

def get_running_pods():

	data = get_k8s_json(["kubectl", "get", "pods", "-A", "-o", "json"])

	running_count = 0

	for pod in data["items"]:

		if pod["status"]["phase"] == "Running":
			running_count += 1

	return running_count


def get_high_restart_pods():

	data = get_k8s_json(["kubectl", "get", "pods", "-A", "-o", "json"])
        
	restart_pods_count = 0

	for pod in data["items"]:
		container_statuses = pod["status"].get("containerStatuses")
		if ( container_statuses and container_statuses[0]["restartCount"] >= 10) :
			restart_pods_count += 1

	return restart_pods_count

def get_crashloop_pods():

	data = get_k8s_json(["kubectl", "get", "pods", "-A", "-o", "json"])

	crashloop_pods_count = 0

	for pod in data["items"]:
		container_statuses = pod["status"].get("containerStatuses")
		if container_statuses:
			state = container_statuses[0].get("state")
			if state:
				waiting = state.get("waiting")
				if waiting:
					reason = waiting.get("reason")
					if reason == "CrashLoopBackOff" :
                        			crashloop_pods_count += 1

	return crashloop_pods_count

def evaluate_status(ready_count,total_count,crash_count,restart_count):

	result = "PASS"
	
	if ready_count != total_count:
		result = "FAIL"
	if crash_count > 0 :
		result = "FAIL"
	if restart_count > 0 :
		result = "FAIL"

	return result

def print_report(ready_count,total_count,running_count,crash_count,restart_count,status):
	print("="*20)
	print("Kubernetes Health Report")
	print("="*20)
	print(f"[INFO] Ready Nodes : {ready_count}/{total_count}")
	print(f"[INFO] Running Pods : {running_count}")
	print(f"[WARN] High Restart Pods : {restart_count}")
	print(f"[ERROR] CrashLoop Pods : {crash_count}")
	print()
	print(f"Overall Status : {status}")

def main():
	
	ready_node_count,total_node_count = get_ready_nodes()
	running_pod_count = get_running_pods()
	crash_pod_count = get_crashloop_pods()
	high_restart_pod_count = get_high_restart_pods()
	status = evaluate_status(ready_node_count,total_node_count,crash_pod_count,high_restart_pod_count)
	print_report(
		ready_node_count,
		total_node_count,
		running_pod_count,
		crash_pod_count,
		high_restart_pod_count,
		status
	)		
		
if __name__ == "__main__":
    	main()
