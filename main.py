import argparse
import sys
from src.pipeline import run_pipeline

def main():
    parser = argparse.ArgumentParser(
        description="Airline Passenger Satisfaction Prediction - ML Pipeline Entry Point"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config/config.yaml",
        help="Path to the YAML configuration file (default: config/config.yaml)"
    )
    args = parser.parse_args()
    
    try:
        run_pipeline(args.config)
    except Exception as e:
        print(f"\n[CRITICAL ERROR] Pipeline execution failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
