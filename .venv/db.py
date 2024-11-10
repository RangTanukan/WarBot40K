import os
from dotenv import load_dotenv
import mongoengine as me

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("BACK4APP_DATABASE_URL")

if DATABASE_URL is None:
    raise ValueError(
        "DATABASE_URL is not defined. Make sure the .env file contains the BACK4APP_DATABASE_URL variable.")

# Connect to the MongoDB database
me.connect(host=DATABASE_URL)


class FAQ(me.Document):
    question = me.StringField(required=True, primary_key=True)
    answer = me.StringField(required=True)


def get_faq_answer(question):
    faq = FAQ.objects(question=question).first()
    return faq.answer if faq else None


def add_faq(question, answer):
    faq = FAQ(question=question, answer=answer)
    faq.save()


if __name__ == "__main__":
    # Add a FAQ to the test database
    add_faq("How do I configure MongoEngine?", "Follow the examples in the db.py file")

    # Retrieve and print the answer
    answer = get_faq_answer("How do I configure MongoEngine?")
    print(f"The answer is: {answer}")