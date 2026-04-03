from database.mongodb import MongoDB

def check():
    db = MongoDB()
    try:
        count = db.interviews.count_documents({})
        print(f"Total interviews in DB: {count}")
        latest = db.interviews.find().sort("created_at", -1).limit(1)
        for doc in latest:
            print(f"Latest session ID: {doc.get('_id')}")
            print(f"Candidate: {doc.get('name')}")
            print(f"Answers saved: {len(doc.get('answers', []))}")
    except Exception as e:
        print("Error connecting to DB:", e)

if __name__ == "__main__":
    check()
