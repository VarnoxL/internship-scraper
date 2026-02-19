from datetime import datetime
from models import InternshipPosting


def main():
    posting = InternshipPosting(
        id="temp",
        source="demo",
        company="Google",
        title="Software Engineer Intern",
        location="United States",
        is_remote=True,
        url="https://example.com",
        date_posted=None,
        scraped_at=datetime.now(),
        tags=["python", "backend"],
    )

    posting.id = posting.compute_id()

    print(posting)


if __name__ == "__main__":
    main()
