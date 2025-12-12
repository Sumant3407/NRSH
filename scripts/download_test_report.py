import requests


# Function: main
def main():
    url = "http://localhost:8000/api/v1/reports/generate"
    data = {"analysis_id": "03b7e81c-8639-49ed-afbb-fdb1e2bd0c82", "report_type": "pdf"}
    try:
        r = requests.post(url, json=data, timeout=60)
        print("Status:", r.status_code)
        if r.status_code == 200:
            fname = "test_report_fixed.pdf"
            with open(fname, "wb") as f:
                f.write(r.content)
            print("Saved", fname, "size", len(r.content))
        else:
            print("Response:", r.text)
    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    main()
