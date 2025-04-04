import yaml
import requests
import time
import logging
import pprint
from collections import defaultdict

# Function to set up logging configs
def config_logging():
    logging.basicConfig(filename=f'./logs/monitor.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - Function: %(funcName)s - %(message)s')
    logging.info("Logging Set Successfully")

# Function to load configuration from the YAML file
def load_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

# Function to perform health checks
def check_health(endpoint):
    url = endpoint['url']
    method = endpoint.get('method', 'GET')
    headers = endpoint.get('headers')
    body = endpoint.get('body') 
    try:
        if body is not None and method in ["POST", "PUT", "PATCH"]: # Only send body for POST, PUT, PATCH requests per RFC 9110 (Which Postman obeys I learned)
            body = yaml.safe_load(body)
            response = requests.request(method, url, headers=headers, json=body)
        else:
            response = requests.request(method, url, headers=headers)
        response_ms = round(response.elapsed.total_seconds() * 1000)
        if 200 <= response.status_code < 300 and response.elapsed.total_seconds() * 1000 < 500 and response.elapsed.total_seconds() < 400:
            logging.warning(f"Endpoint: {url} is UP but response time is high: {response_ms} ms")
            return "UP"
        elif 200 <= response.status_code < 300 and response.elapsed.total_seconds() * 1000 < 500 and response.elapsed.total_seconds() < 400:
            logging.info(f"Endpoint: {url} is UP and response time is normal: {response_ms} ms")
        else:
            logging.info(f"Endpoint: {url} is DOWN with status code: {response.status_code} and response time: {response_ms} ms")
            return "DOWN"
            
    except requests.RequestException as e:
        logging.error(f"Endpoint: {url} is DOWN with exception: {e}")
        return "DOWN"
    
# Main function to monitor endpoints
def monitor_endpoints(file_path):
    config = load_config(file_path)
    domain_stats = defaultdict(lambda: {"up": 0, "total": 0})
    init_start_time = time.time()
    print("Started Monitoring")
    logging.info(f"Started monitoring at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(init_start_time))}")
    while True:
        start_time = time.time()
        for endpoint in config:
            domain = endpoint["url"].split("//")[-1]
            if ':' in domain:
                domain = endpoint["url"].split("//")[-1].split("/")[0].split(":")[0]
            else:
                domain = endpoint["url"].split("//")[-1].split("/")[0]
            result = check_health(endpoint)

            domain_stats[domain]["total"] += 1
            if result == "UP":
                domain_stats[domain]["up"] += 1

        # Log cumulative availability percentages
        for domain, stats in domain_stats.items():
            availability = round(100 * stats["up"] / stats["total"])
            print(f"{domain} has {availability}% availability percentage")

        print("---")
        elapsed_time = time.time() - start_time
        if elapsed_time < 15:
            time.sleep(15 - elapsed_time)

# Entry point of the program
if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python monitor.py <config_file_path>")
        sys.exit(1)
    config_logging()
    config_file = sys.argv[1]
    try:
        monitor_endpoints(config_file)
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")