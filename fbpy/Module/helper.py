from retrying import retry
from os.path import exists
from io import BytesIO
import requests
import dataset


class Helper:

    @retry
    def getNum(self, k, i):
        """
        Get k Number and Validation From User where k can page or message
        """

        print("[+]", "Enter {} No:".format(k), "[+]")
        num = int(input(">>| "))

        if num + 1 <= i:
            return num - 1
        else:
            print("[+]", "Invalid {}".format(k), "[+]")
            raise Exception("Invalid {}".format(k))

    def storeImage(self, url):
        content = requests.get(url).content
        image = BytesIO(content)

        return image.read()


    def first(self, dbfile):
        if not exists(dbfile):
            print("[+] First time setup [+]")
            print("[+] Enter App ID [+]")
            appId = input(">>| ")
            print("[+] Enter App Secret [+]")
            appSecret = input(">>| ")


            db = dataset.connect("sqlite:///{}".format(dbfile))

            # store them
            table = db["app"]

            table.insert(
                {
                    "app_id": appId,
                    "app_secret": appSecret
                }
            )
