import pandas
utils = {
    "db": False,
    "add": "",
    "document": [],
    "photo": [],
    "receiver": {},
    "mel": "",
    "videos": []
}


def save():
    albums = pandas.DataFrame(utils["receiver"], index=[0])
    albums.to_csv("receivers_info.csv", index=False)


def load():
    new_dict = {}
    df = pandas.read_csv("receivers_info.csv")
    for i in df:
        new_dict[int(i)] = df[i].values.tolist()[0]
    utils["receiver"] = new_dict
