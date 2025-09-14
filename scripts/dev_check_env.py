import os

REQUIRED = [
    "BFF_BACKEND_URL",
]


def main():
    missing = [k for k in REQUIRED if not os.getenv(k)]
    if missing:
        print("Missing env vars:", ", ".join(missing))
        raise SystemExit(1)
    print("Env looks ok")


if __name__ == "__main__":
    main()

