"""Bird API exercise. Install dependencies: python -m pip install requests pandas"""

import pandas as pd
import requests


class Bird:
    image: str
    fact: str

    def __init__(self) -> None:
        self.image = ""
        self.fact = ""

    def fetch(self) -> bool:
        """Populate this bird and return True on success, False on failure."""
        try:
            response = requests.get(
                "https://some-random-api.com/animal/bird",
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()

            # Read and validate both fields before updating the object.
            image = data["image"]
            fact = data["fact"]
            if not isinstance(image, str) or not isinstance(fact, str):
                raise ValueError("image and fact must both be strings")

            self.image = image
            self.fact = fact

        except (ValueError, KeyError, TypeError) as error:
            # ValueError includes invalid JSON; KeyError catches missing keys.
            print(f"Invalid bird data: {error}")
            return False
        except requests.exceptions.RequestException as error:
            # Includes connection errors, timeouts, and HTTP errors.
            print(f"Bird request failed: {error}")
            return False

        print(f"Image: {self.image}")
        print(f"Fact: {self.fact}\n")
        return True


def main() -> None:
    rows = []

    for _ in range(3):
        bird = Bird()
        if bird.fetch():
            rows.append({"Image": bird.image, "Fact": bird.fact})

    # Explicit columns preserve the required names even if all fetches fail.
    df = pd.DataFrame(rows, columns=["Image", "Fact"])
    print("Bird Table (3 iterations):")
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
