from database.mongodb import MongoDB

def check():
    db = MongoDB()
    latest = list(db.interviews.find().sort("created_at", -1).limit(1))
    if latest:
        doc = latest[0]
        print("Candidate:", doc.get("name"))
        qs = doc.get("questions", [])
        print("Questions:")
        for q in qs:
            print("-", q.get("question"))
            
if __name__ == "__main__":
    check()
