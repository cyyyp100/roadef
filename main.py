import argparse

from roadef2027.baselines import random_baseline
from roadef2027.loader import load_instance_from_dir
from roadef2027.writer import write_solution


def main():
    parser = argparse.ArgumentParser(description="ROADEF 2007 Loader and Solver")
    parser.add_argument(
        "-i", "--data", required=True, help="Input instance directory"
    )
    parser.add_argument("-o", "--output-dir", required=True, help="Output directory")
    parser.add_argument("--method", choices=["random"], default="random")
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()

    instance = load_instance_from_dir(args.input_dir)

    if args.method == "random":
        solution = random_baseline(instance, seed=args.seed)

    write_solution(
        solution, args.output_dir, method=args.method, params={"seed": args.seed}
    )


if __name__ == "__main__":
    main()
