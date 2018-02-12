from facepy import GraphAPI
from facepy import get_extended_access_token

import dataset
import sys
import os
import argparse

from .Module.helper import Helper
from .exception import FacebookError, ValidationError, NotFoundError

class Poster:

    def __init__(self, db = "database/database.db"):
        # graph
        self.graph = None

        # helper
        self.helper = Helper()

        self.root = os.path.dirname(os.path.abspath(__file__))

        dbpath = os.path.join(self.root, db)

        self.__enter__()

        # first time run
        self.helper.first(dbpath)

        self.db = dataset.connect("sqlite:///{}".format(dbpath))

    def __enter__(self):
        dir = os.path.join(self.root, "database")

        if not os.path.exists(dir):
            os.mkdir(dir)


    def print(self, *msgs, style = '[+]'):
        msgs = list(msgs)
        size = len(msgs) * 5
        msg = " ".join( str(msg) for msg in msgs )

        print( "{:10} {:30} {:s}".format(style, msg, style) )

    def _initGraph(self, a_token):
        if self.graph is None:
            self.graph = GraphAPI(a_token)

    def aboutMe(self):
        check = self.graph.get(
        path = "me?fields=id,name",
        )

        return check["id"], check["name"]


    def getAppInfo(self):
        data = self.db["app"].all()

        for user in data:
            appId = user["app_id"]
            appSecret = user["app_secret"]

        return appId, appSecret


    def genLL(self, token):
        appId, appSecret = self.getAppInfo()

        self.print("Generating Live Long Token")

        # generate live long token
        token, expire = self._genLL(token, appId, appSecret)

        self.print("Token: {}".format(token))
        self.print("Expire: {}".format(expire))

        # store them with page id
        return token

    def addPage(self):
        # ask for user token, app id, secret etc
        self.print("Enter Page Token")
        self.print("https://developers.facebook.com/tools/explorer")
        token = input(">>| ")
        # then init graph and get info
        self._initGraph(token)
        # get my info
        id, name = self.aboutMe()

        self.print("ID: {}".format(id))
        self.print("Name: {}".format(name))

        token = self.genLL(token)

        data = self.db["token"]
        data.insert(
            {
                "pageId": id,
                "token": token,
                "name": name,
            }
        )

        self.print("Page Added!")

    def _genLL(self, token, appId, appSecret):
        try:
            return get_extended_access_token(token, appId, appSecret)
        except Exception as e:
            self.print(e)

    def getPages(self, display = True):
        token = self.db["token"].all()

        pages = []

        i = 0
        for d in token:
            if display:
                self.print("Name: {}".format(d["name"]))
                self.print("Token: {}".format(d["token"]))
                self.print("ID: {}".format(d["id"]))

            pages.append(d)

            i += 1

        if display:
            self.print("Total Pages: {}".format(i))

        return pages

    def _updateToken(self, token):
        self._initGraph(token)

        # get info
        id, name = self.aboutMe()

        # update token
        appId, appSecret = self.getAppInfo()

        token, expire = self._genLL(token, appId, appSecret)

        self._updateNewToken(id, token, name)

        return id, name, token, expire


    def updateToken(self, token = None):
        self.print("Updating Token:")
        self.print(token)

        if token is None:
            self.print("Enter Token")
            token = input(">>| ")

        id, name, token, expire = self._updateToken(token)

        self.print("ID:", id)
        self.print("Name:", name)
        self.print("Token:")
        self.print(token)
        self.print("Expire At:", expire)


    def _updateNewToken(self, pageId, token, name):
        table = self.db["token"]
        table.update(

        {
        "pageId": pageId, "token": token, "name": name,
        },

        ["pageId", "name"]
        )

    def getPage(self, match):
        pages = self.getPages(False)
        for page in pages:
            if match.lower() in page["name"].lower():
                return page

        raise ValidationError("Given Page is not found!")


    def _postPhotos(self, page = None, urls = None, cap = None, albumId = None):
        # search matching name of page
        page = self.getPage(page)

        # take id
        token = page["token"]
        # update and apply token
        self._updateToken(token)
        # message
        msg = cap

        # split url
        urls = urls.split(",")

        # print(urls)

        # check url
        if len(urls) > 1:
            path = "{}/photos".format(page["pageId"])
            published = False
            cap = None
        else:
            path = "me/photos"
            published = True


        # check for albums
        if not albumId is None:
            path = "{}/photos".format(albumId)


        lst = []
        i = 0
        ids = []
        for url in urls:
            check = self.graph.post(
            path = path,
            message = cap,
            published = published,
            url = url
            )

            ids.append(check["id"])

            if not published:
                # make list
                lst.append( {"media_fbid": check["id"]} )
                i += 1

        # call publish
        if not published:
            published = self._publishPhotos(lst, msg, "me/feed")

            return [published]
        return ids

    def postPhotos(self, page, urls, message = None, album = None):
        self.print("Posting Photos")
        if album:
            self.print("Album:", album)

        res = self._postPhotos(page, urls, message, album)
        for id in res:
            self.print("ID:", id)

    def _publishPhotos(self, lst, msg, path):

        # shoot a post
        chk = self.graph.post(
        path = path,
        message = msg,
        attached_media = lst
        )

        return chk["id"]


    def showAlbum(self, token = None, path="me/albums"):
        self._initGraph(token)
        req = self.graph.get(path)
        req = req["data"]

        for data in req:
            name = data["name"]
            id = data["id"]

            self.print("Name:", name)
            self.print("ID:", id)

    def _getAlbum(self, token, match, full = None, path = "me/albums"):
        self._initGraph(token)
        req = self.graph.get(path)
        req = req["data"]

        for data in req:
            name = data["name"].lower()
            id = data["id"]

            if full:
                if match.lower() == name:

                    return name, id
            else:
                if match.lower() in name:

                    return name, id

    def getAlbumId(self, token, name, full = None):

        self.print("Searching Album With Name:", name)


        check = self._getAlbum(token, name, full)

        if check is None:
            raise NotFoundError("Album: %s Is not Found!" % name)

        name, id = check

        self.print("Album Found!")
        self.print("Name:", name)
        self.print("ID:", id)

        return id
