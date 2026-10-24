import json, os, sys
import xml.etree.ElementTree as ET

# read XML file, return {redis_key: value} for everything
def load_entries(path):
    root = ET.parse(path).getroot()

    subdomains = [(e.text or "").strip() for e in root.findall("./subdomains/subdomain")]
    entries = {"subdomains": json.dumps(subdomains)}

    for cookie in root.findall("./cookies/cookie"):
        key = f"cookie:{cookie.get('name')}:{cookie.get('host')}"
        entries[key] = (cookie.text or "").strip()

    return entries


def main(argv, redis_client=None):
    verbose = "-v" in argv
    paths = [a for a in argv if a != "-v"]

    if len(paths) != 1:
        print("Usage: export_to_redis.py [-v] /path/to/xml")
        return 2

    try:
        entries = load_entries(paths[0])
        if redis_client is None:
            import redis
            redis_client = redis.Redis(host=os.environ.get("REDIS_HOST", "localhost"))
        redis_client.mset(entries)
    except Exception as error:
        print(f"Error: {error}")
        return 1

    if verbose:
        for key, value in entries.items():
            print(f"{key} = {value}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
