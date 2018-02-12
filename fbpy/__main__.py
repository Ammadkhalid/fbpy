from .fb import Poster
import sys

def main():
    args = sys.argv
    p = Poster()

    if "--add" in args:
        p.addPage()

    if "--up" in args:
        p.updateToken()

    if len(args) <= 2:
        print("Usage: page name{ important } Image_Urls{ important } cap album_name")
        exit()

    page = args[1]
    token = p.getPage(page)["token"]
    imgs = args[2]
    cap = None
    album = None

    if len(args) >= 3:
        try:
            cap = args[3]
        except:
            pass


    if "-a" in args:
        name = True
    else:
        name = None

    if len(args) >= 4:
        try:
            album = p.getAlbumId(token, args[4], name)
        except:
            pass

    p.postPhotos(page, imgs, cap, album)

if __name__ == "__main__":
    main()
