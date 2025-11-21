from pathlib import Path

from sklearn.datasets import fetch_california_housing

def main() -> None:
    data = fetch_california_housing(as_frame=True)
    df = data.frame

    out_path = Path("data") / "california_housing.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"Saved dataset to {out_path.resolve()}")

if __name__ == "__main__":
    main()
