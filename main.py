import argparse


def factorial(n: int) -> int:
    """Compute the factorial of a non-negative integer."""
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Compute factorial of a number")
    parser.add_argument("number", type=int, help="Non-negative integer")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        result = factorial(args.number)
    except ValueError as exc:
        print(f"Error: {exc}")
        return
    print(f"Factorial of {args.number} is {result}")


if __name__ == "__main__":
    main()
