class ReturnDTO:
    """return"""

    def __init__(self, msg, status):
        self.msg = msg
        self.status = status

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, dict_obj):
        return cls(**dict_obj)


class SessionTextDTO:
    def __init__(self, from_, text, image):
        self.from_ = from_
        self.text = text
        self.image = image

    def to_dict(self):
        # print(self.from_, self.text, self.image)
        return {"from": self.from_, "text": self.text, "image": self.image}

    @classmethod
    def from_dict(cls, dict_obj):
        return cls(from_=bool(dict_obj.get('from')), text=dict_obj.get('text'), image=dict_obj.get('image'))


class SessionRecordDTO:
    def __init__(self, session_id, session_date, session_texts, session_name):
        self.session_id = session_id
        self.session_date = session_date
        self.session_texts = [SessionTextDTO.from_dict(text) for text in session_texts]
        self.session_name = session_name

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "session_date": self.session_date,
            "session_texts": [text.to_dict() for text in self.session_texts],
            "session_name": self.session_name,
        }

    @classmethod
    def from_dict(cls, dict_obj):
        return cls(**dict_obj)


class DataDTO:
    def __init__(self, id, sign, pre_session_records):
        self.id = id
        self.sign = sign
        self.pre_session_records = [SessionRecordDTO.from_dict(record) for record in pre_session_records]

    def to_dict(self):
        return {
            "id": self.id,
            "sign": self.sign,
            "pre_session_records": [record.to_dict() for record in self.pre_session_records],
        }

    @classmethod
    def from_dict(cls, dict_obj):
        return cls(**dict_obj)
