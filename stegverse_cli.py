import argparse

def main():
    parser = argparse.ArgumentParser(prog="stegverse")
    sub = parser.add_subparsers(dest="command")

    run = sub.add_parser("run")
    run.add_argument("demo")

    sub.add_parser("status")
    sub.add_parser("receipts")

    retrieve = sub.add_parser("retrieve")
    retrieve.add_argument("doc")

    args = parser.parse_args()

    if args.command == "run":
        print(f"Running {args.demo}")

    elif args.command == "status":
        print("System status")

    elif args.command == "receipts":
        print("Receipt chain")

    elif args.command == "retrieve":
        print(f"Retrieving {args.doc}")

if __name__ == "__main__":
    main()
