import sys

def main():
    print("Hello from landing-ai!")
    print(f"sys.argv: {sys.argv}")
    print(f"sys.executable: {sys.executable}")
    print(f"sys.version: {sys.version}")
    print(f"sys.platform: {sys.platform}")
    print(f"sys.path: {sys.path}")
    print(f"sys.prefix: {sys.prefix}")
    print(f"sys.base_prefix: {sys.base_prefix}")
    print(f"sys.base_exec_prefix: {sys.base_exec_prefix}")


if __name__ == "__main__":
    main()
