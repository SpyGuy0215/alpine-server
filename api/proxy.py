import requests
import firebase_admin
from firebase_admin import firestore, credentials
from api.constants import vals
import random


async def init_fbs():
    # Initialize the firebase app
    cred = credentials.Certificate("./api/serviceAccount.json")
    app = firebase_admin.initialize_app(cred)
    return app


async def refresh_proxies():
    app = await init_fbs()
    db = firestore.client()
    # get a list of proxy servers that are available
    response = requests.get(vals["domains"]["Proxy"]["ProxyScrape"])
    print(response.text.split("\r\n"))
    for proxy in response.text.split("\r\n"):
        query = db.collection("proxies").where("proxy", "==", proxy)
        if not query.get():
            random_id = None
            while (
                random_id is None
                or db.collection("proxies").where("id", "==", random_id).get()
            ):
                if random_id is not None:
                    print(f"ID {random_id} already exists")
                random_id = random.randint(0, 10000)
            print(f"Adding {proxy}")
            db.collection("proxies").add(
                {
                    "proxy": proxy,
                    "id": random_id,
                }
            )
    # cleanup!
    firebase_admin.delete_app(app)

    return "Proxies have been refreshed"


async def get_random_proxies():
    print("Getting random proxy")
    app = None
    app = await init_fbs()
    db = firestore.client()
    proxy = None
    rand_id = random.randint(0, 10000)
    while proxy is None:
        query = db.collection("proxies").where("id", "==", rand_id)
        if query.get():
            for doc in query.get():
                proxy = doc.to_dict()["proxy"]
        else:
            rand_id = random.randint(0, 10000)

    # cleanup!
    firebase_admin.delete_app(app)
    return proxy
