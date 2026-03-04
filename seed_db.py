from datetime import datetime, timedelta
from random import choice, uniform, randint

from app import utils


def main():
    utils.create_db_if_missing()

    # create waiters
    waiters = [
        ("W001", "Alice"),
        ("W002", "Bob"),
        ("W003", "Carlos"),
        ("W004", "Diana"),
        ("W005", "Eve"),
        ("W006", "Frank"),
    ]

    with utils.SessionLocal() as s:
        for wid, name in waiters:
            existing = s.query(utils.Waiter).filter_by(waiter_id=wid).one_or_none()
            if not existing:
                s.add(utils.Waiter(waiter_id=wid, name=name, phone=""))
        s.commit()

    # generate transactions with varied ratings/feedback
    feedback_options = {
        5: ["Great service", "Excellent!", "Loved the attention"],
        4: ["Good service", "Pleasant experience"],
        3: ["Okay", "Average service"],
        2: ["Slow service", "Long wait"],
        1: ["Rude staff", "Terrible service"],
    }

    # recent dates
    base = datetime.utcnow()
    for wid, _ in waiters:
        # random count of tips per waiter
        count = randint(5, 15)
        for i in range(count):
            days_ago = randint(0, 30)
            rating = choice([1,2,3,4,5])
            amount = round(uniform(1.0, 20.0), 2)
            fb = choice(feedback_options[rating])
            sentiment = "POSITIVE" if rating >= 4 else ("NEGATIVE" if rating <= 2 else "NEUTRAL")
            # use append_tip compatibility helper
            utils.append_tip(wid, amount, rating, fb, sentiment)

    print("Database seeded: waiters and sample transactions added.")


if __name__ == "__main__":
    main()
